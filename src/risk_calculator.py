import pandas as pd
import numpy as np

# BIS Standards (IS 10500:2012) for drinking water quality parameters
# Key is the parameter column substring match, value is (acceptable_limit, permissible_limit)
# If a parameter has no permissible relaxation, permissible_limit is equal to acceptable_limit.
BIS_STANDARDS = {
    "ph": (6.5, 8.5),
    "ec": (750.0, 1500.0),       # Conductivity in uS/cm
    "co3": (10.0, 50.0),         # Carbonate in mg/L
    "hco3": (200.0, 600.0),      # Bicarbonate in mg/L
    "chloride": (250.0, 1000.0), # Chloride in mg/L
    "fluoride": (1.0, 1.5),      # Fluoride in mg/L
    "so4": (200.0, 400.0),       # Sulfate in mg/L
    "nitrate": (45.0, 45.0),     # Nitrate in mg/L
    "po4": (1.0, 2.0),           # Phosphate in mg/L
    "hardness": (200.0, 600.0),  # Hardness in mg/L
    "ca": (75.0, 200.0),         # Calcium in mg/L
    "mg": (30.0, 100.0),         # Magnesium in mg/L
    "na": (200.0, 200.0),        # Sodium in mg/L
    "k": (12.0, 12.0),           # Potassium in mg/L
    "fe": (0.3, 1.0),            # Iron in ppm/mg/L
    "arsenic": (10.0, 50.0),     # Arsenic in ppb (default to ppb, adjusted below)
    "uranium": (30.0, 30.0),     # Uranium in ppb
    "tds": (500.0, 2000.0),
    "turbidity": (1.0, 5.0),
    "dissolved oxygen": (6.0, 4.0)
}

def match_bis_standard(col_name: str):
    """
    Matches a column name to the corresponding BIS standard configuration.
    Uses precise substring matching to avoid collisions (e.g. Ca vs Carbonates, Mg vs mg/L).
    """
    col_lower = col_name.lower()
    
    # Check specific terms first
    mappings = [
        ("ph", "ph"),
        ("total hardness", "hardness"),
        ("hardness", "hardness"),
        ("hco3", "hco3"),
        ("co3", "co3"),
        ("chloride", "chloride"),
        ("cl", "chloride"),
        ("fluoride", "fluoride"),
        ("f (", "fluoride"),
        ("f ", "fluoride"),
        ("so4", "so4"),
        ("no3", "nitrate"),
        ("nitrate", "nitrate"),
        ("po4", "po4"),
        ("ca (", "ca"),
        ("ca ", "ca"),
        ("calcium", "ca"),
        ("mg (", "mg"),
        ("mg ", "mg"),
        ("magnesium", "mg"),
        ("na (", "na"),
        ("na ", "na"),
        ("sodium", "na"),
        ("k (", "k"),
        ("k ", "k"),
        ("potassium", "k"),
        ("fe (", "fe"),
        ("fe ", "fe"),
        ("iron", "fe"),
        ("arsenic", "arsenic"),
        ("as (", "arsenic"),
        ("as ", "arsenic"),
        ("uranium", "uranium"),
        ("u (", "uranium"),
        ("u ", "uranium"),
        ("ec (", "ec"),
        ("ec ", "ec"),
        ("electrical conductivity", "ec"),
        ("conductivity", "ec"),
        ("tds", "tds"),
        ("turbidity", "turbidity"),
        ("dissolved oxygen", "dissolved oxygen")
    ]
    
    for sub, key in mappings:
        if sub in col_lower:
            # Dynamically adjust limits based on units specified in column name
            limits = BIS_STANDARDS[key]
            
            # Unit overrides for Arsenic
            if key == "arsenic":
                is_ppb = "ppb" in col_lower
                acc = 10.0 if is_ppb else 0.01
                perm = 50.0 if is_ppb else 0.05
                limits = (acc, perm)
                
            # Unit overrides for Uranium
            elif key == "uranium":
                is_ppb = "ppb" in col_lower
                acc = 30.0 if is_ppb else 0.03
                perm = 30.0 if is_ppb else 0.03
                limits = (acc, perm)
                
            # Unit overrides for Iron
            elif key == "fe":
                is_ppb = "ppb" in col_lower
                acc = 300.0 if is_ppb else 0.3
                perm = 1000.0 if is_ppb else 1.0
                limits = (acc, perm)
                
            return key, limits
            
    return None, None

