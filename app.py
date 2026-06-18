import os
import requests
import tempfile
import textwrap
import urllib.parse
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

# Import analytical modules
from src.data_cleaning import clean_data
from src.pca_model import run_pca_analysis
from src.risk_calculator import calculate_water_quality_risk_index, match_bis_standard
from src.health_engine import analyze_district_health_hazards
from src.gemini_insights import answer_citizen_query, generate_treatment_recommendation
from src.gis_mapping import render_district_map, render_parameter_map
from src.pdf_generator import generate_district_pdf_report
from src.comparison_tool import render_comparison_tool

def clean_html(html_str):
    return "\n".join(line.strip() for line in html_str.split("\n") if line.strip())

# Page Configuration
st.set_page_config(
    page_title="GroundWater Guardian India",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling (SaaS Dark Theme: Stripe & Apple Weather inspired design)
st.markdown("""
    <style>
    /* Force high-end dark background on Streamlit elements */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background-color: #080c14 !important;
        color: #f3f4f6 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Hiding Streamlit navigation & default headers */
    [data-testid="sidebar"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    header {
        visibility: hidden;
    }
    
    /* Import Modern Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Custom style for native Streamlit selectbox container */
    div[data-testid="stSelectbox"] label {
        display: none !important;
    }
    div[data-testid="stSelectbox"] > div {
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        background-color: #111827 !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2) !important;
        color: #ffffff !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: transparent !important;
        color: #ffffff !important;
    }
    div[data-testid="stSelectbox"] svg {
        fill: #94a3b8 !important;
    }
    
    /* Style for dropdown menu option list */
    ul[role="listbox"] {
        background-color: #111827 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    li[role="option"] {
        color: #ffffff !important;
    }
    li[role="option"]:hover {
        background-color: #1f2937 !important;
    }
    
    /* Custom style for native download button to match design system */
    div[data-testid="stDownloadButton"] button {
        background-color: #3b82f6 !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        border: 1px solid #3b82f6 !important;
        transition: background-color 0.2s, border-color 0.2s !important;
        width: 100% !important;
    }
    div[data-testid="stDownloadButton"] button:hover {
        background-color: #2563eb !important;
        border-color: #2563eb !important;
        color: white !important;
    }
    
    /* Custom advisor input styling */
    div[data-testid="stForm"] {
        max-width: 700px !important;
        margin: 0 auto !important;
        border: 0 !important;
        background: transparent !important;
    }
    div[data-testid="stTextInput"] input {
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        background-color: #111827 !important;
        color: #ffffff !important;
    }
    div[data-testid="stFormSubmitButton"] button {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid #3b82f6 !important;
        font-weight: 700 !important;
    }
    
    /* Navigation Bar */
    .block-container {
        padding-top: 0rem !important;
        max-width: 1180px !important;
    }
    .navbar {
        position: sticky;
        top: 0;
        z-index: 20;
        background-color: rgba(8, 12, 20, 0.78);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 16px 28px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin: 0 -4rem 40px -4rem;
    }
    .brand {
        font-size: 1.25rem;
        font-weight: 800;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .brand-sub {
        font-size: 0.8rem;
        font-weight: 500;
        color: #94a3b8;
    }
    .nav-links {
        display: flex;
        gap: 22px;
        align-items: center;
    }
    .nav-links a {
        color: #cbd5e1 !important;
        text-decoration: none !important;
        font-size: 0.9rem;
        font-weight: 650;
    }
    .nav-links a:hover {
        color: #ffffff !important;
    }
    
    /* Hero Section */
    .hero-box {
        text-align: center;
        max-width: 900px;
        margin: 34px auto 22px auto;
        padding: 42px 20px 20px 20px;
    }
    .hero-box h1 {
        font-size: 4.15rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #ffffff 40%, #94a3b8 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        letter-spacing: -0.04em !important;
        margin-bottom: 12px !important;
        line-height: 1.1 !important;
    }
    .hero-box p {
        font-size: 1.28rem !important;
        color: #94a3b8 !important;
        margin-bottom: 0px !important;
        font-weight: 400 !important;
    }
    .hero-actions {
        margin-top: 28px;
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    
    /* Result card container */
    .result-container {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
        padding: 0 20px;
    }
    
    /* Apple Weather-style Result Card (Glassmorphic Dark) */
    .result-card {
        background-color: rgba(17, 24, 39, 0.75);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 35px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        text-align: center;
        width: 100%;
        max-width: 480px;
    }
    .result-layout {
        display: grid;
        grid-template-columns: minmax(320px, 0.75fr) minmax(420px, 1.25fr);
        gap: 24px;
        align-items: stretch;
        margin: 20px 0 46px 0;
    }
    .map-shell {
        background-color: rgba(17, 24, 39, 0.72);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 14px 14px 2px 14px;
        min-height: 600px;
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.28);
    }
    .section-kicker {
        color: #60a5fa;
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .section-title {
        color: #ffffff;
        font-size: 1.65rem;
        font-weight: 850;
        margin: 0 0 8px 0;
    }
    .section-copy {
        color: #94a3b8;
        margin: 0 0 22px 0;
        line-height: 1.55;
    }
    .nearby-card, .treatment-card {
        background-color: rgba(17, 24, 39, 0.68);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 22px;
        height: 100%;
    }
    .nearby-row {
        display: grid;
        grid-template-columns: 1fr auto auto;
        gap: 12px;
        align-items: center;
        padding: 12px 0;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
    .nearby-name {
        color: #f8fafc;
        font-weight: 750;
    }
    .nearby-meta {
        color: #94a3b8;
        font-size: 0.84rem;
        font-weight: 650;
    }
    .treatment-card div[data-testid="stMarkdownContainer"] {
        color: #dbeafe;
    }
    .result-category-badge {
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 6px 16px;
        border-radius: 30px;
        display: inline-block;
        margin-bottom: 15px;
    }
    .result-location {
        font-size: 1.8rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 5px;
    }
    .result-state {
        font-size: 0.95rem;
        color: #94a3b8;
        font-weight: 500;
        margin-bottom: 20px;
    }
    .score-title {
        font-size: 0.7rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 2px;
    }
    .score-display {
        display: flex;
        justify-content: center;
        align-items: baseline;
        margin-bottom: 8px;
    }
    .score-val {
        font-size: 4.5rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
    }
    .score-max {
        font-size: 1.5rem;
        font-weight: 600;
        color: #64748b;
        margin-left: 5px;
    }
    .result-status-badge {
        padding: 8px 20px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-block;
        margin-bottom: 20px;
    }
    .result-info-grid {
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        padding-top: 20px;
        text-align: left;
        font-size: 0.9rem;
    }
    .info-row {
        margin-bottom: 12px;
        display: flex;
        flex-direction: column;
        gap: 3px;
    }
    .info-label {
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        font-size: 0.7rem;
        letter-spacing: 0.05em;
    }
    .info-val {
        font-weight: 600;
        color: #e2e8f0;
    }
    
    /* Health Insight Cards Grid */
    .insight-card {
        background-color: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        display: flex;
        flex-direction: column;
        height: 100%;
        margin-bottom: 20px;
    }
    .insight-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 12px;
    }
    .insight-label {
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        font-size: 0.7rem;
        letter-spacing: 0.05em;
        margin-bottom: 2px;
    }
    .insight-val {
        font-size: 0.9rem;
        font-weight: 500;
        color: #94a3b8;
        margin-bottom: 15px;
        flex-grow: 1;
        line-height: 1.4;
    }
    .insight-badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.75rem;
        display: inline-block;
        width: fit-content;
    }
    .insight-badge.exceeded {
        background-color: rgba(220, 38, 38, 0.2);
        color: #fca5a5;
    }
    .insight-badge.normal {
        background-color: rgba(16, 185, 129, 0.2);
        color: #a7f3d0;
    }
    
    /* Comparison Card */
    .comp-card {
        background-color: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .anchor-offset {
        scroll-margin-top: 90px;
    }
    @media (max-width: 900px) {
        .navbar {
            margin: 0 -1rem 28px -1rem;
            padding: 14px 18px;
        }
        .nav-links {
            display: none;
        }
        .hero-box h1 {
            font-size: 2.65rem !important;
        }
        .result-layout {
            grid-template-columns: 1fr;
        }
        .map-shell {
            min-height: 460px;
        }
    }
    .comp-name {
        font-size: 1.4rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 5px;
    }
    .comp-score {
        font-size: 2.8rem;
        font-weight: 800;
        color: #ffffff;
        margin: 15px 0 5px 0;
    }
    
    /* State Alert Styling */
    .state-alert-custom {
        max-width: 480px;
        margin: 0 auto 20px auto;
        background-color: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(59, 130, 246, 0.3);
        color: #93c5fd;
        padding: 10px 16px;
        border-radius: 10px;
        text-align: center;
        font-size: 0.85rem;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# Register parent-level navigation listener in parent context using img onerror trick
st.markdown("""
    <img src="x" onerror="
        if (!window.__navigationListenerRegistered) {
            window.__navigationListenerRegistered = true;
            window.addEventListener('message', function(event) {
                if (event.data && event.data.type === 'navigate') {
                    window.location.href = event.data.url;
                }
            });
        }
    " style="display:none;" />
""", unsafe_allow_html=True)

# ----------------- SILENT BACKEND INITIATION -----------------
DEFAULT_EXCEL_PATH = "ground water quality dataset.xlsx"

@st.cache_resource(show_spinner=False)
def initialize_system_database():
    """Reads, cleans, aggregates, and computes PCA risk scores silently on startup."""
    if not os.path.exists(DEFAULT_EXCEL_PATH):
        raise FileNotFoundError(f"Missing core database file: {DEFAULT_EXCEL_PATH}")
        
    raw_data = pd.read_excel(DEFAULT_EXCEL_PATH)
    cleaned_df, clean_report = clean_data(raw_data, impute_method="median", outlier_action="cap")
    
    cols = cleaned_df.columns.tolist()
    district_col = next((c for c in cols if c.lower() in ["district", "dist"]), None)
    state_col = next((c for c in cols if c.lower() in ["state", "st"]), None)
    
    exclude_keywords = [
        "latitude", "longitude", "lat", "lon", "lng", "co-ordinate", "coordinate",
        "s. no.", "s.no.", "sno", "serial", "year", "location", "s.no", "serial number"
    ]
    exclude_cols = [district_col, state_col]
    for c in cols:
        c_l = c.lower()
        if any(kw in c_l for kw in exclude_keywords):
            if c not in exclude_cols:
                exclude_cols.append(c)
                
    water_cols = [c for c in cols if c not in exclude_cols and pd.api.types.is_numeric_dtype(cleaned_df[c])]
    
    pca_results = run_pca_analysis(cleaned_df, water_cols)
    risk_df, risk_weights = calculate_water_quality_risk_index(pca_results, cleaned_df)
    
    return risk_df, clean_report, pca_results, risk_weights, water_cols, district_col, state_col


def haversine_km(lat1, lon1, lat2, lon2):
    """Distance between two coordinates in kilometers."""
    radius_km = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * radius_km * np.arcsin(np.sqrt(a))


def find_safer_nearby_districts(df, active_row, district_col, state_col, limit=4):
    lat_col = next((c for c in df.columns if c.lower() in ["latitude", "lat"]), None)
    lon_col = next((c for c in df.columns if c.lower() in ["longitude", "lon", "lng"]), None)
    if not lat_col or not lon_col or pd.isnull(active_row.get(lat_col)) or pd.isnull(active_row.get(lon_col)):
        return pd.DataFrame()

    nearby = df[df[district_col] != active_row[district_col]].copy()
    nearby = nearby[nearby["Risk Score"] < active_row["Risk Score"]]
    if nearby.empty:
        return pd.DataFrame()

    nearby["Distance Km"] = haversine_km(
        active_row[lat_col],
        active_row[lon_col],
        nearby[lat_col].astype(float),
        nearby[lon_col].astype(float),
    )
    nearby["Nearby Rank"] = nearby["Risk Score"] + (nearby["Distance Km"] / 50.0)
    return nearby.sort_values(["Nearby Rank", "Risk Score"]).head(limit)[
        [district_col, state_col, "Distance Km", "Risk Score", "Risk Category"]
    ]


def get_pca_contributions(df, active_row, pca_results, risk_weights):
    """
    Computes the contribution percentage of each parameter to the WQRI score of the active district,
    based on its standardized z-scores and composite PCA loadings.
    """
    pos = df.index.get_loc(active_row.name)
    std_vals = pca_results["standardized_data"][pos]
    
    loadings = pca_results["loadings"]
    prepared_features = pca_results["prepared_features"]
    feature_names = prepared_features.columns.tolist()
    
    # Calculate composite loadings
    composite_loadings = np.zeros(len(feature_names))
    pc_keys = list(risk_weights.keys())
    pc_w = list(risk_weights.values())
    
    for i, pc in enumerate(pc_keys):
        w = pc_w[i]
        composite_loadings += loadings[pc].values * w
        
    # Element-wise contribution = std_val * composite_loading
    contributions = std_vals * composite_loadings
    
    # Filter for parameters contributing to elevated risk (> 0)
    contrib_list = []
    for idx, feat in enumerate(feature_names):
        clean_name = feat.split(" (")[0]
        # Clean up common representations like "pH" or "EC"
        if clean_name.lower() == "ph":
            clean_name = "pH Deviation"
        elif clean_name.lower() == "ec":
            clean_name = "Electrical Conductivity"
        val = contributions[idx]
        if val > 0:
            contrib_list.append((clean_name, val))
            
    # Fallback if no positive contribution (e.g. pristine water, z-scores negative)
    if not contrib_list:
        for idx, feat in enumerate(feature_names):
            clean_name = feat.split(" (")[0]
            if clean_name.lower() == "ph":
                clean_name = "pH Deviation"
            elif clean_name.lower() == "ec":
                clean_name = "Electrical Conductivity"
            contrib_list.append((clean_name, max(0.001, std_vals[idx])))
            
    # Sort by contribution descending
    contrib_list.sort(key=lambda x: x[1], reverse=True)
    
    # Normalize to percentages
    total = sum(c[1] for c in contrib_list)
    percentage_contribs = []
    for name, val in contrib_list:
        pct = (val / total) * 100 if total > 0 else 0.0
        percentage_contribs.append((name, pct))
        
    return percentage_contribs[:3] # Return top 3


def render_treatment_html(treatment_text):
    # Default values in case parsing fails
    concern = "Elevated chemical levels exceed limits"
    treatment = "Standard water filtration or Reverse Osmosis"
    advice = "Avoid raw drinking water. Filter or boil before consumption."
    severity = "Moderate"
    
    # Parse lines
    lines = [line.strip() for line in treatment_text.split("\n") if ":" in line]
    for line in lines:
        if ":" in line:
            parts = line.split(":", 1)
            k = parts[0].replace("**", "").replace("*", "").strip().lower()
            v = parts[1].replace("**", "").replace("*", "").strip()
            if "concern" in k:
                concern = v
            elif "treatment" in k:
                treatment = v
            elif "advice" in k:
                advice = v
            elif "severity" in k:
                severity = v
                
    # Determine badge color
    severity_lower = severity.lower()
    if "critical" in severity_lower or "immediate" in severity_lower:
        badge_bg = "rgba(220, 38, 38, 0.2)"
        badge_fg = "#fca5a5"
    elif "high" in severity_lower or "moderate" in severity_lower or "requires" in severity_lower:
        badge_bg = "rgba(217, 119, 6, 0.2)"
        badge_fg = "#fde68a"
    else:
        badge_bg = "rgba(22, 163, 74, 0.2)"
        badge_fg = "#a7f3d0"
        
    return clean_html(f"""
    <div class="treatment-card">
        <div class="section-kicker">Treatment Advice</div>
        <div class="section-title" style="font-size: 1.25rem;">What should you do?</div>
        <div style="margin-top: 18px; display: flex; flex-direction: column; gap: 12px;">
            <div>
                <span class="info-label">Primary Concern</span>
                <div style="color: #ffffff; font-weight: 650; font-size: 0.92rem; margin-top: 2px;">{concern}</div>
            </div>
            <div>
                <span class="info-label">Recommended Treatment</span>
                <div style="color: #60a5fa; font-weight: 650; font-size: 0.92rem; margin-top: 2px;">{treatment}</div>
            </div>
            <div>
                <span class="info-label">Household Action</span>
                <div style="color: #94a3b8; font-size: 0.85rem; line-height: 1.45; margin-top: 2px;">{advice}</div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 6px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.06);">
                <span class="info-label">Severity Level</span>
                <span class="insight-badge" style="background-color: {badge_bg}; color: {badge_fg}; font-size: 0.72rem; padding: 4px 10px; border-radius: 6px; font-weight: 700; text-transform: uppercase;">{severity}</span>
            </div>
        </div>
    </div>
    """)


# Silent database launch
try:
    risk_df, clean_report, pca_results, risk_weights, water_cols, district_col, state_col = initialize_system_database()
except Exception as e:
    st.error(f"System Ingestion Failure: {e}")
    st.stop()

# Initialize session state for searched or detected district & API key
if "active_district" not in st.session_state:
    st.session_state.active_district = "Salem" # default starting district
if "active_state" not in st.session_state:
    st.session_state.active_state = "Tamil Nadu" # default starting state

if "nvidia_api_key" not in st.session_state:
    if "NVIDIA_API_KEY" in st.secrets:
        st.session_state.nvidia_api_key = st.secrets["NVIDIA_API_KEY"]
    else:
        st.session_state.nvidia_api_key = os.environ.get("NVIDIA_API_KEY", "")

# ----------------- STANDALONE CHATBOT ROUTER -----------------
if "chat" in st.query_params:
    # Set page style optimized for chatbot popup
    st.markdown("""
        <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background-color: #0f172a !important; /* Slate 900 */
            color: #f1f5f9 !important;
            font-family: 'Inter', sans-serif !important;
        }
        header {
            visibility: hidden;
        }
        .chat-header {
            background-color: #1e293b;
            padding: 15px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            position: sticky;
            top: 0;
            z-index: 100;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    search_dist = st.query_params.get("search", "Salem")
    search_state = st.query_params.get("state", None)
    
    if search_state:
        dist_row = risk_df[(risk_df[district_col].str.lower() == search_dist.lower()) & (risk_df[state_col].str.lower() == search_state.lower())]
    else:
        dist_row = risk_df[risk_df[district_col].str.lower() == search_dist.lower()]
        
    if dist_row.empty:
        active_dist = "Salem"
        active_state = "Tamil Nadu"
    else:
        active_dist = dist_row.iloc[0][district_col]
        active_state = dist_row.iloc[0][state_col]
        
    st.markdown(f"""
        <div class="chat-header">
            <div style="font-weight: 800; font-size: 1.1rem; color: #ffffff;">🛡️ Guardian Advisor: {active_dist}, {active_state}</div>
            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 2px;">AI Water Quality Assistant</div>
        </div>
    """, unsafe_allow_html=True)
    
    if "standalone_chat_history" not in st.session_state:
        st.session_state.standalone_chat_history = [
            {"role": "assistant", "content": f"Hello! I am your GroundWater Guardian Advisor for **{active_dist}, {active_state}**. Ask me any questions about local safety, contaminant limits, or filtration recommendations."}
        ]
        
    for msg in st.session_state.standalone_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Ask a question about local water quality..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.standalone_chat_history.append({"role": "user", "content": prompt})
        
        with st.spinner("Analyzing..."):
            try:
                response = answer_citizen_query(
                    risk_df,
                    prompt,
                    active_dist,
                    water_cols,
                    api_key=st.session_state.nvidia_api_key,
                    active_state=active_state
                )
            except Exception as e:
                response = f"Error calling AI: {e}"
                
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.standalone_chat_history.append({"role": "assistant", "content": response})
        st.rerun()
    st.stop()

# ----------------- PARSE ROUTING QUERY PARAMETERS & SEARCH INPUT -----------------

# Helper function to geolocate user IP on backend (resilient to browser CORS/tracking blocks)
def geolocate_ip_python():
    urls = [
        "https://ipinfo.io/json",
        "https://ipapi.co/json/",
        "https://freeipapi.com/api/json"
    ]
    for url in urls:
        try:
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                data = res.json()
                if "loc" in data:
                    return data["loc"]
                lat = data.get("latitude")
                lon = data.get("longitude")
                if lat and lon:
                    return f"{lat},{lon}"
        except Exception:
            continue
    return None

# Helper function to resolve search query to a district/state
def resolve_search_query(query_str):
    cleaned_search = query_str.strip().lower()
    if not cleaned_search:
        return False
        
    if cleaned_search.startswith("coords:"):
        try:
            coord_part = query_str.split(":", 1)[1]
            lat_str, lon_str = coord_part.split(",", 1)
            user_lat = float(lat_str)
            user_lon = float(lon_str)
            
            lat_col = next((c for c in risk_df.columns if c.lower() in ["latitude", "lat"]), None)
            lon_col = next((c for c in risk_df.columns if c.lower() in ["longitude", "lon", "lng"]), None)
            
            if lat_col and lon_col:
                geo_df = risk_df.dropna(subset=[lat_col, lon_col])
                distances = haversine_km(user_lat, user_lon, geo_df[lat_col].astype(float), geo_df[lon_col].astype(float))
                min_idx = distances.idxmin()
                nearest_district = geo_df.loc[min_idx, district_col]
                nearest_state = geo_df.loc[min_idx, state_col]
                nearest_dist = distances.loc[min_idx]
                
                st.session_state.active_district = nearest_district
                st.session_state.active_state = nearest_state
                if nearest_dist > 500:
                    st.session_state.state_alert = f"Detected location is outside local region. Showing nearest registry district: **{nearest_district}** ({nearest_state}), approx. {nearest_dist:.0f} km away."
                else:
                    st.session_state.state_alert = f"Location matched to nearest district: **{nearest_district}** ({nearest_state})."
                return True
            else:
                st.session_state.state_alert = "Coordinate mapping columns missing in database."
                return False
        except Exception as ex:
            st.session_state.state_alert = f"Error matching coordinates: {ex}"
            return False
            
    if "," in cleaned_search:
        parts = [p.strip() for p in cleaned_search.split(",", 1)]
        d_search, s_search = parts[0], parts[1]
        exact_match = risk_df[(risk_df[district_col].str.lower() == d_search) & (risk_df[state_col].str.lower() == s_search)]
        if not exact_match.empty:
            st.session_state.active_district = exact_match.iloc[0][district_col]
            st.session_state.active_state = exact_match.iloc[0][state_col]
            return True
        else:
            st.session_state.state_alert = f"No match found for district '{d_search}' in state '{s_search}'."
            return False
    else:
        # Check if matches district name
        dist_match = risk_df[risk_df[district_col].str.lower() == cleaned_search]
        if not dist_match.empty:
            st.session_state.active_district = dist_match.iloc[0][district_col]
            st.session_state.active_state = dist_match.iloc[0][state_col]
            return True
        else:
            # Check if matches state name
            state_match = risk_df[risk_df[state_col].str.lower() == cleaned_search]
            if not state_match.empty:
                state_dists = risk_df[risk_df[state_col].str.lower() == cleaned_search].sort_values(by="Risk Score", ascending=False)
                st.session_state.active_district = state_dists.iloc[0][district_col]
                st.session_state.active_state = state_dists.iloc[0][state_col]
                st.session_state.state_alert = f"Showing highest risk district in **{state_dists.iloc[0][state_col]}**."
                return True
            else:
                # Check partial district match
                partial_match = risk_df[risk_df[district_col].str.lower().str.contains(cleaned_search)]
                if not partial_match.empty:
                    st.session_state.active_district = partial_match.iloc[0][district_col]
                    st.session_state.active_state = partial_match.iloc[0][state_col]
                    return True
                else:
                    st.session_state.state_alert = f"No match found for '**{query_str}**'. Please check spelling and try again."
                    return False

# 1. Process native search input if submitted
if "main_search_input" in st.session_state and st.session_state.main_search_input.strip():
    search_val = st.session_state.main_search_input.strip()
    resolve_search_query(search_val)
    st.query_params["search"] = f"{st.session_state.active_district}, {st.session_state.active_state}"
    # Reset the main_search_input widget value in session state to prevent looping
    st.session_state.main_search_input = ""
    st.rerun()

# 2. Check for search string passed via URL query parameter on startup
if "query_param_parsed" not in st.session_state:
    query_params = st.query_params
    if "search" in query_params:
        resolve_search_query(query_params["search"])
    st.session_state.query_param_parsed = True

# Set active district query parameter back to keep URL aligned
st.query_params["search"] = f"{st.session_state.active_district}, {st.session_state.active_state}"

# ----------------- BRANDING HEADER -----------------
st.markdown("""
    <div class="navbar">
        <div class="brand">
            <span>🛡️ GroundWater Guardian</span>
            <span class="brand-sub">India</span>
        </div>
        <nav class="nav-links">
            <a href="#home">Home</a>
            <a href="#compare">Compare</a>
            <a href="#health-risks">Health Risks</a>
            <a href="#national-trends">National Trends</a>
            <a href="#about">About</a>
        </nav>
    </div>
""", unsafe_allow_html=True)

# ----------------- SECTION 1: HERO SECTION -----------------
st.markdown("""
    <div id="home" class="hero-box anchor-offset">
        <h1>Know Your Drinking Water Risk</h1>
        <p>Instant groundwater safety assessment for Indian districts.</p>
    </div>
""", unsafe_allow_html=True)

# Centered Custom Search Container
col_left_space, col_search_main, col_right_space = st.columns([0.3, 3.4, 0.3])

with col_search_main:
    # Inject custom styling to make the native search input fit the SaaS dark mode theme perfectly
    st.markdown("""
        <style>
        div.st-key-main_search_input input {
            padding: 12px 18px !important;
            font-size: 0.95rem !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            background-color: rgba(17, 24, 39, 0.8) !important;
            color: #ffffff !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15) !important;
            transition: border-color 0.2s, box-shadow 0.2s !important;
        }
        div.st-key-main_search_input input:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3), 0 4px 6px rgba(0, 0, 0, 0.15) !important;
            outline: none !important;
        }
        div.st-key-main_search_input input::placeholder {
            color: #64748b !important;
        }
        /* Custom styling for the native Locate Me button */
        div.st-key-locate_me_button button {
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: #cbd5e1 !important;
            font-weight: 600 !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            cursor: pointer !important;
            font-size: 0.9rem !important;
            transition: background-color 0.2s, color 0.2s, border-color 0.2s !important;
            width: 100% !important;
            height: 44px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-sizing: border-box !important;
        }
        div.st-key-locate_me_button button:hover {
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: #ffffff !important;
            border-color: rgba(255, 255, 255, 0.2) !important;
        }
        div.st-key-locate_me_button button:active {
            background-color: rgba(255, 255, 255, 0.15) !important;
        }
        div.st-key-locate_me_button p {
            margin: 0 !important;
            line-height: 1 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col_input, col_loc = st.columns([3.5, 1])
    with col_input:
        # Native search input widget
        st.text_input(
            "Search District",
            value="",
            placeholder="🔍 Search district name (e.g. Salem, Patna...)",
            label_visibility="collapsed",
            key="main_search_input"
        )
    with col_loc:
        # Native Styled "Locate Me" button that runs geolocator in Python
        if st.button("📍 Locate Me", key="locate_me_button"):
            with st.spinner("Locating..."):
                coords = geolocate_ip_python()
                if coords:
                    resolve_search_query(f"coords:{coords}")
                    st.query_params["search"] = f"{st.session_state.active_district}, {st.session_state.active_state}"
                    st.rerun()
                else:
                    st.error("Failed to detect location automatically. Please search manually.")
    
    # Direct browse selectbox dropdowns
    st.write("") # small spacing
    col_drop_state, col_drop_dist = st.columns(2)
    with col_drop_state:
        selected_state = st.selectbox(
            "Select State",
            sorted(risk_df[state_col].unique()),
            index=sorted(risk_df[state_col].unique()).index(st.session_state.active_state) if st.session_state.active_state in risk_df[state_col].values else 0,
            key="main_state_select",
            label_visibility="collapsed"
        )
    with col_drop_dist:
        state_districts = sorted(risk_df[risk_df[state_col] == selected_state][district_col].unique())
        try:
            default_dist_idx = state_districts.index(st.session_state.active_district)
        except ValueError:
            default_dist_idx = 0
            
        selected_district = st.selectbox(
            "Select District",
            state_districts,
            index=default_dist_idx,
            key=f"main_district_select_{selected_state}",
            label_visibility="collapsed"
        )

    if selected_district != st.session_state.active_district or selected_state != st.session_state.active_state:
        st.session_state.active_district = selected_district
        st.session_state.active_state = selected_state
        st.query_params["search"] = f"{selected_district}, {selected_state}"
        st.rerun()
    
    # State redirect alert
    if "state_alert" in st.session_state and st.session_state.state_alert:
        st.markdown(f'<div class="state-alert-custom">{st.session_state.state_alert}</div>', unsafe_allow_html=True)
        del st.session_state.state_alert 

# ----------------- SECTION 2: SAFETY ASSESSMENT & DETAILS -----------------
active_row = risk_df[(risk_df[district_col] == st.session_state.active_district) & (risk_df[state_col] == st.session_state.active_state)].iloc[0]
hazards, risk_tier, dom_hazard, safety_status = analyze_district_health_hazards(active_row, water_cols)

score = active_row["Risk Score"]

# Mapping accent colors & badges based on risk level
if safety_status == "Immediate Attention Required":
    accent_color = "#dc2626"      # Red
    bg_light = "#fee2e2"          # Soft Red
    text_color = "#991b1b"        # Dark Red
    badge_label = "🔴 CRITICAL RISK"
elif safety_status == "Requires Filtration":
    accent_color = "#d97706"      # Orange
    bg_light = "#fef3c7"          # Soft Orange
    text_color = "#92400e"        # Dark Orange
    badge_label = "🟡 MODERATE RISK"
else:
    accent_color = "#16a34a"      # Green
    bg_light = "#d1fae5"          # Soft Green
    text_color = "#065f46"        # Dark Green
    badge_label = "🟢 LOW RISK"

primary_exceedance = active_row['Major Contributors'].split(', ')[0] if pd.notnull(active_row['Major Contributors']) else 'Within Standard Limits'

# Interventions mapping
ex_lower = active_row['Major Contributors'].lower() if pd.notnull(active_row['Major Contributors']) else ""
if "fluoride" in ex_lower:
    recomm = "Deploy domestic defluoridation systems (Activated Alumina). Avoid raw groundwater."
elif "arsenic" in ex_lower:
    recomm = "Prioritize deep tubewells tapping aquifers below clay boundaries."
elif "uranium" in ex_lower:
    recomm = "Deploy certified Reverse Osmosis (RO) filtration systems."
elif "nitrate" in ex_lower:
    recomm = "Avoid shallow well water for infant consumption (Blue Baby Syndrome risk)."
else:
    recomm = "Standard household water filtration (RO/carbon) is sufficient."

# Dashboard Columns
col_card, col_details = st.columns([1, 1.25], gap="large")

with col_card:
    st.markdown(f"""
        <div class="result-container" style="padding:0; margin:0;">
            <div class="result-card" style="border-top: 6px solid {accent_color}; max-width: 100%; width: 100%; box-sizing: border-box; margin:0;">
                <div class="result-category-badge" style="background-color: {bg_light}; color: {text_color};">
                    {badge_label}
                </div>
                <div class="result-location">{active_row[district_col]}</div>
                <div class="result-state">{active_row[state_col]}, India</div>
                <div class="score-title">Water Risk Score</div>
                <div class="score-display">
                    <span class="score-val">{score:.0f}</span>
                    <span class="score-max">/ 100</span>
                </div>
                <div class="result-status-badge" style="background-color: {bg_light}; color: {text_color};">
                    {safety_status}
                </div>
                <div class="result-info-grid">
                    <div class="info-row">
                        <span class="info-label">Primary Concern</span>
                        <span class="info-val">{primary_exceedance}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Recommendation</span>
                        <span class="info-val">{recomm}</span>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Personal Printable Report Card (PDF download wrapper)
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf_path = tmp.name
        generate_district_pdf_report(active_row, water_cols, pdf_path)
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        st.write("") # small spacing
        st.download_button(
            label="💾 Download Water Safety Report Card (PDF)",
            data=pdf_bytes,
            file_name=f"{st.session_state.active_district}_Water_Safety_Report_Card.pdf",
            mime="application/pdf",
            key="pdf_download_top"
        )
        os.unlink(pdf_path)
    except Exception as pdf_error:
        pass

with col_details:
    col_breakdown, col_treatment = st.columns(2)
    
    with col_breakdown:
        # Risk Contributors Breakdown using Z-score math
        percentage_contribs = get_pca_contributions(risk_df, active_row, pca_results, risk_weights)
        contrib_html = ""
        for name, pct in percentage_contribs:
            contrib_html += f"""
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
                    <span style="font-weight: 600; color: #cbd5e1;">{name}</span>
                    <span style="font-weight: 700; color: {accent_color};">{pct:.1f}%</span>
                </div>
                <div style="background-color: rgba(255, 255, 255, 0.05); height: 6px; border-radius: 3px; overflow: hidden;">
                    <div style="background-color: {accent_color}; width: {pct}%; height: 100%; border-radius: 3px;"></div>
                </div>
            </div>
            """
        if not contrib_html:
            contrib_html = "<div style='color: #64748b; font-size: 0.85rem; margin-top: 10px;'>No significant chemical contaminants detected. Water is within standard guidelines.</div>"
            
        breakdown_card_html = f"""
        <div class="nearby-card" style="height: 100%;">
            <div class="section-kicker">Risk Attribution</div>
            <div class="section-title" style="font-size: 1.2rem;">Why is my score high?</div>
            <div style="margin-top: 15px;">
                {contrib_html}
            </div>
        </div>
        """
        st.markdown(clean_html(breakdown_card_html), unsafe_allow_html=True)
        
    with col_treatment:
        # AI Treatment Advice Card
        treatment_cache_key = f"treatment_{active_row[district_col]}"
        if treatment_cache_key not in st.session_state:
            with st.spinner("Preparing treatment guidance..."):
                st.session_state[treatment_cache_key] = generate_treatment_recommendation(
                    active_row,
                    water_cols,
                    hazards,
                    api_key=st.session_state.nvidia_api_key
                )
        treatment_text = st.session_state[treatment_cache_key]
        treatment_card_html = render_treatment_html(treatment_text)
        st.markdown(treatment_card_html, unsafe_allow_html=True)

    # Safer Alternatives Card (full width of col_details)
    safer_nearby = find_safer_nearby_districts(risk_df, active_row, district_col, state_col)
    nearby_html = ""
    if safer_nearby.empty:
        nearby_html = """
        <div class="nearby-card" style="margin-top: 20px;">
            <div class="section-kicker">Safer Alternatives</div>
            <div class="section-title" style="font-size: 1.2rem;">Nearest lower-risk regions</div>
            <div style="margin-top: 15px; color: #94a3b8; font-size: 0.85rem;">No safer nearby districts were found in the database.</div>
        </div>
        """
    else:
        rows_html = ""
        for _, row in safer_nearby.iterrows():
            rows_html += f"""
            <div class="nearby-row">
                <div>
                    <div class="nearby-name">{row[district_col]}</div>
                    <div class="nearby-meta">{row[state_col]}</div>
                </div>
                <div class="nearby-meta">{row['Distance Km']:.0f} km</div>
                <div class="nearby-meta" style="color: #16a34a; font-weight: 700;">Score {row['Risk Score']:.0f}</div>
            </div>
            """
        nearby_html = f"""
        <div class="nearby-card" style="margin-top: 20px;">
            <div class="section-kicker">Safer Alternatives</div>
            <div class="section-title" style="font-size: 1.2rem;">Nearest lower-risk regions</div>
            <div style="margin-top: 10px;">
                {rows_html}
            </div>
        </div>
        """
    st.markdown(clean_html(nearby_html), unsafe_allow_html=True)


# ----------------- HEALTH HAZARDS & VULNERABILITY PROFILE -----------------
st.markdown(f"""
    <div id="health-risks" class="anchor-offset" style="margin-top:48px;">
        <div class="section-kicker" style="text-align:center;">Vulnerability Profile</div>
        <div class="section-title" style="text-align:center;">Chemical Contamination Risks in {active_row[district_col]}</div>
        <p class="section-copy" style="text-align:center;">Specific parameters exceeding standard guidelines and their health associations.</p>
    </div>
""", unsafe_allow_html=True)

if hazards:
    insight_cols = st.columns(min(3, len(hazards)))
    for idx, hz in enumerate(hazards[:3]): # top 3
        with insight_cols[idx % 3]:
            st.markdown(f"""
                <div class="insight-card">
                    <div class="insight-title">{hz['parameter']}</div>
                    <div class="insight-label">Status</div>
                    <div class="insight-val">Above Recommended Limit</div>
                    <div class="insight-label">Associated Concern</div>
                    <div class="insight-val">{hz['title']}</div>
                    <div class="insight-label">Severity</div>
                    <div class="insight-badge exceeded">{hz['severity']} Concentration</div>
                </div>
            """, unsafe_allow_html=True)
else:
    col_ins_l, col_ins_c, col_ins_r = st.columns([1, 2, 1])
    with col_ins_c:
        st.markdown(f"""
            <div class="insight-card" style="text-align:center; padding:30px;">
                <div class="insight-title" style="color:#16a34a;">🟢 All Parameters Within Guidelines</div>
                <div class="insight-val">Measured chemical parameters do not exceed standard acceptable guidelines in {active_row[district_col]}. General water supply poses low cumulative health risks.</div>
            </div>
        """, unsafe_allow_html=True)


# ----------------- SECTION 6: INTERACTIVE INDIA MAP -----------------
st.markdown("""
    <div id="map-section" class="anchor-offset" style="margin-top:48px;">
        <div class="section-kicker" style="text-align:center;">Interactive Map</div>
        <div class="section-title" style="text-align:center;">National Water Safety Explorer</div>
        <p class="section-copy" style="text-align:center;">Click on any district on the map to update the safety assessment and analysis details above.</p>
    </div>
""", unsafe_allow_html=True)

with st.spinner("Rendering interactive map..."):
    fig_map = render_district_map(
        risk_df,
        district_col=district_col,
        state_col=state_col,
        score_col="Risk Score",
        category_col="Risk Category"
    )
    fig_map.update_layout(height=650, margin=dict(l=0, r=0, t=10, b=10))
    event_map = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun")

if event_map and "selection" in event_map and "points" in event_map["selection"] and len(event_map["selection"]["points"]) > 0:
    point = event_map["selection"]["points"][0]
    clicked_district = None
    clicked_state = None
    if "hovertext" in point:
        clicked_district = point["hovertext"]
    elif "location" in point:
        clicked_district = point["location"]
    elif "customdata" in point and len(point["customdata"]) > 0:
        clicked_district = point["customdata"][0]
        
    if "customdata" in point and len(point["customdata"]) > 0:
        clicked_state = point["customdata"][0]
        
    if clicked_district:
        if clicked_state:
            dist_match = risk_df[(risk_df[district_col].str.lower() == clicked_district.strip().lower()) & (risk_df[state_col].str.lower() == clicked_state.strip().lower())]
        else:
            dist_match = risk_df[risk_df[district_col].str.lower() == clicked_district.strip().lower()]
            
        if not dist_match.empty:
            st.session_state.active_district = dist_match.iloc[0][district_col]
            st.session_state.active_state = dist_match.iloc[0][state_col]
            st.query_params["search"] = f"{st.session_state.active_district}, {st.session_state.active_state}"
            st.rerun()


# ----------------- SECTION 8: DISTRICT COMPARISON -----------------
st.markdown("""
    <div id="compare" class="anchor-offset" style="margin-top:48px;">
        <div class="section-kicker" style="text-align:center;">Comparison Tool</div>
        <div class="section-title" style="text-align:center;">Side-by-Side District Comparison</div>
        <p class="section-copy" style="text-align:center;">Select any two districts to compare risk indexes and standard chemical deviations.</p>
    </div>
""", unsafe_allow_html=True)

render_comparison_tool(risk_df, state_col, district_col, water_cols)

# ----------------- SECTION 7: FLOATING AI ADVISOR -----------------
st.markdown(f"""
    <style>
    .custom-chat-fab {{
        position: fixed;
        bottom: 24px;
        right: 24px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white !important;
        border-radius: 50%;
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 26px;
        cursor: pointer;
        z-index: 999999;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-decoration: none !important;
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    .custom-chat-fab:hover {{
        transform: scale(1.08);
        box-shadow: 0 10px 28px rgba(59, 130, 246, 0.6);
        color: white !important;
    }}
    </style>
    <a class="custom-chat-fab" 
       href="/?chat=1&search={urllib.parse.quote(st.session_state.active_district)}&state={urllib.parse.quote(st.session_state.active_state)}" 
       target="_blank" 
       onclick="window.open(this.href, 'GroundWaterGuardianAI', 'width=450,height=650,menubar=no,toolbar=no,location=no,status=no,resizable=yes'); return false;">
       💬
    </a>
""", unsafe_allow_html=True)

# ----------------- NATIONAL TRENDS -----------------
st.markdown("<div style='margin-top:60px;'></div>", unsafe_allow_html=True)

with st.expander("National Trends & Contaminant Explorer"):
    st.markdown("""
        <div id="national-trends" class="anchor-offset">
            <div class="section-kicker">National Trends</div>
            <div class="section-title">Registry statistics</div>
        </div>
    """, unsafe_allow_html=True)
    
    col_reg1, col_reg2 = st.columns(2)
    with col_reg1:
        st.markdown("##### Top 10 Most Affected Districts")
        worst_tbl = risk_df.sort_values(by="Risk Score", ascending=False).head(10)[[district_col, state_col, "Risk Score", "Risk Category", "Major Contributors"]]
        worst_tbl.columns = ["District", "State", "Water Risk Score", "Hazard Level", "Primary Contaminants"]
        st.dataframe(worst_tbl, width="stretch", hide_index=True)
    with col_reg2:
        st.markdown("##### Top 10 Safest Districts")
        safest_tbl = risk_df.sort_values(by="Risk Score", ascending=True).head(10)[[district_col, state_col, "Risk Score", "Risk Category", "Major Contributors"]]
        safest_tbl.columns = ["District", "State", "Water Risk Score", "Hazard Level", "Primary Contaminants"]
        st.dataframe(safest_tbl, width="stretch", hide_index=True)
        
    st.markdown("---")
    st.markdown("#### National Chemical Maps")
    
    EXPLORER_PARAMS = {
        "Fluoride": {"col": "F (mg/L)", "scale": "Oranges"},
        "Arsenic": {"col": "As (ppb)", "scale": "Reds"},
        "Uranium": {"col": "U (ppb)", "scale": "Purples"},
        "Nitrate": {"col": "NO3", "scale": "Blues"},
        "Iron": {"col": "Fe (ppm)", "scale": "YlOrBr"},
        "Total Hardness": {"col": "Total Hardness", "scale": "Greys"},
        "pH": {"col": "pH", "scale": "RdYlBu"}
    }
    
    selected_param = st.selectbox("Select Contaminant Map:", list(EXPLORER_PARAMS.keys()))
    p_info = EXPLORER_PARAMS[selected_param]
    
    with st.spinner(f"Drawing map for {selected_param}..."):
        fig_p = render_parameter_map(
            risk_df,
            param_col=p_info['col'],
            district_col=district_col,
            state_col=state_col,
            color_scale=p_info['scale']
        )
        event_p = st.plotly_chart(fig_p, width="stretch", on_select="rerun")
        if event_p and "selection" in event_p and "points" in event_p["selection"] and len(event_p["selection"]["points"]) > 0:
            point = event_p["selection"]["points"][0]
            clicked_district = None
            clicked_state = None
            if "hovertext" in point:
                clicked_district = point["hovertext"]
            elif "location" in point:
                clicked_district = point["location"]
            elif "customdata" in point and len(point["customdata"]) > 0:
                clicked_district = point["customdata"][0]
                
            if "customdata" in point and len(point["customdata"]) > 0:
                clicked_state = point["customdata"][0]
                
            if clicked_district:
                if clicked_state:
                    dist_match = risk_df[(risk_df[district_col].str.lower() == clicked_district.strip().lower()) & (risk_df[state_col].str.lower() == clicked_state.strip().lower())]
                else:
                    dist_match = risk_df[risk_df[district_col].str.lower() == clicked_district.strip().lower()]
                    
                if not dist_match.empty:
                    st.session_state.active_district = dist_match.iloc[0][district_col]
                    st.session_state.active_state = dist_match.iloc[0][state_col]
                    st.query_params["search"] = f"{st.session_state.active_district}, {st.session_state.active_state}"
                    st.rerun()

# Footer
st.markdown("""
    <div id="about" class="anchor-offset" style="text-align:center; font-size:0.8rem; color:#94a3b8; margin-top:60px; padding-bottom:40px;">
        🛡️ GroundWater Guardian India Registry &copy; 2026. Data compiled from Central Ground Water Board (CGWB) chemical surveys.
    </div>
""", unsafe_allow_html=True)
