# 🎯 START HERE: Couchbase IQ + Spider2-Lite Evaluation

## ✨ What's Been Set Up For You

I've created a **complete evaluation framework** to test Couchbase IQ against the Spider2-Lite benchmark. Everything you need is ready!

## 📚 Documentation (Read in This Order)

### 1️⃣ **SETUP.md** ⭐ START HERE
- Install Python dependencies
- Set up databases (optional)
- Verify installation
- **Time**: 5 minutes

### 2️⃣ **QUICK_REFERENCE.md** ⭐ KEEP OPEN
- Command cheat sheet
- Quick lookup table
- Common issues
- **Use**: While working

### 3️⃣ **COUCHBASE_IQ_GUIDE.md**
- Detailed integration guide
- Database schemas
- Best practices
- **Read**: Before customization

### 4️⃣ **TEST_DATA_README.md**
- How to use test data
- Expected results
- **Use**: For testing

### 5️⃣ **README_EVALUATION_SETUP.md**
- Complete overview
- Folder structure
- Evaluation flow
- **Reference**: Full details

## 🚀 Quick Start (Copy & Paste)

```bash
# 1. Navigate to evaluation suite
cd /Users/soham.sarkar/Documents/evaluations/Spider2/spider2-lite/evaluation_suite

# 2. Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install pandas tqdm

# 4. Generate test data
python3 create_synthetic_test_data.py

# 5. Test evaluation (no database needed!)
python3 evaluate.py --result_dir test_submission_csv_perfect --mode exec_result

# Expected: "Final score: 1.0" ✅
```

## 🎨 Visual Overview

```
┌──────────────────────────────────────────────────────────────┐
│  SPIDER2-LITE: 547 Text-to-SQL Test Questions               │
│  Input: Natural language question                            │
│  Output: SQL query                                           │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  YOUR COUCHBASE IQ INTEGRATION                               │
│  • Load question + database schema                           │
│  • Call Couchbase IQ API                                     │
│  • Generate SQL                                              │
│  • Save to: couchbase_iq_results/{instance_id}.sql          │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  EVALUATION                                                  │
│  • Execute SQL on databases (or use pre-executed CSVs)       │
│  • Compare with gold standard results                        │
│  • Calculate accuracy score                                  │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  RESULTS                                                     │
│  • Accuracy: X / 547 (Y%)                                    │
│  • Per-instance breakdown                                    │
│  • Error analysis                                            │
└──────────────────────────────────────────────────────────────┘
```

## 📁 What You Have Now

```
evaluation_suite/
│
├── 📘 DOCS (5 comprehensive guides)
│   ├── START_HERE.md                 ⭐ THIS FILE
│   ├── SETUP.md                      ⭐ Read first
│   ├── QUICK_REFERENCE.md            ⭐ Keep open
│   ├── COUCHBASE_IQ_GUIDE.md        
│   ├── TEST_DATA_README.md
│   └── README_EVALUATION_SETUP.md
│
├── 🔧 SCRIPTS (ready to use)
│   ├── create_synthetic_test_data.py        # Run to generate tests
│   ├── couchbase_iq_integration_template.py # ⭐ Customize this
│   └── evaluate.py                           # Evaluation engine
│
├── 🧪 TEST DATA (4 test folders - auto-generated)
│   ├── test_submission_csv_perfect/   # 100% accuracy
│   ├── test_submission_csv_wrong/     # 0% accuracy
│   ├── test_submission_sql_perfect/   # 100% accuracy
│   └── test_submission_sql_mixed/     # ~50% accuracy
│
└── 🎯 YOUR WORK
    └── couchbase_iq_results/          # Create this, put your SQLs here
```

## 🎯 Your Mission

### Goal
Evaluate Couchbase IQ's text-to-SQL performance on Spider2-Lite benchmark

### Input
547 natural language questions → SQL queries

### Output
Accuracy score (% of correct SQL queries)

### Baseline
- State-of-the-art (GPT-4): ~35-45%
- Your goal: Beat this! 🏆

## 🔥 Three Ways to Evaluate

### Option 1: CSV Mode (FREE, Easy) ⭐ Recommended for Dev
```bash
# You provide: {instance_id}.csv files (pre-executed results)
# Evaluator: Compares CSVs with gold results
python3 evaluate.py --result_dir couchbase_iq_results --mode exec_result
```
**Pros**: No database setup, free, fast
**Cons**: You must execute SQL separately

