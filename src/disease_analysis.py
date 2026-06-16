import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr

def analyze_disease_correlation(df: pd.DataFrame, risk_col: str = "Risk Score", disease_cols: list = None):
    """
    Analyzes the correlation between the Water Quality Risk Score and disease outbreaks.
    
    Parameters:
    - df: DataFrame containing risk scores and disease columns
    - risk_col: Column name of the calculated risk index
    - disease_cols: List of column names representing disease cases (e.g. ['Cholera Cases', ...])
                    If None, detects columns containing 'case' or 'outbreak' in their name.
                    
    Returns:
    - results: Dict containing:
        - 'correlations': DataFrame of correlation coefficients and p-values
        - 'hotspots': DataFrame of districts in the high-risk, high-disease quadrant
        - 'quadrants': DataFrame of all districts classified into 4 quadrants
    """
    if disease_cols is None:
        disease_cols = [
            c for c in df.columns 
            if any(kw in c.lower() for kw in ["case", "outbreak", "cholera", "typhoid", "diarrhea", "hepatitis"])
            and c != risk_col
        ]
        
    results = {
        "correlations": pd.DataFrame(),
        "hotspots": pd.DataFrame(),
        "quadrants": pd.DataFrame(),
        "detected_disease_cols": disease_cols
    }
    
    if not disease_cols or risk_col not in df.columns:
        return results
        
    # Remove rows where disease or risk score is null for correlation analysis
    temp_df = df.dropna(subset=[risk_col] + disease_cols).copy()
    
    if len(temp_df) < 3:
        return results # Not enough data for meaningful statistics
        
    # Calculate a composite "Total Disease Cases" if multiple diseases exist
    if len(disease_cols) > 1:
        temp_df["Total Disease Cases"] = temp_df[disease_cols].sum(axis=1)
        analysis_cols = disease_cols + ["Total Disease Cases"]
    else:
        analysis_cols = disease_cols
        
    # Compute correlations
    corr_records = []
    for col in analysis_cols:
        x = temp_df[risk_col].values
        y = temp_df[col].values
        
        # Pearson correlation
        p_coeff, p_val = pearsonr(x, y)
        # Spearman correlation
        s_coeff, s_val = spearmanr(x, y)
        
        corr_records.append({
            "Disease Metric": col,
            "Pearson r": p_coeff,
            "Pearson p-value": p_val,
            "Pearson Significance": "Significant" if p_val < 0.05 else "Not Significant",
            "Spearman rho": s_coeff,
            "Spearman p-value": s_val,
            "Spearman Significance": "Significant" if s_val < 0.05 else "Not Significant"
        })
        
    corr_df = pd.DataFrame(corr_records)
    results["correlations"] = corr_df
    
    # Quadrant Classification for Hotspots
    # Divide districts into four quadrants based on:
    #   - X-axis: Water Quality Risk Score (median or fixed 50 threshold)
    #   - Y-axis: Total Disease Cases (median of the dataset)
    disease_agg_col = "Total Disease Cases" if "Total Disease Cases" in temp_df.columns else disease_cols[0]
    
    risk_median = temp_df[risk_col].median()
    disease_median = temp_df[disease_agg_col].median()
    
    # We can also use a fixed risk threshold (e.g. 50, which is the boundary for high risk)
    # and disease median. Let's use standard medians for relative placement, or customizable.
    # We'll stick to medians as it guarantees a balanced distribution for exploration.
    risk_threshold = 50.0 # High risk threshold
    disease_threshold = disease_median
    
    quadrants = []
    for idx, row in temp_df.iterrows():
        r_val = row[risk_col]
        d_val = row[disease_agg_col]
        
        if r_val >= risk_threshold and d_val >= disease_threshold:
            quad = "High Risk, High Outbreaks (Priority Hotspot)"
        elif r_val >= risk_threshold and d_val < disease_threshold:
            quad = "High Risk, Low Outbreaks (Potential Vulnerability)"
        elif r_val < risk_threshold and d_val >= disease_threshold:
            quad = "Low Risk, High Outbreaks (Investigate Other Factors)"
        else:
            quad = "Low Risk, Low Outbreaks (Safe Zone)"
            
        quadrants.append(quad)
        
    temp_df["Vulnerability Quadrant"] = quadrants
    results["quadrants"] = temp_df
    
    # Extract priority hotspots (High Risk, High Outbreaks)
    hotspots = temp_df[temp_df["Vulnerability Quadrant"] == "High Risk, High Outbreaks (Priority Hotspot)"].copy()
    # Sort by risk score and disease cases descending
    if "Total Disease Cases" in hotspots.columns:
        hotspots = hotspots.sort_values(by=["Risk Score", "Total Disease Cases"], ascending=False)
    else:
        hotspots = hotspots.sort_values(by=["Risk Score", disease_cols[0]], ascending=False)
        
    results["hotspots"] = hotspots
    
    return results
