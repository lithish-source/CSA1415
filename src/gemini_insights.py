import os
import json
import requests
import pandas as pd
import numpy as np

DEFAULT_NVIDIA_KEY = "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"
INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL_NAME = "google/diffusiongemma-26b-a4b-it"

def call_nvidia_llm(prompt: str, api_key: str):
    """
    Executes a request to the NVIDIA API endpoint.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2048,
        "temperature": 0.70,
        "top_p": 0.95,
        "stream": False,
        "chat_template_kwargs": {"enable_thinking": True},
    }
    
    response = requests.post(INVOKE_URL, headers=headers, json=payload, timeout=25)
    response.raise_for_status()
    res_json = response.json()
    
    content = res_json["choices"][0]["message"]["content"]
    return content


def generate_policy_brief(df_risk: pd.DataFrame, water_cols: list, api_key: str = None):
    """
    Generates a National Groundwater Safety Policy Brief using the NVIDIA LLM API,
    falling back to a rule-based expert briefing if the API is offline.
    """
    total_districts = len(df_risk)
    critical_count = len(df_risk[df_risk["Risk Category"] == "Critical Risk"])
    high_count = len(df_risk[df_risk["Risk Category"] == "High Risk"])
    critical_percent = (critical_count / total_districts) * 100
    
    top_risk_districts = df_risk.sort_values(by="Risk Score", ascending=False).head(5)
    worst_d_list = [f"{row['District']} ({row['State']}) WQRI: {row['Risk Score']:.1f} - Main Exceedances: {row['Major Contributors']}" 
                    for _, row in top_risk_districts.iterrows()]
    
    state_avgs = df_risk.groupby("State")["Risk Score"].mean().sort_values(ascending=False).head(3)
    worst_s_list = [f"{state} (Avg WQRI: {score:.1f})" for state, score in state_avgs.items()]
    
    from src.risk_calculator import match_bis_standard
    exceedance_rates = {}
    for col in water_cols:
        key, limits = match_bis_standard(col)
        if limits:
            acc_lim, _ = limits
            exceedance_rates[col] = (df_risk[col] > acc_lim).sum() / total_districts * 100
            
    top_exceeded = sorted(exceedance_rates.items(), key=lambda x: x[1], reverse=True)[:3]
    top_exceeded_str = [f"{item[0].split(' (')[0]} ({item[1]:.1f}% of districts exceed standard)" for item in top_exceeded]
    
    # Resolve API Key
    resolved_key = api_key or os.environ.get("NVIDIA_API_KEY")
    if not resolved_key or resolved_key.strip() == "":
        resolved_key = DEFAULT_NVIDIA_KEY
        
    try:
        prompt = f"""
        You are the Chief Scientific Advisor for GroundWater Guardian India.
        Based on the following actual groundwater quality data, draft a National Groundwater Safety Policy Brief.
        
        DATA DETAILS:
        - Total Districts Monitored: {total_districts}
        - Critical Risk Districts (GWQRI >= 70): {critical_count} ({critical_percent:.1f}%)
        - High Risk Districts (GWQRI 50-70): {high_count}
        - Top 3 States with Highest Average Water Risk: {", ".join(worst_s_list)}
        - Top 3 Most Frequent Contaminant Exceedances: {", ".join(top_exceeded_str)}
        - Top 5 Most Impacted Districts:
          {chr(10).join([f"  * {d}" for d in worst_d_list])}
          
        Your brief must contain:
        1. EXECUTIVE SUMMARY: High-level overview.
        2. CHEMICAL CRITICALITY ANALYSIS: Mapped physiological risks.
        3. REGIONAL HOTSPOT ANALYSIS: Commentary on geographical clusters.
        4. STRATEGIC POLICY RECOMMENDATIONS: Engineering and public planning suggestions.
        
        Keep the tone official and objective. Use markdown formatting.
        """
        
        brief_text = call_nvidia_llm(prompt, resolved_key)
        return brief_text
        
    except Exception as e:
        return f"### [API Connection Warning: {e}]\n\n" + generate_offline_brief(
            total_districts, critical_count, high_count, critical_percent, worst_d_list, worst_s_list, top_exceeded_str
        )

def generate_offline_brief(total_districts, critical_count, high_count, critical_percent, worst_d_list, worst_s_list, top_exceeded_str):
    worst_districts_formatted = "\n".join([f"- **{d}**" for d in worst_d_list])
    worst_states_formatted = ", ".join(worst_s_list)
    top_exceeded_formatted = ", ".join(top_exceeded_str)
    
    brief = f"""### GROUNDWATER SAFETY POLICY REPORT
**Office of the Scientific Advisor | GroundWater Guardian India**

---

