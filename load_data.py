import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# File 1: Bitcoin Market Sentiment (Fear/Greed)
sentiment_url = 'https://drive.google.com/uc?export=download&id=1PgQC0tO8XN-wqkNyghWc_-mnrYv_nhSf'
sentiment = pd.read_csv(sentiment_url)

# File 2: Historical Trader Data
trades_url = 'https://drive.google.com/uc?export=download&id=1IAfLZwu6rJzyWKgBToqwSmmVYU6VbjVs'
trades = pd.read_csv(trades_url)

def data_quality_checks(df, dataset_name):
    print("=" * 60)
    print(f"--- Data Quality Checks for {dataset_name} ---")
    print("=" * 60)
    
    # 1. Check for missing values
    print("\n[1. Missing Values Count per Column]")
    print(df.isnull().sum().to_string())
    
    # 2. Identify duplicate rows
    duplicates_count = df.duplicated().sum()
    print(f"\n[2. Number of Duplicate Rows]: {duplicates_count}")
    
    # 3. Display summary statistics
    print("\n[3. Summary Statistics]")
    # Using 'all' to include categorical data statistics as well
    print(df.describe(include='all').to_string())
    
    # 4. Print data types again to verify consistency
    print("\n[4. Data Types (Consistency Check)]")
    print(df.dtypes.to_string())
    
    # 5. Remove duplicates if found
    if duplicates_count > 0:
        print(f"\n[5. Removing {duplicates_count} Duplicate Rows...]")
        df_cleaned = df.drop_duplicates()
        # 6. Display cleaned dataset shape
        print(f"[6. Cleaned Dataset Shape]: {df_cleaned.shape[0]} rows, {df_cleaned.shape[1]} columns")
        return df_cleaned
    else:
        print("\n[5. No duplicates to remove.]")
        # 6. Display cleaned dataset shape
        print(f"[6. Cleaned Dataset Shape]: {df.shape[0]} rows, {df.shape[1]} columns")
        return df


print("Performing data quality checks...\n")
sentiment_clean = data_quality_checks(sentiment, "BITCOIN MARKET SENTIMENT")
print("\n" + "*"*80 + "\n")
trades_clean = data_quality_checks(trades, "HISTORICAL TRADER DATA")

# --- DATE/TIME FORMATTING AND ALIGNMENT ---
print("\n" + "=" * 60)
print("--- Date/Time Formatting and Alignment ---")
print("=" * 60)

# 1. Convert the sentiment dataset 'date' column to datetime format (Daily granularity)
sentiment_clean['date'] = pd.to_datetime(sentiment_clean['date'])

# 2. Convert the trades dataset Unix 'Timestamp' column to a readable datetime format
# The Timestamp column values are large (e.g., 1.73E+12), which indicates milliseconds
trades_clean['datetime'] = pd.to_datetime(trades_clean['Timestamp'], unit='ms')

# 3 & 4. Extract only the date (day-level) into a new common column 'date'
trades_clean['date'] = trades_clean['datetime'].dt.normalize()

# 5. Ensure both datasets have the same granularity 
sentiment_clean['date'] = sentiment_clean['date'].dt.normalize()

# 6. Display sample rows to verify the conversions
print("\n[Sentiment Dataset - Converted 'date' column verification]")
print(sentiment_clean[['date', 'value', 'classification']].head().to_string())

print("\n[Trades Dataset - Converted 'datetime' and extracted 'date' column verification]")
print(trades_clean[['Timestamp', 'datetime', 'date', 'Execution Price']].head().to_string())

print("\n✅ Date columns successfully aligned to daily granularity!")

# --- MERGING DATASETS ---
print("\n" + "=" * 60)
print("--- Merging Datasets (Trades + Sentiment) ---")
print("=" * 60)

# 1 & 2. Perform a left join using the trades dataset as the base and sentiment dataset on the 'date' column.
# We are integrating just the 'value' and 'classification' columns to avoid duplicate timestamp columns
merged_df = trades_clean.merge(sentiment_clean[['date', 'value', 'classification']], on='date', how='left')