### Option 2: SQL Mode - SQLite Only (FREE)
```bash
# You provide: {instance_id}.sql files
# Evaluator: Executes on SQLite databases (~100 instances)
python3 evaluate.py --result_dir couchbase_iq_results --mode sql
```
**Pros**: Automatic execution, free
**Cons**: Only ~100 instances (not full benchmark)

### Option 3: SQL Mode - Full (Costs $$$)
```bash
# You provide: {instance_id}.sql files  
# Evaluator: Executes on ALL databases (547 instances)
python3 evaluate.py --result_dir couchbase_iq_results --mode sql
```
**Pros**: Full benchmark, automatic
**Cons**: BigQuery costs ~$5-50

## ⚡ One-Minute Test

```bash
cd /Users/soham.sarkar/Documents/evaluations/Spider2/spider2-lite/evaluation_suite

# Generate test data
python3 create_synthetic_test_data.py

# Run test (no DB needed!)
python3 evaluate.py --result_dir test_submission_csv_perfect --mode exec_result

# Should output: "Final score: 1.0" ✅
```

If this works, you're ready! 🎉

## 📝 Customization Steps

### 1. Edit Integration Template

Open: `couchbase_iq_integration_template.py`

Find the function:
```python
def generate_sql_with_couchbase_iq(question, database, schema, external_docs):
    # TODO: Replace this stub with your Couchbase IQ API call
    ...
```

Replace with:
```python
def generate_sql_with_couchbase_iq(question, database, schema, external_docs):
    # Your Couchbase IQ integration
    from couchbase_iq import Client  # Your SDK
    client = Client(api_key="your-key")
    
    result = client.generate_sql(
        question=question,
        schema=schema,
        context=external_docs
    )
    
    return result.sql
```

### 2. Run Integration Script

```bash
python3 couchbase_iq_integration_template.py
```

This generates: `couchbase_iq_results/{instance_id}.sql` for each question

### 3. Evaluate

```bash
# CSV mode (free)
python3 evaluate.py --result_dir couchbase_iq_results --mode exec_result

# SQL mode (requires DB)
python3 evaluate.py --result_dir couchbase_iq_results --mode sql
```

## 🎓 Learning Path

1. **Understand** the benchmark (10 min)
   - Read: `SETUP.md` 
   - Explore: `../spider2-lite.jsonl`

2. **Test** the framework (5 min)
   - Generate test data
   - Run test evaluation
   - Verify 100% accuracy

3. **Integrate** Couchbase IQ (30 min)
   - Edit template script
   - Test on 5 instances
   - Debug integration

4. **Evaluate** (1-2 hours)
   - Run on all 547 instances
   - Analyze results
   - Iterate and improve

## 🆘 Need Help?

### Quick Questions
→ Read `QUICK_REFERENCE.md` (command cheat sheet)

### Setup Issues
→ Read `SETUP.md` (installation guide)

### Integration Details
→ Read `COUCHBASE_IQ_GUIDE.md` (detailed guide)

### Test Data
→ Read `TEST_DATA_README.md` (testing guide)

### Full Overview
→ Read `README_EVALUATION_SETUP.md` (complete details)

## ✅ Pre-Flight Checklist

Before full evaluation:

- [ ] Read `SETUP.md`
- [ ] Python 3.7+ installed
- [ ] Dependencies installed: `pip install pandas tqdm`
- [ ] Test data generated: `python3 create_synthetic_test_data.py`
- [ ] Test evaluation passed: 100% on `test_submission_csv_perfect`
- [ ] Integration template customized
- [ ] Tested on 5-10 instances
- [ ] Ready for full evaluation!

## 🎉 You're All Set!

Everything is prepared. Just:

1. ✅ Follow `SETUP.md` to install dependencies (5 min)
2. ✅ Run test evaluation (1 min)
3. ✅ Customize integration template (30 min)
4. ✅ Evaluate Couchbase IQ (1-2 hours)

**Let's see how Couchbase IQ performs! 🚀**

---

**Questions?** All documentation is in this folder.
**Ready?** Start with `SETUP.md`!

