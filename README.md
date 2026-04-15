# Primetrade.ai - Trader Performance vs Market Sentiment Analysis 📊

## Project Overview
This directory contains the analysis pipeline for the Data Science Intern Round-0 Assignment at Primetrade.ai. The overarching objective of this project is to parse, synthesize, and determine explicit quantitative correlations between widespread market sentiment (Fear/Greed) and independent trader behaviors on the Hyperliquid platform. 

The primary analysis engine relies on a robust data engineering `Python` pipeline (`load_data.py`) which automatically accesses datasets via the cloud, cleans structural deviations, builds key metric columns, segments behavior cohorts, and natively plots insights.

## Directory Structure
- `load_data.py`: The core python script performing data extraction, merging, transformations, feature engineering, and chart generations.
- `WRITEUP.md`: A concise one-page summary highlighting the engineering methodology, the verified actionable data insights, and the resulting algorithmic strategy recommendations based purely on the numbers.
- `analyze.ps1`: Optional PowerShell helper script constructed to locally assist massive `.csv` crunching capabilities in sandbox limits.
- `sentiment_performance_charts.png` & `trader_behavior_charts.png`: Visual graphics dynamically rendered and exported upon executing the python script.

## Installation & Setup
To run the analysis cleanly, ensure you have Python 3.8+ installed on your system.

**1. Install Core Dependencies:**
The script utilizes the core data science libraries to efficiently manipulate millions of cells and plot geometric arrays. Run the following command in your terminal:
```bash
pip install pandas numpy matplotlib
```

## How to Run
Trigger the analytics pipeline fully via the native command line instructions.
```bash
python load_data.py
```
> The script is automated efficiently! Upon running, it will actively download the 45MB and 1MB target datasets, strip internal anomalies (nulls/duplicates), configure exact daily granularities to seamlessly left-join, generate output tables natively to the executing shell, and instantly push `.png` data representations directly into your current directory folder.
