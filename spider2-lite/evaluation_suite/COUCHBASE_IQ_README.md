# Couchbase IQ Spider2-Lite Evaluation

Complete integration for evaluating Couchbase IQ on Spider2-Lite benchmark.

## 🚀 Quick Start

### 1. Configure Couchbase Credentials

Edit `couchbase_config.json`:

```json
{
  "couchbase": {
    "connection_string": "couchbase://localhost",
    "username": "Administrator",
    "password": "your_password",
    "query_endpoint": "http://localhost:8093/query/service"
  },
  "couchbase_iq": {
    "natural_cred": "your_capella_username:password",
    "natural_orgid": "your_org_id"
  }
}
```

Or edit directly in `couchbase_iq_spider2_evaluator.py`:
- Lines 17-21: Couchbase connection settings
- Lines 24-25: Couchbase IQ credentials

### 2. Run the Evaluator

```bash
cd /Users/soham.sarkar/Documents/evaluations/Spider2/spider2-lite/evaluation_suite

# Test on 10 questions first
python3 couchbase_iq_spider2_evaluator.py

# For all 547 questions, edit the script and set MAX_QUESTIONS = None
```

### 3. Check Results

Results are saved in:
```
couchbase_iq_results/
├── sql/              # Generated SQL files
│   ├── bq001.sql
│   ├── bq002.sql
│   └── ...
└── csv/              # Execution results
    ├── bq001.csv
    ├── bq002.csv
    └── ...
```

### 4. Run Evaluation

```bash
# Option 1: Evaluate using CSV results (recommended)
python3 evaluate.py --result_dir couchbase_iq_results/csv --mode exec_result

# Option 2: Evaluate using SQL (requires database access)
python3 evaluate.py --result_dir couchbase_iq_results/sql --mode sql
```

## 📊 What It Does

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Load Spider2-Lite Questions (547 total)                 │
│    - Natural language questions                             │
│    - Database context                                       │
│    - External knowledge (if any)                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Generate SQL with Couchbase IQ                          │
│    - Call USING AI WITH {...} <question>                   │
│    - Get generated_statement from response                  │
│    - Save to sql/{instance_id}.sql                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Execute SQL on Couchbase                                 │
│    - POST to /query/service                                 │
│    - Get results array from response                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Convert JSON Results to CSV                              │
│    - Flatten nested JSON structures                         │
│    - Create CSV with headers                                │
│    - Save to csv/{instance_id}.csv                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Ready for Evaluation!                                    │
│    - Compare with gold standard results                     │
│    - Calculate accuracy score                               │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Configuration Options

In `couchbase_iq_spider2_evaluator.py`:

```python
# Test on subset
MAX_QUESTIONS = 10  # Process only 10 questions

# Process all questions
MAX_QUESTIONS = None  # Process all 547 questions

# Control what to save
save_sql=True,      # Save generated SQL files
execute_sql=True,   # Execute SQL and save CSV results
```

## 📝 Output Format

### SQL Files
```sql
-- bq001.sql
SELECT fullvisitorid, 
       DATE_DIFF(PARSE_DATE('%Y%m%d', date_transactions), 
                 PARSE_DATE('%Y%m%d', date_first_visit), DAY) AS time,
       device_transaction
FROM visits_transactions
ORDER BY fullvisitorid;
```

### CSV Files
```csv
fullvisitorid,time,device_transaction
0014253006455543633,0,desktop
0015950283479889703,4,mobile
...
```

## 🎯 Evaluation Modes

### Mode 1: CSV Evaluation (Recommended)
```bash
python3 evaluate.py --result_dir couchbase_iq_results/csv --mode exec_result
```

**Pros:**
- ✅ Fast - no database execution
- ✅ Free - no BigQuery costs
- ✅ You already have the results!

**Cons:**
- ❌ Requires prior SQL execution (which this script does for you)

### Mode 2: SQL Evaluation
```bash
python3 evaluate.py --result_dir couchbase_iq_results/sql --mode sql
```

**Pros:**
- ✅ Tests actual SQL execution
- ✅ Validates SQL syntax

**Cons:**
- ❌ Requires database access
- ❌ BigQuery costs money (~$5-50)
- ❌ Slower execution

## 📈 Expected Performance

Based on Spider2 benchmarks:

| Method | Accuracy | Notes |
|--------|----------|-------|
| GPT-4 + RAG | 35-45% | State-of-the-art |
| Fine-tuned models | 25-35% | Specialized |
| Rule-based | 15-20% | Baseline |
| **Couchbase IQ** | **?%** | Let's find out! |

