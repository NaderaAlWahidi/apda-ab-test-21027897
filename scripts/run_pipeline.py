import argparse
import sys
from pathlib import Path
 
# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
 
from pipeline import (
    load_data,
    inspect_data,
    validate_data_contract,
    clean_data,
    save_data,
    print_inspection_report,
    print_cleaning_report
)
 
 
def main():
    # Parse command-line arguments 
    parser = argparse.ArgumentParser(
        description='A/B test data pipeline: load, validate, clean, and save experiment records'
    )
    
    parser.add_argument(
        '--input',
        required=True,
        type=str,
        help='Path to raw input CSV file (e.g., data/raw/ab_data.csv)'
    )
    
    parser.add_argument(
        '--output-dir',
        required=True,
        type=str,
        help='Output directory for cleaned data files (e.g., data/processed)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("A/B TEST DATA PIPELINE")
    print("="*70)
    
    try:
        # STEP 1: LOAD DATA
        print(f"\n[STEP 1] Loading data from: {args.input}")
        data = load_data(args.input)
        print(f"✓ Successfully loaded {len(data):,} records")
        
        # STEP 2: INSPECT DATA
        print(f"\n[STEP 2] Inspecting data structure and quality...")
        inspection_report = inspect_data(data)
        print_inspection_report(inspection_report)
        
        # STEP 3: VALIDATE DATA CONTRACT
        print(f"\n[STEP 3] Validating data contract...")
        validate_data_contract(data)
        print("✓ Data contract validation passed")
        print("  ✓ All required columns present")
        print("  ✓ All group values valid (control, treatment)")
        print("  ✓ All landing_page values valid (old_page, new_page)")
        print("  ✓ All converted values valid (0, 1)")
        
        # STEP 4: CLEAN DATA
        print(f"\n[STEP 4] Cleaning experiment records...")
        cleaned_data, cleaning_report = clean_data(data)
        print_cleaning_report(cleaning_report)
        print("✓ Data cleaning completed successfully")
        
        # STEP 5: SAVE CLEANED DATA
        print(f"\n[STEP 5] Saving cleaned data to: {args.output_dir}")
        output_paths = save_data(cleaned_data, args.output_dir)
        print(f"✓ Saved CSV: {output_paths['csv_path']}")
        print(f"✓ Saved Parquet: {output_paths['parquet_path']}")
        
        # PRINT SUMMARY
        print("\n" + "="*70)
        print("PIPELINE EXECUTION SUMMARY")
        print("="*70)
        print(f"\nInput file:          {args.input}")
        print(f"Output directory:    {args.output_dir}")
        print(f"\nRecords processed:   {cleaning_report['initial_rows']:,}")
        print(f"Records cleaned:     {cleaning_report['final_rows']:,}")
        print(f"Records removed:     {cleaning_report['initial_rows'] - cleaning_report['final_rows']:,}")
        print(f"  - Alignment issues: {cleaning_report['rows_removed_by_alignment']:,}")
        print(f"  - Duplicates:       {cleaning_report['rows_removed_by_deduplication']:,}")
        print(f"\nSuccess rate:        {(cleaning_report['final_rows'] / cleaning_report['initial_rows'] * 100):.2f}%")
        print(f"\n✓ Pipeline completed successfully!")
        print("="*70 + "\n")
        
        return 0
    
    except FileNotFoundError as e:
        print(f"\n✗ ERROR: {e}", file=sys.stderr)
        return 1
    
    except ValueError as e:
        print(f"\n✗ VALIDATION ERROR: {e}", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}", file=sys.stderr)
        return 1
 
 
if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
 