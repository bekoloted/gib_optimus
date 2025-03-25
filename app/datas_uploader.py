import streamlit as st
from src.data_cleaner import DataCleaner
from src.database_handler import DatabaseHandler
from config.base import Base
import yaml
import pandas as pd
import os

# Chargement de la configuration
with open('config/settings.yaml') as f:
    config = yaml.safe_load(f)




def show_import():
    # Configuration de la page
    st.set_page_config(
        page_title="Gib Optimus - Import Data",
        page_icon="🩸",
        layout="centered"
    )

    # Bouton de retour au dashboard
    if st.button("⬅️ Retour au Dashboard", 
                help="Retourner à l'interface principale",
                use_container_width=True):
        st.switch_page(page="app/dashboard.py")

    st.title("📤 Importation des Données")
    
    # Téléchargement du fichier
    uploaded_file = st.file_uploader("Importer le fichier de données", type=["csv", "xlsx"])
    
    if uploaded_file:
        cleaner = DataCleaner(config)
        #df = cleaner.load_data(uploaded_file)
        df = pd.read_excel(uploaded_file)
        
        # Section de nettoyage
        with st.expander("Options de nettoyage"):
            if st.checkbox("Corriger les noms de colonnes",value=True):
                df = cleaner.clean_column_names(df)
                st.success("Noms de colonnes corrigés avec succès!")
                st.write("Nouvelles colonnes:", list(df.columns))
            if st.checkbox("Gérer les valeurs manquantes"):
                df = cleaner.handle_missing_values(df)
            if st.checkbox("Convertir les types de données"):
                df = cleaner.convert_data_types(df)
        
        # Aperçu des données
        st.subheader("Aperçu des données nettoyées")
        st.dataframe(df)
        
        # Sauvegarde dans la base de données
        if st.button("💾 Enregistrer dans la base de données"):
            db_handler = DatabaseHandler(config)
            with st.spinner("Sauvegarde en cours..."):
                try:
                    db_handler.save_to_database(df)
                    st.success("✅ Données sauvegardées!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erreur : {str(e)}")

if __name__ == "__main__":
    show_import()