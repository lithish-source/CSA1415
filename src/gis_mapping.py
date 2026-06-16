import os
import requests
import json
import pandas as pd
import numpy as np
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Public URLs for simplified India district GeoJSON
GEOJSON_URLS = [
    "https://raw.githubusercontent.com/sab99r/India-Districts-Map/master/india_districts.geojson",
    "https://raw.githubusercontent.com/un-data/india-gis/master/india_districts.geojson"
]

CACHE_DIR = "cache"

# Coordinate mappings for synthetic states to support Scatter Mapbox fallback
STATE_COORDINATES = {
    "Rajasthan": (26.9124, 75.7873),
    "West Bengal": (22.5726, 88.3639),
    "Uttar Pradesh": (26.8467, 80.9462),
    "Kerala": (10.8505, 76.2711),
    "Maharashtra": (19.7515, 75.7139),
    "Punjab": (31.1471, 75.3412),
    "Assam": (26.2006, 92.9376),
    "Andhra Pradesh": (15.9129, 79.7400),
    "Bihar": (25.0961, 85.3131),
    "Tamil Nadu": (11.1271, 78.6569)
}

# Approximate coordinate offset dictionary for synthetic districts
DISTRICT_COORDINATE_OFFSETS = {
    # Rajasthan
    "Jaipur": (26.9124, 75.7873), "Jodhpur": (26.2389, 73.0243), "Udaipur": (24.5854, 73.7125),
    "Kota": (25.2138, 75.8648), "Ajmer": (26.4498, 74.6399), "Bikaner": (28.0191, 73.3119),
    "Alwar": (27.5530, 76.6346), "Barmer": (25.7532, 71.4181), "Nagaur": (27.1983, 73.7493),
    "Bhilwara": (25.3478, 74.6408), "Sikar": (27.6119, 75.1398), "Churu": (28.2936, 74.9602),
    # West Bengal
    "Kolkata": (22.5726, 88.3639), "Howrah": (22.5958, 88.2636), "Darjeeling": (27.0410, 88.2627),
    "Nadia": (23.4734, 88.5565), "Murshidabad": (24.1353, 88.2749), "Purulia": (23.3322, 86.3653),
    "Bankura": (23.2324, 87.0620), "Birbhum": (23.8913, 87.5303), "Malda": (25.0108, 88.1398),
    "Hooghly": (22.9012, 88.3908), "Medinipur": (22.4257, 87.3199), "Jalpaiguri": (26.5211, 88.7190),
    # Uttar Pradesh
    "Lucknow": (26.8467, 80.9462), "Kanpur": (26.4499, 80.3319), "Varanasi": (25.3176, 82.9739),
    "Agra": (27.1767, 78.0081), "Meerut": (28.9845, 77.7064), "Prayagraj": (25.4358, 81.8463),
    "Bareilly": (28.3670, 79.4304), "Aligarh": (27.8974, 78.0880), "Moradabad": (28.8345, 78.7839),
    "Gorakhpur": (26.7606, 83.3731), "Jhansi": (25.4484, 78.5685), "Ghaziabad": (28.6692, 77.4538),
    # Kerala
    "Trivandrum": (8.5241, 76.9366), "Kochi": (9.9312, 76.2673), "Kozhikode": (11.2588, 75.7804),
    "Thrissur": (10.5276, 76.2144), "Kollam": (8.8932, 76.6141), "Alappuzha": (9.4981, 76.3388),
    "Palakkad": (10.7867, 76.6548), "Malappuram": (11.0735, 76.0740), "Kannur": (11.8745, 75.3704),
    "Kottayam": (9.5916, 76.5220), "Idukki": (9.8493, 76.9678), "Wayanad": (11.6854, 76.1320)
}

@st.cache_data(show_spinner=False)
def load_india_geojson():
    """
    Downloads and caches the simplified India district GeoJSON.
    Returns the GeoJSON as a dict, or None if failed.
    """
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
        
    cache_path = os.path.join(CACHE_DIR, "india_districts.geojson")
    
    # Try local cache first
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass # Cache read failed, try re-download
            
    # Try URLs
    for url in GEOJSON_URLS:
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                geojson_data = response.json()
                # Save to cache
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(geojson_data, f)
                return geojson_data
        except Exception:
            continue
            
    return None

