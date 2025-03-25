import pandas as pd
import numpy as np
import re
from unidecode import unidecode

from typing import Dict, Optional

class DataCleaner:
    def __init__(self, config):
        self.config = config
        self._initialize_column_mappings()
        self._initialize_regex_patterns()

    def _initialize_column_mappings(self) -> None:
        """Définit le mapping complet des colonnes avec une structure plus claire"""
        self.column_mapping = {
            # Identifiants et dates
            "ID": "donor_id",
            "Horodateur": "timestamp",
            
            # Démographie
            "Age": "age",
            "Niveau_d'etude": "education_level",
            "Genre_": "gender",
            "Taille_": "height",
            "Poids": "weight",
            "Situation_Matrimoniale_(SM)": "marital_status",
            "Profession_": "profession",
            "Arrondissement_de_résidence_": "district",
            "Quartier_de_Résidence_": "neighborhood",
            "Nationalité_": "nationality",
            "Religion_": "religion",
            
            # Historique de don
            "A-t-il_(elle)_déjà_donné_le_sang_": "has_donated_before",
            "Si_oui_preciser_la_date_du_dernier_don._": "last_donation_date",
            
            # Données médicales
            "Taux_d’hémoglobine_": "hemoglobin_level",
            "ÉLIGIBILITÉ_AU_DON.": "eligibility_status",
            
            # Raisons d'indisponibilité
            "Raison_indisponibilité__[Est_sous_anti-biothérapie__]": "ineligibility_antibiotics",
            "Raison_indisponibilité__[Taux_d’hémoglobine_bas_]": "ineligibility_low_hemoglobin",
            "Raison_indisponibilité__[date_de_dernier_Don_<_3_mois_]": "ineligibility_recent_donation",
            "Raison_indisponibilité__[IST_récente_(Exclu_VIH,_Hbs,_Hcv)]": "ineligibility_recent_sti",
            
            # Données spécifiques aux femmes
            "Date_de_dernières_règles_(DDR)__": "last_menstrual_period",
            "Raison_de_l’indisponibilité_de_la_femme_[La_DDR_est_mauvais_si_<14_jour_avant_le_don]": "ineligibility_menstrual_period",
            "Raison_de_l’indisponibilité_de_la_femme_[Allaitement_]": "ineligibility_breastfeeding",
            "Raison_de_l’indisponibilité_de_la_femme_[A_accoucher_ces_6_derniers_mois__]": "ineligibility_recent_childbirth",
            "Raison_de_l’indisponibilité_de_la_femme_[Interruption_de_grossesse__ces_06_derniers_mois]": "ineligibility_recent_abortion",
            "Raison_de_l’indisponibilité_de_la_femme_[est_enceinte_]": "ineligibility_pregnancy",
            
            # Autres raisons
            "Autre_raisons,__preciser_": "other_reasons",
            "Sélectionner_\"ok\"_pour_envoyer_": "selection_ok",
            
            # Inéligibilités permanentes
            "Raison_de_non-eligibilité_totale__[Antécédent_de_transfusion]": "ineligibility_transfusion_history",
            "Raison_de_non-eligibilité_totale__[Porteur(HIV,hbs,hcv)]": "ineligibility_virus_carrier",
            "Raison_de_non-eligibilité_totale__[Opéré]": "ineligibility_recent_surgery",
            "Raison_de_non-eligibilité_totale__[Drepanocytaire]": "ineligibility_sickle_cell",
            "Raison_de_non-eligibilité_totale__[Diabétique]": "ineligibility_diabetes",
            "Raison_de_non-eligibilité_totale__[Hypertendus]": "ineligibility_hypertension",
            "Raison_de_non-eligibilité_totale__[Asthmatiques]": "ineligibility_asthma",
            "Raison_de_non-eligibilité_totale__[Cardiaque]": "ineligibility_heart_disease",
            "Raison_de_non-eligibilité_totale__[Tatoué]": "ineligibility_tattoo",
            "Raison_de_non-eligibilité_totale__[Scarifié]": "ineligibility_scarification",
            "Si_autres_raison_préciser_": "other_reasons_details",
        }

        # Inversé pour la recherche
        self.reverse_mapping = {v: k for k, v in self.column_mapping.items()}

    def _initialize_regex_patterns(self) -> None:
        """Prépare les motifs regex pour le nettoyage"""
        self.clean_patterns = [
            (r'[\[\]\(\)\/]', ''),       # Supprime les caractères spéciaux
            (r'[^A-Za-z0-9_]+', '_'),    # Remplace les séquences non alphanumériques
            (r'_+', '_'),                # Réduit les underscores multiples
            (r'^_|_$', ''),              # Supprime les underscores en début/fin
        ]

    def _normalize_column_name(self, col_name: str) -> str:
        """Normalise un nom de colonne selon plusieurs étapes"""
        # 1. Unidecode pour les caractères spéciaux
        normalized = unidecode(col_name)
        
        # 2. Application des regex
        for pattern, replacement in self.clean_patterns:
            normalized = re.sub(pattern, replacement, normalized)
            
        # 3. Standardisation finale
        normalized = normalized.strip().lower()
        
        return normalized

    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie et mappe les noms de colonnes selon le schéma défini
        
        Args:
            df: DataFrame à nettoyer
            
        Returns:
            DataFrame avec les noms de colonnes normalisés
        """
        # Création d'un mapping temporaire pour cette opération
        temp_mapping = {}
        
        for original_col in df.columns:
            # Étape 1: Normalisation du nom
            normalized = self._normalize_column_name(str(original_col))
            
            # Étape 2: Recherche du mapping le plus proche
            matched_key = self._find_best_match(original_col)
            
            # Étape 3: Utilisation du mapping ou nom normalisé
            temp_mapping[original_col] = self.column_mapping.get(matched_key, normalized)
        
        # Application du renommage
        return df.rename(columns=temp_mapping)

    def _find_best_match(self, col_name: str) -> Optional[str]:
        """
        Trouve la meilleure correspondance dans les clés du mapping
        
        Args:
            col_name: Nom de colonne original
            
        Returns:
            La clé du mapping la plus proche ou None
        """
        normalized_input = self._normalize_column_name(col_name)
        
        # Recherche exacte d'abord
        for mapping_key in self.column_mapping.keys():
            if self._normalize_column_name(mapping_key) == normalized_input:
                return mapping_key
                
        # Recherche approximative si rien trouvé
        for mapping_key in self.column_mapping.keys():
            if normalized_input in self._normalize_column_name(mapping_key):
                return mapping_key
                
        return None

    def get_expected_columns(self) -> Dict[str, str]:
        """Retourne les colonnes attendues avec leur description"""
        return {
            "donor_id": "Identifiant unique du donneur",
            "age": "Âge en années",
            "timestamp": "Horodateur de l'enregistrement",
            # ... ajoutez toutes les autres descriptions
        }
    #def clean_column_names(self, df):
        # Nettoyage des noms de colonnes
        #return df.rename(columns=lambda x: re.sub('[^A-Za-z0-9_]+', '', x).lower())
         
    
    def load_data(self, file):
        # Implémentation de la lecture de fichiers
        pass
    
    
    def handle_missing_values(self, df):
        # Implémentation de la gestion des valeurs manquantes
        return df.replace([np.inf, -np.inf], np.nan).fillna(
            self.config['missing_values_defaults']
        )
    
    def convert_data_types(self, df):
        # Conversion des types de données selon la configuration
        for col, dtype in self.config['dtype_conversions'].items():
            if col in df.columns:
                df[col] = df[col].astype(dtype)
        return df
    
def clean_location_data(df):
    """
    Nettoie et standardise les colonnes de localisation
    Args:
        df: DataFrame contenant les colonnes 'district' et 'neighborhood'
    Returns:
        DataFrame avec les données géographiques normalisées
    """
    # Dictionnaire de normalisation pour les arrondissements
    district_mapping = {
        r'douala\s*(\d)': 'Douala \\1',
        r'douala\s*\(.*\)': 'Douala (Non précisé)',
        r'non\s*précisé': 'Non précisé',
        r'pas\s*précisé': 'Non précisé',
        r'ras': 'Non précisé',
        r'west': 'Non précisé',
        r'yaounde': 'Yaoundé',
        r'yaoundé': 'Yaoundé',
        r'buea': 'Buéa',
        r'limbe': 'Limbé'
    }

    # Dictionnaire de normalisation pour les quartiers
    neighborhood_mapping = {
        r'ras': 'Non précisé',
        r'non\s*précisé': 'Non précisé',
        r'pas\s*précisé': 'Non précisé',
        r'deido': 'Deïdo',
        r'new\s*bell': 'New Bell',
        r'pk\d+': 'PK',
        r'ange\s*raphael': 'Ange Raphaël',
        r'douala\s*douala': 'Douala Centre'
    }

    # Normalisation des arrondissements
    df['district'] = df['district'].str.strip().str.title()
    for pattern, replacement in district_mapping.items():
        df['district'] = df['district'].str.replace(
            pattern, 
            replacement,
            case=False,
            regex=True
        )

    # Normalisation des quartiers
    if 'neighborhood' in df.columns:
        df['neighborhood'] = df['neighborhood'].str.strip().str.title()
        for pattern, replacement in neighborhood_mapping.items():
            df['neighborhood'] = df['neighborhood'].str.replace(
                pattern,
                replacement,
                case=False,
                regex=True
            )

    # Filtrage pour ne garder que Douala (optionnel) | Stephan doit tenir de cette histoire de neighborhood
    douala_districts = [f"Douala {i}" for i in range(1, 7)] + ['Douala (Non précisé)']
    df = df[df['district'].isin(douala_districts) | (df['district'] == 'Non précisé')]

    return df