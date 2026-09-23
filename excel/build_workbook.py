"""
build_workbook.py
------------------------------------------------------------
Builds NovaCart_AB_Test_Analysis.xlsx with:
  - "Raw Data" sheet: all 20,000 session rows
  - "Summary" sheet: SUMIFS/COUNTIFS formulas computing conversion
    rate, AOV, and abandonment rate per group (recalculates live
    if Raw Data changes)
  - "Dashboard" sheet: a clustered bar chart built from the Summary
    sheet's formula outputs

All numbers on Summary/Dashboard are FORMULAS referencing Raw Data,
not hardcoded values, so the workbook recalculates if you paste in
new data.
------------------------------------------------------------
"""

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.utils import get_column_letter

import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "..", "data", "ab_test_sessions.csv")
OUT_PATH = os.path.join(SCRIPT_DIR, "..", "outputs", "NovaCart_AB_Test_Analysis.xlsx")
os.makedirs(os.path.join(SCRIPT_DIR, "..", "outputs"), exist_ok=True)

df = pd.read_csv(DATA_PATH)
n_rows = len(df)

wb = Workbook()

# ============================================================
# Sheet 1: Raw Data
# ============================================================
ws_raw = wb.active
ws_raw.title = "Raw Data"

headers = list(df.columns)
header_fill = PatternFill(start_color="2E6F95", end_color="2E6F95", fill_type="solid")
header_font = Font(bold=True, color="FFFFFF", name="Arial")
body_font = Font(name="Arial", size=10)