def normalize_name(name):
    """Utility to normalize spelling for matching."""
    if not isinstance(name, str):
        return ""
    # Strip spaces, lower, replace hyphens and common abbreviations
    name = name.strip().lower()
    name = name.replace("-", "").replace(" ", "").replace(".", "")
    # Remove standard suffix words
    for suffix in ["district", "dist", "urban", "rural", "north", "south", "east", "west"]:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
        if name.startswith(suffix):
            name = name[len(suffix):]
    return name

def render_district_map(df: pd.DataFrame, district_col: str, state_col: str, score_col: str, category_col: str):
    """
    Attempts to draw a District Choropleth Map using GeoJSON.
    Falls back to a Scatter Mapbox or State-level averages if GeoJSON is not fetchable.
    """
    geojson = load_india_geojson()
    
    if geojson is None:
        # Fallback 1: Scatter Mapbox (requires latitude/longitude)
        return render_scatter_mapbox(df, district_col, state_col, score_col, category_col)
        
    # Map the district names in the dataset to the GeoJSON keys
    # Let's inspect the GeoJSON properties structure
    # Typically, the key is properties.district or properties.dtname or properties.NAME_2
    features = geojson["features"]
    
    # Find property key for district and state in geojson
    sample_props = features[0]["properties"]
    dist_key = None
    state_key = None
    
    for k in sample_props.keys():
        kl = k.lower()
        if kl in ["district", "dtname", "dist_name", "name_2", "district_name"]:
            dist_key = k
        if kl in ["state", "stname", "st_name", "name_1", "state_name"]:
            state_key = k
            
    if dist_key is None:
        # Hard fallback
        dist_key = list(sample_props.keys())[0]
        
    # Build GeoJSON district dictionary for normalized matching
    geojson_districts = {}
    for i, feat in enumerate(features):
        d_name = feat["properties"].get(dist_key, "")
        s_name = feat["properties"].get(state_key, "") if state_key else ""
        norm_d = normalize_name(d_name)
        norm_s = normalize_name(s_name)
        
        # Store index and full name
        geojson_districts[(norm_d, norm_s)] = d_name
        # Fallback to district-only mapping if state mapping fails
        if norm_d not in geojson_districts:
            geojson_districts[norm_d] = d_name
            
    # Add a matching column to our dataframe
    df_mapped = df.copy()
    match_ids = []
    
    for idx, row in df_mapped.iterrows():
        d_val = row[district_col]
        s_val = row[state_col] if state_col in df_mapped.columns else ""
        
        norm_d = normalize_name(d_val)
        norm_s = normalize_name(s_val)
        
        # Check combined match first
        if (norm_d, norm_s) in geojson_districts:
            match_ids.append(geojson_districts[(norm_d, norm_s)])
        elif norm_d in geojson_districts:
            # Match by district name only (might have slight collisions, but acceptable fallback)
            if isinstance(geojson_districts[norm_d], str):
                match_ids.append(geojson_districts[norm_d])
            else:
                match_ids.append(None)
        else:
            match_ids.append(None)
            
    df_mapped["geojson_district_match"] = match_ids
    
    matched_ratio = df_mapped["geojson_district_match"].notnull().sum() / len(df_mapped)
    
    if matched_ratio < 0.1: # If less than 10% matched, names are mismatched; fallback
        return render_scatter_mapbox(df, district_col, state_col, score_col, category_col)
        
    # Create the Plotly Choropleth Map
    fig = px.choropleth(
        df_mapped,
        geojson=geojson,
        locations="geojson_district_match",
        featureidkey=f"properties.{dist_key}",
        color=score_col,
        color_continuous_scale="Reds",
        range_color=[0, 100],
        labels={score_col: "Risk Index"},
        hover_name=district_col,
        hover_data={
            state_col: True,
            score_col: ":.1f",
            category_col: True,
            "Major Contributors": True,
            "geojson_district_match": False
        }
    )
    
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator"
    )
    
    fig.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(
            title="WQRI",
            thicknessmode="pixels", thickness=15,
            lenmode="fraction", len=0.6,
            yanchor="middle", y=0.5,
            ticks="outside"
        )
    )
    
    return fig

