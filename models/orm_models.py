from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Donneur(Base):
    __tablename__ = 'donneurs'
    
    # Identifiant
    donor_id = Column(String(50), primary_key=True)
    
    # Démographie
    age = Column(Integer)
    timestamp = Column(String)  # Format original préservé
    education_level = Column(String(100))  # Niveau d'étude
    gender = Column(String(20))  # Genre
    height = Column(Float)  # Taille (cm)
    weight = Column(Float)  # Poids (kg)
    marital_status = Column(String(50))  # Situation matrimoniale
    profession = Column(String(100))  # Profession
    
    # Localisation
    district = Column(String(100))  # Arrondissement
    neighborhood = Column(String(100))  # Quartier
    nationality = Column(String(50))  # Nationalité
    religion = Column(String(50))  # Religion
    
    # Historique de don
    has_donated_before = Column(String(10))  # Déjà donné (Oui/Non)
    last_donation_date = Column(String)  # Date dernier don (format original)
    
    # Données médicales
    hemoglobin_level = Column(Float)  # Taux d'hémoglobine
    eligibility_status = Column(String(50))  # Éligibilité
    
    # Raisons d'indisponibilité (booléens)
    ineligibility_antibiotics = Column(Boolean, default=False)  # Sous antibiotiques
    ineligibility_low_hemoglobin = Column(Boolean, default=False)  # Hb bas
    ineligibility_recent_donation = Column(Boolean, default=False)  # Don récent
    ineligibility_recent_sti = Column(Boolean, default=False)  # IST récente
    
    # Données spécifiques aux femmes
    last_menstrual_period = Column(String)  # Dernières règles
    ineligibility_menstrual_period = Column(Boolean, default=False)  # Règles récentes
    ineligibility_breastfeeding = Column(Boolean, default=False)  # Allaitement
    ineligibility_recent_childbirth = Column(Boolean, default=False)  # Accouchement récent
    ineligibility_recent_abortion = Column(Boolean, default=False)  # Avortement récent
    ineligibility_pregnancy = Column(Boolean, default=False)  # Grossesse
    
    # Autres
    other_reasons = Column(String)  # Autres raisons
    selection_ok = Column(String)  # Sélection OK
    
    # Inéligibilités permanentes
    ineligibility_transfusion_history = Column(Boolean, default=False)  # Antécédent transfusion
    ineligibility_virus_carrier = Column(Boolean, default=False)  # Porteur virus
    ineligibility_recent_surgery = Column(Boolean, default=False)  # Opération récente
    ineligibility_sickle_cell = Column(Boolean, default=False)  # Drépanocytose
    ineligibility_diabetes = Column(Boolean, default=False)  # Diabète
    ineligibility_hypertension = Column(Boolean, default=False)  # Hypertension
    ineligibility_asthma = Column(Boolean, default=False)  # Asthme
    ineligibility_heart_disease = Column(Boolean, default=False)  # Cardiopathie
    ineligibility_tattoo = Column(Boolean, default=False)  # Tatouage
    ineligibility_scarification = Column(Boolean, default=False)  # Scarification
    other_reasons_details = Column(String)  # Détails autres raisons

    # Relations (optionnelles)
    indisponibilites = relationship("Indisponibilite", back_populates="donneur", cascade="all, delete-orphan")
    ineligibilites = relationship("Ineligibilite", back_populates="donneur", cascade="all, delete-orphan")
    autres_raisons = relationship("AutreRaison", back_populates="donneur", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Donneur(donor_id={self.donor_id}, age={self.age}, status={self.eligibility_status})>"

class Indisponibilite(Base):
    __tablename__ = 'indisponibilites'
    
    id = Column(Integer, primary_key=True)
    donneur_id = Column(String(50), ForeignKey('donneurs.donor_id'))
    
    # Raisons d'indisponibilité
    sous_antibiotherapie = Column(Boolean, default=False)
    taux_hemoglobine_bas = Column(Boolean, default=False)
    don_recent = Column(Boolean, default=False)
    ist_recente = Column(Boolean, default=False)
    ddr_mauvais = Column(Boolean, default=False)
    
    donneur = relationship("Donneur", back_populates="indisponibilites")

class Ineligibilite(Base):
    __tablename__ = 'ineligibilites'
    
    id = Column(Integer, primary_key=True)
    donneur_id = Column(String(50), ForeignKey('donneurs.donor_id'))
    
    # Raisons d'inéligibilité permanente
    antecedent_transfusion = Column(Boolean, default=False)
    porteur_maladie = Column(Boolean, default=False)
    opere = Column(Boolean, default=False)
    drepanocytaire = Column(Boolean, default=False)
    diabetique = Column(Boolean, default=False)
    hypertendus = Column(Boolean, default=False)
    asthmatiques = Column(Boolean, default=False)
    cardiaque = Column(Boolean, default=False)
    tatoue = Column(Boolean, default=False)
    scarifie = Column(Boolean, default=False)
    
    donneur = relationship("Donneur", back_populates="ineligibilites")

class AutreRaison(Base):
    __tablename__ = 'autres_raisons'
    
    id = Column(Integer, primary_key=True)
    donneur_id = Column(String(50), ForeignKey('donneurs.donor_id'))
    description = Column(String(500))
    type = Column(String(20))  # 'indisponibilite' ou 'ineligibilite'
    
    donneur = relationship("Donneur", back_populates="autres_raisons")