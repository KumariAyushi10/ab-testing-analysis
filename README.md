# ab-testing-analysis
This project analyzes **20,000 user sessions** to measure the impact of the new checkout flow on:  Conversion rate, Average order value (AOV), Cart abandonment rate, Checkout time, Revenue per session
# NovaCart One-Click Checkout — A/B Test Analysis

**Author:** Kumari Ayushi

## Project Overview

NovaCart (a fictional e-commerce brand invented for this project) ran a 3-week
A/B test on its checkout flow.

This project analyzes **20,000 synthetic user sessions** to measure the
impact of the new checkout flow on:

- Conversion rate
- Average order value (AOV)
- Cart abandonment rate
- Checkout time
- Revenue per session

The dataset is **entirely synthetic**, generated with a documented random
process in `python/01_generate_dataset.py` (and reproduced in the Jupyter
notebook) — no real user data and no data from any other source is used.
All code, queries, and the Excel workbook in this repo are original work.

## Repository Structure

```
├── data/
│   ├── ab_test_sessions.csv
│   └── novacart_ab_test.db
├── notebook/
│   └── NovaCart_AB_Test_Analysis.ipynb
├── python/
│   ├── 01_generate_dataset.py
│   └── 02_statistical_analysis.py
├── sql/
│   ├── 00_create_db.py
│   ├── 01_analysis_queries.sql
│   └── 02_export_to_mysql.py
├── excel/
│   └── build_workbook.py
├── outputs/
│   ├── NovaCart_AB_Test_Analysis.xlsx
│   ├── conversion_rate_chart.png
│   ├── aov_chart.png
│   ├── daily_trend_chart.png
│   ├── device_breakdown_chart.png
│   └── statistical_summary.txt
├── LICENSE
└── README.md
```

## Tools Used

| Tool             | What it's used for                                                    |
| ---------------- | --------------------------------------------------------------------- |
| Python / Jupyter | Generating the dataset, running the z-test/t-test, making charts      |
| SQL (SQLite)     | Aggregating conversion, AOV, and abandonment metrics by group/segment |
| Excel            | A formula-driven workbook (SUMIFS/COUNTIFS/AVERAGEIFS) with a chart   |

## Methodology

1. **Dataset generation** (`python/01_generate_dataset.py`): simulates 20,000
   independent user sessions split ~50/50 into Control/Treatment, with
   randomized device, country, traffic source, and visitor type. A treatment
   effect (+2.1pp base conversion lift, extra lift on mobile, slightly higher
   AOV, faster checkout time) is deliberately built in so the "test" has a
   real, discoverable signal — exactly like a real experiment would.
2. **SQL analysis** (`sql/01_analysis_queries.sql`): aggregate metrics by
   group and by segment (device, traffic source, country, visitor type).
3. **Statistical testing** (`python/02_statistical_analysis.py`): a
   two-proportion z-test for conversion rate and a Welch's t-test for order
   value, plus a 95% confidence interval on the lift.
4. **Excel workbook** (`excel/build_workbook.py`): raw data + a Summary sheet
   built entirely from live formulas (`SUMIFS`, `COUNTIFS`, `AVERAGEIFS`) so
   it recalculates if the raw data changes, plus a Dashboard sheet with a
   chart.
5. **Jupyter notebook** (`notebook/NovaCart_AB_Test_Analysis.ipynb`): the
   entire pipeline above — dataset generation, SQL queries, statistical
   tests, and charts — combined into a single runnable notebook, with all
   outputs already shown, for anyone who wants to see (or re-run) the whole
   analysis in one place.

---

# How To Run This Project (Beginner-Friendly Guide)

## Part 1: Install the tools (one-time setup)

### 1. Install Python

1. Go to https://www.python.org/downloads/
2. Download the latest version (3.10 or newer) and run the installer.
3. **Windows only:** on the first install screen, check the box that says
   "Add Python to PATH" before clicking Install.
4. To check it worked: open a terminal (Windows: search "Command Prompt" or
   "PowerShell"; Mac: search "Terminal") and type:
   ```
   python3 --version
   ```
   You should see something like `Python 3.12.1`. (On Windows it might be
   `python --version` instead of `python3`.)

### 2. Install the Python packages this project needs

In the same terminal, run:

```
pip install pandas numpy scipy matplotlib openpyxl jupyter
```

