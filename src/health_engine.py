import pandas as pd
import numpy as np

# Medical risk mappings focusing on potential implications, not claiming active outbreaks.
HAZARD_DATABASE = {
    "fluoride": {
        "critical": {
            "title": "Risk of Crippling Skeletal & Severe Dental Fluorosis",
            "symptoms": "Potential joint stiffness, bone density changes, teeth pitting/mottling.",
            "description": "Exceeds permissible drinking limits. High concentration can lead to structural bone accumulation over long-term intake."
        },
        "high": {
            "title": "Risk of Dental Fluorosis",
            "symptoms": "Chalky white spots or yellow-brown staining of teeth in children.",
            "description": "Exceeds acceptable limits. Poses a mild risk of cosmetic enamel discoloration during tooth development."
        }
    },
    "arsenic": {
        "critical": {
            "title": "Long-Term Arsenicosis & Toxicity Hazard",
            "symptoms": "Skin lesions (pigmentation changes, rough patches on palms/soles), peripheral neuropathy, cardiovascular risks.",
            "description": "Exceeds permissible limits. Heavy metal exposure is associated with dermatological, vascular, and cumulative systemic health concerns."
        },
        "high": {
            "title": "Arsenicosis Exposure Risk",
            "symptoms": "Skin pigmentation changes, chronic fatigue, minor cardiovascular stress.",
            "description": "Exceeds acceptable standard. Long-term consumption is linked to elevated physiological exposure risk."
        }
    },
    "uranium": {
        "critical": {
            "title": "Chemical Nephrotoxicity Risk (Kidney Health)",
            "symptoms": "Elevated indicators of kidney tissue stress, potential chronic kidney irritation.",
            "description": "Uranium in groundwater acts primarily as a chemical kidney irritant rather than a radiological hazard, targeting kidney filtration cells."
        }
    },
    "nitrate": {
        "critical": {
            "title": "Infant Hypoxia Risk (Blue Baby Syndrome)",
            "symptoms": "Methemoglobinemia in infants under 6 months (reduced blood oxygen carrying capacity), adult thyroid stress.",
            "description": "Exceeds standard limits. Excess nitrates can disrupt oxygen transport in infants. Highly recommended to use alternative water for infant formula."
        }
    },
    "iron": {
        "high": {
            "title": "Water Quality Concerns & Iron Overload Risk",
            "symptoms": "Metallic taste, stomach cramping, heavy laundry/fixture staining, rusty appearance.",
            "description": "Exceeds permissible limits. Primarily affects palatability and plumbing, but can contribute to iron overload in predisposed individuals."
        },
        "moderate": {
            "title": "Aesthetic Concerns & Metallic Taste",
            "symptoms": "Brownish staining of laundry and fixtures, turbid appearance, slight metallic taste.",
            "description": "Exceeds acceptable limits. Poses no severe health risk but significantly degrades water taste and appearance."
        }
    },
    "hardness": {
        "high": {
            "title": "Severe Carbonate Hardness & Scaling",
            "symptoms": "Heavy mineral scale build-up in pipes, dry skin/hair, soap lathering failure.",
            "description": "Exceeds permissible limits. High mineral content causes scaling in home appliances and can cause mild digestion discomfort in new users."
        },
        "moderate": {
            "title": "Hard Water Scaling",
            "symptoms": "Mild scale deposits, poor soap lathering, dryness of skin.",
            "description": "Exceeds acceptable limits. Safely consumable, but causes scaling and mineral build-up in plumbing."
        }
    },
    "ph": {
        "acidic": {
            "title": "Acidic Water & Metal Leaching Potential",
            "symptoms": "Corrosive piping damage, bitter metallic taste, risk of leached copper/lead ingestion.",
            "description": "pH is below 6.5. Acidic water is corrosive and can leach heavy metals from household piping into the drinking water supply."
        },
        "alkaline": {
            "title": "Alkaline Taste & Scale Accumulation",
            "symptoms": "Soda-like bitter taste, mineral encrustation, slippery feel.",
            "description": "pH is above 8.5. Alkaline water is prone to mineral scaling and can reduce the efficiency of water chlorination."
        }
    },
    "so4": {
        "critical": {
            "title": "Potential Laxative Effect",
            "symptoms": "Temporary laxative effect, mild digestive upset, risk of dehydration in infants.",
            "description": "Exceeds sulfate limit of 400 mg/L. High concentrations can cause temporary laxative effects in unaccustomed users."
        }
    },
    "chloride": {
        "high": {
            "title": "Palatability & Taste Deterioration",
            "symptoms": "Strong salty taste, accelerated pipe corrosion.",
            "description": "Chloride exceeds 1000 mg/L. Renders water unpalatable for drinking and cooking, causing user rejection."
        }
    },
    "ec": {
        "high": {
            "title": "High Mineral Salinity",
            "symptoms": "Mineralized taste, scale build-up on fixtures.",
            "description": "EC exceeds 1500 uS/cm. Indicates high dissolved mineral content, affecting palatability and appliance lifespan."
        }
    }
}