## 🔍 Instance Types

The script handles all Spider2-Lite instance types:

| Prefix | Database | Count | Example |
|--------|----------|-------|---------|
| `bq*` | BigQuery | ~350 | bq001.sql |
| `ga*` | Google Analytics (BQ) | ~50 | ga010.sql |
| `local*` | SQLite | ~100 | local003.sql |
| `sf_*` | Snowflake | ~47 | sf_bq026.sql |

**Note:** For `local*` and `sf_*` instances, you need to:
1. Import data into Couchbase (like in testimportbird.py)
2. Or adapt the script to use external databases

## 🐛 Troubleshooting

### "Error generating SQL"
- Check Couchbase IQ credentials in config
- Verify `NATURAL_CRED` and `NATURAL_ORGID` are correct
- Check network connectivity to Capella

### "Error executing SQL"
- Verify Couchbase is running: `http://localhost:8093`
- Check authentication credentials
- Ensure keyspaces/buckets exist

### Empty CSV files
- SQL returned no results (might be correct!)
- Or SQL execution failed - check console output

### "Rate limit exceeded"
- Increase `time.sleep()` delay in the script
- Process in smaller batches

## 💡 Tips

1. **Start small**: Test on 5-10 questions first
   ```python
   MAX_QUESTIONS = 10
   ```

2. **Check SQL first**: Review generated SQL before execution
   ```python
   save_sql=True,
   execute_sql=False,  # Don't execute yet
   ```

3. **Monitor progress**: Watch console output for errors

4. **Batch processing**: For 547 questions, consider batching:
   ```python
   questions = load_questions()[0:100]   # First 100
   questions = load_questions()[100:200] # Next 100
   ```

## 📊 Output Example

```
================================================================================
Couchbase IQ + Spider2-Lite Evaluation
================================================================================

✓ Output directories created:
  SQL: couchbase_iq_results/sql
  CSV: couchbase_iq_results/csv

Processing questions...
--------------------------------------------------------------------------------

[1/547] bq011
  Question: How many distinct pseudo users had positive engagement time...
  Database: ga4
  Generating SQL with Couchbase IQ...
  ✓ Generated SQL (245 chars)
  ✓ Saved SQL: bq011.sql
  Executing SQL...
  ✓ Executed SQL (1 rows)
  ✓ Saved CSV: bq011.csv

[2/547] bq010
  Question: Find the top-selling product among customers who bought...
  Database: ga360
  Generating SQL with Couchbase IQ...
  ✓ Generated SQL (312 chars)
  ✓ Saved SQL: bq010.sql
  Executing SQL...
  ✓ Executed SQL (1 rows)
  ✓ Saved CSV: bq010.csv

...

Summary:
  Total questions: 547
  SQL generated: 547
  SQL saved: 547
  CSV saved: 547
  Failed: 0

Next Steps:
  1. Review generated files
  2. Run evaluation:
     python3 evaluate.py --result_dir couchbase_iq_results/csv --mode exec_result
```

## 🔗 Related Files

- `testimportbird.py` - Your existing Couchbase IQ test script
- `evaluate.py` - Spider2-Lite evaluation engine
- `spider2-lite.jsonl` - Benchmark questions
- `gold/` - Reference answers

## 🎓 Understanding the Code

### Key Functions

1. **`CouchbaseIQAPI.generate_sql()`**
   - Calls Couchbase IQ to generate SQL
   - Uses `USING AI WITH {...}` statement
   - Returns generated SQL string

2. **`exec_sql()`**
   - Executes SQL on Couchbase
   - Returns JSON results array

3. **`json_to_csv()`**
   - Converts JSON results to CSV format
   - Handles nested structures
   - Creates proper CSV with headers

4. **`process_question()`**
   - Orchestrates the full pipeline
   - Handles errors gracefully
   - Saves both SQL and CSV

## 🚦 Next Steps

1. ✅ Configure credentials in script or config file
2. ✅ Run on test subset: `MAX_QUESTIONS = 10`
3. ✅ Review generated SQL and CSV files
4. ✅ Run evaluation: `python3 evaluate.py --result_dir couchbase_iq_results/csv --mode exec_result`
5. ✅ Analyze results and iterate!

---

**Ready to evaluate Couchbase IQ? 🚀**

Run: `python3 couchbase_iq_spider2_evaluator.py`