#### 1. Executive Summary
Groundwater quality data across **{total_districts}** districts has been evaluated. The analysis reveals that **{critical_count} districts ({critical_percent:.1f}%)** fall under the **Critical Risk** tier, while another **{high_count} districts** exhibit **High Risk** profiles. Immediate localized interventions are recommended in these hotspots.

#### 2. Chemical Criticality Analysis
The nationwide groundwater hazard landscape is heavily driven by: **{top_exceeded_formatted}**. 
- **Fluoride and Arsenic**: Fluoride concentrations exceeding 1.5 mg/L trigger crippling skeletal fluorosis (joints locking) and permanent dental mottling in children. Arsenic exceedances above 10 ppb lead to hyperkeratosis skin lesions and long-term systemic toxicities.
- **Uranium and Nitrates**: Nitrate accumulation (exceeding 45 mg/L) poses infant hypoxia risks (Blue Baby Syndrome). Uranium exceedances above 30 ppb trigger chemical nephrotoxicity, damaging kidney renal tubules.

#### 3. Regional Hotspot Analysis
The highest average groundwater risk is concentrated in:
- **{worst_states_formatted}**

The top 5 districts requiring immediate water quality remediation are:
{worst_districts_formatted}

#### 4. Strategic Engineering & Policy Directives
1. **Desalination & Softening**: Deploy community-level solar-powered RO plants in high-salinity and high-hardness tracts.
2. **Heavy Metal Containment**: Implement Activated Alumina filters for Fluoride and co-precipitation filters for Arsenic.
3. **Alternate Aquifer Sourcing**: In high-arsenic basins, prioritize deep tube well drilling reaching beneath clay confining layers.
4. **Agricultural fertilizer control**: Promote balanced N-P-K fertilizer usage to limit Nitrate runoff.
"""
    return brief


def answer_citizen_query(df_risk: pd.DataFrame, query: str, active_district: str, water_cols: list, api_key: str = None):
    """
    Answers a citizen's question about groundwater safety in their district,
    using the NVIDIA LLM API or a robust offline rule-based advisor.
    """
    # 1. Parse the query to find which district or state is mentioned
    target_dist = active_district
    query_lower = query.lower()
    
    # Check if a district name is explicitly mentioned in the query
    dist_found = False
    for dist in df_risk["District"].unique():
        if dist.lower() in query_lower:
            target_dist = dist
            dist_found = True
            break
            
    # If no district found, scan for state names (including common variations/misspellings)
    if not dist_found:
        state_mapping = {
            "maharastra": "maharashtra",
            "tamilnadu": "tamil nadu",
            "andhra": "andhra pradesh",
            "bengal": "west bengal",
            "up": "uttar pradesh",
            "mp": "madhya pradesh",
            "chhattisgarh": "chhattisgarh",
            "jammu": "jammu & kashmir",
            "kashmir": "jammu & kashmir",
        }
        
        normalized_query = query_lower
        for variation, proper in state_mapping.items():
            if variation in query_lower:
                normalized_query = normalized_query.replace(variation, proper)
                
        for state in df_risk["State"].unique():
            state_lower = state.lower()
            if state_lower in normalized_query:
                # Find the highest risk district in this state to serve as the benchmark response
                state_dists = df_risk[df_risk["State"].str.lower() == state_lower].sort_values(by="Risk Score", ascending=False)
                if not state_dists.empty:
                    target_dist = state_dists.iloc[0]["District"]
                    dist_found = True
                    break
                    
    # Fetch target district record
    dist_rows = df_risk[df_risk["District"].str.lower() == target_dist.lower()]
    if dist_rows.empty:
        dist_row = df_risk.iloc[0]
        target_dist = dist_row["District"]
    else:
        dist_row = dist_rows.iloc[0]
        
    state_name = dist_row["State"]
    risk_score = dist_row["Risk Score"]
    risk_cat = dist_row["Risk Category"]
    exceedances = dist_row["Major Contributors"]
    
    # Compute Euclidean nearest 4 districts
    lat = dist_row["Latitude"]
    lon = dist_row["Longitude"]
    
    df_temp = df_risk[df_risk["District"] != target_dist].copy()
    df_temp["distance"] = np.sqrt((df_temp["Latitude"] - lat)**2 + (df_temp["Longitude"] - lon)**2)
    nearby_dists = df_temp.sort_values(by="distance").head(4)
    
    safer_nearby = nearby_dists[nearby_dists["Risk Score"] < risk_score]
    safer_list = [f"{r['District']} (WQRI: {r['Risk Score']:.1f})" for _, r in safer_nearby.iterrows()]
    if not safer_list:
        safer_list = [f"{r['District']} (WQRI: {r['Risk Score']:.1f})" for _, r in nearby_dists.sort_values(by="Risk Score").head(2).iterrows()]
        
    # Health and suitability badges
    from src.health_engine import analyze_district_health_hazards
    hazards, _, _, safety_status = analyze_district_health_hazards(dist_row, water_cols)
    
    # Resolve API Key
    resolved_key = api_key or os.environ.get("NVIDIA_API_KEY")
    if not resolved_key or resolved_key.strip() == "":
        resolved_key = DEFAULT_NVIDIA_KEY
        
    # Format actual chemical measurements from the dataset to prevent hallucinations
    from src.risk_calculator import match_bis_standard
    measurements_list = []
    for col in water_cols:
        val = dist_row.get(col)
        if pd.notnull(val):
            _, limits = match_bis_standard(col)
            limit_str = ""
            if limits:
                limit_str = f" [BIS Standard Acceptable: {limits[0]}]"
            measurements_list.append(f"- {col}: {val:.3f}{limit_str}")
    measurements_text = "\n        ".join(measurements_list)
    
    try:
        # Build prompt with exact parameter specifics
        prompt = f"""
        You are the GroundWater Guardian AI Advisor, a helpful and objective AI assistant for citizens of India.
        Your goal is to answer a user's question about groundwater safety in their area using ONLY the following verified data.
        Never invent data or assume chemicals are present if they are not listed.
        
        DISTRICT PROFILE DATA:
        - Target District: {target_dist}
        - State: {state_name}
        - Groundwater Risk Score (GWQRI): {risk_score:.1f} / 100
        - Risk Classification: {risk_cat}
        - Water Safety Status: {safety_status}
        - Primary Exceedance Issues: {exceedances}
        - Nearby Districts for Comparison: {", ".join(safer_list)}
        
        ACTUAL DISTRICT CHEMICAL MEASUREMENTS (FROM DATASET):
        {measurements_text}
        
        USER QUERY: "{query}"
        
        GUIDELINES:
        1. Answer the query directly and clearly using the profile data.
        2. If the user asks for exact values, specifics, or levels of chemicals, quote the numbers directly from the ACTUAL DISTRICT CHEMICAL MEASUREMENTS list.
        3. Keep the answer under 4 sentences. Make it extremely easy to read for a layperson.
        4. Clearly state whether the water is "Safe for Drinking", "Requires Filtration", or if "Immediate Attention is Required".
        5. Explain potential health implications in a helpful, non-alarmist way (e.g. use "associated with risk of" rather than "causes disease").
        6. Suggest practical precautions (like using RO filtration, carbon filters, or testing).
        
        Do not output technical jargon or PCA formulas. Focus on what the citizen should do.
        """
        
        ans_text = call_nvidia_llm(prompt, resolved_key)
        return ans_text
        
    except Exception as e:
        return f"*(API Connection Offline: {e})*\n\n" + generate_offline_citizen_answer(
            target_dist, state_name, risk_score, risk_cat, safety_status, exceedances, safer_list, query
        )

def generate_offline_citizen_answer(district, state, score, cat, status, exceedances, safer_list, query):
    """
    Generates a rule-based offline answer to citizen queries.
    """
    ans = f"### Groundwater Safety Guide: **{district}, {state}**\n\n"
    
    # Check if they are asking about safety
    if "safe" in query.lower():
        if status == "Safe for Drinking":
            ans += f"🟢 **Safety Status: Safe for Drinking.** The groundwater in **{district}** has a low risk index of **{score:.1f}**. No major parameters exceed acceptable safety guidelines. General use is safe."
        elif status == "Requires Filtration":
            ans += f"🟡 **Safety Status: Requires Filtration.** The water in **{district}** has a moderate risk score of **{score:.1f}**. Exceedances like *{exceedances}* indicate filtration (such as active carbon or standard RO filters) is recommended before drinking."
        else:
            ans += f"🔴 **Safety Status: Immediate Attention Required.** The water in **{district}** has a high risk index of **{score:.1f}**. Main pollutants: *{exceedances}*. It is highly advised to avoid drinking raw groundwater without proper filtration (heavy metal filters or RO)."
            
    # Check if they ask about biggest risk
    elif "risk" in query.lower() or "pollutant" in query.lower() or "hazard" in query.lower():
        ans += f"⚠️ **Primary Hazard in {district}:** The main water quality issues are *{exceedances}*. This represents a potential risk over long-term consumption. We recommend home filtration to reduce exposure."
        
    # Check if they ask about nearby districts
    elif "safer" in query.lower() or "nearby" in query.lower() or "comparison" in query.lower():
        ans += f"🗺️ **Safer Surrounding Districts:** Based on distance and risk indicators, the following nearby districts are safer:  \n" + "  \n".join([f"- {item}" for item in safer_list])
        
    # Default fallback answer
    else:
        ans += f"💧 **Water Advisor Advisory for {district}:**  \n"
        ans += f"- **Risk Level:** {cat} (Score: {score:.1f}/100)  \n"
        ans += f"- **Status:** **{status}**  \n"
        ans += f"- **Key Exceedances:** {exceedances}  \n"
        ans += f"- **Precaution:** Home water filtration (RO/Activated Alumina) is recommended. Consider periodic testing if sourcing from private wells."
        
    return ans


def generate_treatment_recommendation(district_row: pd.Series, water_cols: list, hazards: list, api_key: str = None):
    """
    Generates a constrained citizen-facing treatment recommendation from actual
    district measurements. Falls back to deterministic rules if the API is offline.
    """
    from src.risk_calculator import match_bis_standard

    district = district_row.get("District", "Selected district")
    state = district_row.get("State", "")
    score = district_row.get("Risk Score", 0.0)
    category = district_row.get("Risk Category", "Unclassified")
    contributors = district_row.get("Major Contributors", "Within Standard Limits")

    exceedance_rows = []
    for col in water_cols:
        val = district_row.get(col)
        if pd.isnull(val):
            continue
        key, limits = match_bis_standard(col)
        if not limits:
            continue
        acc_lim, perm_lim = limits
        if key == "ph":
            exceeded = val < 6.5 or val > 8.5
            limit_text = "6.5 - 8.5"
        elif key == "dissolved oxygen":
            exceeded = val < acc_lim
            limit_text = f"minimum {acc_lim}"
        else:
            exceeded = val > acc_lim
            limit_text = f"{acc_lim} acceptable, {perm_lim} permissible"
        if exceeded:
            exceedance_rows.append(f"{col}: measured {val:.2f}; standard {limit_text}")

    hazard_text = [
        f"{hz.get('parameter')}: {hz.get('severity')} - {hz.get('title')}"
        for hz in hazards[:4]
    ]

    resolved_key = api_key or os.environ.get("NVIDIA_API_KEY")
    if not resolved_key or resolved_key.strip() == "":
        resolved_key = DEFAULT_NVIDIA_KEY

    if not exceedance_rows:
        return generate_offline_treatment_recommendation(district, score, category, contributors)

    try:
        prompt = f"""
        You are GroundWater Guardian India's treatment recommendation assistant.
        Use ONLY the supplied district measurements below. Do not invent measurements,
        disease counts, outbreaks, or unsupported conclusions.

        DISTRICT:
        - District: {district}
        - State: {state}
        - Water Risk Score: {score:.1f}/100
        - Risk Category: {category}
        - Major Contributors: {contributors}

        ACTUAL EXCEEDANCES:
        {chr(10).join("- " + item for item in exceedance_rows)}

        HEALTH HAZARD FLAGS:
        {chr(10).join("- " + item for item in hazard_text) if hazard_text else "- None triggered"}

        Return exactly this compact markdown format:
        **Primary Concern:** one short phrase
        **Recommended Treatment:** one practical treatment
        **Household Advice:** one citizen-friendly precaution
        **Severity:** Low, Moderate, High, or Critical
        """
        return call_nvidia_llm(prompt, resolved_key)
    except Exception as e:
        return f"*(Treatment engine offline: {e})*\n\n" + generate_offline_treatment_recommendation(
            district, score, category, contributors
        )


def generate_offline_treatment_recommendation(district, score, category, contributors):
    concern = contributors if contributors else "No major exceedance"
    lower = str(contributors).lower()
    if "fluoride" in lower:
        treatment = "Activated Alumina or Nalgonda defluoridation"
        advice = "Avoid untreated borewell water for daily drinking until filtration is verified."
    elif "arsenic" in lower:
        treatment = "Certified arsenic removal filter or safer deep aquifer source"
        advice = "Do not rely on boiling; test the source and use verified treated water."
    elif "uranium" in lower:
        treatment = "Reverse Osmosis or selective ion-exchange treatment"
        advice = "Use treated water for drinking and cooking."
    elif "nitrate" in lower:
        treatment = "Reverse Osmosis or ion-exchange treatment"
        advice = "Avoid using untreated shallow-well water for infant formula."
    elif "hardness" in lower or "chloride" in lower or "ec" in lower:
        treatment = "RO filtration or community desalination/softening"
        advice = "Use treated water for drinking if taste, scaling, or salinity is high."
    else:
        treatment = "Standard sediment, carbon, and UV filtration"
        advice = "Continue periodic water testing, especially for private borewells."

    if score >= 70:
        severity = "Critical"
    elif score >= 50:
        severity = "High"
    elif score >= 30:
        severity = "Moderate"
    else:
        severity = "Low"

    return (
        f"**Primary Concern:** {concern}\n\n"
        f"**Recommended Treatment:** {treatment}\n\n"
        f"**Household Advice:** {advice}\n\n"
        f"**Severity:** {severity}"
    )
