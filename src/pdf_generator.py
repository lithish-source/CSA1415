import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
import pandas as pd
import numpy as np

# NumberedCanvas subclass to compute total pages and draw headers/footers dynamically
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#334155"))
        
        # Header (Only on page 2 and later)
        if self._pageNumber > 1:
            self.drawString(54, 750, "GROUNDWATER HEALTH HAZARD INTELLIGENCE REPORT - POLICY BRIEF")
            self.drawRightString(558, 750, "MINISTRY OF JAL SHAKTI, GOVT OF INDIA")
            self.setStrokeColor(colors.HexColor("#94a3b8"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
        # Footer (On all pages)
        self.setStrokeColor(colors.HexColor("#94a3b8"))
        self.setLineWidth(0.5)
        self.line(54, 50, 558, 50)
        
        self.setFont("Helvetica", 8)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 38, page_text)
        self.drawString(54, 38, "CONFIDENTIAL - GOVERNMENT DECISION SUPPORT USE ONLY")
        
        self.restoreState()


def generate_pdf_report(df: pd.DataFrame, 
                        clean_report: dict, 
                        pca_results: dict, 
                        risk_weights: dict, 
                        correlation_results: dict, 
                        output_path: str):
    """
    Generates a publication-quality government policy report summarizing the analysis.
    Preserved for backwards compatibility with the national policy briefing system.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Government Palette (Navy, Crimson, Slate)
    c_primary = colors.HexColor("#1e3a8a")   # Deep navy blue
    c_alert = colors.HexColor("#991b1b")     # Crimson alert red
    c_secondary = colors.HexColor("#0f766e") # Slate Teal
    c_dark = colors.HexColor("#0f172a")      # Slate 900
    
    title_style = ParagraphStyle(
        'GovTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'GovSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=25
    )
    
    h1_style = ParagraphStyle(
        'GovH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'GovH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=c_alert,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'GovBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_dark,
        spaceAfter=7
    )
    
    bullet_style = ParagraphStyle(
        'GovBullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    table_text_style = ParagraphStyle(
        'GovTableText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=c_dark
    )
    
    story = []
    
    # --- PAGE 1: OFFICE BRIEF & EXECUTIVE SUMMARY ---
    story.append(Paragraph("GROUNDWATER HEALTH HAZARD INTELLIGENCE REPORT", title_style))
    story.append(Paragraph("National Hydrological Risk Assessment & Engineering Policy Briefing", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Document info block box
    info_data = [
        [Paragraph("<b>ISSUED BY:</b> Office of the Scientific Advisor, Ministry of Jal Shakti", table_text_style),
         Paragraph("<b>DATE OF ISSUE:</b> June 2026", table_text_style)],
        [Paragraph("<b>CLASSIFICATION:</b> Government Decision Support (Official)", table_text_style),
         Paragraph("<b>SUBJECT:</b> Groundwater Toxins & Public Health Containment", table_text_style)]
    ]
    t_info = Table(info_data, colWidths=[250, 250])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("1. Executive Summary", h1_style))
    summary_text = (
        "This strategic policy brief outlines sub-surface groundwater toxicity hazards across "
        "monitored Indian districts. By consolidating localized well-level records into district centroids "
        "and applying a principal component hazard index (GWQRI) mapped to the Bureau of Indian Standards (BIS IS 10500:2012), "
        "this system identifies regions under high and critical health stress. The resulting rankings and chemical mappings "
        "aim to prioritize public filter installations, deep well replacements, and regional epidemiological monitoring."
    )
    story.append(Paragraph(summary_text, body_style))
    
    story.append(Paragraph("2. Groundwater Data Ingestion & Centroid Summary", h1_style))
    clean_text = (
        f"A total of <b>{clean_report['initial_rows']}</b> individual water samples/well coordinates were processed. "
        f"The data was collapsed to <b>{clean_report['final_rows']}</b> distinct district centroids to enable a unified, "
        f"district-wise national risk ranking. Missing parameters were resolved using state-wise median imputation, "
        f"and outliers capped. This aggregated database represents the spatial hydrogeological baseline for this policy briefing."
    )
    story.append(Paragraph(clean_text, body_style))
    
    # Parameter summaries
    story.append(Paragraph("National Chemical Exceedance Indicators", h2_style))
    sum_data = [["Parameter Analyzed", "Acceptable Limit (BIS)", "Permissible Limit (BIS)", "Exceedances Imputed/Handled"]]
    all_keys = set(clean_report["missing_imputed"].keys()).union(clean_report["outliers_handled"].keys())
    for k in sorted(list(all_keys))[:6]:
        # Limits lookup
        from src.risk_calculator import match_bis_standard
        _, limits = match_bis_standard(k)
        limits_str = f"{limits[0]}" if limits else "N/A"
        limits_perm = f"{limits[1]}" if limits else "N/A"
        
        sum_data.append([
            k.split(" (")[0],
            limits_str,
            limits_perm,
            f"Imputed: {clean_report['missing_imputed'].get(k, 0)} | Outliers: {clean_report['outliers_handled'].get(k, 0)}"
        ])
    t_sum = Table(sum_data, colWidths=[130, 90, 90, 190])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (1,0), (2,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f1f5f9")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e0")),
    ]))
    story.append(t_sum)
    
    story.append(PageBreak())
    
    # --- PAGE 2: COVARIANCE DRIVERS & EMERGENCY LEDGER ---
    story.append(Paragraph("3. Mathematical Hazard Drivers (PCA Loadings)", h1_style))
    pca_text = (
        "Principal Component Analysis was executed silently on the standardized chemical profiles. "
        "To compile the risk index, parameter directionality was pre-corrected (pH transformed to absolute "
        "deviation from 7.0; all heavy metals and salts standardized so that positive loadings align with threat). "
        "The composite risk index is formed by the explained-variance weights of the principal axes, isolating "
        "the principal geological contributors of water hazards."
    )
    story.append(Paragraph(pca_text, body_style))
    story.append(Spacer(1, 5))
    
    # PCA Table
    pca_headers = [["Principal Axis", "Variance Explained", "Cumulative Variance", "Risk Coefficient Weight", "Dominant Contaminants (Loadings)"]]
    for i, pc in enumerate(risk_weights.keys()):
        var_pct = pca_results["explained_variance"][i] * 100
        cum_pct = pca_results["cumulative_variance"][i] * 100
        weight = risk_weights[pc] * 100
        contributors = pca_results["major_contributors"][pc][:2]
        contrib_str = ", ".join(contributors)
        
        pca_headers.append([
            pc,
            f"{var_pct:.1f}%",
            f"{cum_pct:.1f}%",
            f"{weight:.1f}%",
            contrib_str
        ])
    t_pca = Table(pca_headers, colWidths=[70, 80, 80, 80, 190])
    t_pca.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (1,0), (3,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f1f5f9")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e0")),
    ]))
    story.append(t_pca)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("4. Emergency Hydrological Intervention Ledger", h1_style))
    story.append(Paragraph(
        "The districts below exhibit the highest multi-hazard risk scores (GWQRI) nationwide "
        "and require priority deployment of water purification filters or deep-aquifer replacements.",
        body_style
    ))
    
    # Sort districts by GWQRI
    df_sorted = df.sort_values(by="Risk Score", ascending=False)
    
    # Top 10 High Risk Table
    high_risk_data = [["District", "State", "GWQRI Score", "Risk Tier", "Exceeded Parameters (BIS)"]]
    for idx, row in df_sorted.head(10).iterrows():
        high_risk_data.append([
            row["District"],
            row["State"],
            f"{row['Risk Score']:.1f}",
            row["Risk Category"],
            row["Major Contributors"][:45] + ("..." if len(row["Major Contributors"]) > 45 else "")
        ])
    t_hr = Table(high_risk_data, colWidths=[100, 100, 60, 80, 160])
    t_hr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_alert),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (2,0), (3,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#fef2f2")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e0")),
    ]))
    story.append(t_hr)
    
    story.append(PageBreak())
    
    # --- PAGE 3: HEALTH ENGINE & POLICY DIRECTIVES ---
    story.append(Paragraph("5. Scientific Health Risk Mapping", h1_style))
    story.append(Paragraph(
        "The GHHIS Health Risk Engine automatically maps district chemical concentrations to physiological "
        "hazards, providing clinical context to engineering data.",
        body_style
    ))
    
    health_mappings = [
        ["Contaminant", "Critical Threshold", "Primary Physiological Damage Mapped by Health Engine"],
        [Paragraph("<b>Fluoride (F)</b>", table_text_style), "1.5 mg/L", "Dental fluorosis (yellow staining/pitting) and crippling skeletal fluorosis (joint/bone deformation)."],
        [Paragraph("<b>Arsenic (As)</b>", table_text_style), "10 ppb", "Arsenicosis (skin lesions, melanosis, hyperkeratosis on palms), vascular gangrene, and bladder/lung cancers."],
        [Paragraph("<b>Uranium (U)</b>", table_text_style), "30 ppb", "Chemical nephrotoxicity (necrosis of kidney proximal tubules, chronic kidney disease)."],
        [Paragraph("<b>Nitrate (NO3)</b>", table_text_style), "45 mg/L", "Infant Methemoglobinemia (Blue Baby Syndrome - hypoxia), thyroid disorders, and gastric carcinomas."],
        [Paragraph("<b>Hardness</b>", table_text_style), "600 mg/L", "Severe carbonate scaling, soap wastage, and potential correlation with urolithiasis (kidney stones)."]
    ]
    t_hm = Table(health_mappings, colWidths=[100, 80, 320])
    t_hm.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#475569")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e0")),
    ]))
    story.append(t_hm)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("6. National Strategic Remediation Policy Actions", h1_style))
    story.append(Paragraph(
        "To mitigate sub-surface chemical exposures in high-risk zones, the following structural policy actions "
        "must be prioritized immediately:",
        body_style
    ))
    
    # Dynamic recommendations
    dominant_params = []
    for pc, list_contrib in pca_results["major_contributors"].items():
        for item in list_contrib[:2]:
            param_name = item.split(" (")[0]
            if param_name not in dominant_params:
                dominant_params.append(param_name)
                
    for param in dominant_params[:4]:
        p_lower = param.lower()
        if "fluoride" in p_lower:
            story.append(Paragraph("• <b>Fluoride Containment</b>: Scale up Activated Alumina filter beds and domestic Nalgonda defluoridation buckets in Fluoride-exceeded regions.", bullet_style))
        elif "arsenic" in p_lower:
            story.append(Paragraph("• <b>Arsenic Remediation</b>: Deploy deep tube wells (reaching beneath thick clay beds to tap safe aquifers) and install arsenic co-precipitation filters.", bullet_style))
        elif "uranium" in p_lower or p_lower == "u" or "u (" in p_lower:
            story.append(Paragraph("• <b>Uranium Separation</b>: Construct centralized Reverse Osmosis (RO) plants or specialized selective anion-exchange columns in Uranium-dense clusters.", bullet_style))
        elif "nitrate" in p_lower:
            story.append(Paragraph("• <b>Agricultural Runoff Mitigation</b>: Regulate nitrogenous fertilizer applications near municipal water sources and install concrete sanitary seals on wells.", bullet_style))
        elif "tds" in p_lower or "hardness" in p_lower or "chloride" in p_lower or "ec" in p_lower or "conductivity" in p_lower:
            story.append(Paragraph("• <b>Desalination Infrastructure</b>: Finance community-scale solar-powered RO hubs in high-salinity tracts and implement rainwater-harvesting aquifer recharge schemes.", bullet_style))
        elif "so4" in p_lower or "sulfate" in p_lower:
            story.append(Paragraph("• <b>Sulfate Treatment</b>: Deploy standard RO or ion-exchange filters in sulfate-exceeded zones to protect consumer gastrointestinal tracts.", bullet_style))
        else:
            story.append(Paragraph(f"• <b>{param} Monitoring</b>: Standardize routine laboratory screenings for {param} and configure municipal filtration systems to enforce BIS standards.", bullet_style))
            
    story.append(Paragraph("• <b>Health System Integration</b>: Sync the groundwater risk maps with local primary health centres (PHCs) to coordinate diagnostic screenings for skeletal fluorosis and chronic kidney disorders.", bullet_style))
    
    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)


def generate_district_pdf_report(district_row: pd.Series, water_cols: list, output_path: str):
    """
    Generates a citizen-focused single-page 'Water Safety Report Card' PDF for a selected district.
    """
    # 1. Fetch Health hazards & suitability categories
    from src.health_engine import analyze_district_health_hazards
    from src.risk_calculator import match_bis_standard
    
    hazards, risk_tier, dom_hazard, safety_status = analyze_district_health_hazards(district_row, water_cols)
    
    # Color scheme mapping based on risk level
    if safety_status == "Safe for Drinking":
        c_accent = colors.HexColor("#10b981")     # Green
        c_accent_light = colors.HexColor("#d1fae5")
        c_text_dark = colors.HexColor("#065f46")
        status_symbol = "🟢"
    elif safety_status == "Requires Filtration":
        c_accent = colors.HexColor("#f59e0b")     # Yellow/Orange
        c_accent_light = colors.HexColor("#fef3c7")
        c_text_dark = colors.HexColor("#92400e")
        status_symbol = "🟡"
    else:
        c_accent = colors.HexColor("#dc2626")     # Red
        c_accent_light = colors.HexColor("#fee2e2")
        c_text_dark = colors.HexColor("#991b1b")
        status_symbol = "🔴"

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#0f172a") # Slate 900
    
    # Custom text styles
    banner_title_style = ParagraphStyle(
        'BannerTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.white
    )
    banner_sub_style = ParagraphStyle(
        'BannerSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#94a3b8")
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=c_primary,
        spaceBefore=8,
        spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1e293b")
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    story = []
    
    # ----------------- 1. HEADER BANNER -----------------
    banner_data = [
        [
            Paragraph("🛡️ GroundWater Guardian India", banner_title_style),
            Paragraph("<b>WATER SAFETY REPORT CARD</b>", ParagraphStyle('RC', parent=banner_title_style, alignment=2, fontSize=11))
        ],
        [
            Paragraph("Know Your Water. Protect Your Health.", banner_sub_style),
            Paragraph("Source: CGWB & GHHIS Registry", ParagraphStyle('RS', parent=banner_sub_style, alignment=2))
        ]
    ]
    t_banner = Table(banner_data, colWidths=[300, 240])
    t_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_primary),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 8))
    
    # ----------------- 2. OVERVIEW ROW (DIAL & ADVISORY) -----------------
    # Left Box: Risk Index Dial
    score_p_val = Paragraph(f"<font size=28><b>{district_row['Risk Score']:.0f}</b></font><br/><font size=8><b>WQRI RISK INDEX</b></font>", 
                            ParagraphStyle('DialText', alignment=1, textColor=c_text_dark, leading=16))
    status_p_val = Paragraph(f"<b>{status_symbol} {safety_status}</b>", 
                             ParagraphStyle('StatusText', alignment=1, textColor=c_text_dark, fontSize=9, leading=11))
    
    dial_data = [[score_p_val], [Spacer(1, 4)], [status_p_val]]
    t_dial_box = Table(dial_data, colWidths=[150])
    t_dial_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_accent_light),
        ('BOX', (0,0), (-1,-1), 1.5, c_accent),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    
    # Right Box: Details
    contributors = district_row['Major Contributors']
    if pd.isnull(contributors) or not contributors.strip():
        contributors = "Within Standard Limits"
        
    details_text = f"""
    <b>District:</b> {district_row['District']}<br/>
    <b>State:</b> {district_row['State']}<br/>
    <b>Coordinates:</b> Lat {district_row['Latitude']:.4f}, Lon {district_row['Longitude']:.4f}<br/>
    <b>Primary Concerns:</b> {contributors}<br/>
    <b>Risk Category:</b> {district_row['Risk Category']}
    """
    t_details = Table([[Paragraph(details_text, ParagraphStyle('DetText', parent=body_style, fontSize=9.5, leading=13.5))]], colWidths=[360])
    t_details.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
    ]))
    
    t_overview = Table([[t_dial_box, t_details]], colWidths=[165, 375])
    t_overview.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_overview)
    story.append(Spacer(1, 8))
    
    # ----------------- 3. PARAMETERS TABLE -----------------
    story.append(Paragraph("Water Quality Parameter Diagnostics", h1_style))
    
    table_headers = ["Parameter", "Measured Value", "Acceptable Limit", "Permissible Limit", "Safety Status"]
    grid_data = [table_headers]
    
    for col in water_cols:
        val = district_row[col]
        if pd.isnull(val):
            continue
            
        key, limits = match_bis_standard(col)
        if not limits:
            continue
            
        acc_lim, perm_lim = limits
        clean_name = col.split(" (")[0]
        
        # Format limits & values cleanly
        val_str = f"{val:.2f}"
        if key == "ph":
            acc_str = "6.5 - 8.5"
            perm_str = "No relaxation"
            is_exceeded = val < 6.5 or val > 8.5
        elif key == "dissolved oxygen":
            acc_str = f"Min {acc_lim}"
            perm_str = "N/A"
            is_exceeded = val < acc_lim
        else:
            acc_str = f"{acc_lim}"
            perm_str = f"{perm_lim}" if perm_lim != acc_lim else "No relaxation"
            is_exceeded = val > acc_lim
            
        # Units display
        unit = "mg/L"
        if "ppb" in col.lower():
            unit = "ppb"
        elif "ppm" in col.lower():
            unit = "ppm"
        elif "µS/cm" in col.lower() or "us/cm" in col.lower() or "ec" in key:
            unit = "µS/cm"
            
        param_label = f"{clean_name} ({unit})"
        if key == "ph":
            param_label = "pH"
            
        status_label = "🟢 Within Standard"
        if is_exceeded:
            status_label = "🔴 Exceeds Standard"
            if val > perm_lim and key != "ph" and key != "dissolved oxygen" and perm_lim != acc_lim:
                status_label = "🔴 Permissible Exceeded"
                
        grid_data.append([param_label, val_str, acc_str, perm_str, status_label])
        
    t_grid = Table(grid_data, colWidths=[160, 95, 95, 95, 95])
    
    # Table Styling
    grid_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (1,0), (3,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
    ]
    
    # Alternating rows
    for r_idx in range(1, len(grid_data)):
        bg = colors.HexColor("#f8fafc") if r_idx % 2 == 1 else colors.white
        grid_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), bg))
        
        # Color specific safety status
        status_val = grid_data[r_idx][4]
        if "Exceeds" in status_val or "Permissible" in status_val:
            grid_style.append(('TEXTCOLOR', (4, r_idx), (4, r_idx), colors.HexColor("#dc2626")))
            grid_style.append(('FONTNAME', (4, r_idx), (4, r_idx), 'Helvetica-Bold'))
        else:
            grid_style.append(('TEXTCOLOR', (4, r_idx), (4, r_idx), colors.HexColor("#16a34a")))
            
    t_grid.setStyle(TableStyle(grid_style))
    story.append(t_grid)
    story.append(Spacer(1, 8))
    
    # ----------------- 4. HEALTH ENGINE WARNINGS & ACTIONS -----------------
    story.append(Paragraph("Health Implications & Safety Guidelines", h1_style))
    
    warnings_story = []
    if hazards:
        warnings_story.append(Paragraph("<b>Triggered Physiological Associations:</b>", ParagraphStyle('TitleW', parent=body_style, fontName='Helvetica-Bold')))
        for hz in hazards[:2]: # limit to top 2 for single-page budget
            warnings_story.append(Paragraph(f"• <b>{hz['parameter']} Warning ({hz['severity']}):</b> {hz['title']}. {hz['description']} Symptoms may include {hz['symptoms'].lower()}", bullet_style))
    else:
        warnings_story.append(Paragraph("• No chemical parameters exceed Bureau of Indian Standards acceptable limits. General consumption carries low risk.", bullet_style))
        
    # Household intervention recommendation based on exceedances
    warnings_story.append(Spacer(1, 4))
    warnings_story.append(Paragraph("<b>Recommended Precautions:</b>", ParagraphStyle('TitleRec', parent=body_style, fontName='Helvetica-Bold')))
    
    exceed_lower = contributors.lower()
    if "fluoride" in exceed_lower:
        warnings_story.append(Paragraph("• Avoid drinking raw groundwater. Deploy household Activated Alumina filters or Nalgonda package systems.", bullet_style))
    elif "arsenic" in exceed_lower:
        warnings_story.append(Paragraph("• Do not drink from shallow wells. Prioritize deep tubewells tapping aquifers below clay boundaries.", bullet_style))
    elif "uranium" in exceed_lower:
        warnings_story.append(Paragraph("• Use certified Reverse Osmosis (RO) filters or specialized selective anion-exchange resins.", bullet_style))
    elif "nitrate" in exceed_lower:
        warnings_story.append(Paragraph("• Restrict shallow well usage for infants (Methemoglobinemia risk). Install sanitary concrete seals.", bullet_style))
    else:
        warnings_story.append(Paragraph("• Standard household filtration (Activated Carbon / Sediment filters / UV) is sufficient to maintain water aesthetics.", bullet_style))
        
    t_warn_box = Table([[warnings_story]], colWidths=[540])
    t_warn_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#fef2f2") if safety_status == "Immediate Attention Required" else colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#fecaca") if safety_status == "Immediate Attention Required" else colors.HexColor("#e2e8f0")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_warn_box)
    story.append(Spacer(1, 15))
    
    # ----------------- 5. DISCLAIMER & FOOTER -----------------
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        fontName='Helvetica-Oblique',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#64748b"),
        alignment=1
    )
    disclaimer_text = (
        "Disclaimer: This card provides educational water safety guidance based on aggregated local well-sampling "
        "measurements. Mapped health implications denote potential geological risks and do not declare active clinical disease outbreaks. "
        "Always test private household borewells individually. Compiled by GroundWater Guardian India."
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))
    
    # Build Document
    doc.build(story)
