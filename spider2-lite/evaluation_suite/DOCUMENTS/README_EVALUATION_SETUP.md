# Spider2-Lite Evaluation with Couchbase IQ - Complete Setup

## 📋 Summary

I've created a complete evaluation framework for testing **Couchbase IQ** against the **Spider2-Lite** text-to-SQL benchmark. Everything is ready to use!

## 🎁 What's Been Created

### 📄 Documentation Files

| File | Purpose | Start Here? |
|------|---------|-------------|
| **SETUP.md** | Installation & environment setup | ⭐ YES - Start here |
| **QUICK_REFERENCE.md** | Quick command cheat sheet | ⭐ YES - For lookup |
| **COUCHBASE_IQ_GUIDE.md** | Detailed integration guide | Read after setup |
| **TEST_DATA_README.md** | How to use test data | For testing |
| **README_EVALUATION_SETUP.md** | This file - overview | Overview |

### 🔧 Python Scripts

| Script | Purpose | Modify? |
|--------|---------|---------|
| **create_synthetic_test_data.py** | Generates test submissions | No - run as-is |
| **couchbase_iq_integration_template.py** | Template for your integration | ⭐ YES - Customize this |
| **evaluate.py** | Main evaluation script | No - provided |

### 📁 Test Data Folders (Auto-generated)

| Folder | Content | Expected Score |
|--------|---------|----------------|
| `test_submission_csv_perfect/` | Perfect CSV matches | 100% ✅ |
| `test_submission_csv_wrong/` | Wrong CSV data | 0% ❌ |
| `test_submission_sql_perfect/` | Perfect SQL matches | 100% ✅ |
| `test_submission_sql_mixed/` | Mixed correct/wrong | ~50% ⚖️ |

### 📂 Your Output Folder

| Folder | Purpose | You Create |
|--------|---------|------------|
| `couchbase_iq_results/` | Your generated SQL/CSV files | ⭐ YES |

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies (1 min)

```bash
cd /Users/soham.sarkar/Documents/evaluations/Spider2/spider2-lite/evaluation_suite

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install pandas tqdm
```

### 2. Generate Test Data (1 min)

```bash
python3 create_synthetic_test_data.py
```

**Output**: Creates 4 test folders with synthetic data

### 3. Test Evaluation - No Database Needed! (1 min)

```bash
# Test with perfect data (should get 100%)
python3 evaluate.py --result_dir test_submission_csv_perfect --mode exec_result
```

**Expected Output**:
```
Final score: 1.0, Correct examples: 4, Total examples: 4
```

### 4. Customize Integration Template (2 min)

Edit `couchbase_iq_integration_template.py`:

```python
def generate_sql_with_couchbase_iq(question, database, schema, external_docs):
    # Replace stub with your Couchbase IQ call
    # Example:
    from your_couchbase_iq_sdk import Client
    client = Client(api_key="your-key")
    return client.generate_sql(
        question=question,
        schema=schema,
        context=external_docs
    )
```

### 5. Run Your Evaluation

```bash
# Generate SQL files
python3 couchbase_iq_integration_template.py

# Evaluate (CSV mode - no DB required)
python3 evaluate.py --result_dir couchbase_iq_results --mode exec_result

# Or SQL mode (requires DB access)
python3 evaluate.py --result_dir couchbase_iq_results --mode sql
```

## 📊 Understanding the Evaluation

### Input: Spider2-Lite Questions (547 total)

Located in: `../spider2-lite.jsonl`

```json
{
  "instance_id": "bq001",
  "db": "ga360", 
  "question": "For each visitor who made at least one transaction...",
  "external_knowledge": "google_analytics_sample.ga_sessions.md"
}
```

### Your Task: Generate SQL

For each question, generate SQL and save as `{instance_id}.sql`:

```
couchbase_iq_results/
├── bq001.sql
├── bq002.sql
├── local003.sql
└── ...
```

### Evaluation: Compare Results

The evaluator:
1. Executes your SQL (or reads your CSVs)
2. Compares with gold standard results
3. Returns accuracy score

## 🎯 Two Evaluation Modes

### Mode 1: SQL Execution (Automatic)

```bash
python3 evaluate.py --result_dir couchbase_iq_results --mode sql
```

- **Input**: `.sql` files
- **Process**: Executes on real databases
- **Output**: Accuracy score
- **Requires**: Database access (BigQuery costs $$$)

### Mode 2: CSV Results (Manual)

```bash
python3 evaluate.py --result_dir couchbase_iq_results --mode exec_result
```

- **Input**: `.csv` files (pre-executed results)
- **Process**: Direct comparison
- **Output**: Accuracy score
- **Requires**: Nothing (free!)

**Recommendation**: Use CSV mode during development to avoid costs.

## 📁 Complete Folder Structure

