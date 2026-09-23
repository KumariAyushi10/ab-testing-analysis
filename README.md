# ab-testing-analysis

An end-to-end data analytics and statistical engineering project analyzing a three-week A/B test for NovaCart, an e-commerce platform. The analysis tracks the behavioral impact of a new one-click checkout flow across 20,000 user sessions, assessing key revenue performance indicators and statistical significance.

## Business Questions Answered

* **Conversion Rate Lift:** Does the new checkout layout yield a statistically significant improvement in overall purchase completion rates?
* **Average Order Value (AOV):** Does a faster checkout process inadvertently alter consumer transaction sizing or cart metrics?
* **Friction Elimination:** How successfully does the new interface reduce cart abandonment across mobile vs. desktop devices?
* **Speed Performance:** Does the variant design accelerate average user task completion times at the checkout gate?
* **Segment Variations:** Are there underlying differences in performance indicators based on traffic channels, geographic regions, or user types?

## Dataset Highlights

* **Size & Scope:** 20,000 simulated independent user sessions distributed via a controlled ~50/50 test matrix split.
* **Granular Dimensions:** Captures device categories, geographic country codes, inbound traffic channels, session runtimes, checkout states, and transactional values.

## Tools & Technical Deck

* **Statistical Testing:** Python (`scipy.stats`, `numpy`, `pandas`) running two-proportion Z-tests for conversion rates and Welch's T-tests for continuous order valuations.
* **Database Modeling:** SQLite engine for querying structured behavioral metrics and segment aggregations.
* **Automated Reporting:** An openpyxl script that generates a production-ready Excel workbook complete with dynamic, live cross-referencing formulas (`SUMIFS`, `COUNTIFS`, `AVERAGEIFS`).
* **Visualizations:** `matplotlib` and `seaborn` pipelines outputting daily trend and breakdown dashboards.

## Repository Structure

```text
├── data/        
├── excel/       
├── notebook/    
├── outputs/     
├── python/      
├── sql/         
└── README.md    
```

## How to Run It

To run this testing application environment locally, you will need [Python 3](https://python.org) installed:

1. Click the green **Code** button at the top of this GitHub page and select **Download ZIP**.
2. Extract the downloaded ZIP file on your computer.
3. Open your terminal or command prompt, change directory into the project folder, and run:
   ```bash
   pip install pandas numpy scipy matplotlib openpyxl jupyter
   ```
4. Start the interactive testing workspace:
   ```bash
   jupyter notebook
   ```
5. Open `notebook/NovaCart_AB_Test_Analysis.ipynb` and select **Kernel -> Restart & Run All** to run the analytical framework from scratch.


