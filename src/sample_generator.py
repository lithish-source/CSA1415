import pandas as pd
import numpy as np

def generate_synthetic_data(num_districts_per_state=12, seed=42):
    """
    Generates a highly realistic synthetic dataset containing drinking water quality parameters
    and disease outbreaks for various Indian districts.
    
    The generation mimics known hydrogeological characteristics of Indian states:
    - Rajasthan: High Fluoride, High TDS, High Hardness
    - West Bengal: High Arsenic, High Iron
    - Uttar Pradesh: High Nitrate (agricultural runoff), High Turbidity
    - Kerala: Acidic pH, Low TDS, moderate outbreaks
    - Maharashtra: Moderate Hardness and TDS
    - Punjab: High TDS, High Nitrate
    - Assam: High Iron, High Turbidity
    - Andhra Pradesh: High Fluoride, High TDS
    - Bihar: High Arsenic, High Nitrate, high outbreaks
    - Tamil Nadu: High Hardness, High Chloride (coastal)
    """
    np.random.seed(seed)
    
    states_config = {
        "Rajasthan": {
            "fluoride": (1.2, 3.5), "tds": (800, 2000), "hardness": (300, 800),
            "arsenic": (0.001, 0.005), "nitrate": (20, 60), "turbidity": (1, 5),
            "ph": (7.2, 8.5), "chloride": (250, 700), "conductivity": (1200, 3000),
            "do": (6.5, 8.0), "iron": (0.1, 0.5), "disease_factor": 0.8
        },
        "West Bengal": {
            "fluoride": (0.2, 0.8), "tds": (200, 600), "hardness": (100, 250),
            "arsenic": (0.02, 0.12), "nitrate": (10, 35), "turbidity": (4, 12),
            "ph": (6.8, 7.6), "chloride": (50, 200), "conductivity": (350, 900),
            "do": (5.5, 7.2), "iron": (1.0, 4.5), "disease_factor": 1.6
        },
        "Uttar Pradesh": {
            "fluoride": (0.4, 1.2), "tds": (400, 1000), "hardness": (200, 450),
            "arsenic": (0.002, 0.025), "nitrate": (40, 95), "turbidity": (5, 15),
            "ph": (7.0, 8.2), "chloride": (100, 300), "conductivity": (600, 1500),
            "do": (5.0, 7.0), "iron": (0.3, 1.2), "disease_factor": 1.8
        },
        "Kerala": {
            "fluoride": (0.1, 0.5), "tds": (80, 250), "hardness": (40, 120),
            "arsenic": (0.0001, 0.002), "nitrate": (5, 20), "turbidity": (1, 4),
            "ph": (6.0, 6.9), "chloride": (20, 80), "conductivity": (120, 400),
            "do": (7.0, 8.5), "iron": (0.1, 0.6), "disease_factor": 0.6
        },
        "Maharashtra": {
            "fluoride": (0.3, 1.1), "tds": (300, 800), "hardness": (180, 400),
            "arsenic": (0.001, 0.008), "nitrate": (15, 45), "turbidity": (2, 8),
            "ph": (7.1, 8.0), "chloride": (80, 250), "conductivity": (450, 1200),
            "do": (6.0, 7.8), "iron": (0.2, 0.8), "disease_factor": 1.1
        },
        "Punjab": {
            "fluoride": (0.5, 1.6), "tds": (600, 1500), "hardness": (250, 600),
            "arsenic": (0.005, 0.035), "nitrate": (45, 110), "turbidity": (2, 6),
            "ph": (7.3, 8.3), "chloride": (150, 400), "conductivity": (900, 2200),
            "do": (6.2, 7.5), "iron": (0.2, 0.7), "disease_factor": 1.2
        },
        "Assam": {
            "fluoride": (0.3, 1.0), "tds": (150, 450), "hardness": (80, 200),
            "arsenic": (0.002, 0.015), "nitrate": (8, 25), "turbidity": (6, 18),
            "ph": (6.5, 7.4), "chloride": (40, 150), "conductivity": (220, 700),
            "do": (5.8, 7.4), "iron": (1.5, 6.0), "disease_factor": 1.4
        },
        "Andhra Pradesh": {
            "fluoride": (1.0, 2.8), "tds": (500, 1200), "hardness": (220, 500),
            "arsenic": (0.001, 0.005), "nitrate": (20, 55), "turbidity": (2, 7),
            "ph": (7.2, 8.3), "chloride": (120, 350), "conductivity": (800, 1800),
            "do": (6.2, 7.8), "iron": (0.1, 0.4), "disease_factor": 1.0
        },
        "Bihar": {
            "fluoride": (0.4, 1.4), "tds": (350, 800), "hardness": (180, 380),
            "arsenic": (0.015, 0.08), "nitrate": (35, 80), "turbidity": (5, 14),
            "ph": (6.9, 7.9), "chloride": (90, 220), "conductivity": (500, 1200),
            "do": (5.2, 7.1), "iron": (0.5, 2.2), "disease_factor": 1.9
        },
        "Tamil Nadu": {
            "fluoride": (0.3, 1.2), "tds": (450, 1100), "hardness": (250, 550),
            "arsenic": (0.001, 0.006), "nitrate": (15, 40), "turbidity": (2, 6),
            "ph": (7.0, 8.1), "chloride": (180, 450), "conductivity": (700, 1600),
            "do": (6.2, 7.7), "iron": (0.1, 0.5), "disease_factor": 1.1
        }
    }
    
    # Famous districts in these states
    districts_db = {
        "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer", "Bikaner", "Alwar", "Barmer", "Nagaur", "Bhilwara", "Sikar", "Churu"],
        "West Bengal": ["Kolkata", "Howrah", "Darjeeling", "Nadia", "Murshidabad", "Purulia", "Bankura", "Birbhum", "Malda", "Hooghly", "Medinipur", "Jalpaiguri"],
        "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Meerut", "Prayagraj", "Bareilly", "Aligarh", "Moradabad", "Gorakhpur", "Jhansi", "Ghaziabad"],
        "Kerala": ["Trivandrum", "Kochi", "Kozhikode", "Thrissur", "Kollam", "Alappuzha", "Palakkad", "Malappuram", "Kannur", "Kottayam", "Idukki", "Wayanad"],
        "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Thane", "Aurangabad", "Solapur", "Amravati", "Kolhapur", "Sangli", "Satara", "Jalgaon"],
        "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Hoshiarpur", "Pathankot", "Moga", "Firozpur", "Gurdaspur", "Sangrur", "Mohali"],
        "Assam": ["Guwahati", "Dibrugarh", "Silchar", "Jorhat", "Nagaon", "Tezpur", "Tinsukia", "Sivasagar", "Karimganj", "Dhubri", "Barpeta", "Goalpara"],
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Rajahmundry", "Kadapa", "Tirupati", "Anantapur", "Eluru", "Ongole", "Chittoor"],
        "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia", "Darbhanga", "Arrah", "Begusarai", "Katihar", "Munger", "Chapra", "Nalanda"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Trichy", "Salem", "Tirunelveli", "Vellore", "Erode", "Thanjavur", "Dindigul", "Kanchipuram", "Tuticorin"]
    }
    
    data = []
    
    for state, config in states_config.items():
        districts = districts_db.get(state, [f"District_{i}" for i in range(num_districts_per_state)])
        # Trim list if we need fewer, or pad if we need more
        districts = districts[:num_districts_per_state]
        
        for dist in districts:
            # Generate water quality parameters based on state boundaries
            ph = np.random.uniform(*config["ph"])
            tds = np.random.uniform(*config["tds"])
            turbidity = np.random.uniform(*config["turbidity"])
            nitrate = np.random.uniform(*config["nitrate"])
            fluoride = np.random.uniform(*config["fluoride"])
            chloride = np.random.uniform(*config["chloride"])
            hardness = np.random.uniform(*config["hardness"])
            conductivity = np.random.uniform(*config["conductivity"])
            do = np.random.uniform(*config["do"])
            iron = np.random.uniform(*config["iron"])
            arsenic = np.random.uniform(*config["arsenic"])
            
            # Introduce occasional null values (approx 5% of data) for cleaning practice
            row = {
                "District": dist,
                "State": state,
                "pH": ph if np.random.rand() > 0.05 else np.nan,
                "TDS (mg/L)": tds if np.random.rand() > 0.05 else np.nan,
                "Turbidity (NTU)": turbidity if np.random.rand() > 0.05 else np.nan,
                "Nitrate (mg/L)": nitrate if np.random.rand() > 0.05 else np.nan,
                "Fluoride (mg/L)": fluoride if np.random.rand() > 0.05 else np.nan,
                "Chloride (mg/L)": chloride if np.random.rand() > 0.05 else np.nan,
                "Hardness (mg/L)": hardness if np.random.rand() > 0.05 else np.nan,
                "Electrical Conductivity (µS/cm)": conductivity if np.random.rand() > 0.05 else np.nan,
                "Dissolved Oxygen (mg/L)": do if np.random.rand() > 0.05 else np.nan,
                "Iron (mg/L)": iron if np.random.rand() > 0.05 else np.nan,
                "Arsenic (mg/L)": arsenic if np.random.rand() > 0.05 else np.nan,
            }
            
            # Inject outliers into ~5% of records
            if np.random.rand() < 0.05:
                # Extreme TDS
                row["TDS (mg/L)"] = np.random.uniform(3500, 6000)
            if np.random.rand() < 0.05:
                # Extreme Nitrate (agricultural dumping)
                row["Nitrate (mg/L)"] = np.random.uniform(180, 300)
            if np.random.rand() < 0.05:
                # Highly acidic or basic pH
                row["pH"] = np.random.choice([3.2, 10.8])
            
            # Disease Outbreak Statistics
            # Disease cases are positively correlated with Turbidity, Nitrate, and Arsenic/Iron,
            # and negatively correlated with Dissolved Oxygen.
            base_risk = (
                (turbidity / 15.0) * 0.4 +
                (nitrate / 100.0) * 0.3 +
                (fluoride / 3.0) * 0.1 +
                (arsenic / 0.1) * 0.1 +
                ((8.5 - do) / 8.5) * 0.1
            )
            base_risk = max(0.1, base_risk) * config["disease_factor"]
            
            # Base cases scaled with random Poisson noise
            diarrhea = int(np.random.poisson(base_risk * 150 + 10))
            typhoid = int(np.random.poisson(base_risk * 50 + 5))
            cholera = int(np.random.poisson(base_risk * 15 + 1))
            hepatitis = int(np.random.poisson(base_risk * 25 + 2))
            
            # Sometimes disease data is missing for some districts (approx 8%)
            is_reported = np.random.rand() > 0.08
            row["Diarrhea Cases"] = diarrhea if is_reported else np.nan
            row["Typhoid Cases"] = typhoid if is_reported else np.nan
            row["Cholera Cases"] = cholera if is_reported else np.nan
            row["Hepatitis Cases"] = hepatitis if is_reported else np.nan
            
            data.append(row)
            
    # Add a duplicate record for cleaning demo
    data.append(data[0].copy())
    
    # Introduce small name spelling errors to test spelling standardisation
    data[-1]["District"] = data[0]["District"] + " " # trailing whitespace
    
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    df = generate_synthetic_data()
    df.to_csv("sample_water_quality.csv", index=False)
    print(f"Generated synthetic dataset with {df.shape[0]} rows and saved to 'sample_water_quality.csv'.")