def render_scatter_mapbox(df: pd.DataFrame, district_col: str, state_col: str, score_col: str, category_col: str):
    """
    Renders an interactive map using Mapbox Scatter Plotly.
    Uses district lookup coordinates or state coordinates with small random jitters.
    """
    df_coords = df.copy()
    
    # Check if lat/long are already in dataset
    lat_col = next((c for c in df_coords.columns if c.lower() in ["latitude", "lat"]), None)
    lon_col = next((c for c in df_coords.columns if c.lower() in ["longitude", "lon", "lng"]), None)
    
    if not lat_col or not lon_col:
        # Populate coordinates from lookup dictionary
        lats = []
        lons = []
        for idx, row in df_coords.iterrows():
            d_val = row[district_col]
            s_val = row[state_col]
            
            # Match district specifically
            if d_val in DISTRICT_COORDINATE_OFFSETS:
                lat, lon = DISTRICT_COORDINATE_OFFSETS[d_val]
            elif s_val in STATE_COORDINATES:
                # Fallback to state center with small random jitter so they don't overlap completely
                s_lat, s_lon = STATE_COORDINATES[s_val]
                lat = s_lat + np.random.uniform(-0.3, 0.3)
                lon = s_lon + np.random.uniform(-0.3, 0.3)
            else:
                # Center of India
                lat = 20.5937 + np.random.uniform(-2.0, 2.0)
                lon = 78.9629 + np.random.uniform(-2.0, 2.0)
                
            lats.append(lat)
            lons.append(lon)
            
        df_coords["Latitude"] = lats
        df_coords["Longitude"] = lons
        lat_col = "Latitude"
        lon_col = "Longitude"
        
    # Map color scale based on categories
    color_map = {
        "Low Risk": "#2ecc71",       # Emerald Green
        "Moderate Risk": "#f1c40f",  # Sunflower Yellow
        "High Risk": "#e67e22",      # Carrot Orange
        "Critical Risk": "#e74c3c"   # Alizarin Red
    }
    
    fig = px.scatter_mapbox(
        df_coords,
        lat=lat_col,
        lon=lon_col,
        color=category_col,
        color_discrete_map=color_map,
        size=df_coords[score_col].clip(lower=10), # size proportional to risk score
        hover_name=district_col,
        hover_data={
            state_col: True,
            score_col: ":.1f",
            "Major Contributors": True,
            "Latitude": False,
            "Longitude": False
        },
        zoom=3.8,
        center={"lat": 22.9734, "lon": 78.6569}, # center of India
        mapbox_style="carto-darkmatter"
    )
    
    fig.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            title="Risk Categories",
            yanchor="top", y=0.99,
            xanchor="left", x=0.01,
            bgcolor="rgba(255,255,255,0.7)"
        )
    )
    
    return fig

def render_state_average_chart(df: pd.DataFrame, state_col: str, score_col: str):
    """
    Generates a state-wise risk score average bar chart using Plotly.
    """
    state_avg = df.groupby(state_col)[score_col].mean().reset_index()
    state_avg = state_avg.sort_values(by=score_col, ascending=False)
    
    fig = px.bar(
        state_avg,
        x=state_col,
        y=score_col,
        color=score_col,
        color_continuous_scale="Reds",
        labels={score_col: "Average WQRI", state_col: "State"},
        title="State-wise Average Water Quality Risk Index (WQRI)"
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False
    )
    
    fig.update_yaxes(gridcolor="rgba(200,200,200,0.2)")
    return fig