for col_idx, h in enumerate(headers, start=1):
    cell = ws_raw.cell(row=1, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center")

for row_idx, row in enumerate(df.itertuples(index=False), start=2):
    for col_idx, value in enumerate(row, start=1):
        c = ws_raw.cell(row=row_idx, column=col_idx, value=value)
        c.font = body_font

# Freeze header row, set column widths
ws_raw.freeze_panes = "A2"
widths = [10, 20, 11, 12, 9, 14, 11, 13, 20, 10, 15, 13, 15]
for i, w in enumerate(widths, start=1):
    ws_raw.column_dimensions[get_column_letter(i)].width = w

last_row = n_rows + 1  # last data row number in Raw Data

# Column letters for reference (based on df column order)
col_letter = {name: get_column_letter(i + 1) for i, name in enumerate(headers)}

# ============================================================
# Sheet 2: Summary (formulas only)
# ============================================================
ws_sum = wb.create_sheet("Summary")
ws_sum.sheet_view.showGridLines = False

title_font = Font(bold=True, size=14, name="Arial", color="2E6F95")
label_font = Font(bold=True, name="Arial")
note_font = Font(italic=True, size=9, name="Arial", color="777777")

ws_sum["A1"] = "NovaCart One-Click Checkout A/B Test — Summary"
ws_sum["A1"].font = title_font
ws_sum.merge_cells("A1:E1")

ws_sum["A2"] = "All figures below are computed live via formulas referencing the 'Raw Data' sheet."
ws_sum["A2"].font = note_font
ws_sum.merge_cells("A2:E2")

table_header_row = 4
headers_summary = ["Metric", "Control (A)", "Treatment (B)", "Difference (B - A)", "Notes"]
for i, h in enumerate(headers_summary, start=1):
    cell = ws_sum.cell(row=table_header_row, column=i, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center", wrap_text=True)

rd = "'Raw Data'"
grp_col = col_letter["test_group"]
conv_col = col_letter["converted"]
order_col = col_letter["order_value_usd"]
cart_col = col_letter["added_to_cart"]
aband_col = col_letter["abandoned_cart"]
checkout_col = col_letter["checkout_time_seconds"]

rows_data = [
    (
        "Total Sessions",
        f'=COUNTIF({rd}!{grp_col}2:{grp_col}{last_row},"A")',
        f'=COUNTIF({rd}!{grp_col}2:{grp_col}{last_row},"B")',
        None,
        "Number of test sessions in each group",
    ),
    (
        "Total Conversions",
        f'=SUMIFS({rd}!{conv_col}2:{conv_col}{last_row},{rd}!{grp_col}2:{grp_col}{last_row},"A")',
        f'=SUMIFS({rd}!{conv_col}2:{conv_col}{last_row},{rd}!{grp_col}2:{grp_col}{last_row},"B")',
        None,
        "Sessions that completed checkout",
    ),
    (
        "Conversion Rate",
        "=B6/B5",
        "=C6/C5",
        "=C7-B7",
        "Conversions / Total sessions",
    ),
    (
        "Total Revenue (USD)",
        f'=SUMIFS({rd}!{order_col}2:{order_col}{last_row},{rd}!{grp_col}2:{grp_col}{last_row},"A")',
        f'=SUMIFS({rd}!{order_col}2:{order_col}{last_row},{rd}!{grp_col}2:{grp_col}{last_row},"B")',
        "=C8-B8",
        "Sum of order value",
    ),
    (
        "Average Order Value (AOV)",
        "=IFERROR(B8/B6,0)",
        "=IFERROR(C8/C6,0)",
        "=C9-B9",
        "Total revenue / Total conversions",
    ),
    (
        "Revenue per Session",
        "=B8/B5",
        "=C8/C5",
        "=C10-B10",
        "Total revenue / Total sessions (blended KPI)",
    ),
    (
        "Carts Started",
        f'=SUMIFS({rd}!{cart_col}2:{cart_col}{last_row},{rd}!{grp_col}2:{grp_col}{last_row},"A")',
        f'=SUMIFS({rd}!{cart_col}2:{cart_col}{last_row},{rd}!{grp_col}2:{grp_col}{last_row},"B")',
        None,
        "Sessions where a cart was created",
    ),
    (
        "Carts Abandoned",
        f'=SUMIFS({rd}!{aband_col}2:{aband_col}{last_row},{rd}!{grp_col}2:{grp_col}{last_row},"A")',
        f'=SUMIFS({rd}!{aband_col}2:{aband_col}{last_row},{rd}!{grp_col}2:{grp_col}{last_row},"B")',
        None,
        "Carts started but not converted",
    ),
    (
        "Cart Abandonment Rate",
        "=IFERROR(B12/B11,0)",
        "=IFERROR(C12/C11,0)",
        "=C13-B13",
        "Carts abandoned / Carts started",
    ),
    (
        "Avg Checkout Time (sec)",
        f'=AVERAGEIFS({rd}!{checkout_col}2:{checkout_col}{last_row},{rd}!{grp_col}2:{grp_col}{last_row},"A")',
        f'=AVERAGEIFS({rd}!{checkout_col}2:{checkout_col}{last_row},{rd}!{grp_col}2:{grp_col}{last_row},"B")',
        "=C14-B14",
        "Average time spent on checkout page",
    ),
]

r = table_header_row + 1
pct_rows = []
currency_rows = []
for label, val_a, val_b, val_diff, note in rows_data:
    ws_sum.cell(row=r, column=1, value=label).font = label_font
    ws_sum.cell(row=r, column=2, value=val_a)
    ws_sum.cell(row=r, column=3, value=val_b)
    if val_diff:
        ws_sum.cell(row=r, column=4, value=val_diff)
    ws_sum.cell(row=r, column=5, value=note).font = note_font

    if "Rate" in label:
        pct_rows.append(r)
    if "Revenue" in label or "Value" in label or "Session" in label and "Total" not in label:
        currency_rows.append(r)
    r += 1

# Number formatting
for row_num in range(table_header_row + 1, r):
    label_cell = ws_sum.cell(row=row_num, column=1).value
    for col in [2, 3, 4]:
        c = ws_sum.cell(row=row_num, column=col)
        if c.value is None:
            continue
        if "Rate" in str(label_cell):
            c.number_format = "0.00%"
        elif any(k in str(label_cell) for k in ["Revenue", "Value", "Session"]) and "Total Sessions" not in str(label_cell) and "Carts" not in str(label_cell):
            c.number_format = "$#,##0.00"
        elif "Time" in str(label_cell):
            c.number_format = "0.0"
        else:
            c.number_format = "#,##0"

# Column widths for Summary
sum_widths = [26, 16, 16, 18, 40]
for i, w in enumerate(sum_widths, start=1):
    ws_sum.column_dimensions[get_column_letter(i)].width = w

# Statistical significance note (values pasted from Python scipy analysis,
# documented as such since Excel has no built-in two-proportion z-test)
note_row = r + 2
ws_sum.cell(row=note_row, column=1, value="Statistical Significance (from Python analysis)").font = label_font
ws_sum.cell(row=note_row + 1, column=1, value="Conversion rate p-value:")
ws_sum.cell(row=note_row + 1, column=2, value=0.00000)
ws_sum.cell(row=note_row + 1, column=2).number_format = "0.00000"
ws_sum.cell(row=note_row + 1, column=3, value="Source: python/02_statistical_analysis.py (two-proportion z-test). Significant at p < 0.05.").font = note_font
ws_sum.cell(row=note_row + 2, column=1, value="AOV p-value:")
ws_sum.cell(row=note_row + 2, column=2, value=0.01420)
ws_sum.cell(row=note_row + 2, column=2).number_format = "0.00000"
ws_sum.cell(row=note_row + 2, column=3, value="Source: python/02_statistical_analysis.py (Welch's t-test). Significant at p < 0.05.").font = note_font

# ============================================================
# Sheet 3: Dashboard (chart pulling from Summary formulas)
# ============================================================
ws_dash = wb.create_sheet("Dashboard")
ws_dash.sheet_view.showGridLines = False
ws_dash["A1"] = "NovaCart A/B Test — Dashboard"
ws_dash["A1"].font = title_font
ws_dash.merge_cells("A1:F1")

# Small helper table the chart will read (mirrors Summary via formulas)
ws_dash["A3"] = "Metric"
ws_dash["B3"] = "Control (A)"
ws_dash["C3"] = "Treatment (B)"
for c in ["A3", "B3", "C3"]:
    ws_dash[c].font = header_font
    ws_dash[c].fill = header_fill

ws_dash["A4"] = "Conversion Rate"
ws_dash["B4"] = "=Summary!B7"
ws_dash["C4"] = "=Summary!C7"
ws_dash["B4"].number_format = "0.00%"
ws_dash["C4"].number_format = "0.00%"

ws_dash["A5"] = "Cart Abandonment Rate"
ws_dash["B5"] = "=Summary!B13"
ws_dash["C5"] = "=Summary!C13"
ws_dash["B5"].number_format = "0.00%"
ws_dash["C5"].number_format = "0.00%"

for i, w in enumerate([24, 14, 14], start=1):
    ws_dash.column_dimensions[get_column_letter(i)].width = w

chart = BarChart()
chart.type = "col"
chart.title = "Conversion & Abandonment Rate: Control vs Treatment"
chart.y_axis.title = "Rate"
chart.x_axis.title = "Metric"
chart.y_axis.numFmt = "0%"

data_ref = Reference(ws_dash, min_col=2, max_col=3, min_row=3, max_row=5)
cats_ref = Reference(ws_dash, min_col=1, min_row=4, max_row=5)
chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(cats_ref)
chart.width = 16
chart.height = 10

ws_dash.add_chart(chart, "A8")

wb.save(OUT_PATH)
print(f"Saved workbook to {OUT_PATH}")
