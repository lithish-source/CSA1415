# GroundWater Guardian India 🛡️💧

> **Know Your Drinking Water Safety Instantly.** A citizen-facing water quality and safety platform designed like a premium weather app or Air Quality Index (AQI) dashboard. 

GroundWater Guardian India is a data-driven safety platform built to answer one simple, critical question for any citizen: **"Is the water in my area safe to drink?"**

Unlike complex research portals or raw spreadsheets, this application translates complex chemical measurements and multivariate statistics into a clean, actionable safety status, specific health alerts, and household purification advice.

---

## 🌟 Key Features

*   **Citizen-First Safety Status Card**: An Apple Weather-style district card displaying the **Water Quality Risk Index (WQRI)**, safety category (Safe, Moderate Risk, High Risk), primary contaminant concern, and standard household recommendations.
*   **Mathematical Risk Attribution**: Real-time breakdown of which chemical contaminants (Fluoride, Arsenic, Nitrate, Salinity, etc.) contribute most to the risk level, computed using PCA loadings and Z-scores.
*   **AI Treatment Advice**: Generates customized household filtration recommendations (e.g., Activated Alumina for Fluoride, specific RO membranes for Uranium) and severity badges, powered by LLM integrations.
*   **Safer Alternatives Finder**: Calculates and lists the nearest lower-risk districts in your state using the Haversine distance formula.
*   **Interactive District Choropleth Map**: Clicking on any district on the interactive SVG/Plotly map instantly updates the active dashboard.
*   **Dual-District Side-by-Side Comparison**: Select any two districts to compare their chemical levels using an interactive radar/scatterpolar chart.
*   **Floating Collapsible AI Advisor**: A collapsible chatbot anchored in the bottom-right corner, equipped with interactive suggestion chips for rapid citizen Q&A.
*   **Printable PDF Report Card**: Generate and download a professional, single-page PDF report card containing the safety score, raw parameter levels, health warnings, and treatment recommendations.

---

## 🚀 Quick Start (Local Setup)

### Prerequisites

Ensure you have **Python 3.9+** installed on your system.

### 1. Clone & Navigate
```bash
git clone https://github.com/lithish-source/GroundWater-Guardian.git
cd GroundWater-Guardian
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit Dashboard
```bash
python3 -m streamlit run app.py --server.port 8503
```
Open **[http://localhost:8503](http://localhost:8503)** in your browser.

---

## 📁 Repository Structure

```
├── app.py                      # Main Streamlit dashboard & styling
├── requirements.txt            # Python dependencies
├── ground water quality dataset.xlsx # Ground truth chemical measurements
├── src/                        # Core application modules
│   ├── data_cleaning.py        # Dataset loading & missing value imputation
│   ├── pca_model.py            # Principal Component Analysis & weights extraction
│   ├── risk_calculator.py      # WQRI scoring engine & BIS standards matching
│   ├── health_engine.py        # Medical hazard & disease mapping
│   ├── gemini_insights.py      # LLM integration & prompt engineering
│   ├── gis_mapping.py          # Plotly Choropleth map renderers
│   ├── pdf_generator.py        # PDF Report card builder using FPDF
│   └── sample_generator.py     # Fallback synthetic data generator
└── ppt/                        # Project presentations & documentation
    ├── risk_calculator.pdf
    └── waterreview 1.key
```

---

## 🧪 Scientific Methodology & Mathematical Engine

The core scoring engine does not rely on arbitrary rules. It uses **Multivariate Statistical Analysis** to compute a relative **Water Quality Risk Index (WQRI)** normalized between `0` (Safest) and `100` (Highest Risk).

### 1. Principal Component Analysis (PCA)
To extract objective weights for the chemical parameters, we apply PCA to the normalized chemical variables:
$$\mathbf{X}_{std} = \frac{\mathbf{X} - \mu}{\sigma}$$

From the covariance matrix, we compute eigenvectors (Principal Components) and eigenvalues ($\lambda_k$). The parameter weight ($w_i$) for chemical parameter $i$ is calculated as the sum of its squared loadings across the components, weighted by each component's explained variance:
$$w_i = \sum_{k=1}^{m} \left( L_{ik}^2 \times \frac{\lambda_k}{\sum \lambda_j} \right)$$
where $L_{ik}$ is the loading of parameter $i$ on component $k$.

### 2. Z-Score Contaminant Attribution
To explain *why* a district's score is high, we calculate the parameter-level contribution using local Z-scores to represent deviations from the national baseline:
$$Z_{i} = \frac{x_i - \mu_i}{\sigma_i}$$
$$\text{Contribution}_i = \frac{\max(0, Z_i) \times w_i}{\sum \left(\max(0, Z_j) \times w_j\right)} \times 100\%$$

### 3. BIS Standards Matching
All individual parameters are validated against the **Bureau of Indian Standards (BIS) IS 10500:2012** guidelines:
*   **Acceptable Limit**: Safe for consumption without treatment.
*   **Permissible Limit**: Tolerable in the absence of alternative water sources.
*   **Exceeded**: Requires immediate home filtration or alternative water supplies.

---

## 🛡️ License

This project is prepared as a capstone project for academic and research purposes. All rights reserved.
