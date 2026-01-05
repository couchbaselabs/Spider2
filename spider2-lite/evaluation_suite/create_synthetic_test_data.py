#!/usr/bin/env python3
"""
Script to create synthetic test data for Spider2-Lite evaluation.
This creates both correct and incorrect examples to test the evaluation framework.
"""

import os
import shutil
import json
import csv
from pathlib import Path

# Get the directory of this script
SCRIPT_DIR = Path(__file__).parent
GOLD_SQL_DIR = SCRIPT_DIR / "gold" / "sql"
GOLD_RESULT_DIR = SCRIPT_DIR / "gold" / "exec_result"
EVAL_CONFIG = SCRIPT_DIR / "gold" / "spider2lite_eval.jsonl"

def load_eval_config():
    """Load evaluation configuration"""
    config = {}
    with open(EVAL_CONFIG, 'r') as f:
        for line in f:
            item = json.loads(line.strip())
            config[item['instance_id']] = item
    return config

def create_test_folders():
    """Create test submission folders"""
    folders = {
        'test_submission_sql_perfect': 'SQL mode - Perfect match (should score 100%)',
        'test_submission_sql_mixed': 'SQL mode - Mixed correct/incorrect',
        'test_submission_csv_perfect': 'CSV mode - Perfect match (should score 100%)',
        'test_submission_csv_wrong': 'CSV mode - Wrong answers (should score 0%)',
    }
    
    for folder, description in folders.items():
        folder_path = SCRIPT_DIR / folder
        if folder_path.exists():
            shutil.rmtree(folder_path)
        folder_path.mkdir()
        print(f"✓ Created {folder}: {description}")
    
    return folders.keys()

def get_available_gold_instances(limit=10):
    """Get list of available gold instances across all platforms"""
    instances = {
        'bq': [],      # BigQuery
        'ga': [],      # Google Analytics (BigQuery)
        'local': [],   # SQLite
        'sf_': []      # Snowflake
    }
    
    # Get from gold SQL files
    if GOLD_SQL_DIR.exists():
        for sql_file in GOLD_SQL_DIR.glob("*.sql"):
            instance_id = sql_file.stem
            for prefix in instances.keys():
                if instance_id.startswith(prefix):
                    instances[prefix].append(instance_id)
                    break
    
    # Limit instances for testing
    result = []
    for prefix, ids in instances.items():
        result.extend(sorted(ids)[:min(limit, len(ids))])
    
    return result[:limit]

def create_perfect_sql_submission():
    """Create SQL submission with perfect matches (copies from gold)"""
    output_dir = SCRIPT_DIR / "test_submission_sql_perfect"
    instances = get_available_gold_instances(limit=5)
    
    copied = 0
    for instance_id in instances:
        gold_sql = GOLD_SQL_DIR / f"{instance_id}.sql"
        if gold_sql.exists():
            shutil.copy(gold_sql, output_dir / f"{instance_id}.sql")
            copied += 1
    
    print(f"  → Copied {copied} gold SQL files (should get 100% accuracy)")
    return copied

def create_mixed_sql_submission():
    """Create SQL submission with mix of correct and incorrect queries"""
    output_dir = SCRIPT_DIR / "test_submission_sql_mixed"
    instances = get_available_gold_instances(limit=6)
    
    # Copy first 3 as correct
    correct = 0
    for instance_id in instances[:3]:
        gold_sql = GOLD_SQL_DIR / f"{instance_id}.sql"
        if gold_sql.exists():
            shutil.copy(gold_sql, output_dir / f"{instance_id}.sql")
            correct += 1
    
    # Create intentionally wrong queries for next 3
    wrong = 0
    for instance_id in instances[3:6]:
        gold_sql = GOLD_SQL_DIR / f"{instance_id}.sql"
        if gold_sql.exists():
            # Read and modify the query to make it wrong
            with open(gold_sql, 'r') as f:
                content = f.read()
            
            # Add a WHERE clause that filters everything out
            modified = content.rstrip()
            if not modified.endswith(';'):
                modified += '\n'
            
            # Wrap in a subquery with impossible condition
            modified = f"SELECT * FROM (\n{modified}\n) WHERE 1=0"
            
            with open(output_dir / f"{instance_id}.sql", 'w') as f:
                f.write(modified)
            wrong += 1
    
    print(f"  → Created {correct} correct + {wrong} wrong SQL files (should get ~50% accuracy)")
    return correct + wrong

def create_perfect_csv_submission():
    """Create CSV submission with perfect matches (copies from gold)"""
    output_dir = SCRIPT_DIR / "test_submission_csv_perfect"
    instances = get_available_gold_instances(limit=5)
    
    copied = 0
    for instance_id in instances:
        # Handle multiple gold CSVs (some instances have variants like bq002_a.csv, bq002_b.csv)
        gold_csv = GOLD_RESULT_DIR / f"{instance_id}.csv"
        if gold_csv.exists():
            shutil.copy(gold_csv, output_dir / f"{instance_id}.csv")
            copied += 1
    
    print(f"  → Copied {copied} gold CSV files (should get 100% accuracy)")
    return copied

