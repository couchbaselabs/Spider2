# Spider2-Lite + Couchbase IQ: Quick Reference Card

## 📁 Folder Structure You Need

```
evaluation_suite/
├── couchbase_iq_results/          # CREATE THIS - Your SQL outputs
│   ├── bq001.sql
│   ├── bq002.sql
│   └── ...
├── gold/                           # PROVIDED - Reference answers
│   ├── sql/                       # Gold SQL queries
│   └── exec_result/               # Gold execution results
├── evaluate.py                     # PROVIDED - Evaluation script
└── couchbase_iq_integration_template.py  # TEMPLATE - Customize this
```

## 🚀 Quick Start (3 Steps)

### 1️⃣ Generate SQL files

```python
# Customize couchbase_iq_integration_template.py
# Replace the stub with your Couchbase IQ API call
python3 couchbase_iq_integration_template.py
```

### 2️⃣ Run evaluation

```bash
# SQL mode (requires DB access)
python3 evaluate.py --result_dir couchbase_iq_results --mode sql

# CSV mode (no DB needed - if you pre-executed)
python3 evaluate.py --result_dir couchbase_iq_results --mode exec_result
```

### 3️⃣ Check results

Results in: `log.txt` and console output

## 📊 Two Evaluation Modes

| Mode | Input | Pros | Cons | Command |
|------|-------|------|------|---------|
| **SQL** | `.sql` files | Tests actual SQL execution | Requires DB access, costs $ | `--mode sql` |
| **CSV** | `.csv` files | No DB needed, free | Must execute SQL separately | `--mode exec_result` |

## 📝 Input Data Format

Questions in `../spider2-lite.jsonl`:

```json
{
  "instance_id": "bq001",           // File name without extension
  "db": "ga360",                    // Database identifier
  "question": "Natural language...", // What to convert to SQL
  "external_knowledge": "doc.md"    // Optional context file
}
```

## 📤 Output Format

### SQL Mode Output:
```
couchbase_iq_results/
├── bq001.sql      # Your generated SQL
├── bq002.sql
└── ...
```

### CSV Mode Output:
```
couchbase_iq_results/
├── bq001.csv      # Executed results
├── bq002.csv
└── ...
```

## 🎯 Instance ID Prefixes

| Prefix | Database | Example | Notes |
|--------|----------|---------|-------|
| `bq*` | BigQuery | `bq001.sql` | Google Cloud, costs $ |
| `ga*` | BigQuery (GA) | `ga010.sql` | Analytics data |
| `local*` | SQLite | `local003.sql` | Free, local files |
| `sf_*` | Snowflake | `sf_bq026.sql` | Requires account |

## 🧪 Test Before Real Eval

```bash
# Test with synthetic data (no DB needed!)
cd evaluation_suite

# Should get 100% accuracy
python3 evaluate.py --result_dir test_submission_csv_perfect --mode exec_result

# Should get 0% accuracy
python3 evaluate.py --result_dir test_submission_csv_wrong --mode exec_result
```

## 🔧 Couchbase IQ Integration Points

Edit `couchbase_iq_integration_template.py`:

```python
def generate_sql_with_couchbase_iq(question, database, schema, external_docs):
    # Replace this stub:
    
    # Option 1: REST API
    response = requests.post("https://api.couchbase-iq.com/generate", 
                            json={"question": question, "schema": schema})
    return response.json()["sql"]
    
    # Option 2: SDK
    from couchbase_iq import Client
    client = Client(api_key="...")
    return client.generate_sql(question, schema)
```

## 📈 What Gets Evaluated

✅ Column names match
✅ Row values match (±0.01 for floats)
✅ Row order (if required)
✅ All expected columns present

## 🗂️ Helper Files Created

| File | Purpose |
|------|---------|
| `COUCHBASE_IQ_GUIDE.md` | Comprehensive integration guide |
| `QUICK_REFERENCE.md` | This file - quick lookup |
| `TEST_DATA_README.md` | How to test with synthetic data |
| `create_synthetic_test_data.py` | Generates test submissions |
| `couchbase_iq_integration_template.py` | Template to customize |

## 💡 Pro Tips

1. **Start small**: Test on 5-10 questions first
2. **Use CSV mode for dev**: Avoid BigQuery costs
3. **Check external_knowledge**: Some questions need extra docs
4. **Load schemas**: Schema files in `../resource/databases/`
5. **Test syntax**: Each DB has different SQL dialect

## 🐛 Common Issues

| Error | Solution |
|-------|----------|
| `No module named 'pandas'` | `pip install pandas` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Set in `bigquery_credential.json` |
| `Error occurred while fetching data` | Check SQL syntax for target DB |
| `No data found` | Query returned empty - check logic |

## 📞 Need Help?

1. Read `COUCHBASE_IQ_GUIDE.md` for detailed walkthrough
2. Check `TEST_DATA_README.md` for testing instructions
3. Run synthetic tests first: `python3 create_synthetic_test_data.py`
4. Review example submissions in `example_submission_folder/`

## 🎓 Expected Performance

- **State-of-the-art**: ~35-45% (GPT-4 + RAG)
- **Fine-tuned models**: ~25-35%
- **Rule-based**: ~15-20%

## ⚡ Quick Commands Cheat Sheet

```bash
# Generate test data
python3 create_synthetic_test_data.py

# Test evaluation (CSV mode - no DB)
python3 evaluate.py --result_dir test_submission_csv_perfect --mode exec_result

# Run your Couchbase IQ integration
python3 couchbase_iq_integration_template.py

# Evaluate Couchbase IQ results (SQL mode)
python3 evaluate.py --result_dir couchbase_iq_results --mode sql

# View results
cat log.txt
```

---

**Ready? Start here:**
1. ✅ Run `python3 create_synthetic_test_data.py`
2. ✅ Test with `python3 evaluate.py --result_dir test_submission_csv_perfect --mode exec_result`
3. ✅ Customize `couchbase_iq_integration_template.py`
4. ✅ Generate SQLs and evaluate!