def analyze_district_health_hazards(row: pd.Series, numeric_cols: list):
    """
    Evaluates a district's water parameters and compiles its health hazard profile.
    
    Returns:
    - hazards: List of dicts representing triggered health hazards
    - risk_tier: String (Low, Moderate, High, Critical) based on severity of triggered hazards
    - dominant_hazard: String representing the main hazard concern
    - safety_status: String ("Safe for Drinking", "Requires Filtration", "Immediate Attention Required")
    """
    from src.risk_calculator import match_bis_standard
    
    hazards = []
    max_severity = 0  # 0: Low, 1: Moderate, 2: High, 3: Critical
    severity_rank = {"Critical": 3, "High": 2, "Moderate": 1}
    
    # Track critical parameter exceedances
    critical_contaminants_triggered = False
    any_standard_exceeded = False
    
    for col in numeric_cols:
        val = row[col]
        if pd.isnull(val):
            continue
            
        key, limits = match_bis_standard(col)
        if not limits:
            continue
            
        acc_lim, perm_lim = limits
        
        # Check standard violation
        if val > acc_lim:
            any_standard_exceeded = True
            
        # 1. Fluoride
        if key == "fluoride":
            if val > perm_lim:
                hazards.append({
                    "parameter": "Fluoride",
                    "value": f"{val:.2f} mg/L",
                    "standard": f"Max {perm_lim} mg/L",
                    "severity": "Critical",
                    **HAZARD_DATABASE["fluoride"]["critical"]
                })
                max_severity = max(max_severity, 3)
                critical_contaminants_triggered = True
            elif val > acc_lim:
                hazards.append({
                    "parameter": "Fluoride",
                    "value": f"{val:.2f} mg/L",
                    "standard": f"Max {acc_lim} mg/L",
                    "severity": "High",
                    **HAZARD_DATABASE["fluoride"]["high"]
                })
                max_severity = max(max_severity, 2)
                critical_contaminants_triggered = True
                
        # 2. Arsenic
        elif key == "arsenic":
            is_ppb = "ppb" in col.lower()
            val_ppb = val if is_ppb else val * 1000.0
            
            if val_ppb > 50.0:
                hazards.append({
                    "parameter": "Arsenic",
                    "value": f"{val:.2f} ppb",
                    "standard": "Max 50 ppb",
                    "severity": "Critical",
                    **HAZARD_DATABASE["arsenic"]["critical"]
                })
                max_severity = max(max_severity, 3)
                critical_contaminants_triggered = True
            elif val_ppb > 10.0:
                hazards.append({
                    "parameter": "Arsenic",
                    "value": f"{val:.2f} ppb",
                    "standard": "Max 10 ppb",
                    "severity": "High",
                    **HAZARD_DATABASE["arsenic"]["high"]
                })
                max_severity = max(max_severity, 2)
                critical_contaminants_triggered = True
                
        # 3. Uranium
        elif key == "uranium":
            is_ppb = "ppb" in col.lower()
            val_ppb = val if is_ppb else val * 1000.0
            
            if val_ppb > 30.0:
                hazards.append({
                    "parameter": "Uranium",
                    "value": f"{val:.2f} ppb",
                    "standard": "Max 30 ppb",
                    "severity": "Critical",
                    **HAZARD_DATABASE["uranium"]["critical"]
                })
                max_severity = max(max_severity, 3)
                critical_contaminants_triggered = True
                
        # 4. Nitrate
        elif key == "nitrate":
            if val > perm_lim:
                hazards.append({
                    "parameter": "Nitrate",
                    "value": f"{val:.2f} mg/L",
                    "standard": f"Max {perm_lim} mg/L",
                    "severity": "Critical",
                    **HAZARD_DATABASE["nitrate"]["critical"]
                })
                max_severity = max(max_severity, 3)
                critical_contaminants_triggered = True
                
        # 5. Iron
        elif key == "fe":
            is_ppb = "ppb" in col.lower()
            val_ppm = val / 1000.0 if is_ppb else val
            
            if val_ppm > 1.0:
                hazards.append({
                    "parameter": "Iron",
                    "value": f"{val:.2f} ppm" if not is_ppb else f"{val:.1f} ppb",
                    "standard": "Max 1.0 ppm" if not is_ppb else "Max 1000 ppb",
                    "severity": "High",
                    **HAZARD_DATABASE["iron"]["high"]
                })
                max_severity = max(max_severity, 2)
            elif val_ppm > 0.3:
                hazards.append({
                    "parameter": "Iron",
                    "value": f"{val:.2f} ppm" if not is_ppb else f"{val:.1f} ppb",
                    "standard": "Max 0.3 ppm" if not is_ppb else "Max 300 ppb",
                    "severity": "Moderate",
                    **HAZARD_DATABASE["iron"]["moderate"]
                })
                max_severity = max(max_severity, 1)
                
        # 6. Hardness
        elif key == "hardness":
            if val > perm_lim:
                hazards.append({
                    "parameter": "Total Hardness",
                    "value": f"{val:.2f} mg/L",
                    "standard": f"Max {perm_lim} mg/L",
                    "severity": "High",
                    **HAZARD_DATABASE["hardness"]["high"]
                })
                max_severity = max(max_severity, 2)
            elif val > acc_lim:
                hazards.append({
                    "parameter": "Total Hardness",
                    "value": f"{val:.2f} mg/L",
                    "standard": f"Max {acc_lim} mg/L",
                    "severity": "Moderate",
                    **HAZARD_DATABASE["hardness"]["moderate"]
                })
                max_severity = max(max_severity, 1)
                
        # 7. pH
        elif key == "ph":
            if val < 6.5:
                hazards.append({
                    "parameter": "pH",
                    "value": f"{val:.2f}",
                    "standard": "6.5 - 8.5",
                    "severity": "Moderate",
                    **HAZARD_DATABASE["ph"]["acidic"]
                })
                max_severity = max(max_severity, 1)
            elif val > 8.5:
                hazards.append({
                    "parameter": "pH",
                    "value": f"{val:.2f}",
                    "standard": "6.5 - 8.5",
                    "severity": "Moderate",
                    **HAZARD_DATABASE["ph"]["alkaline"]
                })
                max_severity = max(max_severity, 1)
                
        # 8. Sulfate
        elif key == "so4":
            if val > perm_lim:
                hazards.append({
                    "parameter": "Sulfate",
                    "value": f"{val:.2f} mg/L",
                    "standard": f"Max {perm_lim} mg/L",
                    "severity": "Critical",
                    **HAZARD_DATABASE["so4"]["critical"]
                })
                max_severity = max(max_severity, 3)
                
        # 9. Chloride
        elif key == "chloride":
            if val > perm_lim:
                hazards.append({
                    "parameter": "Chloride",
                    "value": f"{val:.2f} mg/L",
                    "standard": f"Max {perm_lim} mg/L",
                    "severity": "High",
                    **HAZARD_DATABASE["chloride"]["high"]
                })
                max_severity = max(max_severity, 2)
                
        # 10. EC (Conductivity)
        elif key == "ec":
            if val > perm_lim:
                hazards.append({
                    "parameter": "Electrical Conductivity",
                    "value": f"{val:.2f} µS/cm",
                    "standard": f"Max {perm_lim} µS/cm",
                    "severity": "High",
                    **HAZARD_DATABASE["ec"]["high"]
                })
                max_severity = max(max_severity, 2)
                
    # Sort triggered hazards by severity
    severity_rank = {"Critical": 3, "High": 2, "Moderate": 1}
    hazards.sort(key=lambda x: severity_rank.get(x["severity"], 0), reverse=True)
    
    # Map max severity to risk tier
    tiers = {0: "Low Risk", 1: "Moderate Risk", 2: "High Risk", 3: "Critical Risk"}
    risk_tier = tiers[max_severity]
    
    dominant_hazard = "No significant hazards detected. Safe for consumption."
    if hazards:
        dominant_hazard = f"{hazards[0]['severity']} Concern: {hazards[0]['title']} due to {hazards[0]['parameter']} ({hazards[0]['value']})"
        
    # Determine Suitability Rating / Safety Status Badge
    # Safe for Drinking: WQRI < 30 and NO critical heavy metals/F exceeded standard
    # Requires Filtration: 30 <= WQRI < 70, or some parameter exceeded acceptable standard
    # Immediate Attention Required: WQRI >= 70, or critical toxins (As, F, U, NO3) exceeded standard
    risk_score = row.get("Risk Score", 0.0)
    
    if risk_score >= 70.0 or critical_contaminants_triggered:
        safety_status = "Immediate Attention Required"
    elif risk_score >= 30.0 or any_standard_exceeded:
        safety_status = "Requires Filtration"
    else:
        safety_status = "Safe for Drinking"
        
    return hazards, risk_tier, dominant_hazard, safety_status
