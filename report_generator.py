from fpdf import FPDF
from utils import format_inr
from datetime import datetime

def generate_pdf_report(results: dict, filename="cost_intelligence_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "Enterprise Cost Intelligence Report", ln=True, align="C")
    
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", ln=True, align="C")
    pdf.ln(6)

    def section(title):
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_fill_color(230, 230, 250)
        pdf.cell(0, 10, title, ln=True, fill=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.ln(2)

    def line(label, value):
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(80, 8, label)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, str(value), ln=True)

    vendor = results.get("vendor", {})
    spend = results.get("spend", {})
    sla = results.get("sla", {})
    reinvest = results.get("reinvest", {})

    total = (vendor.get("total_savings_inr", 0) +
             spend.get("wasted_inr", 0) +
             sla.get("penalty_exposure_inr", 0))

    section("Executive Summary")
    line("Total Annual Impact:", format_inr(total))
    line("Vendor Savings:", format_inr(vendor.get("total_savings_inr", 0)))
    line("Cloud Recovery:", format_inr(spend.get("wasted_inr", 0)))
    line("SLA Penalty Avoided:", format_inr(sla.get("penalty_exposure_inr", 0)))
    pdf.ln(4)

    section("Agent 1 — Vendor Duplicate Detection")
    line("Duplicates Found:", vendor.get("duplicates_found", 0))
    line("Estimated Savings:", format_inr(vendor.get("total_savings_inr", 0)))
    pdf.ln(4)

    section("Agent 2 — Cloud Spend Anomaly")
    line("Anomaly Detected:", "Yes" if spend.get("anomaly_detected") else "No")
    line("Spike:", f"{spend.get('change_pct', 0)}%")
    line("Root Cause:", spend.get("root_cause", "N/A"))
    line("Recovery Amount:", format_inr(spend.get("wasted_inr", 0)))
    pdf.ln(4)

    section("Agent 3 — SLA Breach Prevention")
    line("Tasks At Risk:", sla.get("at_risk_count", 0))
    line("Penalty Avoided:", format_inr(sla.get("penalty_exposure_inr", 0)))
    pdf.ln(4)

    section("Agent 4 — Reinvestment Plan")
    line("Total Reinvestable:", format_inr(reinvest.get("total_saved_inr", 0)))
    if reinvest.get("reinvestment_plan"):
        pdf.set_font("Helvetica", "", 10)
        text = reinvest["reinvestment_plan"][:800]
        pdf.multi_cell(0, 6, text)

    pdf.output(filename)
    print(f"Report saved: {filename}")
    return filename

if __name__ == "__main__":
    dummy = {
        "vendor": {"total_savings_inr": 1840000, "duplicates_found": 14},
        "spend": {"anomaly_detected": True, "change_pct": 40, "wasted_inr": 980000, "root_cause": "Autoscaling Misconfiguration"},
        "sla": {"at_risk_count": 5, "penalty_exposure_inr": 500000},
        "reinvest": {"total_saved_inr": 3320000, "reinvestment_plan": "Invest in AI tooling and engineering talent."}
    }
    generate_pdf_report(dummy)