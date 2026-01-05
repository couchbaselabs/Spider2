# Couchbase IQ Evaluation Guide for Spider2-Lite

This guide explains how to evaluate Couchbase IQ's text-to-SQL capabilities using the Spider2-Lite benchmark.

## 📋 Overview

**What is Spider2-Lite?**
- A text-to-SQL benchmark with 547 test instances
- Tests ability to convert natural language → SQL queries
- Supports BigQuery, Snowflake, and SQLite databases

**What is Couchbase IQ?**
- A text-to-SQL system that generates SQL from natural language
- We'll evaluate its SQL generation quality against Spider2-Lite

## 🎯 Evaluation Process

```
Natural Language Question → Couchbase IQ → SQL Query → Execute → Compare with Gold
```

## 📁 Folder Structure

```
evaluation_suite/
├── gold/                              # Reference data (DON'T MODIFY)
│   ├── sql/                          # Gold SQL queries
│   ├── exec_result/                  # Gold execution results
│   └── spider2lite_eval.jsonl        # Evaluation config
├── evaluate.py                        # Main evaluation script
├── couchbase_iq_results/             # YOUR OUTPUT FOLDER
│   ├── bq001.sql                     # Generated SQL files
│   ├── bq002.sql
│   ├── local003.sql
│   └── ...
└── TEST_DATA_README.md               # Testing guide
```

## 🚀 Quick Start

### Step 1: Understand the Input Format

Questions are in `../spider2-lite.jsonl`:

```json
{
  "instance_id": "bq001",
  "db": "ga360",
  "question": "For each visitor who made at least one transaction...",
  "external_knowledge": "google_analytics_sample.ga_sessions.md"
}
```

### Step 2: Set Up Database Access (for SQL mode)

```bash
# 1. Download SQLite databases
# wget and unzip to ../resource/databases/spider2-localdb/

# 2. Configure BigQuery credentials
# Edit bigquery_credential.json with your GCP credentials

# 3. Configure Snowflake credentials (optional)
# Edit snowflake_credential.json or request access
```

### Step 3: Generate SQL with Couchbase IQ

Create a Python script to generate SQL files:

```python
import json
from pathlib import Path

# Read test questions
questions = []
with open('../spider2-lite.jsonl', 'r') as f:
    for line in f:
        questions.append(json.loads(line))

# Create output directory
output_dir = Path('couchbase_iq_results')
output_dir.mkdir(exist_ok=True)

# Generate SQL for each question
for item in questions:
    instance_id = item['instance_id']
    question = item['question']
    db = item['db']
    external_knowledge = item.get('external_knowledge')
    
    # TODO: Call Couchbase IQ API/SDK here
    sql_query = generate_sql_with_couchbase_iq(
        question=question,
        database=db,
        schema=load_schema(db),
        external_docs=external_knowledge
    )
    
    # Save to file
    with open(output_dir / f"{instance_id}.sql", 'w') as f:
        f.write(sql_query)
```

### Step 4: Run Evaluation

```bash
# SQL Mode (executes your queries)
python evaluate.py --result_dir couchbase_iq_results --mode sql

# CSV Mode (if you pre-executed queries)
python evaluate.py --result_dir couchbase_iq_results --mode exec_result
```

## 📊 Evaluation Modes

### Mode 1: SQL Execution (Recommended)

You provide: `.sql` files
Evaluator: Executes SQL on databases and compares results

**Pros**: Tests end-to-end SQL correctness
**Cons**: Requires database access (costs money for BigQuery)

```bash
python evaluate.py --result_dir couchbase_iq_results --mode sql
```

### Mode 2: Pre-executed Results

You provide: `.csv` files with query results
Evaluator: Compares CSVs directly with gold results

**Pros**: No database access needed, no execution costs
**Cons**: You must execute queries separately

```bash
python evaluate.py --result_dir couchbase_iq_results --mode exec_result
```

## 🗂️ Database Schema Access

Schemas are available in JSON format:

```
../resource/databases/
├── bigquery/
│   └── {dataset}/{project}.{dataset}/{table}.json
├── snowflake/
│   └── {database}/{schema}/{table}.json
└── sqlite/
    └── {database_name}/{table}.json
```

Example schema file structure:
```json
{
  "table_name": "events",
  "columns": [
    {"name": "event_date", "type": "STRING"},
    {"name": "event_timestamp", "type": "INT64"},
    ...
  ]
}
```

## 📚 External Knowledge

Some questions reference external documentation in `../resource/documents/`:

```python
# Load external knowledge if specified
if external_knowledge:
    doc_path = Path(f"../resource/documents/{external_knowledge}")
    with open(doc_path, 'r') as f:
        context = f.read()
```

## 🧪 Testing Before Full Evaluation

Test with synthetic data first (no database needed):

```bash
# Should get 100% accuracy
python evaluate.py --result_dir test_submission_csv_perfect --mode exec_result

# Should get 0% accuracy  
python evaluate.py --result_dir test_submission_csv_wrong --mode exec_result
```

## 📈 Evaluation Metrics

The evaluator compares dataframes with:

1. **Exact Column Match**: Same columns in same order (or subset if configured)
2. **Row-wise Comparison**: Each row must match (with tolerance for floats)
3. **Optional Order Ignoring**: Some queries allow any row order
4. **Tolerance**: Numeric values matched with ±0.01 tolerance

Configuration is in `gold/spider2lite_eval.jsonl`:

```json
{
  "instance_id": "bq001",
  "condition_cols": [],      # Empty = all columns, [1,2] = only columns 1,2
  "ignore_order": true,      # true = row order doesn't matter
  "toks": "132"             # Token count reference
}
```

## 🔍 Instance ID Prefixes

- `bq*` - BigQuery (Google Cloud)
- `ga*` - Google Analytics (BigQuery)
- `local*` - SQLite (local database files)
- `sf_*` - Snowflake

## 💡 Best Practices

1. **Start Small**: Test on 10-20 instances first
2. **Use CSV Mode for Development**: Avoid BigQuery costs during dev
3. **Handle SQL Dialects**: 
   - BigQuery: Standard SQL, backticks for tables
   - Snowflake: ANSI SQL, double quotes optional
   - SQLite: Basic SQL, limited functions
4. **Check Schema First**: Load database schemas before generation
5. **Use External Docs**: Some queries require domain knowledge

## 🐛 Troubleshooting

### "No module named 'pandas'"
```bash
pip install pandas google-cloud-bigquery snowflake-connector-python
```

### BigQuery Authentication Error
```bash
export GOOGLE_APPLICATION_CREDENTIALS="bigquery_credential.json"
```

### Missing SQLite Databases
Download from: https://drive.usercontent.google.com/download?id=1coEVsCZq-Xvj9p2TnhBFoFTsY-UoYGmG

### "Error occurred while fetching data"
- Check SQL syntax for target database dialect
- Verify table names and schema match database

## 📊 Expected Results

Baseline performance (from paper):
- GPT-4 + RAG: ~35-45% accuracy
- Fine-tuned models: ~25-35% accuracy
- Rule-based: ~15-20% accuracy

## 📝 Output Format

The evaluator produces:
- **Console output**: Score, correct/total, errors
- **log.txt**: Full execution log
- **{result_dir}-ids.csv**: List of correct instance IDs

Example output:
```
Final score: 0.421, Correct examples: 230, Total examples: 547
Real score: 0.421, Correct examples: 230, Total examples: 547
```

## 🔗 Resources

- Spider2 GitHub: https://github.com/xlang-ai/Spider2
- BigQuery Setup: https://github.com/xlang-ai/Spider2/blob/main/assets/Bigquery_Guideline.md
- Snowflake Setup: https://github.com/xlang-ai/Spider2/blob/main/assets/Snowflake_Guideline.md

---

**Ready to evaluate Couchbase IQ?**

1. ✅ Generate SQL files → `couchbase_iq_results/`
2. ✅ Run: `python evaluate.py --result_dir couchbase_iq_results --mode sql`
3. ✅ Analyze results in `log.txt`

