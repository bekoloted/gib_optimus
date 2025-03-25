# dashboard.py
import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session

def show_dashboard():
    # Configuration de la page
    st.set_page_config(
        page_title="Gib Optimus - Dashboard",
        page_icon="🩸",
        layout="wide"
    )

    # Bouton de navigation dans la sidebar
    with st.sidebar:
        st.header("🔍 Filtres Dynamiques")
        
        # Bouton pour aller à l'interface d'import
        if st.button("📤 Aller à l'import des données", 
                    help="Accéder à l'interface d'import et de nettoyage des données",
                    use_container_width=True):
            st.switch_page(page="app/datas_uploader.py")

    # Onglets principaux
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["🌍 Cartographie", "🏥 Santé", "📈 Campagnes", "🔄 Fidélisation", "💬 Sentiment", "🤖 Éligibilité IA"]
    )

    with tab1:
        st.header("Cartographie des Donneurs")
        st.write("Visualisation géographique des donneurs")

    with tab2:
        st.header("Analyse Santé")
        st.write("Statistiques médicales des donneurs")

    with tab3:
        st.header("Performance des Campagnes")
        st.write("Analyse des campagnes de collecte")

    with tab4:
        st.header("Fidélisation des Donneurs")
        st.write("Suivi des donneurs réguliers")

    with tab5:
        st.header("Analyse de Sentiment")
        st.write("Feedback des donneurs")

    with tab6:
        st.header("Prédiction d'Éligibilité IA")
        st.write("Modèle prédictif d'éligibilité")

if __name__ == "__main__":
    show_dashboard()