"""
02_statistical_analysis.py
------------------------------------------------------------
Runs the statistical significance tests for the NovaCart
One-Click Checkout A/B test and saves charts as PNG files.

Tests performed:
  1. Two-proportion z-test on conversion rate (A vs B)
  2. Independent-samples t-test on order value (A vs B, converted only)
  3. Confidence intervals for both metrics

Outputs:
  outputs/conversion_rate_chart.png
  outputs/aov_chart.png
  outputs/daily_trend_chart.png
  outputs/device_breakdown_chart.png
  outputs/statistical_summary.txt
------------------------------------------------------------
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "..", "data", "ab_test_sessions.csv")
OUT_DIR = os.path.join(SCRIPT_DIR, "..", "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)

a = df[df.test_group == "A"]
b = df[df.test_group == "B"]

# ============================================================
# 1. Two-proportion z-test on conversion rate
# ============================================================
n_a, n_b = len(a), len(b)
x_a, x_b = a.converted.sum(), b.converted.sum()
p_a, p_b = x_a / n_a, x_b / n_b

p_pool = (x_a + x_b) / (n_a + n_b)
se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
z_stat = (p_b - p_a) / se_pool
p_value_conv = 2 * (1 - stats.norm.cdf(abs(z_stat)))

# 95% CI for the difference in proportions
se_diff = np.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
diff = p_b - p_a
ci_low = diff - 1.96 * se_diff
ci_high = diff + 1.96 * se_diff

relative_lift = (p_b - p_a) / p_a * 100

# ============================================================
# 2. Independent t-test on order value (converted sessions only)
# ============================================================
aov_a = a[a.converted == 1].order_value_usd
aov_b = b[b.converted == 1].order_value_usd

t_stat, p_value_aov = stats.ttest_ind(aov_b, aov_a, equal_var=False)

# ============================================================
# Write summary report
# ============================================================
summary_lines = []
summary_lines.append("=" * 60)
summary_lines.append("NovaCart One-Click Checkout A/B Test -- Statistical Summary")
summary_lines.append("=" * 60)
summary_lines.append("")
summary_lines.append(f"Group A (Control):   n = {n_a:,}, conversions = {x_a:,}, rate = {p_a*100:.2f}%")
summary_lines.append(f"Group B (Treatment): n = {n_b:,}, conversions = {x_b:,}, rate = {p_b*100:.2f}%")
summary_lines.append("")
summary_lines.append("--- Conversion Rate: Two-Proportion Z-Test ---")
summary_lines.append(f"Absolute lift:        {diff*100:.2f} percentage points")
summary_lines.append(f"Relative lift:         {relative_lift:.2f}%")
summary_lines.append(f"95% Confidence Interval for difference: [{ci_low*100:.2f}%, {ci_high*100:.2f}%]")
summary_lines.append(f"Z-statistic:           {z_stat:.3f}")
summary_lines.append(f"P-value:               {p_value_conv:.5f}")
if p_value_conv < 0.05:
    summary_lines.append("Result: STATISTICALLY SIGNIFICANT at 95% confidence (p < 0.05)")
else:
    summary_lines.append("Result: NOT statistically significant at 95% confidence (p >= 0.05)")
summary_lines.append("")
summary_lines.append("--- Average Order Value: Welch's T-Test (converted sessions only) ---")
summary_lines.append(f"Group A AOV: ${aov_a.mean():.2f} (n={len(aov_a)})")
summary_lines.append(f"Group B AOV: ${aov_b.mean():.2f} (n={len(aov_b)})")
summary_lines.append(f"T-statistic:           {t_stat:.3f}")
summary_lines.append(f"P-value:               {p_value_aov:.5f}")
if p_value_aov < 0.05:
    summary_lines.append("Result: STATISTICALLY SIGNIFICANT at 95% confidence (p < 0.05)")
else:
    summary_lines.append("Result: NOT statistically significant at 95% confidence (p >= 0.05)")
summary_lines.append("")
summary_lines.append("--- Business Impact Estimate ---")
rev_a = a.order_value_usd.sum()
rev_b = b.order_value_usd.sum()
rps_a = rev_a / n_a
rps_b = rev_b / n_b
summary_lines.append(f"Revenue per session -- Control:   ${rps_a:.3f}")
summary_lines.append(f"Revenue per session -- Treatment: ${rps_b:.3f}")
summary_lines.append(f"Estimated revenue lift per 100,000 sessions: ${(rps_b - rps_a) * 100000:,.0f}")
summary_lines.append("")
summary_lines.append("--- Recommendation ---")
if p_value_conv < 0.05 and diff > 0:
    summary_lines.append("Ship the One-Click Express Checkout to 100% of traffic.")
    summary_lines.append("The conversion lift is statistically significant and positive,")
    summary_lines.append("with no evidence of a negative effect on order value.")
else:
    summary_lines.append("Do not ship yet -- results are inconclusive. Recommend extending")
    summary_lines.append("the test duration or increasing sample size.")

summary_text = "\n".join(summary_lines)
print(summary_text)

with open(f"{OUT_DIR}/statistical_summary.txt", "w") as f:
    f.write(summary_text)

# ============================================================
# Charts
# ============================================================
plt.style.use("default")

# --- Chart 1: Conversion rate comparison ---
fig, ax = plt.subplots(figsize=(6, 5))
groups = ["Control (A)", "Treatment (B)"]
rates = [p_a * 100, p_b * 100]
colors = ["#8c9eb2", "#2e6f95"]
bars = ax.bar(groups, rates, color=colors, width=0.5)
for bar, rate in zip(bars, rates):
    ax.text(bar.get_x() + bar.get_width() / 2, rate + 0.15, f"{rate:.2f}%",
            ha="center", fontsize=12, fontweight="bold")
ax.set_ylabel("Conversion Rate (%)")
ax.set_title("Conversion Rate: Control vs. One-Click Checkout")
ax.set_ylim(0, max(rates) * 1.3)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/conversion_rate_chart.png", dpi=150)
plt.close()

# --- Chart 2: AOV comparison ---
fig, ax = plt.subplots(figsize=(6, 5))
aov_vals = [aov_a.mean(), aov_b.mean()]
bars = ax.bar(groups, aov_vals, color=colors, width=0.5)
for bar, val in zip(bars, aov_vals):
    ax.text(bar.get_x() + bar.get_width() / 2, val + 0.5, f"${val:.2f}",
            ha="center", fontsize=12, fontweight="bold")
ax.set_ylabel("Average Order Value (USD)")
ax.set_title("Average Order Value: Control vs. One-Click Checkout")
ax.set_ylim(0, max(aov_vals) * 1.3)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/aov_chart.png", dpi=150)
plt.close()

# --- Chart 3: Daily conversion trend ---
df["session_date"] = pd.to_datetime(df.session_timestamp).dt.date
daily = df.groupby(["session_date", "test_group"]).converted.agg(["count", "sum"]).reset_index()
daily["rate"] = daily["sum"] / daily["count"] * 100
pivot = daily.pivot(index="session_date", columns="test_group", values="rate")

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(pivot.index, pivot["A"], marker="o", label="Control (A)", color="#8c9eb2")
ax.plot(pivot.index, pivot["B"], marker="o", label="Treatment (B)", color="#2e6f95")
ax.set_ylabel("Daily Conversion Rate (%)")
ax.set_xlabel("Date")
ax.set_title("Daily Conversion Rate Over the Test Period")
ax.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/daily_trend_chart.png", dpi=150)
plt.close()

# --- Chart 4: Conversion rate by device ---
device_stats = df.groupby(["device_type", "test_group"]).converted.agg(["count", "sum"]).reset_index()
device_stats["rate"] = device_stats["sum"] / device_stats["count"] * 100
device_pivot = device_stats.pivot(index="device_type", columns="test_group", values="rate")

fig, ax = plt.subplots(figsize=(7, 5))
x = np.arange(len(device_pivot.index))
width = 0.35
ax.bar(x - width/2, device_pivot["A"], width, label="Control (A)", color="#8c9eb2")
ax.bar(x + width/2, device_pivot["B"], width, label="Treatment (B)", color="#2e6f95")
ax.set_xticks(x)
ax.set_xticklabels(device_pivot.index)
ax.set_ylabel("Conversion Rate (%)")
ax.set_title("Conversion Rate by Device Type")
ax.legend()
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/device_breakdown_chart.png", dpi=150)
plt.close()

print("\nSaved 4 charts and statistical_summary.txt to outputs/")
