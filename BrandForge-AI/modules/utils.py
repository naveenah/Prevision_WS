"""
Utility Functions for BrandForge AI
Includes KPI calculations, data formatting, and helper functions
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import zipfile
from io import BytesIO


def calculate_kpi_projections(
    base_visitors: int,
    conversion_rate: float,
    growth_rate: float = 0.10,
    weeks: int = 12,
    lead_conversion: float = 0.30,
    revenue_per_lead: float = 500.0
) -> pd.DataFrame:
    """
    Calculate week-by-week KPI projections for launch planning.
    
    Args:
        base_visitors: Starting weekly visitor count
        conversion_rate: Percentage of visitors who signup (0.0-1.0)
        growth_rate: Weekly growth rate (0.0-1.0)
        weeks: Number of weeks to project
        lead_conversion: Percentage of signups that become qualified leads
        revenue_per_lead: Average revenue per lead
        
    Returns:
        DataFrame with weekly projections
    """
    data = []
    
    for week in range(1, weeks + 1):
        # Compound growth
        visitors = int(base_visitors * ((1 + growth_rate) ** week))
        signups = int(visitors * conversion_rate)
        leads = int(signups * lead_conversion)
        revenue = leads * revenue_per_lead
        
        data.append({
            "Week": week,
            "Visitors": visitors,
            "Signups": signups,
            "Leads": leads,
            "Revenue": revenue,
            "Conversion_Rate": f"{conversion_rate * 100:.1f}%"
        })
    
    return pd.DataFrame(data)


def format_currency(amount: float) -> str:
    """Format a number as USD currency."""
    return f"${amount:,.2f}"


def format_percentage(value: float) -> str:
    """Format a decimal as percentage."""
    return f"{value * 100:.1f}%"


def generate_google_sheets_formulas() -> Dict[str, str]:
    """
    Generate Google Sheets formulas for KPI tracking.
    
    Returns:
        Dictionary of formula names and their Excel/Sheets syntax
    """
    return {
        "Total Visitors": "=SUM(B2:B13)",
        "Total Signups": "=SUM(C2:C13)",
        "Total Leads": "=SUM(D2:D13)",
        "Total Revenue": "=SUM(E2:E13)",
        "Average Conversion": "=AVERAGE(F2:F13)",
        "Week over Week Growth": "=(B3-B2)/B2",
        "Cumulative Revenue": "=SUM($E$2:E2)",
        "0-30 Day Pipeline": "=SUMIF(G2:G13,\"0-30\",D2:D13)",
        "31-60 Day Pipeline": "=SUMIF(G2:G13,\"31-60\",D2:D13)",
        "61-90 Day Pipeline": "=SUMIF(G2:G13,\"61-90\",D2:D13)",
        "Conditional Format (Completed)": "=IF(H2=\"Completed\",TRUE,FALSE)"
    }


def create_weeks_list(start_date: str, num_weeks: int = 13) -> List[Dict]:
    """
    Create a list of week dictionaries with start/end dates.
    
    Args:
        start_date: ISO format date string (YYYY-MM-DD)
        num_weeks: Number of weeks to generate
        
    Returns:
        List of dicts with week number and date ranges
    """
    start = datetime.fromisoformat(start_date)
    weeks = []
    
    for week_num in range(1, num_weeks + 1):
        week_start = start + timedelta(weeks=week_num - 1)
        week_end = week_start + timedelta(days=6)
        
        weeks.append({
            "week": week_num,
            "start_date": week_start.strftime("%Y-%m-%d"),
            "end_date": week_end.strftime("%Y-%m-%d"),
            "label": f"Week {week_num}"
        })
    
    return weeks


def export_to_csv(df: pd.DataFrame) -> str:
    """
    Convert DataFrame to CSV string.
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        CSV string
    """
    return df.to_csv(index=False)


def create_brand_playbook_zip(
    state: Dict,
    launch_plan_df: Optional[pd.DataFrame] = None,
    kpi_df: Optional[pd.DataFrame] = None
) -> BytesIO:
    """
    Create a ZIP file containing all brand deliverables.
    
    Args:
        state: BrandState dictionary
        launch_plan_df: Optional 90-day plan DataFrame
        kpi_df: Optional KPI projections DataFrame
        
    Returns:
        BytesIO buffer containing ZIP file
    """
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 1. Brand Playbook Markdown
        playbook_md = generate_playbook_markdown(state)
        zip_file.writestr("Brand_Playbook.md", playbook_md)
        
        # 2. 90-Day Launch Plan CSV
        if launch_plan_df is not None:
            csv_content = launch_plan_df.to_csv(index=False)
            zip_file.writestr("90_Day_Launch_Plan.csv", csv_content)
        
        # 3. KPI Projections CSV
        if kpi_df is not None:
            kpi_csv = kpi_df.to_csv(index=False)
            zip_file.writestr("KPI_Projections.csv", kpi_csv)
        
        # 4. Google Sheets Formulas
        formulas = generate_google_sheets_formulas()
        formulas_text = "# Google Sheets Formulas for KPI Tracking\n\n"
        for name, formula in formulas.items():
            formulas_text += f"## {name}\n```\n{formula}\n```\n\n"
        zip_file.writestr("Google_Sheets_Formulas.txt", formulas_text)
        
        # 5. README
        readme = """# BrandForge AI - Brand Playbook Export

