import streamlit as st
import pandas as pd
import os
import requests
import plotly.graph_objects as go
from pathlib import Path

# Configuration de la page
# ============================
st.set_page_config(
    page_title="Dashboard d'Éligibilité Crédit",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================
# Chargement du CSV
# ============================
file_path = os.path.join(os.path.dirname(__file__), "dashboard_eligibilite2.csv")
df = pd.read_csv(file_path, sep=";")

#API_URL = "http://127.0.0.1:8000/predict" pour lancement local
API_URL = "https://bloc4-dashboard-credit.onrender.com/predict"
# CSS 
# ============================

st.markdown("""
<style>
    .stApp {
        background-color: #F5F6FA;
    }
    .header-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .form-card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #E3F2FD;
        width: 800px;
        margin: 60px auto;
        padding: 40px 50px;
    }
    .footer {
        background-color: #E0E0E0;
        padding: 15px;
        text-align: center;
        color: #616161;
        border-radius: 8px;
        margin-top: 40px;
    }
    .score-yes {
        background-color: #E8F5E9;
        color: #2E7D32;
        padding: 15px 40px;
        border-radius: 10px;
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        display: inline-block;
    }
    .score-no {
        background-color: #FFEBEE;
        color: #C62828;
        padding: 15px 40px;
        border-radius: 10px;
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ============================
# HEADER
logo_path = Path(__file__).parent / "logoPage.webp"


col_logo, col_title = st.columns([0.1, 0.9])

with col_logo:
    st.image(logo_path, width=60)  # Affiche le logo

with col_title:
    st.markdown("""
    <span style="color: #1976D2; font-size: 24px; font-weight: 500;">CréditApp</span>
    <h1 style="color: #212121; margin-bottom: 10px;">Dashboard d'Éligibilité Crédit Client</h1>
    <p style="color: #616161; margin: 0;">Saisissez l'ID client et les champs à afficher, puis prédisez son éligibilité.</p>
    """, unsafe_allow_html=True)

# ====== CSS pour aligner les colonnes ======
st.set_page_config(layout="wide")

st.markdown("""
<style>
/* CSS pour aligner colonnes */
div[data-testid="column"] > div {
    display: flex !important;
    flex-direction: column !important;
    justify-content: flex-start !important;
}

/* Champ ID client */
div[data-testid="stTextInput"] input {
    height: 42px !important;
    background-color: #000 !important;
    color: #fff !important;
    border-radius: 8px !important;
    border: 1px solid #B0BEC5 !important;
    padding: 0 12px !important;
    font-size: 14px !important;
}

/* Multiselect */
div[data-baseweb="select"] {
    height: 42px !important;
    background-color: #F0F2F6 !important;
    border-radius: 8px !important;
    border: 1px solid #B0BEC5 !important;
}

/* Bouton prédire */
.stButton>button {
    height: 42px !important;
    border-radius: 8px !important;
    background-color: #1976D2 !important;
    color: white !important;
    font-size: 14px !important;
    margin-top: 8px !important;
}
</style>
""", unsafe_allow_html=True)
col1, col2 = st.columns([1, 1])  # ajuster les largeurs

with col1:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("<p class='label'>ID client</p>", unsafe_allow_html=True)
    client_id_input = st.text_input(
        label="",
        value="Ex:123456",
        max_chars=6,
        placeholder="Ex: 123456",
        label_visibility="collapsed"
    )
    
    st.markdown("<div style='flex-grow:1'></div>", unsafe_allow_html=True)  
    predict_button = st.button("🔍 Prédire l’éligibilité", use_container_width=True)

    if predict_button:
        if not client_id_input.isdigit() or len(client_id_input) != 6:
            st.error("❌ ID client non valide. Veuillez saisir un identifiant à 6 chiffres.")
            st.stop()
        else:
            client_id = int(client_id_input)

with col2:
    # Ajouter un espace pour aligner visuellement
  #   st.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)
    st.markdown("<p class='label'>Champs à afficher</p>", unsafe_allow_html=True)
    cols_filtrables = [c for c in df.columns if c not in ['SK_ID_CURR', 'Score_Eligibilite', 'Prediction']]
    show_fields = st.multiselect(
        label="",
        options=cols_filtrables,
        default=[],
        placeholder="Ajouter des filtres..."
    )

st.markdown("</div>", unsafe_allow_html=True)


# RÉSULTATS
# ============================
if predict_button:
    client_row = df[df['SK_ID_CURR'] == client_id]

    
    if client_row.empty:
        st.error("❌ ID client invalide ou inexistant. Veuillez vérifier le numéro saisi.")
        st.stop()

    # Afficher les infos filtrées
    if show_fields:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("<h3 style='color: #616161;'>👤 Informations du client</h3>", unsafe_allow_html=True)
        st.dataframe(client_row[show_fields].T)
        st.markdown('</div>', unsafe_allow_html=True)

    # Appel API
    payload_cols = [
        'CODE_GENDER', 'NAME_FAMILY_STATUS', 'NAME_EDUCATION_TYPE',
        'OCCUPATION_TYPE', 'FLAG_OWN_CAR', 'FLAG_OWN_REALTY',
        'AMT_INCOME_TOTAL', 'AMT_CREDIT', 'AMT_ANNUITY', 'AMT_GOODS_PRICE',
        'DAYS_BIRTH', 'DAYS_EMPLOYED', 'DAYS_REGISTRATION',
        'DAYS_ID_PUBLISH', 'CNT_CHILDREN', 'EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3'
    ]
    payload = client_row.iloc[0][payload_cols].to_dict()

    response = requests.post(API_URL, json=payload)
    if response.status_code != 200:
        st.error(f"⚠️ Erreur API ({response.status_code}) : {response.text}")
        st.stop()

    result = response.json()
    score = float(result["Score_Eligibilite"])
    decision = result["Decision"]

    # ======================
    # JAUGE 
    # ======================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #616161;'>Score d'Éligibilité</h2>", unsafe_allow_html=True)

    # Couleur selon la décision
    if decision == "Yes":
        color = '#2E7D32'
        steps = [
            {'range': [0, 50], 'color': '#E8F5E9'},
            {'range': [50, 80], 'color': '#C8E6C9'},
            {'range': [80, 100], 'color': '#81C784'}
        ]
    else:
        color = '#C62828'
        steps = [
            {'range': [0, 50], 'color': '#FFCDD2'},
            {'range': [50, 80], 'color': '#EF9A9A'},
            {'range': [80, 100], 'color': '#E57373'}
        ]

    # Jauge Plotly
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score * 100,
        number={'suffix': "%", 'font': {'size': 60, 'color': color}},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': '#BDBDBD'},
            'bar': {'color': color},
            'steps': steps,
            'borderwidth': 2,
            'bordercolor': '#f0f0f0',
            'bgcolor': 'white'
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    st.plotly_chart(fig, use_container_width=True)

    status_class = "score-yes" if decision == "Yes" else "score-no"
    st.markdown(f"""
    <div style='text-align: center; margin: 20px 0;'>
        <div class='{status_class}'>{decision}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# FOOTER
# ============================
st.markdown("""
<div class="footer">
    🔒 Seules les informations nécessaires sont affichées pour respecter le RGPD.
</div>
""", unsafe_allow_html=True)