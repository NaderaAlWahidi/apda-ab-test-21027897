import duckdb
import pandas as pd
from pathlib import Path
 
 
def create_output_directory():
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)
    return output_dir
 
 
def execute_query(query, query_name):
    print(f"\n[QUERY] {query_name}")
    print("-" * 70)
    
    try:
        # Connect to DuckDB (in-memory by default)
        conn = duckdb.connect(':memory:')
        
        # Execute query
        result = conn.execute(query).fetchall()
        columns = [desc[0] for desc in conn.description]
        
        # Convert to DataFrame
        df = pd.DataFrame(result, columns=columns)
        
        print(f"✓ Query executed successfully")
        print(f"✓ Rows returned: {len(df)}")
        
        return df
    
    except Exception as e:
        print(f"✗ Error executing query: {e}")
        raise
 
 
def query_4_1_experiment_summary():
    query = """
    SELECT 
        "group",
        COUNT(DISTINCT user_id) AS users,
        SUM(converted) AS conversions,
        ROUND(SUM(converted)::FLOAT / COUNT(*)::FLOAT, 6) AS conversion_rate
    FROM 'data/processed/clean_ab_data.parquet'
    GROUP BY "group"
    ORDER BY "group";
    """
    
    return execute_query(query, "4.1 - Experiment Summary (Group Statistics)")
 
 
def query_4_2_daily_summary():
  
    query = """
    SELECT 
        experiment_date,
        "group",
        COUNT(DISTINCT user_id) AS users,
        SUM(converted) AS conversions,
        ROUND(SUM(converted)::FLOAT / COUNT(*)::FLOAT, 6) AS conversion_rate
    FROM 'data/processed/clean_ab_data.parquet'
    GROUP BY experiment_date, "group"
    ORDER BY experiment_date, "group";
    """
    
    return execute_query(query, "4.2 - Daily Summary (Time Series by Group)")
 
 
def query_4_3_data_verification():
   
    query = """
    SELECT 
        COUNT(*) AS total_rows,
        COUNT(DISTINCT user_id) AS distinct_user_ids,
        MIN(experiment_date) AS min_experiment_date,
        MAX(experiment_date) AS max_experiment_date
    FROM 'data/processed/clean_ab_data.parquet';
    """
    
    return execute_query(query, "4.3 - Data Verification (Quality Assurance)")
 
 
def save_results(df, filename):
  
    output_path = Path('outputs') / filename
    df.to_csv(output_path, index=False)
    return str(output_path)
 
 
def print_results_summary(df, title):

    print(f"\n{title}")
    print("=" * 70)
    print(df.to_string(index=False))
    print()
 
 
def verify_data_integrity(verification_df):

    print("\n[VERIFICATION] Data Integrity Check")
    print("=" * 70)
    
    total_rows = verification_df['total_rows'].iloc[0]
    distinct_users = verification_df['distinct_user_ids'].iloc[0]
    min_date = verification_df['min_experiment_date'].iloc[0]
    max_date = verification_df['max_experiment_date'].iloc[0]
    
    print(f"Total rows in cleaned data:        {total_rows:,}")
    print(f"Distinct user IDs:                 {distinct_users:,}")
    print(f"Date range:                        {min_date} to {max_date}")
    
    # Verify data integrity
    if total_rows == distinct_users:
        print(f"\n✓ Data integrity verified!")
        print(f"✓ Total rows ({total_rows:,}) == Distinct users ({distinct_users:,})")
        print(f"✓ No duplicate user IDs found (as expected after cleaning)")
    else:
        print(f"\n✗ Data integrity issue detected!")
        print(f"✗ Total rows ({total_rows:,}) != Distinct users ({distinct_users:,})")
        print(f"✗ Found {total_rows - distinct_users} duplicate records")
 
 
def main():
    #Execute all DuckDB queries and save results.
    
    print("\n" + "=" * 70)
    print("DuckDB ANALYSIS: A/B TEST DATA")
    print("=" * 70)
    
    try:
        # Create output directory
        output_dir = create_output_directory()
        print(f"\n[SETUP] Output directory: {output_dir}")
         
        # 4.1: EXPERIMENT SUMMARY
        print(f"\n" + "=" * 70)
        print("PART 4.1: EXPERIMENT SUMMARY")
        print("=" * 70)
        
        group_summary = query_4_1_experiment_summary()
        print_results_summary(group_summary, "Group Summary Results")
        
        # Save to CSV
        csv_path_1 = save_results(group_summary, 'group_summary.csv')
        print(f"✓ Saved to: {csv_path_1}")
        
        # 4.2: DAILY SUMMARY
        print(f"\n" + "=" * 70)
        print("PART 4.2: DAILY SUMMARY")
        print("=" * 70)
        
        daily_summary = query_4_2_daily_summary()
        print(f"\nDaily Summary (first 5 rows):")
        print_results_summary(daily_summary.head(), "Daily Conversion Rates")
        
        # Save to CSV
        csv_path_2 = save_results(daily_summary, 'daily_conversion.csv')
        print(f"✓ Saved to: {csv_path_2}")
        print(f"✓ Total days in experiment: {daily_summary['experiment_date'].nunique()}")
        
        # 4.3: DATA VERIFICATION
        print(f"\n" + "=" * 70)
        print("PART 4.3: DATA VERIFICATION")
        print("=" * 70)
        
        verification = query_4_3_data_verification()
        verify_data_integrity(verification)
        
        # FINAL SUMMARY
        print(f"\n" + "=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)
        
        print(f"\nGenerated files:")
        print(f"  1. {csv_path_1}")
        print(f"  2. {csv_path_2}")
        print(f"\nKey findings:")
        print(f"  • Control group: {group_summary[group_summary['group'] == 'control']['conversion_rate'].values[0]:.4f} conversion rate")
        print(f"  • Treatment group: {group_summary[group_summary['group'] == 'treatment']['conversion_rate'].values[0]:.4f} conversion rate")
        print(f"  • Experiment duration: {daily_summary['experiment_date'].nunique()} days")
        print(f"  • Total users analyzed: {verification['distinct_user_ids'].iloc[0]:,}")
        
        print(f"\n✓ All queries executed successfully!")
        print(f"✓ Ready for R statistical analysis (PART 5)")
        
        return 0
    
    except FileNotFoundError as e:
        print(f"\n✗ ERROR: {e}")
        print(f"Make sure data/processed/clean_ab_data.parquet exists")
        print(f"Run the pipeline first: python scripts/run_pipeline.py --input data/raw/ab_data.csv --output-dir data/processed")
        return 1
    
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        return 1
 
 
if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
 