def get_exceeded_pollutants(row: pd.Series, numeric_cols: list):
    """
    Identifies which parameters exceed BIS limits in a district row
    and ranks them by exceedance ratio.
    """
    exceedances = []
    
    for col in numeric_cols:
        val = row[col]
        if pd.isnull(val):
            continue
            
        key, limits = match_bis_standard(col)
        if not limits:
            continue
            
        acc_lim, perm_lim = limits
        
        # pH handles range deviation
        if key == "ph":
            if val < 6.5:
                ratio = (6.5 - val) / 6.5
                exceedances.append((col, ratio, f"Acidic pH ({val:.2f} < 6.5)"))
            elif val > 8.5:
                ratio = (val - 8.5) / 8.5
                exceedances.append((col, ratio, f"Alkaline pH ({val:.2f} > 8.5)"))
        # Dissolved Oxygen: lower is worse
        elif key == "dissolved oxygen":
            if val < acc_lim:
                ratio = (acc_lim - val) / acc_lim
                exceedances.append((col, ratio, f"Low DO ({val:.1f} mg/L < 6.0)"))
        # Standard pollutants: higher is worse
        else:
            if val > acc_lim:
                ratio = val / acc_lim
                limit_type = "Permissible" if val > perm_lim else "Acceptable"
                # Label cleanly without unit details in label if not needed
                clean_name = col.split(" (")[0]
                exceedances.append((col, ratio, f"High {clean_name} ({val:.2f} > {acc_lim}) [{limit_type} Exceeded]"))
                
    # Sort by exceedance ratio descending
    exceedances.sort(key=lambda x: x[1], reverse=True)
    
    if exceedances:
        return ", ".join([item[2] for item in exceedances[:3]])
    else:
        return "None (Within Limits)"

def calculate_water_quality_risk_index(pca_results: dict, df: pd.DataFrame, n_pcs_to_use: int = None):
    """
    Calculates the Water Quality Risk Index (WQRI) using PCA results.
    
    Parameters:
    - pca_results: Dict output from run_pca_analysis
    - df: The clean DataFrame (for merging with state/district details)
    - n_pcs_to_use: Number of PCs to combine. If None, uses PCs explaining up to 80% cumulative variance.
    
    Returns:
    - final_df: DataFrame containing the original columns plus PCA scores, Risk Index, and Risk Category.
    - index_weights: Dict representing the weight assigned to each PC
    """
    scores = pca_results["scores"]
    explained_var = pca_results["explained_variance"]
    cum_var = pca_results["cumulative_variance"]
    
    # 1. Decide how many PCs to use
    if n_pcs_to_use is None:
        # Select PCs that sum up to 80% variance, or at least 2 PCs
        n_pcs_to_use = 2
        for i, cv in enumerate(cum_var):
            if cv >= 0.80:
                n_pcs_to_use = i + 1
                break
        n_pcs_to_use = max(2, min(n_pcs_to_use, len(explained_var)))
        
    pcs_selected = [f"PC{i+1}" for i in range(n_pcs_to_use)]
    selected_vars = explained_var[:n_pcs_to_use]
    sum_vars = sum(selected_vars)
    
    # Calculate weights for selected PCs
    weights = [v / sum_vars for v in selected_vars]
    index_weights = {pcs_selected[i]: weights[i] for i in range(n_pcs_to_use)}
    
    # 2. Compute the weighted composite index
    composite_index = np.zeros(len(scores))
    for i, pc in enumerate(pcs_selected):
        composite_index += scores[pc].values * weights[i]
        
    # 3. Min-Max Scale the composite index to a 0-100 score
    idx_min = composite_index.min()
    idx_max = composite_index.max()
    
    # Prevent division by zero if all scores are identical
    if idx_max == idx_min:
        normalized_scores = np.zeros(len(scores))
    else:
        normalized_scores = 100.0 * (composite_index - idx_min) / (idx_max - idx_min)
        
    # 4. Assemble the results dataframe
    final_df = df.copy()
    
    # Add scores and index
    for pc in scores.columns:
        final_df[pc] = scores[pc]
        
    final_df["Risk Score"] = normalized_scores
    
    # Categorise risk levels
    # Low: 0 - 30, Moderate: 30 - 50, High: 50 - 70, Critical: 70 - 100
    def categorize_risk(score):
        if score < 30.0:
            return "Low Risk"
        elif score < 50.0:
            return "Moderate Risk"
        elif score < 70.0:
            return "High Risk"
        else:
            return "Critical Risk"
            
    final_df["Risk Category"] = final_df["Risk Score"].apply(categorize_risk)
    
    # 5. Extract major contributing pollutants for hover tools / insights
    # Find numeric columns
    numeric_cols = pca_results["prepared_features"].columns.tolist()
    final_df["Major Contributors"] = final_df.apply(lambda r: get_exceeded_pollutants(r, numeric_cols), axis=1)
    
    # If a district has "None (Within Limits)" but has a moderate/high risk score, 
    # find its top 2 parameters by standardized value to provide details anyway
    std_data = pca_results["standardized_data"]
    for idx, row_idx in enumerate(final_df.index):
        if final_df.loc[row_idx, "Major Contributors"] == "None (Within Limits)":
            row_std = std_data[idx]
            top_indices = np.argsort(row_std)[-2:] # top 2 highest z-scores
            features = pca_results["prepared_features"].columns
            contribs = []
            for t_idx in top_indices:
                val_std = row_std[t_idx]
                if val_std > 0: # positive deviation is bad
                    contribs.append(f"{features[t_idx]} (Elevated)")
            if contribs:
                final_df.loc[row_idx, "Major Contributors"] = ", ".join(contribs[::-1])
                
    return final_df, index_weights