def render_parameter_map(df: pd.DataFrame, param_col: str, district_col: str, state_col: str, color_scale: str = "Oranges"):
    """
    Renders a choropleth or scatter map showing the concentrations of a specific parameter.
    """
    geojson = load_india_geojson()
    
    if geojson is None:
        return render_parameter_scatter_mapbox(df, param_col, district_col, state_col, color_scale)
        
    features = geojson["features"]
    sample_props = features[0]["properties"]
    dist_key = None
    state_key = None
    
    for k in sample_props.keys():
        kl = k.lower()
        if kl in ["district", "dtname", "dist_name", "name_2", "district_name"]:
            dist_key = k
        if kl in ["state", "stname", "st_name", "name_1", "state_name"]:
            state_key = k
            
    if dist_key is None:
        dist_key = list(sample_props.keys())[0]
        
    geojson_districts = {}
    for feat in features:
        d_name = feat["properties"].get(dist_key, "")
        s_name = feat["properties"].get(state_key, "") if state_key else ""
        norm_d = normalize_name(d_name)
        norm_s = normalize_name(s_name)
        geojson_districts[(norm_d, norm_s)] = d_name
        if norm_d not in geojson_districts:
            geojson_districts[norm_d] = d_name
            
    df_mapped = df.copy()
    match_ids = []
    
    for idx, row in df_mapped.iterrows():
        d_val = row[district_col]
        s_val = row[state_col] if state_col in df_mapped.columns else ""
        norm_d = normalize_name(d_val)
        norm_s = normalize_name(s_val)
        
        if (norm_d, norm_s) in geojson_districts:
            match_ids.append(geojson_districts[(norm_d, norm_s)])
        elif norm_d in geojson_districts:
            if isinstance(geojson_districts[norm_d], str):
                match_ids.append(geojson_districts[norm_d])
            else:
                match_ids.append(None)
        else:
            match_ids.append(None)
            
    df_mapped["geojson_district_match"] = match_ids
    matched_ratio = df_mapped["geojson_district_match"].notnull().sum() / len(df_mapped)
    
    if matched_ratio < 0.1:
        return render_parameter_scatter_mapbox(df, param_col, district_col, state_col, color_scale)
        
    fig = px.choropleth(
        df_mapped,
        geojson=geojson,
        locations="geojson_district_match",
        featureidkey=f"properties.{dist_key}",
        color=param_col,
        color_continuous_scale=color_scale,
        labels={param_col: param_col},
        hover_name=district_col,
        hover_data={
            state_col: True,
            param_col: ":.2f",
            "geojson_district_match": False
        }
    )
    
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator"
    )
    
    fig.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(
            title=param_col.split(" (")[0],
            thicknessmode="pixels", thickness=15,
            lenmode="fraction", len=0.6,
            yanchor="middle", y=0.5,
            ticks="outside"
        )
    )
    
    return fig


def render_parameter_scatter_mapbox(df: pd.DataFrame, param_col: str, district_col: str, state_col: str, color_scale: str = "Oranges"):
    """
    Renders Mapbox Scatter plot for a specific parameter.
    """
    df_coords = df.copy()
    lat_col = next((c for c in df_coords.columns if c.lower() in ["latitude", "lat"]), None)
    lon_col = next((c for c in df_coords.columns if c.lower() in ["longitude", "lon", "lng"]), None)
    
    if not lat_col or not lon_col:
        lats = []
        lons = []
        for idx, row in df_coords.iterrows():
            d_val = row[district_col]
            s_val = row[state_col]
            if d_val in DISTRICT_COORDINATE_OFFSETS:
                lat, lon = DISTRICT_COORDINATE_OFFSETS[d_val]
            elif s_val in STATE_COORDINATES:
                s_lat, s_lon = STATE_COORDINATES[s_val]
                lat = s_lat + np.random.uniform(-0.3, 0.3)
                lon = s_lon + np.random.uniform(-0.3, 0.3)
            else:
                lat = 20.5937 + np.random.uniform(-2.0, 2.0)
                lon = 78.9629 + np.random.uniform(-2.0, 2.0)
            lats.append(lat)
            lons.append(lon)
        df_coords["Latitude"] = lats
        df_coords["Longitude"] = lons
        lat_col = "Latitude"
        lon_col = "Longitude"
        
    fig = px.scatter_mapbox(
        df_coords,
        lat=lat_col,
        lon=lon_col,
        color=param_col,
        color_continuous_scale=color_scale,
        size=df_coords[param_col].abs().clip(lower=1.0),
        hover_name=district_col,
        hover_data={
            state_col: True,
            param_col: ":.2f",
            "Latitude": False,
            "Longitude": False
        },
        zoom=3.8,
        center={"lat": 22.9734, "lon": 78.6569},
        mapbox_style="carto-darkmatter"
    )
    
    fig.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig
