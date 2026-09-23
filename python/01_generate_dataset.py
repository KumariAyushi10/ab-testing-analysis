"""
01_generate_dataset.py
------------------------------------------------------------
Generates a fully SYNTHETIC dataset for an A/B test project.

Scenario (original, invented for this project):
An online store called "NovaCart" tested a new "One-Click Express
Checkout" button against its existing multi-step checkout flow.
Goal: measure impact on conversion rate, average order value (AOV),
and cart abandonment.

- Group A = Control  (old multi-step checkout)
- Group B = Treatment (new one-click checkout)

This script creates data/ab_test_sessions.csv, which is the single
raw dataset used by the SQL and Excel parts of this project.
No external data source is used -- everything here is randomly
generated with numpy/pandas so the whole project is original work.
------------------------------------------------------------
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Reproducible randomness
np.random.seed(42)

N_USERS = 20000              # total sessions in the experiment
START_DATE = datetime(2026, 6, 1)
TEST_DAYS = 21                # 3-week test window

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

    # ---- Baseline conversion probability (Control, Group A) ----
    base_conv = 0.112  # 11.2% baseline conversion rate

    device_adj = {"mobile": -0.010, "desktop": 0.020, "tablet": -0.005}[device]
    visitor_adj = -0.018 if new_visitor else 0.014
    traffic_adj = {
        "organic": 0.005, "paid_search": -0.006, "social": -0.012,
        "email": 0.022, "direct": 0.010
    }[traffic_source]

    conv_prob = base_conv + device_adj + visitor_adj + traffic_adj

    # ---- Treatment (Group B) effect: one-click checkout lifts conversion ----
    if group == "B":
        conv_prob += 0.021          # +2.1 percentage points absolute lift
        if device == "mobile":
            conv_prob += 0.010      # extra lift on mobile

    conv_prob = float(np.clip(conv_prob, 0.01, 0.95))
    converted = np.random.binomial(1, conv_prob)

    # ---- Order value only exists if converted ----
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

import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(SCRIPT_DIR, "..", "data", "ab_test_sessions.csv")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
df.to_csv(out_path, index=False)

print(f"Saved {len(df):,} rows to {out_path}")
print(df.groupby("test_group")["converted"].mean())