```
evaluation_suite/
│
├── 📘 DOCUMENTATION
│   ├── SETUP.md                          # ⭐ Start here: Install & setup
│   ├── QUICK_REFERENCE.md                # ⭐ Command cheat sheet
│   ├── COUCHBASE_IQ_GUIDE.md            # Detailed integration guide
│   ├── TEST_DATA_README.md               # Test data usage
│   └── README_EVALUATION_SETUP.md        # This file
│
├── 🔧 SCRIPTS
│   ├── create_synthetic_test_data.py     # Generates test data
│   ├── couchbase_iq_integration_template.py  # ⭐ Customize this
│   └── evaluate.py                       # Evaluation script (provided)
│
├── 🧪 TEST DATA (auto-generated)
│   ├── test_submission_csv_perfect/      # 100% accuracy test
│   ├── test_submission_csv_wrong/        # 0% accuracy test
│   ├── test_submission_sql_perfect/      # 100% accuracy test
│   └── test_submission_sql_mixed/        # ~50% accuracy test
│
├── 🎯 YOUR OUTPUT
│   └── couchbase_iq_results/             # ⭐ Create this folder
│       ├── bq001.sql                     # Your generated SQL
│       ├── bq002.sql
│       └── ...
│
├── 📊 REFERENCE DATA (provided)
│   └── gold/
│       ├── sql/                          # Gold SQL queries
│       ├── exec_result/                  # Gold results
│       └── spider2lite_eval.jsonl        # Eval config
│
└── 🔑 CREDENTIALS (you provide)
    ├── bigquery_credential.json          # For BigQuery
    └── snowflake_credential.json         # For Snowflake
```

## 🎓 Evaluation Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Load Questions                                           │
│    spider2-lite.jsonl (547 questions)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Generate SQL with Couchbase IQ                           │
│    • Load database schemas                                   │
│    • Load external knowledge                                │
│    • Call Couchbase IQ API                                  │
│    • Save {instance_id}.sql                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Evaluate                                                 │
│    • Execute SQL on databases (or load CSVs)                │
│    • Compare with gold results                              │
│    • Calculate accuracy                                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Results                                                  │
│    • Accuracy score                                         │
│    • Per-instance results                                   │
│    • Error analysis                                         │
└─────────────────────────────────────────────────────────────┘
```

## 🔍 Instance Distribution

| Prefix | Database | Count | Cost | Notes |
|--------|----------|-------|------|-------|
| `bq*` | BigQuery | ~350 | $$$ | Google Cloud |
| `ga*` | BigQuery | ~50 | $$$ | Analytics |
| `local*` | SQLite | ~100 | Free | Local files |
| `sf_*` | Snowflake | ~47 | $ | Test account |
| **Total** | - | **547** | - | Full benchmark |

## 💡 Best Practices

### For Development
1. ✅ Use CSV mode (free, fast)
2. ✅ Test on 5-10 instances first
3. ✅ Use synthetic test data
4. ✅ Focus on `local*` instances (SQLite, free)

### For Production
1. ✅ Set up all databases
2. ✅ Use SQL mode (full automation)
3. ✅ Run on all 547 instances
4. ✅ Budget for BigQuery costs (~$5-50)

## 📈 Expected Performance

Based on Spider2 paper benchmarks:

| Method | Accuracy | Notes |
|--------|----------|-------|
| GPT-4 + RAG | 35-45% | State-of-the-art |
| Fine-tuned T5 | 25-35% | Specialized models |
| Rule-based | 15-20% | Baseline |
| **Your Goal** | **?%** | Test Couchbase IQ! |

## 🎯 Your Next Steps

1. **Read** `SETUP.md` - Install dependencies
2. **Run** `python3 create_synthetic_test_data.py`
3. **Test** with CSV mode (no DB needed)
4. **Edit** `couchbase_iq_integration_template.py`
5. **Generate** SQL with Couchbase IQ
6. **Evaluate** your results
7. **Analyze** performance

## 📞 Questions?

- **Setup issues?** → Read `SETUP.md`
- **Quick commands?** → Read `QUICK_REFERENCE.md`
- **Integration details?** → Read `COUCHBASE_IQ_GUIDE.md`
- **Testing?** → Read `TEST_DATA_README.md`

## ✅ Validation Checklist

Before full evaluation:

- [ ] Python 3.7+ installed
- [ ] Dependencies installed (pandas, tqdm)
- [ ] Test data generated (4 folders)
- [ ] Test evaluation runs (100% on perfect data)
- [ ] Template script runs (creates placeholder SQLs)
- [ ] Couchbase IQ integration customized
- [ ] Database credentials configured (if using SQL mode)
- [ ] Output folder created (`couchbase_iq_results/`)

## 🎉 You're Ready!

Everything is set up. Just follow `SETUP.md` to install dependencies and you can start evaluating Couchbase IQ against Spider2-Lite!

---

**Created**: October 31, 2025
**Location**: `/Users/soham.sarkar/Documents/evaluations/Spider2/spider2-lite/evaluation_suite/`
**Purpose**: Evaluate Couchbase IQ's text-to-SQL capabilities on the Spider2-Lite benchmark