# 3. Check the merged dataset shape
print("\n[Merged Dataset Shape]")
print(f"{merged_df.shape[0]} rows, {merged_df.shape[1]} columns")

# 4. Display the first few rows of the merged dataset
print("\n[Merged Dataset - First 5 rows (Showing key columns)]")
columns_to_show = ['date', 'Execution Price', 'Side', 'Size USD', 'value', 'classification']
print(merged_df[columns_to_show].head().to_string())

# 5. Verify that the sentiment classification column has been correctly added
print("\n[Verification: New Columns]")
if 'classification' in merged_df.columns:
    print("✅ Sentiment 'classification' column is correctly present.")
else:
    print("❌ Error: 'classification' column is missing!")

# 6. Check for any missing sentiment values after the merge
missing_sentiments = merged_df['classification'].isnull().sum()
total_records = len(merged_df)
missing_percentage = (missing_sentiments / total_records) * 100

print(f"\n[Missing Sentiments Check]")
print(f"Number of trade records with missing sentiment data: {missing_sentiments}")
print(f"Percentage of missing sentiments: {missing_percentage:.2f}%")

print("\n✅ Dataset merged, checked for quality, and ready for feature engineering!")

# --- FEATURE ENGINEERING & ANALYTICS ---
print("\n" + "=" * 60)
print("--- Feature Engineering & Key Analytical Metrics ---")
print("=" * 60)

# 1. Create a new 'win' column where True if Closed PnL > 0, False otherwise
merged_df['win'] = merged_df['Closed PnL'] > 0

# 2. Calculate daily PnL per account (Grouping by Account and Date)
daily_pnl = merged_df.groupby(['Account', 'date'])['Closed PnL'].sum().reset_index()
daily_pnl.rename(columns={'Closed PnL': 'Daily PnL'}, inplace=True)

# 3 & 4. Calculate win rate per account & average trade size (Size USD)
account_metrics = merged_df.groupby('Account').agg(
    Total_Trades=('win', 'count'),
    Winning_Trades=('win', 'sum'),
    Average_Trade_Size=('Size USD', 'mean')
).reset_index()

# Calculate Win Rate Percentage
account_metrics['Win Rate (%)'] = (account_metrics['Winning_Trades'] / account_metrics['Total_Trades']) * 100

# 5. Calculate number of trades per day
daily_trades = merged_df.groupby('date').size().reset_index(name='Number of Trades')

# 6. Calculate long vs short ratio using the 'Side' column
side_counts = merged_df['Side'].value_counts()
long_count = side_counts.get('BUY', 0)     # Assuming 'BUY' implies taking a long position
short_count = side_counts.get('SELL', 0)   # Assuming 'SELL' implies short/closing

long_short_ratio = long_count / short_count if short_count > 0 else float('inf')

# 7. Check for a leverage column and compute distribution if it exists
leverage_stats = "No 'Leverage' column found in the dataset."
for col in merged_df.columns:
    if col.lower() == 'leverage':
        leverage_stats = merged_df[col].describe().to_string()
        break

# 8. Display sample outputs for each verified metric
print("\n[1. 'win' Feature Preview (First 5 rows)]")
print(merged_df[['Account', 'date', 'Closed PnL', 'win']].head().to_string())

print("\n[2. Daily PnL per Account (Preview)]")
print(daily_pnl.head().to_string())

print("\n[3 & 4. Win Rate, Total Trades, and Avg Trade Size per Account]")
print(account_metrics[['Account', 'Total_Trades', 'Win Rate (%)', 'Average_Trade_Size']].head().to_string())

print("\n[5. Number of Trades per Day (Preview)]")
print(daily_trades.head().to_string())

print("\n[6. Long vs Short Ratio]")
print(f"Long (BUY) Trades: {long_count}")
print(f"Short (SELL) Trades: {short_count}")
print(f"Ratio (Long/Short): {long_short_ratio:.2f}")

print("\n[7. Leverage Distribution]")
print(leverage_stats)

print("\n✅ Analytical metrics calculated successfully!")