def create_wrong_csv_submission():
    """Create CSV submission with wrong data"""
    output_dir = SCRIPT_DIR / "test_submission_csv_wrong"
    instances = get_available_gold_instances(limit=5)
    
    created = 0
    for instance_id in instances:
        gold_csv = GOLD_RESULT_DIR / f"{instance_id}.csv"
        if gold_csv.exists():
            # Read gold CSV headers only
            with open(gold_csv, 'r') as f:
                reader = csv.reader(f)
                headers = next(reader)
            
            # Create wrong data by writing only headers (empty result)
            with open(output_dir / f"{instance_id}.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            created += 1
    
    print(f"  → Created {created} wrong CSV files (should get 0% accuracy)")
    return created

def create_readme():
    """Create README with instructions"""
    readme_content = """# Synthetic Test Data for Spider2-Lite Evaluation

This folder contains synthetic test submissions to validate the evaluation framework.

## Test Folders

### 1. test_submission_sql_perfect/
- **Mode**: SQL
- **Expected Score**: 100%
- **Description**: Contains exact copies of gold SQL queries
- **Run**: `python evaluate.py --result_dir test_submission_sql_perfect --mode sql`

### 2. test_submission_sql_mixed/
- **Mode**: SQL
- **Expected Score**: ~50%
- **Description**: Mix of correct queries and intentionally wrong ones
- **Run**: `python evaluate.py --result_dir test_submission_sql_mixed --mode sql`

### 3. test_submission_csv_perfect/
- **Mode**: exec_result (CSV)
- **Expected Score**: 100%
- **Description**: Contains exact copies of gold execution results
- **Run**: `python evaluate.py --result_dir test_submission_csv_perfect --mode exec_result`

### 4. test_submission_csv_wrong/
- **Mode**: exec_result (CSV)
- **Expected Score**: 0%
- **Description**: Contains empty results (wrong answers)
- **Run**: `python evaluate.py --result_dir test_submission_csv_wrong --mode exec_result`

## Quick Test

Run all tests:
```bash
# Test perfect SQL submission
python evaluate.py --result_dir test_submission_sql_perfect --mode sql

# Test mixed SQL submission  
python evaluate.py --result_dir test_submission_sql_mixed --mode sql

# Test perfect CSV submission
python evaluate.py --result_dir test_submission_csv_perfect --mode exec_result

# Test wrong CSV submission
python evaluate.py --result_dir test_submission_csv_wrong --mode exec_result
```

## For Couchbase IQ Evaluation

1. Create a new folder: `couchbase_iq_results/`
2. Generate SQL files for each instance_id: `{instance_id}.sql`
3. Run: `python evaluate.py --result_dir couchbase_iq_results --mode sql`

## Instance ID Prefixes
- `bq*` = BigQuery queries
- `ga*` = Google Analytics (BigQuery)
- `local*` = SQLite (local database)
- `sf_*` = Snowflake queries

Generated by: create_synthetic_test_data.py
"""
    
    with open(SCRIPT_DIR / "TEST_DATA_README.md", 'w') as f:
        f.write(readme_content)
    
    print("✓ Created TEST_DATA_README.md with instructions")

def main():
    print("=" * 60)
    print("Creating Synthetic Test Data for Spider2-Lite Evaluation")
    print("=" * 60)
    print()
    
    # Check if gold data exists
    if not GOLD_SQL_DIR.exists() or not GOLD_RESULT_DIR.exists():
        print("❌ Error: Gold data not found!")
        print(f"   Expected: {GOLD_SQL_DIR}")
        print(f"   Expected: {GOLD_RESULT_DIR}")
        return
    
    print("Step 1: Creating test folders...")
    folders = create_test_folders()
    print()
    
    print("Step 2: Generating test data...")
    print()
    print("test_submission_sql_perfect:")
    create_perfect_sql_submission()
    print()
    
    print("test_submission_sql_mixed:")
    create_mixed_sql_submission()
    print()
    
    print("test_submission_csv_perfect:")
    create_perfect_csv_submission()
    print()
    
    print("test_submission_csv_wrong:")
    create_wrong_csv_submission()
    print()
    
    print("Step 3: Creating documentation...")
    create_readme()
    print()
    
    print("=" * 60)
    print("Synthetic test data created successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Read TEST_DATA_README.md for instructions")
    print("  2. Test the evaluation with CSV mode (no DB needed):")
    print("     python evaluate.py --result_dir test_submission_csv_perfect --mode exec_result")
    print()
    print("  3. For Couchbase IQ, create folder 'couchbase_iq_results/'")
    print("     and generate {instance_id}.sql files for each question")
    print()

if __name__ == "__main__":
    main()

