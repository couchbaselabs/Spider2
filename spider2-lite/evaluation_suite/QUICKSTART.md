# 🚀 Quick Start: Couchbase IQ Spider2 Evaluation

## ⚡ TL;DR (1 Minute)

```bash
cd /Users/soham.sarkar/Documents/evaluations/Spider2/spider2-lite/evaluation_suite

# 1. Update config
nano couchbase_config.json  # Add your credentials

# 2. Run evaluation (generates SQL + executes + saves CSV)
python3 couchbase_iq_spider2_evaluator.py

# 3. Evaluate results
python3 evaluate.py --result_dir couchbase_iq_results/csv --mode exec_result
```

## 📋 What You Have

### New Files Created
- ✅ `couchbase_iq_spider2_evaluator.py` - Main script (generates SQL, executes, saves CSV)
- ✅ `couchbase_config.json` - Configuration file
- ✅ `COUCHBASE_IQ_README.md` - Detailed guide
- ✅ `QUICKSTART.md` - This file

### From Before
- ✅ `create_synthetic_test_data.py` - Test data generator
- ✅ `evaluate.py` - Spider2 evaluation engine
- ✅ Test folders with synthetic data

## 🔧 Setup (2 Minutes)

### Step 1: Configure Credentials

Edit `couchbase_config.json`:

```json
{
  "couchbase": {
    "username": "Administrator",
    "password": "your_password",
    "query_endpoint": "http://localhost:8093/query/service"
  },
  "couchbase_iq": {
    "natural_cred": "your_username:password",
    "natural_orgid": "your_org_id"
  },
  "evaluation": {
    "max_questions": 10
  }
}
```

### Step 2: Test on Small Subset

```bash
# Edit config to test on 10 questions
nano couchbase_config.json
# Set: "max_questions": 10

# Run
python3 couchbase_iq_spider2_evaluator.py
```

Expected output:
```
================================================================================
Couchbase IQ + Spider2-Lite Evaluation
================================================================================

✓ Loading config from: couchbase_config.json

✓ Output directories created:
  SQL: couchbase_iq_results/sql
  CSV: couchbase_iq_results/csv

Processing questions...
--------------------------------------------------------------------------------

[1/10] bq011
  Question: How many distinct pseudo users had positive engagement time...
  Database: ga4
  Generating SQL with Couchbase IQ...
  ✓ Generated SQL (245 chars)
  ✓ Saved SQL: bq011.sql
  Executing SQL...
  ✓ Executed SQL (1 rows)
  ✓ Saved CSV: bq011.csv

...

Summary:
  Total questions: 10
  SQL generated: 10
  SQL saved: 10
  CSV saved: 10
  Failed: 0
```

### Step 3: Evaluate Results

```bash
# Evaluate using CSV results
python3 evaluate.py --result_dir couchbase_iq_results/csv --mode exec_result
```

Expected output:
```
Final score: 0.XX, Correct examples: X, Total examples: 10
```

## 📊 Full Evaluation (All 547 Questions)

Once testing looks good:

```json
// In couchbase_config.json
{
  "evaluation": {
    "max_questions": null  // Process all questions
  }
}
```

```bash
# Run full evaluation (will take time!)
python3 couchbase_iq_spider2_evaluator.py

# Evaluate
python3 evaluate.py --result_dir couchbase_iq_results/csv --mode exec_result
```

## 🎯 What The Script Does

```
Load Questions → Generate SQL (Couchbase IQ) → Execute SQL → Save CSV → Ready for Eval
     547          USING AI WITH {...}          POST /query    Convert     Compare
  questions       Returns SQL string           JSON results   to CSV      with gold
```

## 📁 Output Structure

```
couchbase_iq_results/
├── sql/                    # Generated SQL files
│   ├── bq001.sql
│   ├── bq002.sql
│   └── ...
└── csv/                    # Execution results
    ├── bq001.csv
    ├── bq002.csv
    └── ...
```

## 🔍 Check Results

```bash
# View generated SQL
cat couchbase_iq_results/sql/bq001.sql

# View execution results
cat couchbase_iq_results/csv/bq001.csv

# Count files
ls couchbase_iq_results/sql | wc -l
ls couchbase_iq_results/csv | wc -l
```

## 🐛 Common Issues

### "Error generating SQL"
```bash
# Check credentials in couchbase_config.json
# Verify natural_cred and natural_orgid are correct
```

### "Error executing SQL"
```bash
# Check Couchbase is running
curl http://localhost:8093

# Verify credentials
# Check if keyspaces/buckets exist
```

### "Config file not found"
```bash
# Script will use defaults
# Either:
# 1. Create couchbase_config.json
# 2. Or edit values in couchbase_iq_spider2_evaluator.py (lines 34-51)
```

## 💡 Configuration Options

```json
{
  "evaluation": {
    "max_questions": 10,        // Limit to 10 questions (or null for all)
    "save_sql": true,           // Save generated SQL files
    "execute_sql": true,        // Execute SQL and save CSV
    "delay_between_requests": 0.5  // Delay between API calls (seconds)
  }
}
```

## 📈 Expected Performance

| Method | Accuracy |
|--------|----------|
| GPT-4 + RAG | 35-45% |
| Fine-tuned | 25-35% |
| Couchbase IQ | **?%** |

## 🎓 Understanding the Flow

### 1. Generate SQL with Couchbase IQ
```python
# From your testimportbird.py
USING AI WITH {"keyspaces":["db_name"], "execute":false} <question>
# Returns: {"generated_statement": "SELECT ..."}
```

### 2. Execute SQL
```python
# POST to /query/service with SQL
# Returns: {"results": [{"col1": "val1", ...}, ...]}
```

### 3. Convert to CSV
```python
# Flatten JSON and write as CSV
# fullvisitorid,time,device_transaction
# 123,0,desktop
```

### 4. Evaluate
```python
# Compare with gold/exec_result/{instance_id}.csv
# Calculate accuracy
```

## 🔗 Related Documentation

- **COUCHBASE_IQ_README.md** - Comprehensive guide with examples
- **testimportbird.py** - Your original Couchbase IQ test script
- **Spider2/README.md** - Spider2 benchmark documentation

## ✅ Checklist

- [ ] Couchbase is running (`http://localhost:8093`)
- [ ] `couchbase_config.json` has correct credentials
- [ ] Config set to `max_questions: 10` for testing
- [ ] Run `python3 couchbase_iq_spider2_evaluator.py`
- [ ] Check output in `couchbase_iq_results/`
- [ ] Run evaluation: `python3 evaluate.py --result_dir couchbase_iq_results/csv --mode exec_result`
- [ ] Review results
- [ ] Set `max_questions: null` for full evaluation

## 🎉 Ready to Go!

```bash
# Start here
cd /Users/soham.sarkar/Documents/evaluations/Spider2/spider2-lite/evaluation_suite

# Configure
nano couchbase_config.json

# Run
python3 couchbase_iq_spider2_evaluator.py

# Evaluate
python3 evaluate.py --result_dir couchbase_iq_results/csv --mode exec_result
```

**That's it! You're evaluating Couchbase IQ on Spider2-Lite! 🚀**

