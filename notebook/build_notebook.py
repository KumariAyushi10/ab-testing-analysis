import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))

def code(text):
    cells.append(nbf.v4.new_code_cell(text))


md("""# NovaCart One-Click Checkout — A/B Test Analysis

**Scenario (original, invented for this project):** NovaCart, a fictional
online store, tested a new **One-Click Express Checkout** button against its
existing multi-step checkout flow.

- **Group A = Control** (old multi-step checkout)
- **Group B = Treatment** (new one-click checkout)

This notebook walks through the entire analysis end-to-end:

1. Generate a synthetic dataset (20,000 sessions)
2. Load it into a SQL database and run analysis queries
3. Run statistical significance tests (two-proportion z-test, t-test)
4. Visualize the results
5. State the final recommendation

Every dataset value here is randomly generated in this notebook — no
external or copied data is used, so this notebook and its outputs are
original work.
""")


md("## 1. Setup — import libraries")

code("""import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from scipy import stats
from datetime import datetime, timedelta

np.random.seed(42)
pd.set_option("display.max_columns", None)
""")


md("""## 2. Generate the synthetic dataset

We simulate 20,000 independent checkout sessions split ~50/50 between
Control (A) and Treatment (B). A deliberate treatment effect is built in
(+2.1 percentage points base conversion lift, extra lift on mobile, slightly
higher average order value, and faster checkout time) so the test has a
real, discoverable signal — just like a real experiment would.""")

code("""N_USERS = 20000
START_DATE = datetime(2026, 6, 1)
TEST_DAYS = 21

devices = ["mobile", "desktop", "tablet"]
device_probs = [0.58, 0.35, 0.07]

countries = ["IN", "US", "UK", "DE", "AE", "SG"]
country_probs = [0.40, 0.25, 0.10, 0.10, 0.08, 0.07]

traffic_sources = ["organic", "paid_search", "social", "email", "direct"]
traffic_probs = [0.35, 0.25, 0.15, 0.10, 0.15]

rows = []
user_id_start = 100000

for i in range(N_USERS):
    user_id = user_id_start + i
    group = np.random.choice(["A", "B"], p=[0.5, 0.5])

    session_day = np.random.randint(0, TEST_DAYS)
    session_date = START_DATE + timedelta(days=int(session_day))
    session_hour = np.random.randint(0, 24)
    timestamp = session_date + timedelta(hours=int(session_hour),
                                          minutes=int(np.random.randint(0, 60)))

    device = np.random.choice(devices, p=device_probs)
    country = np.random.choice(countries, p=country_probs)
    traffic_source = np.random.choice(traffic_sources, p=traffic_probs)
    new_visitor = np.random.choice([1, 0], p=[0.62, 0.38])

    base_conv = 0.112
    device_adj = {"mobile": -0.010, "desktop": 0.020, "tablet": -0.005}[device]
    visitor_adj = -0.018 if new_visitor else 0.014
    traffic_adj = {
        "organic": 0.005, "paid_search": -0.006, "social": -0.012,
        "email": 0.022, "direct": 0.010
    }[traffic_source]

    conv_prob = base_conv + device_adj + visitor_adj + traffic_adj

    if group == "B":
        conv_prob += 0.021
        if device == "mobile":
            conv_prob += 0.010

    conv_prob = float(np.clip(conv_prob, 0.01, 0.95))
    converted = np.random.binomial(1, conv_prob)

    if converted:
        base_aov = np.random.normal(loc=54.0, scale=18.0)
        if group == "B":
            base_aov += 1.8
        order_value = round(max(base_aov, 8.0), 2)
        items_in_cart = np.random.randint(1, 6)
    else:
        order_value = 0.0
        items_in_cart = np.random.randint(0, 4)

    added_to_cart = 1 if (items_in_cart > 0 or converted) else 0
    abandoned_cart = 1 if (added_to_cart and not converted) else 0

    checkout_time = np.random.normal(loc=95, scale=25) if group == "A" else np.random.normal(loc=58, scale=18)
    checkout_time = round(max(checkout_time, 8), 1)

    rows.append({
        "user_id": user_id,
        "session_timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "test_group": group,
        "device_type": device,
        "country": country,
        "traffic_source": traffic_source,
        "new_visitor": new_visitor,
        "added_to_cart": added_to_cart,
        "checkout_time_seconds": checkout_time,
        "converted": converted,
        "order_value_usd": order_value,
        "items_in_cart": items_in_cart,
        "abandoned_cart": abandoned_cart,
    })

df = pd.DataFrame(rows)
df.sort_values("session_timestamp", inplace=True)
df.reset_index(drop=True, inplace=True)

print(f"Generated {len(df):,} sessions")
df.head()
""")