# --- SENTIMENT PERFORMANCE ANALYSIS ---
print("\n" + "=" * 60)
print("--- Trader Performance: Fear vs. Greed ---")
print("=" * 60)

# Filter out rows missing sentiment classification
valid_sentiment_df = merged_df.dropna(subset=['classification']).copy()

# 1. Group the merged dataset by sentiment classification (Fear vs Greed)
sentiment_analysis = valid_sentiment_df.groupby('classification').agg(
    Total_Trades=('win', 'count'),
    Winning_Trades=('win', 'sum'),
    Average_Closed_PnL=('Closed PnL', 'mean'), # 2. Calculate average Closed PnL
    PnL_Std_Dev=('Closed PnL', 'std')          # 4. Drawdown proxy (variability)
).reset_index()

# 3. Calculate win rate for each sentiment
sentiment_analysis['Win Rate (%)'] = (sentiment_analysis['Winning_Trades'] / sentiment_analysis['Total_Trades']) * 100

# 5. Present the results in a clear table
pd.set_option('display.float_format', lambda x: '%.2f' % x)
print("\n[Performance by Sentiment Classification]")
print(sentiment_analysis.to_string(index=False))

# 6. Create bar charts to compare
plt.figure(figsize=(14, 6))

sentiment_colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0']
colors = sentiment_colors[:len(sentiment_analysis)] if len(sentiment_analysis) <= len(sentiment_colors) else None

# Plot 1: Average PnL (Fear vs Greed)
plt.subplot(1, 2, 1)
plt.bar(sentiment_analysis['classification'], sentiment_analysis['Average_Closed_PnL'], color=colors)
plt.title('Average PnL by Market Sentiment')
plt.xlabel('Market Sentiment')
plt.ylabel('Average Closed PnL (USD)')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Plot 2: Win Rate (Fear vs Greed)
plt.subplot(1, 2, 2)
plt.bar(sentiment_analysis['classification'], sentiment_analysis['Win Rate (%)'], color=colors)
plt.title('Win Rate by Market Sentiment')
plt.xlabel('Market Sentiment')
plt.ylabel('Win Rate (%)')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
chart_filename = 'sentiment_performance_charts.png'
plt.savefig(chart_filename)
print(f"\n✅ Bar charts successfully created and saved locally as '{chart_filename}'!")

# --- TRADER BEHAVIOR ANALYSIS ---
print("\n" + "=" * 60)
print("--- Part 1: Trader Behavior Analysis (Fear vs. Greed) ---")
print("=" * 60)

# Calculate trade frequency by sentiment
behavior_analysis = valid_sentiment_df.groupby('classification').agg(
    Average_Trade_Size=('Size USD', 'mean'),
    Trade_Frequency=('Account', 'count')
).reset_index()

# Calculate long/short distribution
long_short_dist = valid_sentiment_df.groupby(['classification', 'Side']).size().unstack(fill_value=0)
if 'BUY' in long_short_dist.columns and 'SELL' in long_short_dist.columns:
    behavior_analysis = behavior_analysis.merge(long_short_dist.reset_index(), on='classification', how='left')
    behavior_analysis.rename(columns={'BUY': 'Long_Trades', 'SELL': 'Short_Trades'}, inplace=True)
    behavior_analysis['Long_Ratio'] = behavior_analysis['Long_Trades'] / (behavior_analysis['Long_Trades'] + behavior_analysis['Short_Trades'])

# Calculate average leverage if available
if 'Leverage' in valid_sentiment_df.columns:
    leverage_agg = valid_sentiment_df.groupby('classification')['Leverage'].mean().reset_index()
    behavior_analysis = behavior_analysis.merge(leverage_agg, on='classification', how='left')
    behavior_analysis.rename(columns={'Leverage': 'Average_Leverage'}, inplace=True)
elif 'leverage' in valid_sentiment_df.columns:
    leverage_agg = valid_sentiment_df.groupby('classification')['leverage'].mean().reset_index()
    behavior_analysis = behavior_analysis.merge(leverage_agg, on='classification', how='left')
    behavior_analysis.rename(columns={'leverage': 'Average_Leverage'}, inplace=True)

