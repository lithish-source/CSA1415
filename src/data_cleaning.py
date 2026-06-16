import pandas as pd
import numpy as np

def clean_data(df: pd.DataFrame, 
               impute_method: str = "median", 
               outlier_action: str = "cap", 
               iqr_threshold: float = 1.5):
    """
    Cleans the input water quality and disease dataset.
    Supports well-wise data and aggregates it to district level.
    
    Parameters:
    - df: Raw pandas DataFrame
    - impute_method: "mean", "median", or "drop" for handling missing values
    - outlier_action: "cap" (winsorize), "remove" (drop rows), or "none"
    - iqr_threshold: Factor to multiply IQR by for outlier detection (default 1.5)
    
    Returns:
    - cleaned_df: Cleaned pandas DataFrame at district level
    - report: Dict summarizing the operations performed (counts of duplicates, missing, outliers)
    """
    raw_df = df.copy()
    report = {
        "initial_rows": len(raw_df),
        "duplicates_removed": 0,
        "missing_imputed": {},
        "outliers_handled": {},
        "final_rows": 0
    }
    
    # 1. Drop rows with null state or district
    state_col = None
    dist_col = None
    for col in raw_df.columns:
        col_lower = col.lower()
        if "state" in col_lower:
            state_col = col
        elif "district" in col_lower or "dist" == col_lower:
            dist_col = col
            
    if not state_col or not dist_col:
        raise ValueError("Dataset must contain 'State' and 'District' columns.")
        
    raw_df = raw_df.dropna(subset=[state_col, dist_col])
    
    # Standardise text names
    raw_df[state_col] = raw_df[state_col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True).str.title()
    raw_df[dist_col] = raw_df[dist_col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True).str.title()
    
    # 2. Identify and convert parameters to numeric
    # S. No., State, District, Location, and Year should not be converted
    exclude_conversion = [state_col.lower(), dist_col.lower(), "location", "s. no.", "s.no.", "year"]
    cols_to_convert = [
        c for c in raw_df.columns 
        if not any(exc in c.lower() for exc in exclude_conversion)
    ]
    
    # Convert parameters to float (coercing dashes or text to NaN)
    for col in cols_to_convert:
        raw_df[col] = pd.to_numeric(raw_df[col], errors='coerce')
        
    # 3. Aggregate well-level data to district level
    # We aggregate by State and District using mean
    # This also averages coordinates (Latitude, Longitude) to get district centroids
    grouped_df = raw_df.groupby([state_col, dist_col])
    
    # We can take the mean of all numeric columns
    numeric_cols_grouped = [c for c in raw_df.columns if pd.api.types.is_numeric_dtype(raw_df[c]) and c not in ["s. no.", "s.no.", "year"]]
    
    # Aggregate
    aggregated_df = grouped_df[numeric_cols_grouped].mean().reset_index()
    report["aggregated_from"] = report["initial_rows"]
    report["aggregated_to"] = len(aggregated_df)
    
    cleaned_df = aggregated_df.copy()
    
    # 4. Handle Missing Values
    # Impute missing values on the aggregated district data
    ph_cols = [c for c in numeric_cols_grouped if "ph" in c.lower()]
    
    for col in numeric_cols_grouped:
        # Skip coordinates and year
        if any(kw in col.lower() for kw in ["latitude", "longitude", "lat", "lon", "coordinate"]):
            continue
            
        missing_count = cleaned_df[col].isnull().sum()
        if missing_count > 0:
            report["missing_imputed"][col] = int(missing_count)
            if impute_method == "drop":
                cleaned_df = cleaned_df.dropna(subset=[col])
            else:
                # Group by state to get regional average/median
                if len(cleaned_df[state_col].unique()) > 1:
                    if impute_method == "median":
                        state_values = cleaned_df.groupby(state_col)[col].transform("median")
                    else:  # mean
                        state_values = cleaned_df.groupby(state_col)[col].transform("mean")
                    
                    cleaned_df[col] = cleaned_df[col].fillna(state_values)
                
                # If there are still missing values, fill with global median/mean
                if cleaned_df[col].isnull().sum() > 0:
                    global_val = cleaned_df[col].median() if impute_method == "median" else cleaned_df[col].mean()
                    # For toxins like Arsenic, Uranium, Nitrate, default to 0.0 if entire column is null
                    if pd.isnull(global_val):
                        global_val = 0.0
                    cleaned_df[col] = cleaned_df[col].fillna(global_val)
                    
    # 5. Outlier Detection and Handling
    exclude_keywords = ["cases", "outbreak", "latitude", "longitude", "lat", "lon", "co-ordinate", "coordinate", "year", "population"]
    parameters_to_check = [
        col for col in numeric_cols_grouped 
        if not any(kw in col.lower() for kw in exclude_keywords)
    ]
    
    outlier_rows_to_remove = set()
    
    for col in parameters_to_check:
        q1 = cleaned_df[col].quantile(0.25)
        q3 = cleaned_df[col].quantile(0.75)
        iqr = q3 - q1
        
        lower_bound = q1 - (iqr_threshold * iqr)
        upper_bound = q3 + (iqr_threshold * iqr)
        
        # Enforce physical limits: water quality measurements must be >= 0
        if col not in ph_cols:
            lower_bound = max(0.0, lower_bound)
        else:
            lower_bound = max(0.0, lower_bound)
            upper_bound = min(14.0, upper_bound)
            
        outliers_mask = (cleaned_df[col] < lower_bound) | (cleaned_df[col] > upper_bound)
        outliers_count = outliers_mask.sum()
        
        if outliers_count > 0:
            report["outliers_handled"][col] = int(outliers_count)
            if outlier_action == "cap":
                cleaned_df[col] = np.clip(cleaned_df[col], lower_bound, upper_bound)
            elif outlier_action == "remove":
                indices = cleaned_df[cleaned_df[col] < lower_bound].index.tolist() + \
                          cleaned_df[cleaned_df[col] > upper_bound].index.tolist()
                outlier_rows_to_remove.update(indices)
                
    if outlier_action == "remove" and outlier_rows_to_remove:
        cleaned_df = cleaned_df.drop(index=list(outlier_rows_to_remove))
        
    report["final_rows"] = len(cleaned_df)
    return cleaned_df, report
