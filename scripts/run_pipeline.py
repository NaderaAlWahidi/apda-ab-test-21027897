# from pathlib import Path
# import pandas as pd
 
# ROOT = Path(__file__).resolve().parents[1]
# output = ROOT / 'data' / 'processed' / \
#     'ab_processed_data.parquet'
 
# data = pd.DataFrame({
#     'visitor_id': range(201, 213),
#     'event_date': pd.to_datetime(
#         ['2026-08-01'] * 4 +
#         ['2026-08-02'] * 4 +
#         ['2026-08-03'] * 4),
#     'version': ['control', 'control',
#         'treatment', 'treatment'] * 3,
#     'converted': [
#         0,1,0,1, 0,0,1,0, 1,0,1,0]
# })
# data.to_parquet(output, index=False)


# import argparse
# import sys
# from pathlib import Path

# import pandas as pd

# ROOT = Path(__file__).resolve().parents[1]
# sys.path.insert(0, str(ROOT))

# from src.pipeline import (  # noqa: E402
#     DEFAULT_INPUT, DEFAULT_OUTPUT_DIR, run_pipeline)


# def parse_args(argv=None):
#     """Parse the --input and --output-dir command line arguments."""
#     parser = argparse.ArgumentParser(
#         description='Clean the landing page A/B test experiment records.')
#     parser.add_argument(
#         '--input', default=str(DEFAULT_INPUT),
#         help='Path to the raw ab_data.csv file.')
#     parser.add_argument(
#         '--output-dir', default=str(DEFAULT_OUTPUT_DIR),
#         help='Directory that receives the processed CSV and Parquet files.')
#     return parser.parse_args(argv)


# def report(summary):
#     """Print the inspection results, row counts and saved file paths."""
#     inspection = summary['inspection']
#     counts = summary['row_counts']

#     print('Input file:', summary['input_path'])
#     print('\n--- Raw data contract ---')
#     print('Shape:', inspection['shape'])
#     print('Data types:')
#     for column, dtype in inspection['dtypes'].items():
#         print(f'  {column}: {dtype}')
#     print('Missing values:')
#     for column, missing in inspection['missing_values'].items():
#         print(f'  {column}: {missing}')
#     print('Duplicate user IDs:', inspection['duplicate_user_ids'])
#     print('Group and landing page counts:')
#     print(inspection['group_page_counts'].to_string(index=False))

#     print('\n--- Cleaning ---')
#     print('Rows before cleaning:', counts['rows_before_cleaning'])
#     print('Rows after assignment cleaning:',
#           counts['rows_after_assignment_cleaning'],
#           f"(removed {counts['rows_removed_misaligned']})")
#     print('Rows after duplicate-user cleaning:',
#           counts['rows_after_duplicate_user_cleaning'],
#           f"(removed {counts['rows_removed_duplicate_users']})")
#     print('Unique user IDs after cleaning:',
#           summary['clean_data']['user_id'].nunique())

#     print('\n--- Saved files ---')
#     for label, path in summary['saved_files'].items():
#         print(f'  {label}: {path}')


# def main(argv=None):
#     """Run the pipeline with the given arguments and print the report."""
#     args = parse_args(argv)
#     try:
#         summary = run_pipeline(args.input, args.output_dir)
#     except (FileNotFoundError, ValueError) as error:
#         print(f'Pipeline failed: {error}', file=sys.stderr)
#         return 1
#     report(summary)
#     return 0


# if __name__ == '__main__':
#     pd.set_option('display.width', 100)
#     raise SystemExit(main())


from pathlib import Path
import sys
import matplotlib
import numpy as np
import pandas as pd

print("Python:", sys.version.split()[0])
print("Executable:", sys.executable)
print("Working directory:", Path.cwd())
print("NumPy:", np.__version__)
print("pandas:", pd.__version__)
print("Matplotlib:", matplotlib.__version__)