(On Windows, if `pip` doesn't work, try `pip3` or `python -m pip install ...`)

### 3. (Optional but recommended) Install a code editor

[VS Code](https://code.visualstudio.com/) is free and makes it much easier to
open folders, run Python files, and open Jupyter notebooks. Not required — a
terminal is enough for the scripts.

### 4. Download this project

- If you got this as a ZIP file: unzip it anywhere (e.g. your Desktop).
- If it's already on GitHub: click the green **Code** button → **Download
  ZIP**, then unzip it. Or, if you have `git` installed:
  ```
  git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
  ```

## Part 2: Run the project, step by step

Open a terminal and navigate into the project folder. For example, if you
unzipped it to your Desktop:

```
cd Desktop/ab_test_project
```

(`cd` = "change directory". If your folder has a different name, use that
name instead.)

### Option A — Easiest: run the Jupyter notebook (does everything in one file)

1. In the terminal, from the project folder, run:
   ```
   jupyter notebook
   ```
   This opens Jupyter in your web browser.
2. In the browser, click into the `notebook/` folder, then open
   `NovaCart_AB_Test_Analysis.ipynb`.
3. In the menu bar, click **Kernel → Restart & Run All** (or **Run → Run All
   Cells**, depending on your Jupyter version).
4. Watch it run top to bottom: it generates the dataset, runs the SQL
   queries, runs the statistical tests, and draws all 4 charts — all inside
   the notebook, with no other files needed.

If you'd rather use VS Code: open the project folder in VS Code, click
`notebook/NovaCart_AB_Test_Analysis.ipynb`, and click "Run All" at the top.

### Option B — Step by step with individual scripts (matches the repo folders)

#### Step 1 — Generate the dataset

This creates `data/ab_test_sessions.csv` (20,000 rows of test data).

```
python3 python/01_generate_dataset.py
```

You should see: `Saved 20,000 rows to .../ab_test_sessions.csv`

#### Step 2 — Load the data into a SQL database

This creates `data/novacart_ab_test.db`, a SQLite database file.

```
python3 sql/00_create_db.py
```

You should see: `Loaded 20,000 rows into .../novacart_ab_test.db`

#### Step 3 — Run the SQL analysis queries

Pick whichever tool you already have or prefer. The queries in
`sql/01_analysis_queries.sql` are plain ANSI SQL and work unmodified in all
three options below.

**Option A — Easiest: DB Browser for SQLite (a free app with buttons, no
typing SQL commands into a terminal)**

1. Download it free from https://sqlitebrowser.org/dl/
2. Open the app → File → Open Database → select `data/novacart_ab_test.db`
3. Click the **Execute SQL** tab
4. Open `sql/01_analysis_queries.sql` in a text editor, copy one query block
   at a time (everything between two `/* ... */` comments), paste it into
   the Execute SQL tab, and click the "Play" (▶) button to run it.

**Option B — MySQL Workbench**
The raw database is SQLite, so to use MySQL Workbench you first import the
data into a real MySQL server using the ready-made script
`sql/mysql_import.sql`:

1. Install MySQL Server + Workbench: https://dev.mysql.com/downloads/installer/
2. Open MySQL Workbench and connect to your local MySQL server (the default
   "Local instance MySQL" connection created during install).
3. **File → Open SQL Script...** → select `sql/mysql_import.sql`
4. Click the **lightning bolt icon** (Execute) to run the whole script. This
   creates a `novacart_ab_test` schema and loads all 20,000 rows into an
   `ab_test_sessions` table (takes a few seconds).
5. In the left sidebar under **Schemas**, right-click `novacart_ab_test` →
   **Set as Default Schema**.
6. **Check it worked:** open a new query tab and run `SELECT COUNT(*) FROM
ab_test_sessions;` — it should return exactly `20000`.
7. Now open `sql/01_analysis_queries.sql` the same way (File → Open SQL
   Script), highlight one query block at a time, and click the lightning
   bolt to run just the highlighted query. The first query should return two
   rows (`A` and `B`) with conversion rates around `10.68` and `13.09`.

**Option C — Command line (if your system has the `sqlite3` command)**

```
sqlite3 data/novacart_ab_test.db
.read sql/01_analysis_queries.sql
```

Type `.quit` to exit.

#### Step 4 — Run the Python statistical analysis

This runs the significance tests and creates 4 chart images plus a summary
text file, all saved into the `outputs/` folder.

```
python3 python/02_statistical_analysis.py
```

You'll see the full statistical write-up printed in the terminal, and these
new files appear in `outputs/`:

- `conversion_rate_chart.png`
- `aov_chart.png`
- `daily_trend_chart.png`
- `device_breakdown_chart.png`
- `statistical_summary.txt`

#### Step 5 — Build the Excel workbook

```
python3 excel/build_workbook.py
```

This creates `outputs/NovaCart_AB_Test_Analysis.xlsx`. Open it with
Microsoft Excel, Google Sheets, or LibreOffice Calc. It has 3 tabs:

- **Raw Data** — all 20,000 rows
- **Summary** — conversion rate, AOV, abandonment rate, etc., all computed
  with live formulas (SUMIFS / COUNTIFS / AVERAGEIFS) referencing Raw Data
- **Dashboard** — a bar chart comparing Control vs. Treatment

## Part 3: Push it to GitHub

If you already have a GitHub account and just need to upload this folder:

1. Go to https://github.com/new and create a new repository (do **not**
   initialize it with a README, since you already have one).
2. In your terminal, inside the project folder, run:
   ```
   git init
   git add .
   git commit -m "Initial commit: NovaCart A/B test analysis project"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   git push -u origin main
   ```
   Replace `YOUR-USERNAME/YOUR-REPO-NAME` with your actual GitHub username
   and the repository name you chose.
3. Refresh your GitHub page — your files, including the README with the
   chart image, should now be visible.

If `git` isn't installed, download it from https://git-scm.com/downloads,
or simply drag-and-drop the whole folder into GitHub's web upload feature
(open your new repo → "Add file" → "Upload files").

## Troubleshooting

| Problem                                         | Fix                                                                                            |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `python3: command not found`                    | Try `python` instead of `python3`                                                              |
| `pip: command not found`                        | Try `pip3`, or `python3 -m pip install ...`                                                    |
| `ModuleNotFoundError: No module named 'pandas'` | Re-run the pip install command in Part 1, Step 2                                               |
| `jupyter: command not found`                    | Re-run `pip install jupyter` from Part 1, Step 2                                               |
| Excel file won't open / looks broken            | Make sure you ran Step 5 (`build_workbook.py`) — don't edit the `.xlsx` before opening it once |
| `sqlite3: command not found`                    | Use Option A (DB Browser for SQLite) instead — no command line needed                          |