code("""# Save to CSV so it matches the rest of the project (data/, sql/, excel/ folders)
import os
os.makedirs("../data", exist_ok=True)
df.to_csv("../data/ab_test_sessions.csv", index=False)
print("Saved to ../data/ab_test_sessions.csv")
""")


md("""## 3. Load into SQL (SQLite) and run analysis queries

We load the dataframe into an in-memory-style SQLite database and run the
same queries found in `sql/01_analysis_queries.sql`.""")

code("""conn = sqlite3.connect("../data/novacart_ab_test.db")
df.to_sql("ab_test_sessions", conn, if_exists="replace", index=False)
print("Loaded into SQLite table ab_test_sessions")
""")

code("""# Query 1: Conversion rate by group
q1 = '''
SELECT
    test_group,
    COUNT(*) AS total_sessions,
    SUM(converted) AS total_conversions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2) AS conversion_rate_pct
FROM ab_test_sessions
GROUP BY test_group
ORDER BY test_group;
'''
pd.read_sql(q1, conn)
""")

code("""# Query 2: Average order value (AOV) -- converted sessions only
q2 = '''
SELECT
    test_group,
    COUNT(*) AS orders,
    ROUND(AVG(order_value_usd), 2) AS avg_order_value_usd,
    ROUND(SUM(order_value_usd), 2) AS total_revenue_usd
FROM ab_test_sessions
WHERE converted = 1
GROUP BY test_group
ORDER BY test_group;
'''
pd.read_sql(q2, conn)
""")

code("""# Query 3: Cart abandonment rate by group
q3 = '''
SELECT
    test_group,
    SUM(added_to_cart) AS carts_started,
    SUM(abandoned_cart) AS carts_abandoned,
    ROUND(100.0 * SUM(abandoned_cart) / NULLIF(SUM(added_to_cart), 0), 2) AS abandonment_rate_pct
FROM ab_test_sessions
GROUP BY test_group
ORDER BY test_group;
'''
pd.read_sql(q3, conn)
""")

code("""# Query 4: Conversion rate by device type and group
q4 = '''
SELECT
    device_type,
    test_group,
    COUNT(*) AS sessions,
    SUM(converted) AS conversions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2) AS conversion_rate_pct
FROM ab_test_sessions
GROUP BY device_type, test_group
ORDER BY device_type, test_group;
'''
pd.read_sql(q4, conn)
""")

code("""# Query 5: Conversion rate by traffic source and group
q5 = '''
SELECT
    traffic_source,
    test_group,
    COUNT(*) AS sessions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2) AS conversion_rate_pct
FROM ab_test_sessions
GROUP BY traffic_source, test_group
ORDER BY traffic_source, test_group;
'''
pd.read_sql(q5, conn)
""")

code("""conn.close()""")


md("""## 4. Statistical significance testing

We run a **two-proportion z-test** on conversion rate and a **Welch's
t-test** on order value to confirm the difference between groups is real
and not just random noise.""")

code("""a = df[df.test_group == "A"]
b = df[df.test_group == "B"]

n_a, n_b = len(a), len(b)
x_a, x_b = a.converted.sum(), b.converted.sum()
p_a, p_b = x_a / n_a, x_b / n_b

p_pool = (x_a + x_b) / (n_a + n_b)
se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
z_stat = (p_b - p_a) / se_pool
p_value_conv = 2 * (1 - stats.norm.cdf(abs(z_stat)))

se_diff = np.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
diff = p_b - p_a
ci_low = diff - 1.96 * se_diff
ci_high = diff + 1.96 * se_diff
relative_lift = (p_b - p_a) / p_a * 100

print(f"Group A (Control):   n={n_a:,}, conversions={x_a:,}, rate={p_a*100:.2f}%")
print(f"Group B (Treatment): n={n_b:,}, conversions={x_b:,}, rate={p_b*100:.2f}%")
print()
print(f"Absolute lift: {diff*100:.2f} pp   |   Relative lift: {relative_lift:.2f}%")
print(f"95% CI for difference: [{ci_low*100:.2f}%, {ci_high*100:.2f}%]")
print(f"Z-statistic: {z_stat:.3f}   |   P-value: {p_value_conv:.5f}")
print("SIGNIFICANT (p < 0.05)" if p_value_conv < 0.05 else "NOT significant (p >= 0.05)")
""")