print("\n[Behavior Analysis by Sentiment]")
print(behavior_analysis.to_string(index=False))

# Plotting Behavior
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
plt.bar(behavior_analysis['classification'], behavior_analysis['Trade_Frequency'], color=colors)
plt.title('Trade Frequency by Market Sentiment')
plt.xlabel('Market Sentiment')
plt.ylabel('Number of Trades')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.subplot(1, 2, 2)
plt.bar(behavior_analysis['classification'], behavior_analysis['Average_Trade_Size'], color=colors)
plt.title('Average Trade Size by Market Sentiment')
plt.xlabel('Market Sentiment')
plt.ylabel('Average Trade Size (USD)')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
behavior_chart_filename = 'trader_behavior_charts.png'
plt.savefig(behavior_chart_filename)
print(f"\n✅ Behavior charts created and saved as '{behavior_chart_filename}'!")

# --- TRADER SEGMENTATION ---
print("\n" + "=" * 60)
print("--- Part 2: Trader Segmentation Analysis ---")
print("=" * 60)

# Calculate base metrics per account for segmentation
account_seg = merged_df.groupby('Account').agg(
    Total_Trades=('win', 'count'),
    Winning_Trades=('win', 'sum'),
    Average_PnL=('Closed PnL', 'mean'),
    PnL_Std=('Closed PnL', 'std')
).reset_index()

account_seg['Win Rate (%)'] = (account_seg['Winning_Trades'] / account_seg['Total_Trades']) * 100

# Handle NaN standard deviations for accounts with 1 trade
account_seg['PnL_Std'] = account_seg['PnL_Std'].fillna(0)

# Frequency-based segments
freq_median = account_seg['Total_Trades'].median()
account_seg['Frequency_Segment'] = np.where(account_seg['Total_Trades'] >= freq_median, 'Frequent', 'Infrequent')

# Consistency segments
std_median = account_seg['PnL_Std'].median()
account_seg['Consistency_Segment'] = np.where(account_seg['PnL_Std'] <= std_median, 'Consistent', 'Inconsistent')

print("\n[Frequency-Based Segments]")
freq_summary = account_seg.groupby('Frequency_Segment').agg(
    Avg_PnL=('Average_PnL', 'mean'),
    Avg_Win_Rate=('Win Rate (%)', 'mean'),
    Account_Count=('Account', 'count')
).reset_index()
print(freq_summary.to_string(index=False))

print("\n[Consistency Segments]")
consistency_summary = account_seg.groupby('Consistency_Segment').agg(
    Avg_PnL=('Average_PnL', 'mean'),
    Avg_Win_Rate=('Win Rate (%)', 'mean'),
    Account_Count=('Account', 'count')
).reset_index()
print(consistency_summary.to_string(index=False))

# Leverage-based segments
lev_col_found = None
if 'Leverage' in merged_df.columns:
    lev_col_found = 'Leverage'
elif 'leverage' in merged_df.columns:
    lev_col_found = 'leverage'

if lev_col_found:
    account_lev = merged_df.groupby('Account')[lev_col_found].mean().reset_index()
    account_seg = account_seg.merge(account_lev, on='Account', how='left')
    lev_median = account_seg[lev_col_found].median()
    account_seg['Leverage_Segment'] = np.where(account_seg[lev_col_found] >= lev_median, 'High Leverage', 'Low Leverage')
    
    print("\n[Leverage-Based Segments]")
    lev_summary = account_seg.groupby('Leverage_Segment').agg(
        Avg_PnL=('Average_PnL', 'mean'),
        Avg_Win_Rate=('Win Rate (%)', 'mean'),
        Account_Count=('Account', 'count')
    ).reset_index()
    print(lev_summary.to_string(index=False))
else:
    print("\n[Leverage-Based Segments]: Skipped due to missing leverage column in original dataset.")

print("\n✅ Trader segmentation calculations compiled successfully!")
