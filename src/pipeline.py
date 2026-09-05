import pandas as pd
import numpy as np
from pathlib import Path


def load_data(input_path):
    
    try:
        data = pd.read_csv(input_path)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except pd.errors.ParserError as e:
        raise pd.errors.ParserError(f"Error parsing CSV file: {e}")


def inspect_data(data):
  
    inspection_report = {
        'shape': data.shape,
        'columns': list(data.columns),
        'data_types': data.dtypes.to_dict(),
        'missing_values': data.isnull().sum().to_dict(),
        'duplicate_user_ids': data['user_id'].duplicated().sum(),
        'group_value_counts': data['group'].value_counts().to_dict(),
        'landing_page_value_counts': data['landing_page'].value_counts().to_dict(),
        'converted_value_counts': data['converted'].value_counts().to_dict(),
        'group_page_combinations': data.groupby(['group', 'landing_page']).size().to_dict()
    }
    return inspection_report


def validate_data_contract(data):
   
    # Check required columns
    required_columns = ['user_id', 'timestamp', 'group', 'landing_page', 'converted']
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}. "
            f"Expected: {required_columns}. "
            f"Got: {list(data.columns)}"
        )
    
    # Validate group values
    valid_groups = {'control', 'treatment'}
    invalid_groups = set(data['group'].unique()) - valid_groups
    
    if invalid_groups:
        raise ValueError(
            f"Invalid group values: {invalid_groups}. "
            f"Expected: {valid_groups}"
        )
    
    # Validate landing_page values
    valid_pages = {'old_page', 'new_page'}
    invalid_pages = set(data['landing_page'].unique()) - valid_pages
    
    if invalid_pages:
        raise ValueError(
            f"Invalid landing_page values: {invalid_pages}. "
            f"Expected: {valid_pages}"
        )
    
    # Validate converted values
    valid_converted = {0, 1}
    invalid_converted = set(data['converted'].unique()) - valid_converted
    
    if invalid_converted:
        raise ValueError(
            f"Invalid converted values: {invalid_converted}. "
            f"Expected: {valid_converted}"
        )


def clean_data(data):

    # Make a copy to avoid modifying original
    df = data.copy()
    
    # Track row counts
    initial_rows = len(df)
    
    # Step 1: Remove misaligned records
    # Correct alignment: control->old_page, treatment->new_page
    correct_alignment = (
        ((df['group'] == 'control') & (df['landing_page'] == 'old_page')) |
        ((df['group'] == 'treatment') & (df['landing_page'] == 'new_page'))
    )
    
    df = df[correct_alignment].copy()
    rows_after_alignment = len(df)
    rows_removed_alignment = initial_rows - rows_after_alignment
    
    # Step 2: Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Step 3: Create experiment_date from timestamp
    df['experiment_date'] = df['timestamp'].dt.date
    
    # Step 4: Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Step 5: Keep only the earliest record for each user_id
    df = df.drop_duplicates(subset='user_id', keep='first').copy()
    rows_after_dedup = len(df)
    rows_removed_dedup = rows_after_alignment - rows_after_dedup
    
    # Verify unique user_id
    if df['user_id'].duplicated().sum() > 0:
        raise ValueError("Failed to achieve unique user_id after deduplication")
    
    # Verify all remaining records are correctly aligned
    invalid_records = len(df) - len(df[
        ((df['group'] == 'control') & (df['landing_page'] == 'old_page')) |
        ((df['group'] == 'treatment') & (df['landing_page'] == 'new_page'))
    ])
    
    if invalid_records > 0:
        raise ValueError(f"Found {invalid_records} misaligned records after cleaning")
    
    # Create cleaning report
    cleaning_report = {
        'initial_rows': initial_rows,
        'rows_after_alignment_cleaning': rows_after_alignment,
        'rows_removed_by_alignment': rows_removed_alignment,
        'rows_after_deduplication': rows_after_dedup,
        'rows_removed_by_deduplication': rows_removed_dedup,
        'final_rows': rows_after_dedup,
        'unique_user_ids': df['user_id'].nunique(),
        'all_user_ids_unique': df['user_id'].nunique() == len(df)
    }
    
    return df, cleaning_report


def save_data(data, output_dir, csv_name='clean_ab_data', parquet_name='clean_ab_data'):

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    csv_path = output_path / f"{csv_name}.csv"
    parquet_path = output_path / f"{parquet_name}.parquet"
    
    # Save CSV without index
    data.to_csv(csv_path, index=False)
    
    # Save Parquet
    data.to_parquet(parquet_path, index=False)
    
    return {
        'csv_path': str(csv_path),
        'parquet_path': str(parquet_path)
    }


def print_inspection_report(report):

    print("\n" + "="*70)
    print("DATA INSPECTION REPORT")
    print("="*70)
    
    print(f"\nShape: {report['shape'][0]} rows × {report['shape'][1]} columns")
    
    print("\nData Types:")
    for col, dtype in report['data_types'].items():
        print(f"  {col}: {dtype}")
    
    print("\nMissing Values:")
    missing_found = False
    for col, count in report['missing_values'].items():
        if count > 0:
            print(f"  {col}: {count}")
            missing_found = True
    if not missing_found:
        print("  None")
    
    print(f"\nDuplicate User IDs: {report['duplicate_user_ids']}")
    
    print("\nGroup Distribution:")
    for group, count in report['group_value_counts'].items():
        print(f"  {group}: {count}")
    
    print("\nLanding Page Distribution:")
    for page, count in report['landing_page_value_counts'].items():
        print(f"  {page}: {count}")
    
    print("\nConversion Distribution:")
    for converted, count in report['converted_value_counts'].items():
        label = "Converted" if converted == 1 else "Not Converted"
        print(f"  {label} ({converted}): {count}")
    
    print("\nGroup × Landing Page Combinations:")
    for (group, page), count in report['group_page_combinations'].items():
        alignment = "✓ CORRECT" if (
            (group == 'control' and page == 'old_page') or
            (group == 'treatment' and page == 'new_page')
        ) else "✗ MISALIGNED"
        print(f"  {group} × {page}: {count} {alignment}")


def print_cleaning_report(report):

    print("\n" + "="*70)
    print("DATA CLEANING REPORT")
    print("="*70)
    
    print(f"\nInitial rows:                           {report['initial_rows']:,}")
    print(f"Rows after alignment cleaning:         {report['rows_after_alignment_cleaning']:,}")
    print(f"Rows removed by alignment:             {report['rows_removed_by_alignment']:,}")
    print(f"Rows after deduplication:              {report['rows_after_deduplication']:,}")
    print(f"Rows removed by deduplication:         {report['rows_removed_by_deduplication']:,}")
    print(f"\nFinal cleaned rows:                    {report['final_rows']:,}")
    print(f"Unique user IDs:                       {report['unique_user_ids']:,}")
    print(f"All user IDs unique:                   {'YES ✓' if report['all_user_ids_unique'] else 'NO ✗'}")