code("""# Welch's t-test on average order value (converted sessions only)
aov_a = a[a.converted == 1].order_value_usd
aov_b = b[b.converted == 1].order_value_usd

t_stat, p_value_aov = stats.ttest_ind(aov_b, aov_a, equal_var=False)

print(f"Group A AOV: ${aov_a.mean():.2f} (n={len(aov_a)})")
print(f"Group B AOV: ${aov_b.mean():.2f} (n={len(aov_b)})")
print(f"T-statistic: {t_stat:.3f}   |   P-value: {p_value_aov:.5f}")
print("SIGNIFICANT (p < 0.05)" if p_value_aov < 0.05 else "NOT significant (p >= 0.05)")
""")


md("## 5. Charts")

code("""fig, ax = plt.subplots(figsize=(6, 5))
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
plt.show()
""")

code("""fig, ax = plt.subplots(figsize=(6, 5))
aov_vals = [aov_a.mean(), aov_b.mean()]
bars = ax.bar(groups, aov_vals, color=colors, width=0.5)
for bar, val in zip(bars, aov_vals):
    ax.text(bar.get_x() + bar.get_width() / 2, val + 0.5, f"${val:.2f}",
            ha="center", fontsize=12, fontweight="bold")
ax.set_ylabel("Average Order Value (USD)")
ax.set_title("Average Order Value: Control vs. One-Click Checkout")
ax.set_ylim(0, max(aov_vals) * 1.3)
plt.tight_layout()
plt.show()
""")

code("""df["session_date"] = pd.to_datetime(df.session_timestamp).dt.date
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
plt.show()
""")

code("""device_stats = df.groupby(["device_type", "test_group"]).converted.agg(["count", "sum"]).reset_index()
device_stats["rate"] = device_stats["sum"] / device_stats["count"] * 100
device_pivot = device_stats.pivot(index="device_type", columns="test_group", values="rate")

x = np.arange(len(device_pivot.index))
width = 0.35
fig, ax = plt.subplots(figsize=(7, 5))
ax.bar(x - width/2, device_pivot["A"], width, label="Control (A)", color="#8c9eb2")
ax.bar(x + width/2, device_pivot["B"], width, label="Treatment (B)", color="#2e6f95")
ax.set_xticks(x)
ax.set_xticklabels(device_pivot.index)
ax.set_ylabel("Conversion Rate (%)")
ax.set_title("Conversion Rate by Device Type")
ax.legend()
plt.tight_layout()
plt.show()
""")


md("""## 6. Business impact and recommendation""")

code("""rev_a = a.order_value_usd.sum()
rev_b = b.order_value_usd.sum()
rps_a = rev_a / n_a
rps_b = rev_b / n_b

print(f"Revenue per session -- Control:   ${rps_a:.3f}")
print(f"Revenue per session -- Treatment: ${rps_b:.3f}")
print(f"Estimated revenue lift per 100,000 sessions: ${(rps_b - rps_a) * 100000:,.0f}")
print()
if p_value_conv < 0.05 and diff > 0:
    print("RECOMMENDATION: Ship the One-Click Express Checkout to 100% of traffic.")
    print("The conversion lift is statistically significant and positive, with no")
    print("evidence of a negative effect on order value.")
else:
    print("RECOMMENDATION: Do not ship yet -- results are inconclusive.")
""")

md("""---
**Note:** This notebook reproduces the same results as `python/01_generate_dataset.py`,
`sql/01_analysis_queries.sql`, and `python/02_statistical_analysis.py` in this
repository. Use whichever format (notebook or standalone scripts) is more
convenient for you — they contain the same logic.
""")

nb['cells'] = cells

import os
os.makedirs("/home/claude/ab_test_project/notebook", exist_ok=True)
with open("/home/claude/ab_test_project/notebook/NovaCart_AB_Test_Analysis.ipynb", "w") as f:
    nbf.write(nb, f)

print("Notebook saved.")
