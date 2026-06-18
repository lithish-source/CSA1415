import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.risk_calculator import match_bis_standard

def render_comparison_tool(risk_df: pd.DataFrame, state_col: str, district_col: str, water_cols: list):
    """
    Renders the side-by-side comparison tool for two districts.
    Ensures state-aware filtering and handles dynamic dependent dropdown race conditions.
    """
    col_comp_sel1, col_comp_sel2 = st.columns(2)
    with col_comp_sel1:
        comp_state1 = st.selectbox(
            "Select State 1", 
            sorted(risk_df[state_col].unique()),
            key="comp_state_select_1"
        )
        comp_districts1 = sorted(risk_df[risk_df[state_col] == comp_state1][district_col].unique())
        comp_dist1 = st.selectbox(
            "Select District 1", 
            comp_districts1,
            key=f"comp_district_select_1_{comp_state1}"
        )
    with col_comp_sel2:
        comp_state2 = st.selectbox(
            "Select State 2", 
            sorted(risk_df[state_col].unique()),
            key="comp_state_select_2"
        )
        comp_districts2 = sorted(risk_df[risk_df[state_col] == comp_state2][district_col].unique())
        comp_dist2 = st.selectbox(
            "Select District 2", 
            comp_districts2,
            key=f"comp_district_select_2_{comp_state2}"
        )

    if comp_dist1 != comp_dist2 or comp_state1 != comp_state2:
        match1 = risk_df[(risk_df[state_col] == comp_state1) & (risk_df[district_col] == comp_dist1)]
        match2 = risk_df[(risk_df[state_col] == comp_state2) & (risk_df[district_col] == comp_dist2)]
        
        # Guard against race conditions where dropdown options have not synchronized yet
        if match1.empty or match2.empty:
            st.info("Synchronizing selected districts...")
            return

        row1 = match1.iloc[0]
        row2 = match2.iloc[0]

        col_c1, col_c_radar, col_c2 = st.columns([1, 1.8, 1])
        
        # Left Card
        with col_c1:
            st.markdown(f"""
                <div class="comp-card" style="margin-top:20px; height:100%;">
                    <div class="comp-name">{row1[district_col]}</div>
                    <div style="font-size:0.8rem; color:#64748b; font-weight:600;">{row1[state_col]}</div>
                    <div class="comp-score">{row1['Risk Score']:.0f}</div>
                    <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#94a3b8;">Water Risk Score</div>
                    <div style="font-size:0.85rem; font-weight:700; color:#cbd5e1; margin-top:15px; background:rgba(255,255,255,0.05); padding:6px; border-radius:6px;">{row1['Risk Category']}</div>
                </div>
            """, unsafe_allow_html=True)
            
        # Right Card
        with col_c2:
            st.markdown(f"""
                <div class="comp-card" style="margin-top:20px; height:100%;">
                    <div class="comp-name">{row2[district_col]}</div>
                    <div style="font-size:0.8rem; color:#64748b; font-weight:600;">{row2[state_col]}</div>
                    <div class="comp-score">{row2['Risk Score']:.0f}</div>
                    <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#94a3b8;">Water Risk Score</div>
                    <div style="font-size:0.85rem; font-weight:700; color:#cbd5e1; margin-top:15px; background:rgba(255,255,255,0.05); padding:6px; border-radius:6px;">{row2['Risk Category']}</div>
                </div>
            """, unsafe_allow_html=True)
            
        # Radar Chart
        with col_c_radar:
            radar_features = []
            for term in ["ph", "ec (", "f (", "no3", "hardness", "fe (", "as (", "u ("]:
                match = next((c for c in water_cols if term in c.lower()), None)
                if match:
                    radar_features.append(match)
                    
            if len(radar_features) >= 3:
                r1_vals = []
                r2_vals = []
                labels = []
                for f in radar_features:
                    labels.append(f.split(" (")[0])
                    _, limits = match_bis_standard(f)
                    
                    val1 = row1.get(f)
                    val2 = row2.get(f)
                    
                    # Clean NaN/Null values to avoid Plotly axis scale failures
                    if pd.isnull(val1) or pd.isna(val1):
                        val1 = 7.0 if f.lower() == "ph" else 0.0
                    if pd.isnull(val2) or pd.isna(val2):
                        val2 = 7.0 if f.lower() == "ph" else 0.0
                        
                    if limits:
                        acc = limits[0]
                        if f.lower() == "ph":
                            r1_vals.append(abs(val1 - 7.0) / 1.5)
                            r2_vals.append(abs(val2 - 7.0) / 1.5)
                        else:
                            r1_vals.append(val1 / acc if acc > 0 else 0.0)
                            r2_vals.append(val2 / acc if acc > 0 else 0.0)
                    else:
                        r1_vals.append(0.0)
                        r2_vals.append(0.0)
                        
                r1_vals.append(r1_vals[0])
                r2_vals.append(r2_vals[0])
                labels.append(labels[0])
                
                # Check for any remaining NaNs in values list and force default to 0.0
                r1_vals = [0.0 if pd.isnull(x) or pd.isna(x) else x for x in r1_vals]
                r2_vals = [0.0 if pd.isnull(x) or pd.isna(x) else x for x in r2_vals]
                
                fig_r = go.Figure()
                fig_r.add_trace(go.Scatterpolar(
                    r=r1_vals, theta=labels, fill='toself', name=comp_dist1,
                    line_color="#3b82f6", fillcolor="rgba(59,130,246,0.08)"
                ))
                fig_r.add_trace(go.Scatterpolar(
                    r=r2_vals, theta=labels, fill='toself', name=comp_dist2,
                    line_color="#dc2626", fillcolor="rgba(220,38,38,0.08)"
                ))
                
                # Determine absolute max to ensure a valid range boundary
                max_val = max(max(r1_vals), max(r2_vals), 1.5)
                if pd.isnull(max_val) or pd.isna(max_val):
                    max_val = 1.5
                    
                fig_r.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0.0, float(max_val * 1.1)])),
                    showlegend=False,
                    height=300,
                    margin=dict(l=35, r=35, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_r, use_container_width=True)
    else:
        st.info("Select two different districts or states to view side-by-side comparison metrics.")
