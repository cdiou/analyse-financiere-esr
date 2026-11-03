# BLOC 1
import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import io
from datetime import datetime

# Configuration de la page en mode large avec icône d'onglet
st.set_page_config(page_title="Indicateurs Financiers ESR", page_icon="📊", layout="wide")

st.title("📊 Analyse Multi-Indicateurs des Opérateurs de l'ESR")

# MISE À JOUR : Nouveau nom de fichier par défaut
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
            st.error(f"Erreur lors de la lecture du fichier JSON : {e}")
            return pd.DataFrame()
    else:
        st.info("👋 Bienvenue ! Veuillez glisser le fichier de données dans la barre latérale pour initialiser l'application.")
        return pd.DataFrame()

df = load_api_json_local()

# Affichage de la date de mise à jour basée sur le nouveau fichier
if os.path.exists(FICHIER_JSON):
    timestamp_mod = os.path.getmtime(FICHIER_JSON)
    date_Fichier = datetime.fromtimestamp(timestamp_mod).strftime('%d/%m/%Y à %H:%M')
    st.write(f"📅 **Dernière mise à jour du fichier de données :** {date_Fichier}")
else:
    st.write("📅 **Aucun fichier de données chargé actuellement.**")

# BLOC 2A
# --- SYSTÈME DE MISE À JOUR PAR LE NAVIGATEUR ---
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

if os.path.exists(FICHIER_JSON):
    try:
        with open(FICHIER_JSON, "r", encoding="utf-8") as f:
            r_data = json.load(f)
        df = pd.DataFrame(r_data if isinstance(r_data, list) else r_data.get("results", []))
    except:
        df = pd.DataFrame()

if not df.empty:
    col_etab = "etablissement_lib"
    col_annee = "exercice"
    
    if "selected_etabs" not in st.session_state:
        st.session_state.selected_etabs = []
        
    df[col_annee] = pd.to_numeric(df[col_annee], errors='coerce')
    df = df.dropna(subset=[col_annee])
    df[col_annee] = df[col_annee].astype(int)
    
    st.sidebar.header("🎯 Filtres et Paramètres")
    liste_etab = sorted(df[col_etab].dropna().unique())
    
    # Alliances Historiques
    udice_targets = ["Aix-Marseille Université", "Université d'Aix-Marseille", "Sorbonne Université", "Université Claude Bernard - Lyon 1", "Université Lyon 1 - Claude Bernard", "Université Côte d'Azur", "Université Grenoble Alpes", "Université Paris Cité", "Université Paris sciences et lettres", "Université Paris Sciences et Lettres", "Université PSL", "Université de Bordeaux", "Université de Lorraine", "Université de Montpellier", "Université de Strasbourg", "Université Paris-Saclay"]
    udice_existants = [e for e in liste_etab if any(target.lower() in e.lower() for target in udice_targets) and not "paul" in e.lower()]

    initiative_targets = ["CY Cergy Paris Université", "Université de Cergy-Pontoise", "Université Clermont Auvergne", "Université Gustave Eiffel", "Université de Lille", "Université de Nantes", "Nantes Université", "Université de Pau et des Pays de l'Adour", "Université de Pau"]
    initiative_existants = [e for e in liste_etab if any(target.lower() in e.lower() for target in initiative_targets)]
	
# BLOC 2B
    # Configuration Strict du Groupe Supérieur
    sup_strict_targets = [
        "Aix-Marseille Université", "Université d'Aix-Marseille", "Sorbonne Université",
        "Université Claude Bernard - Lyon 1", "Université Lyon 1 - Claude Bernard", "Université Grenoble Alpes",
        "Université Paris Cité", "Université Paris-Saclay", "Université de Bordeaux", "Université de Lille",
        "Université de Lorraine", "Université de Montpellier", "Université de Strasbourg",
        "Université Toulouse III", "Université Toulouse III - Paul Sabatier", "Université de Toulouse"
    ]
    groupe_sup_existants = [
        e for e in liste_etab 
        if e in sup_strict_targets or any(t.lower() in e.lower() for t in ["toulouse iii", "paul sabatier"])
    ]

    # Configuration Strict du Groupe I
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

    # Configuration Strict du Groupe II
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

    # --- AFFICHAGE DES COMMANDES ---
    st.sidebar.subheader("🚀 Raccourcis Alliances")
    if st.sidebar.button("🎓 Alliance Udice"):
        st.session_state.selected_etabs = udice_existants
    if st.sidebar.button("✨ Alliance L'Initiative"):
        st.session_state.selected_etabs = initiative_existants
        
    st.sidebar.markdown("---")
    st.sidebar.subheader("🏛️ Groupes - Code de l'éducation")
    if st.sidebar.button("💎 Groupe Supérieur"):
        st.session_state.selected_etabs = groupe_sup_existants
    if st.sidebar.button("🏢 Groupe I"):
        st.session_state.selected_etabs = groupe_1_existants
    if st.sidebar.button("🏫 Groupe II"):
        st.session_state.selected_etabs = groupe_2_existants

    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Réinitialiser la sélection", type="primary"):
        st.session_state.selected_etabs = []

    st.sidebar.markdown("---")
    etabs_selectionnes = st.sidebar.multiselect("Sélection manuelle / ajustement :", options=liste_etab, key="selected_etabs")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Période d'analyse")
    min_annee = int(df[col_annee].min())
    max_annee = int(df[col_annee].max())
    
    intervalle_annees = st.sidebar.slider("Sélectionner l'intervalle d'années :", min_value=min_annee, max_value=max_annee, value=(min_annee, max_annee), step=1)
    annee_debut, annee_fin = intervalle_annees

    liste_annees_filtrees = sorted([a for a in df[col_annee].unique() if annee_debut <= a <= annee_fin], reverse=True)
    options_selectbox = [str(a) for a in liste_annees_filtrees]
    if not options_selectbox:
        options_selectbox = [str(a) for a in sorted(df[col_annee].unique(), reverse=True)]
    
    annee_selectionnee = st.sidebar.selectbox("Exercice cible pour les comparatifs bas :", options=options_selectbox, index=0 if options_selectbox else None)

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Options du graphique global")
    nb_top = st.sidebar.slider("Taille du Top National :", min_value=5, max_value=100, value=15, step=5)

# BLOC 3    
    exclusions = [col_annee, col_etab, "uai_identifiant", "code_de_la_commune", "code_de_l_academie", "code_de_la_region", "rce", "vague", "commune", "academie", "region", "etablissement_id_paysage", "source"]
    colonnes_numeriques = df.select_dtypes(include=['number']).columns.tolist()
    indicateurs_presents = [c for c in colonnes_numeriques if c not in exclusions]
    labels_propres = {c: c.replace('_', ' ').capitalize() for c in indicateurs_presents}
    
    if indicateurs_presents:
        st.subheader("📊 Sélection des indicateurs de performance")
        
        # Définition de l'indicateur cible par défaut
        indicateur_par_defaut = "resultat_net_comptable"
        valeurs_par_defaut = [indicateur_par_defaut] if indicateur_par_defaut in indicateurs_presents else [indicateurs_presents[0]]
        
        indicateurs_choisis = st.multiselect(
            "Sélectionnez UN ou DEUX indicateurs financiers à croiser :", 
            options=indicateurs_presents, 
            default=valeurs_par_defaut, 
            format_func=lambda x: labels_propres[x]
        )
        
        if not indicateurs_choisis:
            st.warning("⚠️ Veuillez sélectionner au moins un indicateur financier pour afficher les graphiques.")
        elif len(indicateurs_choisis) > 2:
            st.error("❌ Limitez votre sélection à deux indicateurs maximum pour préserver la visibilité.")
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
                    fig_line = px.line(df_melted, x=col_annee, y="Montant", color=col_etab, line_dash="Indicateur",
                                       title="Comparatif historique croisé (Continu = 1er indicateur, Pointillé = 2e indicateur)", markers=True)
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("💡 Sélectionnez des établissements à gauche pour tracer les courbes.")
                    
# BLOC 4    
            st.write("---")
            
            # Ajustement dynamique du titre avec l'année sélectionnée explicitement
            if 'annee_selectionnee' in locals() and annee_selectionnee:
                st.write(f"## 🏛️ Analyses Comparatives (Année {annee_selectionnee})")
            else:
                st.write("## 🏛️ Analyses Comparatives")
            
            if 'annee_selectionnee' in locals() and annee_selectionnee:
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
                        else:
                            st.warning("Aucune donnée disponible.")
                    else:
                        st.info("💡 Sélectionnez des établissements pour voir le classement personnalisé.")
                
                with graphe_col2:
                    st.write("### 🌐 Contexte National Global")
                    df_global_clean = df_annee_base.dropna(subset=indicateurs_choisis)
                    top_df = df_global_clean.nlargest(nb_top, indicateurs_choisis)
                    df_glob_melted = top_df.melt(id_vars=[col_etab], value_vars=indicateurs_choisis, var_name="Indicateur", value_name="Montant").dropna()
                    df_glob_melted["Indicateur"] = df_glob_melted["Indicateur"].map(labels_propres)
                    if not df_glob_melted.empty:
                        fig_bar_glob = px.bar(df_glob_melted, x="Montant", y=col_etab, color="Indicateur", barmode="group", orientation='h', title=f"Top National basé sur le premier indicateur")
                        fig_bar_glob.update_layout(yaxis={'categoryorder':'total ascending'}, height=300 + (nb_top * 20))
                        st.plotly_chart(fig_bar_glob, use_container_width=True)
                    else:
                        st.warning("Aucune donnée disponible.")
            else:
                st.info("💡 Veuillez charger un fichier de données pour afficher les graphiques comparatifs.")
                    
            st.write("---")
            df_table = df[(df[col_annee] >= annee_debut) & (df[col_annee] <= annee_fin)].copy()
            if etabs_selectionnes:
                df_table = df_table[df_table[col_etab].isin(etabs_selectionnes)]
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_table.to_excel(writer, index=False, sheet_name='Données Filtrées')
            buffer.seek(0)
            
            st.download_button(label="📥 Télécharger la sélection actuelle au format Excel", data=buffer, file_name="indicateurs_financiers_filtres.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            with st.expander("👀 Explorer la table brute des données"):
                df_table[col_annee] = df_table[col_annee].astype(str)
                st.dataframe(df_table)
    else:
        st.warning("Aucun indicateur financier majeur n'a pu être extrait.")
else:
    st.error("Le fichier de données est vide ou introuvable.")
