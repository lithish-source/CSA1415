import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def prepare_pca_features(df: pd.DataFrame, selected_features: list):
    """
    Prepares water quality features for PCA by correcting parameter directionality:
    - pH: Risk increases as pH deviates from neutral (7.0). We use |pH - 7.0|.
    - Dissolved Oxygen: Risk increases as DO decreases. We invert it: (max_possible_do - DO) or (-1 * DO).
      Typically, max saturated DO at standard temperature is around 10.0 mg/L. We'll use (10.0 - DO) clipped at 0.
    - Other parameters (TDS, Nitrate, Fluoride, etc.): Higher values mean worse quality (high risk), 
      so they are left unchanged.
      
    Parameters:
    - df: Cleaned DataFrame
    - selected_features: List of column names representing water quality parameters
    
    Returns:
    - prepared_df: DataFrame with corrected directionality
    - feature_mappings: Dictionary explaining how features were transformed
    """
    prepared_df = df[selected_features].copy()
    feature_mappings = {}
    
    for col in selected_features:
        col_lower = col.lower()
        if "ph" == col_lower or "p-h" in col_lower:
            # Shift pH to absolute deviation from 7.0
            prepared_df[col] = (prepared_df[col] - 7.0).abs()
            feature_mappings[col] = "Absolute deviation from neutral pH: |pH - 7.0|"
        elif "dissolved oxygen" in col_lower or "do " in col_lower or col_lower == "do" or "do(" in col_lower:
            # Invert Dissolved Oxygen. Let's assume a reference saturation of 10.0 mg/L.
            prepared_df[col] = (10.0 - prepared_df[col]).clip(lower=0)
            feature_mappings[col] = "Oxygen depletion index: (10.0 - DO)"
        else:
            feature_mappings[col] = "Raw parameter value (Higher concentration = Higher risk)"
            
    return prepared_df, feature_mappings

def run_pca_analysis(df: pd.DataFrame, selected_features: list, n_components: int = None):
    """
    Standardises features, runs Principal Component Analysis, and extracts all weights and scores.
    
    Parameters:
    - df: Cleaned DataFrame
    - selected_features: List of columns to run PCA on
    - n_components: Number of components. If None, uses min(n_samples, n_features).
    
    Returns:
    - results: Dict containing:
        - 'pca_object': Fitted sklearn PCA object
        - 'standardized_data': Standardised feature values (numpy array)
        - 'scores': Principal Component scores for each sample (DataFrame)
        - 'loadings': PCA loading matrix (DataFrame)
        - 'explained_variance': Explained variance ratio per component (list)
        - 'cumulative_variance': Cumulative explained variance ratio (list)
        - 'major_contributors': Dict mapping each PC to its top contributing parameters
        - 'feature_mappings': The transformation details applied for directionality
    """
    # 1. Correct parameter directionality
    prepared_df, feature_mappings = prepare_pca_features(df, selected_features)
    
    # Guard against zero-variance features to prevent division by zero in standard scaling
    valid_cols = []
    dropped_cols = []
    for col in prepared_df.columns:
        if prepared_df[col].std(ddof=0) > 1e-5:
            valid_cols.append(col)
        else:
            dropped_cols.append(col)
            
    if dropped_cols:
        # Filter prepared features to only keep valid ones
        prepared_df = prepared_df[valid_cols]
        # Keep only feature mappings of valid features
        feature_mappings = {k: v for k, v in feature_mappings.items() if k in valid_cols}
        
    # 2. Standardise features (Z-score scaling)
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(prepared_df)
    
    # 3. Fit PCA
    max_components = min(scaled_data.shape[0], scaled_data.shape[1])
    if n_components is None:
        n_components = max_components
    else:
        n_components = min(n_components, max_components)
        
    pca = PCA(n_components=n_components)
    pca_scores = pca.fit_transform(scaled_data)
    
    # 4. Create Column names for components
    pc_names = [f"PC{i+1}" for i in range(pca.n_components_)]
    
    # 5. Build Scores DataFrame
    scores_df = pd.DataFrame(pca_scores, columns=pc_names, index=df.index)
    
    # 6. Build Loadings DataFrame (eigenvectors)
    # Loadings are eigenvectors multiplied by sqrt(eigenvalues), representing correlation
    # between original variables and principal components.
    # Alternatively, loadings can be raw eigenvectors:
    loadings_df = pd.DataFrame(
        pca.components_.T,
        index=prepared_df.columns.tolist(),
        columns=pc_names
    )
    
    # 7. Extract variance details
    explained_variance = list(pca.explained_variance_ratio_)
    cumulative_variance = list(np.cumsum(pca.explained_variance_ratio_))
    
    # 8. Determine major contributors for each PC
    # A feature is a major contributor if its loading is high.
    # We will identify the top contributors by:
    #   - Features with absolute loading > 0.35, OR
    #   - The top 3 features by absolute loading value if none exceed 0.35.
    major_contributors = {}
    for pc in pc_names:
        loadings = loadings_df[pc]
        abs_loadings = loadings.abs().sort_values(ascending=False)
        
        # Primary contributors
        primary = abs_loadings[abs_loadings >= 0.35]
        if primary.empty:
            # Fallback to top 2 contributors
            contributors = list(abs_loadings.head(2).index)
        else:
            contributors = list(primary.index)
            
        # Add loading sign for context (+ or -)
        contributors_with_signs = [
            f"{c} ({'+' if loadings[c] >= 0 else '-'}{abs(loadings[c]):.2f})"
            for c in contributors
        ]
        major_contributors[pc] = contributors_with_signs
        
    results = {
        "pca_object": pca,
        "scaler": scaler,
        "prepared_features": prepared_df,
        "standardized_data": scaled_data,
        "scores": scores_df,
        "loadings": loadings_df,
        "explained_variance": explained_variance,
        "cumulative_variance": cumulative_variance,
        "major_contributors": major_contributors,
        "feature_mappings": feature_mappings
    }
    
    return results
