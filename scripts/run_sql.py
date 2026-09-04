from pathlib import Path
import duckdb
 
ROOT = Path(__file__).resolve().parents[1]
SQL_FILE = ROOT / 'sql' / \
    'practice_analysis.sql'
OUTPUT_DIR = ROOT / 'outputs'
 
OUTPUT_DIR.mkdir(parents=True,exist_ok=True)
sql_text = SQL_FILE.read_text(encoding='utf-8')

with duckdb.connect() as connection:
    connection.execute(sql_text)
    group = connection.sql(
        'SELECT * FROM group_summary').df()
    daily = connection.sql(
        'SELECT * FROM daily_conversion').df()
    check = connection.sql(
        'SELECT * FROM data_verification').df()
 
group.to_csv(OUTPUT_DIR /
    'practice_group_summary.csv', index=False)
daily.to_csv(OUTPUT_DIR /
    'practice_daily_conversion.csv', index=False)
print(group)
print(check)