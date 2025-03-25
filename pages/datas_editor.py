import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, inspect
from src.database import init_db
from models.orm_models import Base, Donneur
from src.data_cleaner import DataCleaner
import yaml
import os

# Configuration de la page
st.set_page_config(
    page_title="Gib Optimus - Éditeur de Données",
    page_icon="✏️",
    layout="wide"
)

# Chargement de la configuration
with open('config/settings.yaml') as f:
    config = yaml.safe_load(f)

# Initialisation des ressources
@st.cache_resource
def init_resources():
    engine = init_db(config['database']['uri'])
    cleaner = DataCleaner(config)
    return engine, cleaner

engine, cleaner = init_resources()

def load_data():
    """Charge uniquement les données principales avec vérification des colonnes"""
    try:
        inspector = inspect(engine)
        
        # Vérification de l'existence des tables
        if not inspector.has_table('donneurs'):
            Base.metadata.create_all(engine)
            return pd.DataFrame(columns=[c.name for c in Donneur.__table__.columns])
        
        # Chargement des colonnes existantes
        cols = inspector.get_columns('donneurs')
        existing_columns = [col['name'] for col in cols]
        
        # Construction de la requête avec seulement les colonnes existantes
        query = f"SELECT {', '.join(existing_columns)} FROM donneurs"
        df = pd.read_sql(query, engine)
        
        # Ajout des colonnes manquantes avec valeurs par défaut
        expected_columns = [c.name for c in Donneur.__table__.columns]
        for col in expected_columns:
            if col not in df.columns:
                if col in ['femme_enceinte', 'allaitement']:  # Colonnes booléennes
                    df[col] = False
                elif col in ['age', 'taux_hemoglobine']:  # Colonnes numériques
                    df[col] = 0
                else:  # Colonnes texte
                    df[col] = None
        
        return df
    
    except Exception as e:
        st.error(f"Erreur de chargement: {str(e)}")
        return pd.DataFrame()

def save_data(df):
    """Sauvegarde uniquement les colonnes principales"""
    try:
        # Filtrage des colonnes valides
        valid_columns = [c.name for c in Donneur.__table__.columns]
        df_to_save = df[[col for col in df.columns if col in valid_columns]]
        
        # Sauvegarde
        df_to_save.to_sql(
            name='donneurs',
            con=engine,
            if_exists='replace',
            index=False
        )
        st.success("✅ Données sauvegardées avec succès!")
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde: {str(e)}")

def main():
    st.title("✏️ Éditeur de Données")
    
    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Retour au Dashboard"):
            st.switch_page("dashboard.py")
    with col2:
        if st.button("📤 Aller à l'import"):
            st.switch_page("pages/datas_uploader.py")
    
    # Chargement des données
    df = load_data()
    
    if df.empty:
        st.warning("Aucune donnée trouvée. Importez d'abord des données.")
        return

    # Outils de nettoyage
    with st.expander("🔧 Outils de Nettoyage", expanded=True):
        cols = st.columns(3)
        
        with cols[0]:
            if st.checkbox("Corriger les noms de colonnes", False):
                df = cleaner.clean_column_names(df)
            
            if st.checkbox("Supprimer les doublons (ID)"):
                df = df.drop_duplicates(subset=['id'], keep='last')
                
        with cols[1]:
            if st.checkbox("Remplacer les valeurs manquantes"):
                df = cleaner.handle_missing_values(df)
                
        with cols[2]:
            if st.checkbox("Convertir les types de données"):
                df = cleaner.convert_data_types(df)
    
    # Édition des données
    st.subheader("📝 Édition des Données")
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        height=600,
        disabled=["id"]  # Bloque l'édition de l'ID
    )
    
    # Statistiques
    with st.expander("📊 Statistiques",True):
        st.write(f"Nombre d'enregistrements: {len(edited_df)}")
        st.dataframe(edited_df.describe(include='all'), use_container_width=True)
        
    # Actions
    st.divider()
    if st.button("💾 Sauvegarder les modifications", type="primary"):
        save_data(edited_df)
    

if __name__ == "__main__":
    """if st.button("Vérifier manuellement la DB"):
        st.write(pd.read_sql("SELECT * FROM donneurs LIMIT 50", engine))"""
    main()