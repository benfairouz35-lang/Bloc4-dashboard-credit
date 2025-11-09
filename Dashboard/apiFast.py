from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from scipy.sparse import hstack, csr_matrix
from pathlib import Path


#  Chargement du modèle et métadonnées
# 
# chemin du dossier où se trouve ce script
BASE_DIR = Path(__file__).parent

# chargement des fichiers avec chemin relatif
model = joblib.load(BASE_DIR / "modele_xgboost_eligibilite_credit.pkl")
encoder = joblib.load(BASE_DIR / "encodeur_variables_categorielles.pkl")
colonnes_modele = joblib.load(BASE_DIR / "colonnes_modele.pkl")





app = FastAPI(
    title="API Éligibilité Crédit",
    description="Renvoie le score de probabilité d'acceptation d’un crédit client",
    version="1.0"
)


class ClientData(BaseModel):
    CODE_GENDER: str
    NAME_FAMILY_STATUS: str
    NAME_EDUCATION_TYPE: str
    OCCUPATION_TYPE: str
    FLAG_OWN_CAR: str
    FLAG_OWN_REALTY: str
    AMT_INCOME_TOTAL: float
    AMT_CREDIT: float
    AMT_ANNUITY: float
    AMT_GOODS_PRICE: float
    DAYS_BIRTH: int
    DAYS_EMPLOYED: float
    DAYS_REGISTRATION: float
    DAYS_ID_PUBLISH: float
    CNT_CHILDREN: int
    EXT_SOURCE_1: float | None = None
    EXT_SOURCE_2: float | None = None
    EXT_SOURCE_3: float | None = None


 
@app.post("/predict")
def predict(client: ClientData):
    try:
        df_client = pd.DataFrame([client.dict()])

        # Colonnes catégorielles et numériques
        cat_cols = ['CODE_GENDER', 'NAME_FAMILY_STATUS', 'NAME_EDUCATION_TYPE',
                    'OCCUPATION_TYPE', 'FLAG_OWN_CAR', 'FLAG_OWN_REALTY']
        num_cols = ['AMT_INCOME_TOTAL', 'AMT_CREDIT', 'AMT_ANNUITY',
                    'AMT_GOODS_PRICE', 'DAYS_BIRTH', 'DAYS_EMPLOYED',
                    'DAYS_REGISTRATION', 'DAYS_ID_PUBLISH', 'CNT_CHILDREN',
                    'EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3']

        # Encodage des variables catégorielles (avec même encoder qu’à l’entraînement)
        X_cat = encoder.transform(df_client[cat_cols])
        X_num = df_client[num_cols].fillna(0)

        # Fusionner numérique + catégoriel
        X_final = hstack([csr_matrix(X_num.to_numpy()), X_cat])

        # Vérifier et réaligner les colonnes au besoin
        n_input = X_final.shape[1]
        n_expected = len(colonnes_modele)
        if n_input != n_expected:
            raise HTTPException(
                status_code=400,
                detail=f"Mauvais format : attendu {n_expected} colonnes, reçu {n_input}"
            )

        # Prédiction de la probabilité
        proba = model.predict_proba(X_final)[0, 1]

        # 
        threshold = 0.3
        y_pred_class = int(proba >= threshold)  # 0 ou 1

        # Conversion en Yes/No comme dans le notebook
        decision = "Yes" if y_pred_class == 0 else "No"

        return {
            "Score_Eligibilite": round(float(proba), 4),
            "Decision": decision
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint racine

@app.get("/")
def home():
    return {"message": " API d'éligibilité crédit opérationnelle."}