# Landing Page A/B Test Analysis

![Tests](https://github.com/NaderaAlWahidi/apda-ab-test-21027897/actions/workflows/tests.yml/badge.svg)

A reproducible analytics project testing whether a new landing page improves conversion rates compared to the control page.

## Project Question
Does the new landing page (treatment) have a statistically significantly different conversion rate compared to the old landing page (control)?

## Dataset Source
- **Source**: [A/B Testing on Kaggle](https://www.kaggle.com/datasets/zainabq/ab-testing)
- **File**: `ab_data.csv`
- **License**: Public dataset
- **Description**: Online experiment comparing conversion rates between control (old page) and treatment (new page) groups
- **Time Period**: January 2-24, 2017
- **Sample Size**: 294,478 user records (~146,000 per group)

## Project Structure
```
apda-ab-test-STUDENT_ID/
├── README.md                          
├── requirements.txt                   
├── .gitignore                         
│
├── data/
│   ├── raw/
│   │   ├── README.md                 
│   │   └── ab_data.csv               
│   └── processed/
│       ├── clean_ab_data.csv         
│       └── clean_ab_data.parquet    
│
├── src/
│   └── pipeline.py                   
│
├── scripts/
│   ├── run_pipeline.py               
│   └── run_sql.py                    
│
├── sql/
│   └── analysis.sql                  
│
├── r/
│   └── ab_test.R                    
│
├── tests/
│   └── test_pipeline.py              
│
├── outputs/
│   ├── group_summary.csv             
│   ├── daily_conversion.csv          
│   └── figures/
│       ├── bar_conversion_rate_comparison.png       
│       └── line_daily_conversion_trend.png
│
└── .github/
    └── workflows/
        └── tests.yml                 
```

## Requirements

### Python Requirements
- **Python 3.9+**
- **Pandas**: Data manipulation
- **NumPy**: Numerical operations
- **DuckDB**: SQL analysis
- **pytest**: Unit testing

### R Requirements
- **R 4.0+**
- **readr**: Reading CSV files
- **dplyr**: Data manipulation
- **ggplot2**: Visualization
- **base R stats**: Statistical testing (`prop.test`)

## Setup

### Step 1: Download the Raw Dataset
The raw dataset is NOT included in the repository. You must download it separately:

1. Go to [A/B Testing on Kaggle](https://www.kaggle.com/datasets/zainabq/ab-testing)
2. Download `ab_data.csv`
3. Place it in `data/raw/ab_data.csv` (create the directory if needed)
4. Do NOT commit this file to GitHub

### Step 2: Create Python Virtual Environment (Windows)
```powershell
# Create virtual environment
py -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Note: If you get an execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Create Python Virtual Environment (macOS/Linux)
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

### Step 4: Install Python Dependencies
```bash
# From the repository root with .venv activated
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Verify Setup
```bash
# Check Python
python --version

# Check Pandas installed
python -c "import pandas; print(f'Pandas {pandas.__version__}')"

# Check DuckDB installed
python -c "import duckdb; print(f'DuckDB {duckdb.__version__}')"

# Check pytest installed
pytest --version
```

## Running the Analysis

### Run the Python Data Pipeline
Clean and process the raw data:

```bash
# From repository root with .venv activated
python scripts/run_pipeline.py --input data/raw/ab_data.csv --output-dir data/processed
```

**Expected Output:**
- `data/processed/clean_ab_data.csv` (cleaned data in CSV format)
- `data/processed/clean_ab_data.parquet` (cleaned data in Parquet format)
- Console output showing data quality checks

### Run Python Tests
Execute unit tests to verify the pipeline works correctly:

```bash
# From repository root with .venv activated
pytest -v

# Or run with coverage report
pytest -v --cov=src
```

**Expected Output:**
- ✓ Test validation rejects missing required columns
- ✓ Test cleaning removes incorrect group/page assignments
- ✓ Test cleaning keeps earliest record for duplicate users

### Run DuckDB Analysis
Execute SQL queries to generate summary statistics:

```bash
# From repository root with .venv activated
python scripts/run_sql.py
```

**Expected Output:**
- `outputs/group_summary.csv` - Summary statistics by group (users, conversions, rate)
- `outputs/daily_conversion.csv` - Daily conversion rates by group and date
- Console output with data verification queries

Or run SQL directly:
```bash
# View the SQL queries
cat sql/analysis.sql
```

### Run R Statistical Analysis
Execute R analysis to perform hypothesis testing and create visualizations:

```bash
# From repository root (R must be installed)
# Option 1: From terminal
Rscript r/ab_test.R

# Option 2: In RStudio
# Open r/ab_test.R and run all lines (Ctrl+A, Ctrl+Enter)
```

**Expected Output:**
- Console output with hypothesis test results:
  - H0 and H1 statements
  - Group conversion rates
  - Absolute lift (percentage points)
  - Relative lift (percentage)
  - P-value and 95% confidence interval
  - Decision: REJECT or FAIL TO REJECT H0
  - Interpretation with practical limitations
  
- Generated figures:
  - `outputs/figures/bar_conversion_rate_comparison.png` (Figure 1)
  - `outputs/figures/line_daily_conversion_trend.png` (Figure 2)

## Generated Outputs

### Data Outputs
| File | Purpose | Format |
|------|---------|--------|
| `data/processed/clean_ab_data.csv` | Cleaned experiment data | CSV |
| `data/processed/clean_ab_data.parquet` | Cleaned experiment data | Parquet |

### Analysis Outputs
| File | Purpose | Format |
|------|---------|--------|
| `outputs/group_summary.csv` | Users, conversions, rates by group | CSV |
| `outputs/daily_conversion.csv` | Daily conversion rates by group | CSV |

### Visualization Outputs
| File | Purpose | Type |
|------|---------|------|
| `outputs/figures/bar_conversion_rate_comparison.png` | Overall group comparison | Bar chart (PNG, 6×5", 300 DPI) |
| `outputs/figures/line_daily_conversion_trend.png` | Temporal conversion trends | Line chart (PNG, 8×5", 300 DPI) |

## Complete Workflow Example

Run the entire analysis from start to finish:

```bash
# 1. Activate virtual environment (Windows)
.\.venv\Scripts\Activate.ps1

# Or (macOS/Linux)
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run Python pipeline (cleans data)
python scripts/run_pipeline.py --input data/raw/ab_data.csv --output-dir data/processed

# 4. Run pytest tests
pytest -v

# 5. Run DuckDB analysis
python scripts/run_sql.py

# 6. Run R analysis and create visualizations
Rscript r/ab_test.R

# 7. Verify all outputs were created
ls -lh outputs/
ls -lh outputs/figures/
```

## Key Analysis Results

### Primary Metric
Proportion of users who converted (binary outcome: 1 = converted, 0 = no conversion)

### Hypothesis Test
- **H0**: Treatment and control population conversion rates are equal
- **H1**: Treatment and control population conversion rates are different
- **α**: 0.05 (significance level)
- **Test Method**: Two-proportion Z-test (`prop.test` with `correct = FALSE`)

### Interpretation Requirements
The final recommendation considers:
1. **Direction and size of effect**: Is treatment better/worse? By how much?
2. **Confidence interval**: Does it include zero?
3. **P-value**: Is the result statistically significant?
4. **Practical limitations**: Can we realistically implement this? What are the costs?

⚠️ **Note**: Statistical significance alone is NOT sufficient for a recommendation.

## Important Notes

### Data Privacy
- The raw `data/raw/ab_data.csv` file is excluded from GitHub (see `.gitignore`)
- Do NOT commit raw or processed data to the repository
- The processed data is generated by the pipeline and not committed

### Reproducibility
- All commands use relative paths from the repository root
- No absolute paths (e.g., `/Users/yourname/...`) are used
- The pipeline runs identically on Windows, macOS, and Linux
- GitHub Actions automatically runs tests on every push and pull request

### Python Requirements File
The `requirements.txt` should contain:
```
pandas>=2.0,<3.0
numpy>=1.24,<3.0
duckdb>=1.1,<2.0
pytest>=7.0,<9.0
pytest-cov>=4.0,<6.0
```

Install with:
```bash
pip install -r requirements.txt
```

## Troubleshooting

### "ab_data.csv not found"
```bash
# Verify the file exists in the correct location
ls -lh data/raw/ab_data.csv

# If missing, download from Kaggle and place it there
```

### "pytest: command not found"
```bash
# Ensure .venv is activated and requirements installed
pip install -r requirements.txt
pytest --version
```

### "Rscript: command not found"
```bash
# R must be installed on your system
# macOS: brew install r
# Windows: Download from https://cran.r-project.org/
# Linux: sudo apt-get install r-base
```

### DuckDB file not found error
```bash
# Ensure the pipeline was run first to generate cleaned data
python scripts/run_pipeline.py --input data/raw/ab_data.csv --output-dir data/processed

# Then verify the parquet file exists
ls -lh data/processed/clean_ab_data.parquet
```

## GitHub Repository

- **Repository Name**: `apda-ab-test-STUDENT_ID`
- **Access**: Public or add instructor as collaborator
- **Status**: Include GitHub Actions badge showing test status

## Final Deliverables

1. ✅ GitHub repository with all code and documentation
2. ✅ Word report: `StudentID_FullName_APDA_Project_Report.docx`
   - Project question and hypothesis test results
   - DuckDB summary tables
   - Two R visualizations
   - Final recommendation with practical limitations
3. ✅ All outputs generated by running the pipeline and R script

## Questions or Issues?

Refer to the full project brief or contact your instructor.

---

**Last Updated**: September 2024  
**Course**: Advanced Programming for Data Analysis  
**Instructor**: Hamzeh Hailat