This package contains your complete brand strategy and launch plan.

## Files Included:

1. **Brand_Playbook.md** - Complete brand strategy document
2. **90_Day_Launch_Plan.csv** - Week-by-week launch tasks
3. **KPI_Projections.csv** - Revenue and growth projections
4. **Google_Sheets_Formulas.txt** - Ready-to-use formulas for tracking

## Next Steps:

1. Review the Brand Playbook with your team
2. Import the 90-Day Launch Plan into your project management tool
3. Set up KPI tracking in Google Sheets using the provided formulas
4. Schedule weekly check-ins to track progress

Generated by BrandForge AI - Powered by Google Gemini
"""
        zip_file.writestr("README.txt", readme)
    
    # Seek to beginning for reading
    zip_buffer.seek(0)
    return zip_buffer


def generate_playbook_markdown(state: Dict) -> str:
    """
    Generate a complete brand playbook in Markdown format.
    
    Args:
        state: BrandState dictionary
        
    Returns:
        Markdown string
    """
    company_name = state.get("company_name", "Your Company")
    
    markdown = f"""# {company_name} Brand Playbook
*Generated by BrandForge AI (Powered by Google Gemini)*  
*Date: {datetime.now().strftime('%B %d, %Y')}*

---

## Executive Summary

### Vision
{state.get('vision', 'TBD')}

### Mission
{state.get('mission', 'TBD')}

### Values
"""
    
    values = state.get('values', [])
    if values:
        for value in values:
            markdown += f"- {value}\n"
    else:
        markdown += "- TBD\n"
    
    markdown += f"""

---

## Target Audience

{state.get('target_audience', 'TBD')}

### Core Problem We Solve
{state.get('core_problem', 'TBD')}

---

## Market Positioning

### Positioning Statement
{state.get('positioning_statement', 'TBD')}

### Competitive Differentiation
{state.get('differentiation_points', 'TBD')}

### Gap Analysis
{state.get('gap_analysis', 'TBD')}

---

## Brand Identity

### Brand Voice
{state.get('brand_voice', 'TBD')}

### Color Palette
{state.get('color_palette_desc', 'TBD')}

### Typography
{state.get('font_recommendations', 'TBD')}

---

## Brand Messaging

### Messaging Guide
{state.get('messaging_guide', 'TBD')}

### One-Pager Copy
{state.get('one_pager_copy', 'TBD')}

---

## Launch Strategy

### Launch Date
{state.get('launch_start_date', 'TBD')}

### Brand Type
{state.get('brand_type', 'TBD')}

### 90-Day Plan
See attached CSV file for detailed week-by-week tasks.

---

## KPI Targets

"""
    
    kpi_targets = state.get('kpi_targets', {})
    if kpi_targets:
        for metric, target in kpi_targets.items():
            markdown += f"- **{metric}:** {target}\n"
    else:
        markdown += "- TBD\n"
    
    markdown += f"""

---

## Assets Checklist

- [ ] Logo & Brand Mark
- [ ] Color Palette
- [ ] Typography System
- [ ] Brand Guidelines Document
- [ ] Website Wireframes
- [ ] Social Media Templates
- [ ] Email Templates
- [ ] Pitch Deck
- [ ] One-Pager
- [ ] Business Cards

---

*This playbook is a living document. Review and update quarterly as your brand evolves.*

---

**Next Steps:**
1. Share this playbook with key stakeholders
2. Begin executing the 90-day launch plan
3. Set up KPI tracking dashboard
4. Schedule monthly brand reviews
"""
    
    return markdown


def calculate_workflow_statistics(state: Dict) -> Dict[str, any]:
    """
    Calculate statistics about the workflow progress.
    
    Args:
        state: BrandState dictionary
        
    Returns:
        Dictionary of statistics
    """
    total_fields = 20  # Approximate number of key fields
    filled_fields = sum(1 for v in state.values() if v and v != "" and v != [])
    
    return {
        "completion_percentage": (filled_fields / total_fields) * 100,
        "filled_fields": filled_fields,
        "total_fields": total_fields,
        "current_step": state.get("current_step", 0),
        "last_updated": state.get("last_updated", "Never")
    }


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        suffix: String to append when truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
