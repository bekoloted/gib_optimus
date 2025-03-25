# Stephan doit me donner l'api à utiliser pour la Prédiction d'Éligibilité IA
# Ne pas oublié de donner ce codes à ChatGPT pour l'ajout des commentaires et pour bien renommer mes variables
# S'il y'a le temps on doit Dockeriser cet app
# A la fin du projet faut que je teste si 
# Penser à améliorer la orm_models.py
import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
from src.data_cleaner import clean_location_data
from src.database import init_db
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
from shapely.geometry import shape

def generate_geodata():
    """Données géospatiales fictives pour Douala"""
    arrondissements = {
        "Douala 1": {"coordinates": [[9.68, 4.04], [9.72, 4.04], [9.72, 4.07], [9.68, 4.07]]},
        "Douala 2": {"coordinates": [[9.72, 4.04], [9.76, 4.04], [9.76, 4.07], [9.72, 4.07]]},
        "Douala 3": {"coordinates": [[9.68, 4.01], [9.72, 4.01], [9.72, 4.04], [9.68, 4.04]]},
        "Douala 4": {"coordinates": [[9.72, 4.01], [9.76, 4.01], [9.76, 4.04], [9.72, 4.04]]},
        "Douala 5": {"coordinates": [[9.76, 4.01], [9.80, 4.01], [9.80, 4.04], [9.76, 4.04]]}
    }
    
    features = []
    for name, data in arrondissements.items():
        features.append({
            "type": "Feature",
            "properties": {"name": name},
            "geometry": {
                "type": "Polygon",
                "coordinates": [data["coordinates"]]
            }
        })
    
    geojson = {"type": "FeatureCollection", "features": features}
    os.makedirs("data", exist_ok=True)
    with open("data/douala_arrondissements.geojson", "w") as f:
        json.dump(geojson, f)
    
    return gpd.GeoDataFrame.from_features(geojson["features"])

def load_geodata():
    """Charge les données géospatiales avec fallback"""
    try:
        if not os.path.exists("data/douala_arrondissements.geojson"):
            return generate_geodata()
        return gpd.read_file("data/douala_arrondissements.geojson") #Me rapeller d'acheter ces datas de la ville de douala
    except Exception as e:
        st.warning(f"Chargement géodata échoué : {str(e)}")
        return generate_geodata()

def show_cartography():
    st.header("🌍 Cartographie des Donneurs")
    
    # Chargement des données
    @st.cache_data
    def load_data():
        engine = init_db()
        query = """
        SELECT donor_id, age, gender, district, neighborhood, 
               hemoglobin_level, eligibility_status
        FROM donneurs
        WHERE district IS NOT NULL
        """
        df = pd.read_sql(query, engine)
        return clean_location_data(df)  # Nettoyage des données
    
    df = load_data()
    
    # Filtres dans la sidebar
    with st.sidebar:
        st.subheader("Filtres Cartographiques")
        
        # Options d'arrondissements après nettoyage
        douala_districts = [f"Douala {i}" for i in range(1, 6)] + ['Non précisé']
        selected_districts = st.multiselect(
            "Arrondissements",
            options=douala_districts,
            default=douala_districts
        )
        
        age_range = st.slider(
            "Tranche d'âge",
            min_value=int(df['age'].min()),
            max_value=int(df['age'].max()),
            value=(20, 50)
        )
        
        show_other_cities = st.checkbox("Afficher les autres villes", False)
    
    # Application des filtres
    filtered_df = df[df['age'].between(*age_range)]
    if not show_other_cities:
        filtered_df = filtered_df[filtered_df['district'].isin(douala_districts)]
    if selected_districts:
        filtered_df = filtered_df[filtered_df['district'].isin(selected_districts)]
    
    # Carte interactive
    st.subheader("Répartition Géographique")
    gdf = load_geodata()
    
    # Compter les donneurs par arrondissement
    donors_count = filtered_df['district'].value_counts().reset_index()
    donors_count.columns = ['district', 'donors_count']
    
    # Fusion avec les données géospatiales
    gdf = gdf.merge(donors_count, left_on='name', right_on='district', how='left')
    gdf['donors_count'] = gdf['donors_count'].fillna(0)
    
    # Création de la carte
    fig = px.choropleth_mapbox(
        gdf,
        geojson=gdf.geometry,
        locations=gdf.index,
        color='donors_count',
        hover_name='name',
        hover_data={'donors_count': True},
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron",
        zoom=12,
        center={"lat": 4.0511, "lon": 9.7679},
        opacity=0.7,
        labels={'donors_count': 'Nombre de donneurs'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Autres visualisations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Donneurs par Arrondissement")
        fig = px.bar(
            donors_count.sort_values('donors_count'),
            x='district',
            y='donors_count',
            labels={'donors_count': 'Nombre de donneurs', 'district': 'Arrondissement'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Âge Moyen par Quartier")
        avg_age = filtered_df.groupby('neighborhood')['age'].mean().sort_values()
        fig = px.bar(
            avg_age,
            x=avg_age.values,
            y=avg_age.index,
            orientation='h',
            labels={'x': 'Âge moyen', 'y': 'Quartier'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Analyse approfondie
    st.subheader("Analyse Démographique")
    tab1, tab2, tab3 = st.tabs(["Âge", "Genre", "Statut Médical"])
    
    with tab1:
        fig, ax = plt.subplots()
        sns.histplot(filtered_df['age'], bins=20, kde=True, ax=ax)
        ax.set_title("Distribution des Âges")
        st.pyplot(fig)
    
    with tab2:
        gender_counts = filtered_df['gender'].value_counts()
        fig = px.pie(gender_counts, names=gender_counts.index, values=gender_counts.values)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = px.box(
            filtered_df,
            x='eligibility_status',
            y='hemoglobin_level',
            color='gender',
            points="all"
        )
        st.plotly_chart(fig, use_container_width=True)

def show_dashboard():
    st.set_page_config(
        page_title="Gib Optimus - Dashboard",
        page_icon="🩸",
        layout="wide"
    )

    with st.sidebar:
        st.header("🔍 Filtres Dynamiques")
        if st.button("📤 Aller à l'import des données", use_container_width=True):
            st.switch_page("pages/datas_uploader.py")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["🌍 Cartographie", "🏥 Santé", "📈 Campagnes", "🔄 Fidélisation", "💬 Sentiment", "🤖 Éligibilité IA"]
    )

    with tab1:
        """st.header("Cartographie des Donneurs")
        st.write("Visualisation géographique des donneurs")"""
        show_cartography()

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