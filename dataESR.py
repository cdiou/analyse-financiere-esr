import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import io
from datetime import datetime

st.set_page_config(page_title="Indicateurs Financiers ESR", page_icon="📊", layout="wide")
st.title("📊 Analyse Multi-Indicateurs des Opérateurs de l'ESR")

FICHIER_JSON = "fr-esr-operateurs-indicateurs-financiers.json"

@st.cache_data
def load_api_json_local():
    if os.path.exists(FICHIER_JSON):
        try:
            with open(FICHIER_JSON, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            if isinstance(raw_data, list):
                return pd.DataFrame(raw_data)
            elif isinstance(raw_data, dict) and "results" in raw_data:
                return pd.DataFrame(raw_data["results"])
            else:
                st.error("Format de fichier non reconnu.")
                return pd.DataFrame()
        except Exception as e:
            st.error(f"Erreur : {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()

df = load_api_json_local()

if os.path.exists(FICHIER_JSON):
    timestamp_mod = os.path.getmtime(FICHIER_JSON)
    date_Fichier = datetime.fromtimestamp(timestamp_mod).strftime('%d/%m/%Y à %H:%M')
    st.write(f"📅 **Dernière mise à jour du fichier de données :** {date_Fichier}")
else:
    st.write("📅 **Aucun fichier de données chargé actuellement.**")
    st.info("👋 Bienvenue ! Veuillez glisser le fichier de données dans la barre latérale pour initialiser l'application.")

st.sidebar.header("🔄 Mise à jour du fichier")
url_ministere = "https://enseignementsup-recherche.gouv.fr"
st.sidebar.link_button("🌐 1. Télécharger via le Navigateur", url_ministere)
fichier_uploade = st.sidebar.file_uploader("2. Glissez le fichier JSON reçu ici :", type=["json"])

if fichier_uploade is not None:
    try:
        contenu_json = json.load(fichier_uploade)
        with open(FICHIER_JSON, "w", encoding="utf-8") as f:
            json.dump(contenu_json, f, ensure_ascii=False)
        st.sidebar.success("🎉 Fichier enregistré avec succès !")
        st.cache_data.clear()
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Fichier JSON invalide : {e}")

st.sidebar.markdown("---")

if not df.empty:
    col_etab = "etablissement_lib"
    col_annee = "exercice"
    df[col_annee] = pd.to_numeric(df[col_annee], errors='coerce')
    df = df.dropna(subset=[col_annee])
    df[col_annee] = df[col_annee].astype(int)
    
    st.sidebar.header("🎯 Filtres et Paramètres")
    liste_etab = sorted(df[col_etab].dropna().unique())
    
    udice_targets = ["Aix-Marseille Université", "Université d'Aix-Marseille", "Sorbonne Université", "Université Claude Bernard - Lyon 1", "Université Lyon 1 - Claude Bernard", "Université Côte d'Azur", "Université Grenoble Alpes", "Université Paris Cité", "Université Paris sciences et lettres", "Université Paris Sciences et Lettres", "Université PSL", "Université de Bordeaux", "Université de Lorraine", "Université de Montpellier", "Université de Strasbourg", "Université Paris-Saclay"]
    udice_existants = [e for e in liste_etab if any(target.lower() in e.lower() for target in udice_targets) and not "paul" in e.lower()]

    initiative_targets = ["CY Cergy Paris Université", "Université de Cergy-Pontoise", "Université Clermont Auvergne", "Université Gustave Eiffel", "Université de Lille", "Université de Nantes", "Nantes Université", "Université de Pau et des Pays de l'Adour", "Université de Pau"]
    initiative_existants = [e for e in liste_etab if any(target.lower() in e.lower() for target in initiative_targets)]
	
    auref_targets = [
        "Artois", "Angers", "Avignon", "Bordeaux Montaigne", "Bordeaux-Montaigne", 
        "Bretagne Sud", "Bretagne-Sud", "Caen Normandie", "Caen", "Corse", "Pasquale Paoli", 
        "Champollion", "Guyane", "Haute Alsace", "Haute-Alsace", "Mulhouse", "Polytechnique Hauts-de-France", 
        "Polytechnique des Hauts-de-France", "La Rochelle", "Le Havre", "Le Mans", "Limoges", 
        "Lumière Lyon 2", "Lumière - Lyon 2", "Jean Moulin Lyon 3", "Jean Moulin - Lyon 3", 
        "Mayotte", "Paul Valéry", "Paul-Valéry", "Montpellier 3", "Nîmes", "Unîmes", 
        "Paris 8", "Vincennes", "Orléans", "Pau", "Pays de l'Adour", "Perpignan", "Via Domitia", 
        "Picardie", "Jules Verne", "Poitiers", "Reims", "Champagne-Ardenne", "Rennes 2", 
        "Rouen", "Savoie Mont-Blanc", "Savoie Mont Blanc", "Jean Monnet", "Saint-Étienne", 
        "Saint-Etienne", "Toulon", "Tours", "Littoral", "Paris Nanterre", "Paris 10", "CNAM"
    ]
    auref_exclusions = [
        "comue", 
        "institut national des sciences appliquées", "insa", 
        "école nationale supérieure", 
        "école nationale d'ingénieur", "eni", 
        "toulouse capitole",
        "toulouse iii", "paul sabatier"
    ]
    auref_existants = [
        e for e in liste_etab 
        if any(target.lower() in e.lower() for target in auref_targets) 
        and not any(excl in e.lower() for excl in auref_exclusions)
    ]

    sup_strict_targets = [
        "Aix-Marseille Université", "Université d'Aix-Marseille", "Sorbonne Université",
        "Université Claude Bernard - Lyon 1", "Université Lyon 1 - Claude Bernard", "Université Grenoble Alpes",
        "Université Paris Cité", "Université Paris-Saclay", "Université de Bordeaux", "Université de Lille",
        "Université de Lorraine", "Université de Montpellier", "Université de Strasbourg",
        "Université Toulouse III", "Université Toulouse III - Paul Sabatier", "Université de Toulouse"
    ]
    groupe_sup_existants = [e for e in liste_etab if e in sup_strict_targets or any(t.lower() in e.lower() for t in ["toulouse iii", "paul sabatier"])]

    g1_strict_targets = [
        "CY Cergy Paris Université", "Université de Cergy-Pontoise", "Université d'Angers",
        "Université de Picardie Jules Verne", "Université d'Amiens", "Université de Franche-Comté", 
        "Université de Besançon", "Université Marie et Louis Pasteur", "Université de Bretagne Occidentale", 
        "Université de Brest", "Université de Caen Normandie", "Université de Caen", "Université Clermont Auvergne",
        "Université Côte d'Azur", "Université de Bourgogne", "Université de Dijon", "Université Gustave Eiffel",
        "Université de Limoges", "Université de Nantes", "Nantes Université", "Université d'Orléans",
        "Université Paris 1 - Panthéon Sorbonne", "Université Paris-I", "Université Paris I", "Université Paris Nanterre", 
        "Université Paris-X", "Université Paris 10", "Université Paris-Est Créteil", "Université Paris-XII", 
        "Université Paris 12", "Université Sorbonne Paris Nord", "Université Paris-XIII", "Université Paris 13",
        "Université de Poitiers", "Université de Reims Champagne-Ardenne", "Université de Reims", "Université de Rennes", 
        "Université de Rennes 1", "Université Rennes-I", "Université de Rouen Normandie", "Université de Rouen",
        "Université Toulouse - Jean Jaurès", "Université Toulouse II", "Université Toulouse-II", "Université de Tours"
    ]
    groupe_1_existants = [
        e for e in liste_etab 
        if (e in g1_strict_targets or any(t.lower() in e.lower() for t in ["picardie jules verne", "caen normandie", "panthéon sorbonne", "paris nanterre", "sorbonne paris nord", "reims champagne", "rouen normandie", "jean jaurès", "franche-comté", "marie et louis pasteur"]))
        and not any(ex in e.lower() for ex in ["institut national des sciences appliquées", "insa"])
    ]

    g2_strict_targets = [
        "Université des Antilles", "Université d'Artois", "Université d'Avignon", "Université Bordeaux Montaigne", 
        "Université Bordeaux-III", "Université Bordeaux 3", "Université de Bretagne Sud", "Université de Bretagne-Sud",
        "Université Savoie Mont Blanc", "Université de Chambéry", "Université de Corse Pasquale Paoli", "Université de Corse",
        "Université d'Evry Paris-Saclay", "Université d'Evry-Val d'Essonne", "Université d'Évry-Val-d'Essonne",
        "Université Le Havre Normandie", "Université du Havre", "Université de La Réunion", "Université de La Rochelle",
        "Université du Littoral", "Université du Littoral Côte d'Opale", "Université Lumière - Lyon 2", "Université Lumière Lyon 2", 
        "Université Lyon-II", "Université Lyon II", "Université Jean Moulin - Lyon 3", "Université Jean Moulin Lyon 3", 
        "Université Lyon-III", "Université Lyon III", "Le Mans Université", "Université du Mans", "Université de Montpellier Paul-Valéry", 
        "Université de Montpellier-Paul Valéry", "Université Montpellier-III", "Université Montpellier 3", "Université de Montpellier Paul-Val-ry", 
        "Université Paul-Valéry - Montpellier 3", "Université de Haute-Alsace", "Université de Haute Alsace", "Université de Mulhouse",
        "Université Panthéon-Assas", "Université Paris-II", "Université Paris II", "Université Sorbonne Nouvelle", "Université Paris-III", 
        "Université Paris III", "Université Paris 8", "Université Paris-VIII", "Université Paris VIII", "Université de Pau et des Pays de l'Adour", 
        "Université de Pau", "Université de Perpignan Via Domitia", "Université de Perpignan", "Université polytechnique Hauts-de-France", 
        "Université Polytechnique Hauts-de-France", "Université Rennes 2", "Université Rennes-II", "Université Rennes II", "Université Jean Monnet", 
        "Université Jean Monnet - Saint-Etienne", "Université Jean Monnet Saint-Étienne", "Université de Saint-Etienne", "Université de Saint-Étienne",
        "Université de Toulon", "Université Toulouse Capitole", "Université Toulouse-I", "Université Toulouse I", "Université Toulouse 1 Capitole",
        "Université de Versailles-Saint-Quentin-en-Yvelines", "Université de Versailles Saint-Quentin-en-Yvelines"
    ]
    groupe_2_existants = [
        e for e in liste_etab 
        if (e in g2_strict_targets or any(t.lower() in e.lower() for t in ["bordeaux montaigne", "savoie mont blanc", "pasquale paoli", "le havre normandie", "littoral côte", "lumière - lyon 2", "jean moulin - lyon 3", "le mans université", "paul-valéry", "haute-alsace", "panthéon-assas", "sorbonne nouvelle", "pays de l'adour", "via domitia", "polytechnique hauts-de-france", "jean monnet", "toulouse capitole", "versailles saint-quentin"]))
        and not any(ex in e.lower() for ex in ["institut national des sciences appliquées", "insa", "chimie", "ingénieur", "sciences po", "centrale"])
    ]

    type_sante_targets = [
        "Université de Poitiers", "Université Clermont Auvergne", "Université de Bretagne Occidentale", "Université de Brest",
        "Université Paris-Est Créteil", "Université de Caen Normandie", "Université de Caen", "Université des Antilles",
        "Université de Tours", "Université de Limoges", "Université de Montpellier", "Aix-Marseille Université",
        "Université d'Angers", "Université de Reims", "Université de Reims Champagne-Ardenne", "Université de Picardie Jules Verne",
        "Université d'Amiens", "Université Bourgogne Europe", "Université de Bourgogne", "Université de Dijon",
        "Université de Strasbourg", "Université Marie et Louis Pasteur", "Université de Franche-Comté", "Université de Besançon",
        "Université Jean Monnet", "Université Jean Monnet - Saint-Etienne", "Université Jean Monnet Saint-Étienne", "Université de Saint-Etienne",
        "Nantes Université", "Université de Nantes", "Université de Rouen Normandie", "Université de Rouen", "Université de La Réunion",
        "Université Sorbonne Paris Nord", "Université Paris-XIII", "Université Paris 13", "Université de Bordeaux", "Sorbonne Université",
        "Université de Lille", "Université Côte d'Azur", "Université Grenoble Alpes", "Université de Lorraine"
    ]
    type_sante_existants = [
        e for e in liste_etab 
        if (e in type_sante_targets or any(t.lower() in e.lower() for t in ["poitiers", "clermont auvergne", "bretagne occidentale", "créteil", "caen normandie", "antilles", "tours", "limoges", "montpellier", "versailles", "aix-marseille", "angers", "reims", "picardie", "bourgogne", "strasbourg", "franche-comté", "jean monnet", "nantes", "rouen", "réunion", "paris nord", "bordeaux", "sorbonne université", "lille", "côte d'azur", "grenoble alpes", "lorraine"]))
        and not any(ex in e.lower() for ex in ["paul-valéry", "chimie", "sciences po", "centrale", "technologie", "institut national des sciences appliquées", "insa", "normale supérieure", "ens", "école normale", "bibliothèque", "bnu", "comue", "observatoire", "supérieur", "géologie", "mines", "ponts", "aéronautique"])
    ]

    type_sans_sante_targets = [
        "Université d'Orléans", "Centre universitaire de formation et de recherche de Mayotte", "CUFR de Mayotte",
        "CY Cergy Paris Université", "Université de Cergy-Pontoise", "Université de Corse Pasquale Paoli", "Université de Corse",
        "Université Savoie Mont Blanc", "Université de Chambéry", "Université d'Evry Paris-Saclay", "Université d'Evry-Val d'Essonne",
        "Université Polytechnique Hauts-de-France", "Université polytechnique Hauts-de-France", "Université d'Artois",
        "Le Mans Université", "Université du Mans", "Avignon Université", "Université d'Avignon", "Université de Haute-Alsace",
        "Université de Haute Alsace", "Université de Mulhouse", "Université de Toulon", "Université de la Nouvelle-Calédonie",
        "Université de la Polynésie Française", "Université du Littoral Côte d'Opale", "Université du Littoral",
        "Université Bretagne Sud", "Université de Bretagne-Sud", "Université Le Havre Normandie", "Université du Havre",
        "Université de Pau et des Pays de l'Adour", "Université de Pau", "La Rochelle Université", "Université de La Rochelle",
        "Université de Perpignan Via Domitia", "Université de Perpignan", "Université Gustave Eiffel", "Nîmes université",
        "Université de Nîmes", "Université Paris sciences et lettres", "Université Paris Sciences et Lettres", "Université PSL",
        "Institut national universitaire Jean-François Champollion", "Institut National Universitaire Jean-François Champollion"
    ]
    type_sans_sante_existants = [
        e for e in liste_etab 
        if (e in type_sans_sante_targets or any(t.lower() in e.lower() for t in ["orléans", "mayotte", "cergy", "pasquale paoli", "savoie mont blanc", "chambéry", "evry", "évry", "polytechnique hauts-de-france", "valenciennes", "artois", "le mans université", "avignon", "haute-alsace", "toulon", "nouvelle-calédonie", "polynésie", "littoral côte d'opale", "bretagne sud", "le havre normandie", "pays de l'adour", "la rochelle", "via domitia", "gustave eiffel", "nîimes", "paris sciences et lettres", "psl", "champollion"]))
        and not any(ex in e.lower() for ex in ["chimie", "sciences po", "centrale", "technologie", "institut national des sciences appliquées", "insa", "lorraine", "lille", "bordeaux", "normale supérieure", "ens", "école normale", "comue"])
    ]

    type_science_med_targets = [
        "Université Claude Bernard - Lyon 1", "Université Lyon 1 - Claude Bernard", "Université Claude Bernard Lyon 1",
        "Université Paris Cité", "Université Paris-Saclay", "Université de Rennes", "Université de Rennes 1", "Université Rennes-I",
        "Université Toulouse III", "Université Toulouse III - Paul Sabatier", "Université de Toulouse", "Université Toulouse 3"
    ]
    type_science_med_existants = [
        e for e in liste_etab 
        if (e in type_science_med_targets or any(t.lower() in e.lower() for t in ["lyon 1", "lyon i", "paris cité", "paris-saclay", "rennes 1", "rennes-i", "toulouse iii", "paul sabatier"]))
        and not any(ex in e.lower() for ex in ["rennes 2", "lyon 2", "lyon 3", "toulouse 1", "toulouse 2", "chimie", "sciences po", "centrale", "technologie", "institut national des sciences appliquées", "insa", "normale supérieure", "ens", "école normale", "comue"])
    ]

    type_droit_eco_targets = [
        "Université Jean Moulin - Lyon 3", "Université Jean Moulin Lyon 3", "Université Lyon-III", "Université Lyon III",
        "Université Paris 1 - Panthéon Sorbonne", "Université Paris-I", "Université Paris I", "Université Paris 1",
        "Université Paris-Panthéon-Assas", "Université Panthéon-Assas", "Université Paris-II", "Université Paris II", "Université Paris 2",
        "Université Toulouse Capitole", "Université Toulouse-I", "Université Toulouse I", "Université Toulouse 1 Capitole"
    ]
    type_droit_eco_existants = [
        e for e in liste_etab 
        if e in type_droit_eco_targets or any(t.lower() in e.lower() for t in ["jean moulin", "lyon 3", "panthéon sorbonne", "paris 1", "panthéon-assas", "paris-assas", "paris 2", "toulouse capitole", "toulouse 1"])
        and not any(ex in e.lower() for ex in ["lyon 1", "lyon 2", "toulouse 2", "toulouse 3", "chimie", "sciences po", "centrale", "technologie", "institut national des sciences appliquées", "insa", "normale supérieure", "ens", "école normale", "comue"])
    ]

    type_lettres_targets = [
        "Université Bordeaux Montaigne", "Université Bordeaux-III", "Université Bordeaux 3",
        "Université Lumière - Lyon 2", "Université Lumière Lyon 2", "Université Lyon-II", "Université Lyon II",
        "Université Paris 8", "Université Paris-VIII", "Université Paris VIII",
        "Université Paris Nanterre", "Université Paris-X", "Université Paris 10",
        "Université Rennes 2", "Université Rennes-II", "Université Rennes II",
        "Université Sorbonne Nouvelle", "Université Paris-III", "Université Paris III",
        "Université Toulouse - Jean Jaurès", "Université Toulouse II", "Université Toulouse-II",
        "Université de Montpellier Paul-Valéry", "Université de Montpellier-Paul Valéry", "Université Montpellier-III", "Université Montpellier 3"
    ]
    type_lettres_existants = [
        e for e in liste_etab 
        if e in type_lettres_targets or any(t.lower() in e.lower() for t in ["bordeaux montaigne", "lumière - lyon 2", "paris 8", "vincennes", "nanterre", "paris 10", "rennes 2", "sorbonne nouvelle", "paris 3", "jean jaurès", "toulouse 2", "paul-valéry", "paul valéry", "montpellier 3"])
        and not any(ex in e.lower() for ex in ["lyon 1", "lyon 3", "toulouse 1", "toulouse 3", "montpellier 1", "bordeaux 1", "chimie", "sciences po", "centrale", "technologie", "institut national des sciences appliquées", "insa", "normale supérieure", "ens", "école normale", "comue"])
    ]

    etabs_groupes = set()
    st.sidebar.subheader("🚀 Alliances d'universités")
    if st.sidebar.checkbox("🎓 Alliance Udice"):
        etabs_groupes.update(udice_existants)
    if st.sidebar.checkbox("✨ Alliance L'Initiative"):
        etabs_groupes.update(initiative_existants)
    if st.sidebar.checkbox("🏫 Alliance Auref"):
        etabs_groupes.update(auref_existants)
        
    st.sidebar.subheader("🏛️ Groupes - Code de l'éducation")
    if st.sidebar.checkbox("💎 Groupe Supérieur"):
        etabs_groupes.update(groupe_sup_existants)
    if st.sidebar.checkbox("🏢 Groupe I"):
        etabs_groupes.update(groupe_1_existants)
    if st.sidebar.checkbox("🏫 Groupe II"):
        etabs_groupes.update(groupe_2_existants)

    st.sidebar.subheader("🧬 Typologie des Établissements")
    if st.sidebar.checkbox("🩺 Pluridisciplinaire avec santé"):
        etabs_groupes.update(type_sante_existants)
    if st.sidebar.checkbox("🍃 Pluridisciplinaire sans santé"):
        etabs_groupes.update(type_sans_sante_existants)
    if st.sidebar.checkbox("🔬 Scientifique et/ou médicale"):
        etabs_groupes.update(type_science_med_existants)
    if st.sidebar.checkbox("⚖️ Tertiaire - Droit et économie"):
        etabs_groupes.update(type_droit_eco_existants)
    if st.sidebar.checkbox("📚 Tertiaire - Lettres et SHS"):
        etabs_groupes.update(type_lettres_existants)

    st.sidebar.markdown("---")
    liste_pre_selectionnee = sorted(list(etabs_groupes))
    etabs_selectionnes = st.sidebar.multiselect("Sélection manuelle / ajustement :", options=liste_etab, default=liste_pre_selectionnee)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Période d'analyse")
    min_annee, max_annee = int(df[col_annee].min()), int(df[col_annee].max())
    intervalle_annees = st.sidebar.slider("Sélectionner l'intervalle d'années :", min_value=min_annee, max_value=max_annee, value=(min_annee, max_annee), step=1)
    annee_debut, annee_fin = intervalle_annees

    liste_annees_filtrees = sorted([a for a in df[col_annee].unique() if annee_debut <= a <= annee_fin], reverse=True)
    options_selectbox = [str(a) for a in liste_annees_filtrees]
    if not options_selectbox: options_selectbox = [str(a) for a in sorted(df[col_annee].unique(), reverse=True)]
    annee_selectionnee = st.sidebar.selectbox("Exercice cible pour les comparatifs bas :", options=options_selectbox, index=0 if options_selectbox else None)

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Options du graphique global")
    nb_top = st.sidebar.slider("Taille du Top National :", min_value=5, max_value=100, value=15, step=5)

    exclusions = [col_annee, col_etab, "uai_identifiant", "code_de_la_commune", "code_de_l_academie", "code_de_la_region", "rce", "vague", "commune", "academie", "region", "etablissement_id_paysage", "source"]
    colonnes_numeriques = df.select_dtypes(include=['number']).columns.tolist()
    indicateurs_presents = [c for c in colonnes_numeriques if c not in exclusions]
    labels_propres = {c: c.replace('_', ' ').capitalize() for c in indicateurs_presents}
    
    if indicateurs_presents:
        st.subheader("📊 Sélection des indicateurs de performance")
        indicateur_par_defaut = "resultat_net_comptable"
        valeurs_par_defaut = [indicateur_par_defaut] if indicateur_par_defaut in indicateurs_presents else [indicateurs_presents]
        indicateurs_choisis = st.multiselect("Sélectionnez UN ou DEUX indicateurs financiers à croiser :", options=indicateurs_presents, default=valeurs_par_defaut, format_func=lambda x: labels_propres[x])
        
        if not indicateurs_choisis:
            st.warning("⚠️ Veuillez sélectionner au moins un indicateur financier pour afficher les graphiques.")
        elif len(indicateurs_choisis) > 2:
            st.error("❌ Limitez votre sélection à deux indicateurs maximum.")
        else:
            st.write("---")
            st.write(f"## ⏱️ Évolution Historique Multilatérale ({annee_debut} - {annee_fin})")
            if etabs_selectionnes:
                df_evt = df[(df[col_etab].isin(etabs_selectionnes)) & (df[col_annee] >= annee_debut) & (df[col_annee] <= annee_fin)].sort_values(by=[col_etab, col_annee])
                df_evt[col_annee] = df_evt[col_annee].astype(str)
                df_melted = df_evt.melt(id_vars=[col_etab, col_annee], value_vars=indicateurs_choisis, var_name="Indicateur", value_name="Montant")
                df_melted["Indicateur"] = df_melted["Indicateur"].map(labels_propres)
                if len(etabs_selectionnes) == 1:
                    fig_line = px.line(df_melted, x=col_annee, y="Montant", color="Indicateur", title=f"Suivi annuel pour {etabs_selectionnes}", markers=True)
                else:
                    fig_line = px.line(df_melted, x=col_annee, y="Montant", color=col_etab, line_dash="Indicateur", title="Comparatif historique croisé", markers=True)
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("💡 Sélectionnez des établissements à gauche pour tracer les courbes.")
                    
            st.write("---")
            if annee_selectionnee:
                st.write(f"## 🏛️ Analyses Comparatives (Année {annee_selectionnee})")
                graphe_col1, graphe_col2 = st.columns(2)
                df_annee_base = df[df[col_annee] == int(annee_selectionnee)]
                
                with graphe_col1:
                    st.write("### 🎯 Zoom sur votre sélection")
                    if etabs_selectionnes:
                        df_selection_clean = df_annee_base[df_annee_base[col_etab].isin(etabs_selectionnes)]
                        df_sel_melted = df_selection_clean.melt(id_vars=[col_etab], value_vars=indicateurs_choisis, var_name="Indicateur", value_name="Montant").dropna()
                        df_sel_melted["Indicateur"] = df_sel_melted["Indicateur"].map(labels_propres)
                        if not df_sel_melted.empty:
                            fig_bar_sel = px.bar(df_sel_melted, x="Montant", y=col_etab, color="Indicateur", barmode="group", orientation='h', title="Structure interne du groupe")
                            fig_bar_sel.update_layout(yaxis={'categoryorder':'total ascending'}, height=300 + (len(df_selection_clean) * 25))
                            st.plotly_chart(fig_bar_sel, use_container_width=True)
                        else: st.warning("Aucune donnée disponible.")
                    else: st.info("💡 Sélectionnez des établissements.")
                
                with graphe_col2:
                    st.write("### 🌐 Contexte National Global")
                    df_global_clean = df_annee_base.dropna(subset=indicateurs_choisis)
                    if not df_global_clean.empty:
                        top_df = df_global_clean.nlargest(nb_top, indicateurs_choisis)
                        df_glob_melted = top_df.melt(id_vars=[col_etab], value_vars=indicateurs_choisis, var_name="Indicateur", value_name="Montant").dropna()
                        df_glob_melted["Indicateur"] = df_glob_melted["Indicateur"].map(labels_propres)
                        if not df_glob_melted.empty:
                            fig_bar_glob = px.bar(df_glob_melted, x="Montant", y=col_etab, color="Indicateur", barmode="group", orientation='h', title=f"Top National")
                            fig_bar_glob.update_layout(yaxis={'categoryorder':'total ascending'}, height=300 + (nb_top * 20))
                            st.plotly_chart(fig_bar_glob, use_container_width=True)
                        else: st.warning("Aucune donnée disponible.")
                    else: st.warning("Aucune donnée disponible pour cette année.")
            else: st.info("💡 Veuillez charger un fichier de données.")
                    
            st.write("---")
            df_table = df[(df[col_annee] >= annee_debut) & (df[col_annee] <= annee_fin)].copy()
            if etabs_selectionnes: df_table = df_table[df_table[col_etab].isin(etabs_selectionnes)]
            
            try:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_table.to_excel(writer, index=False, sheet_name='Données Filtrées')
                buffer.seek(0)
                st.download_button(label="📥 Télécharger la sélection actuelle au format Excel", data=buffer, file_name="indicateurs_financiers_filtres.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except ImportError: st.warning("⚠️ Installation requise de openpyxl.")
                
            with st.expander("👀 Explorer la table brute des données"):
                df_table[col_annee] = df_table[col_annee].astype(str)
                st.dataframe(df_table)
    else: st.warning("Aucun indicateur trouvé.")
else: st.error("Le fichier de données est vide ou introuvable.")
