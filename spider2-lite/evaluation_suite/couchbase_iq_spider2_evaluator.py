#!/usr/bin/env python3
"""
Couchbase IQ Integration for Spider2-Lite Evaluation

This script:
1. Loads Spider2-Lite questions
2. Calls Couchbase IQ to generate SQL
3. Executes SQL and gets results
4. Converts JSON to CSV
5. Saves for evaluation
"""

import json
import csv
import os
import requests
from pathlib import Path
from typing import Dict, List, Optional
import time

# ============================================================================
# CONFIGURATION - UPDATE THESE OR USE couchbase_config.json
# ============================================================================

# Paths
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "couchbase_config.json"
SPIDER2_LITE_QUESTIONS = SCRIPT_DIR.parent / "spider2-lite.jsonl"
OUTPUT_DIR = SCRIPT_DIR / "couchbase_iq_results"
OUTPUT_SQL_DIR = OUTPUT_DIR / "sql"
OUTPUT_CSV_DIR = OUTPUT_DIR / "csv"

# Default Configuration (overridden by couchbase_config.json if exists)
DEFAULT_CONFIG = {
    "couchbase": {
        "connection_string": "couchbase://localhost",
        "username": "Administrator",
        "password": "password",
        "query_endpoint": "http://localhost:8093/query/service"
    },
    "couchbase_iq": {
        "natural_cred": "<capella_username:password>",
        "natural_orgid": "<capella_orgid>"
    },
    "evaluation": {
        "max_questions": None,
        "save_sql": True,
        "execute_sql": True,
        "delay_between_requests": 0.5
    }
}


def load_config():
    """Load configuration from JSON file or use defaults"""
    if CONFIG_FILE.exists():
        print(f"✓ Loading config from: {CONFIG_FILE.name}")
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config
    else:
        print(f"⚠ Config file not found: {CONFIG_FILE.name}")
        print(f"  Using default configuration")
        return DEFAULT_CONFIG


# ============================================================================
# COUCHBASE IQ API INTEGRATION
# ============================================================================

class CouchbaseIQAPI:
    """Interface to Couchbase IQ for SQL generation"""
    
    def __init__(self, query_endpoint, natural_cred, natural_orgid, couchbase_user, couchbase_pass):
        self.query_endpoint = query_endpoint
        self.natural_cred = natural_cred
        self.natural_orgid = natural_orgid
        self.couchbase_user = couchbase_user
        self.couchbase_pass = couchbase_pass
    
    def generate_sql(self, keyspaces: List[str], question: str, evidence: Optional[str] = None) -> str:
        """
        Generate SQL using Couchbase IQ.
        
        Args:
            keyspaces: List of keyspace/database names
            question: Natural language question
            evidence: Optional additional context/evidence
            
        Returns:
            Generated SQL query string
        """
        # Combine question with evidence if provided
        print(f"================================================= SS ================================================")
        full_question = question
        if evidence:
            full_question = f"Dear AI, here is a hint for you to generate the best SQL++ query to answer the question: {evidence}. Here is the question I need the SQL++ query for: {question}"
        print(f"SS:  Full Question: {full_question}")
        payload = {
            "statement": f"USING AI WITH {{\"keyspaces\":{json.dumps(keyspaces)}, \"execute\":false}} {full_question}",
            "natural_cred": self.natural_cred,
            "natural_orgid": self.natural_orgid
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": requests.auth._basic_auth_str(self.couchbase_user, self.couchbase_pass)
        }
        
        print(f"SS:  Payload: {payload}")
        print(f"SS:  Headers: {headers}")
        print(f"SS:  Query Endpoint: {self.query_endpoint}")
        try:
            print(f"SS:  Trying to generate SQL...")
            response = requests.post(self.query_endpoint, json=payload, headers=headers)
            print(f"SS:  Response: {response}")
            # response.raise_for_status()
            data = response.json()
            print(f"SS:  Response: {data}")
            return data.get('generated_statement', '')
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error generating SQL: {e}")
            if response:
                try:
                    print(f"  Response: {response.json()}")
                except:
                    print(f"  Response text: {response.text}")
            return ""


def exec_sql(sql_query: str, couchbase_user: str, couchbase_pass: str, query_endpoint: str) -> Optional[List[Dict]]:
    """
    Execute SQL query on Couchbase and return results.
    
    Args:
        sql_query: SQL query to execute
        couchbase_user: Couchbase username
        couchbase_pass: Couchbase password
        query_endpoint: Query service endpoint
        
    Returns:
        List of result rows as dictionaries
    """
    payload = {
        "statement": sql_query,
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": requests.auth._basic_auth_str(couchbase_user, couchbase_pass)
    }
    
    try:
        response = requests.post(query_endpoint, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error executing SQL: {e}")
        if response:
            try:
                error_data = response.json()
                print(f"  Error details: {error_data}")
            except:
                print(f"  Response text: {response.text}")
        return []


def json_to_csv(json_results: List[Dict], output_file: Path) -> bool:
    """
    Convert JSON results to CSV format.
    
    Args:
        json_results: List of result dictionaries
        output_file: Path to output CSV file
        
    Returns:
        True if successful, False otherwise
    """
    if not json_results:
        # Empty result - create CSV with no data
        with open(output_file, 'w', newline='') as f:
            f.write('')
        return True
    
    try:
        # Get all unique keys from all results
        all_keys = set()
        for result in json_results:
            # Handle nested dictionaries (Couchbase results might be nested)
            if isinstance(result, dict):
                for key, value in result.items():
                    if isinstance(value, dict):
                        # Flatten nested dict
                        for nested_key in value.keys():
                            all_keys.add(f"{key}.{nested_key}")
                    else:
                        all_keys.add(key)
        
        if not all_keys:
            # No keys found - empty result
            with open(output_file, 'w', newline='') as f:
                f.write('')
            return True
        
        fieldnames = sorted(all_keys)
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in json_results:
                row = {}
                for key, value in result.items():
                    if isinstance(value, dict):
                        # Flatten nested dict
                        for nested_key, nested_value in value.items():
                            row[f"{key}.{nested_key}"] = nested_value
                    else:
                        row[key] = value
                writer.writerow(row)
        
        return True
    except Exception as e:
        print(f"  ✗ Error converting to CSV: {e}")
        return False


# ============================================================================
# MAIN EVALUATION LOGIC
# ============================================================================

def load_questions() -> List[Dict]:
    """Load all Spider2-Lite questions"""
    questions = []
    with open(SPIDER2_LITE_QUESTIONS, 'r') as f:
        for line in f:
            questions.append(json.loads(line.strip()))
    return questions


def get_keyspaces_for_db(db_id: str, instance_id: str) -> List[str]:
    """
    Get keyspace names for a given database.
    For Spider2-Lite, this depends on the database type.
    
    Args:
        db_id: Database identifier
        instance_id: Instance ID (bq*, local*, sf_*)
        
    Returns:
        List of keyspace names
    """
    # For now, return the db_id as the keyspace
    # You may need to customize this based on your Couchbase setup
    if instance_id.startswith("local"):
        # SQLite databases - might need table names
        return [db_id]
    elif instance_id.startswith("bq") or instance_id.startswith("ga"):
        # BigQuery databases
        return [db_id]
    elif instance_id.startswith("sf_"):
        # Snowflake databases
        return [db_id]
    else:
        return [db_id]


def process_question(
    item: Dict,
    couchbase_iq: CouchbaseIQAPI,
    couchbase_user: str,
    couchbase_pass: str,
    query_endpoint: str,
    save_sql: bool = True,
    execute_sql: bool = True
) -> tuple:
    """
    Process a single question: generate SQL, execute, and save results.
    
    Args:
        item: Question item from spider2-lite.jsonl
        couchbase_iq: CouchbaseIQ API instance
        save_sql: Whether to save generated SQL
        execute_sql: Whether to execute SQL and save CSV
        
    Returns:
        Tuple of (success, sql_generated, csv_saved)
    """
    instance_id = item['instance_id']
    question = item['question']
    db = item['db']
    external_knowledge = item.get('external_knowledge')
    
    # Get keyspaces for this database
    keyspaces = get_keyspaces_for_db(db, instance_id)
    
    # Generate SQL with Couchbase IQ
    print(f"  Generating SQL with Couchbase IQ...")
    generated_sql = couchbase_iq.generate_sql(
        keyspaces=keyspaces,
        question=question,
        evidence=external_knowledge
    )
    
    if not generated_sql:
        print(f"  ✗ Failed to generate SQL")
        return (False, False, False)
    
    print(f"  ✓ Generated SQL ({len(generated_sql)} chars)")
    
    # Save SQL if requested
    sql_saved = False
    if save_sql:
        sql_file = OUTPUT_SQL_DIR / f"{instance_id}.sql"
        try:
            with open(sql_file, 'w') as f:
                f.write(generated_sql)
            print(f"  ✓ Saved SQL: {sql_file.name}")
            sql_saved = True
        except Exception as e:
            print(f"  ✗ Failed to save SQL: {e}")
    
    # Execute SQL and save CSV if requested
    csv_saved = False
    if execute_sql:
        print(f"  Executing SQL...")
        results = exec_sql(
            sql_query=generated_sql,
            couchbase_user=couchbase_user,
            couchbase_pass=couchbase_pass,
            query_endpoint=query_endpoint
        )
        
        if results is None:
            print(f"  ✗ Failed to execute SQL")
            return (False, sql_saved, False)
        
        print(f"  ✓ Executed SQL ({len(results)} rows)")
        
        # Convert to CSV
        csv_file = OUTPUT_CSV_DIR / f"{instance_id}.csv"
        if json_to_csv(results, csv_file):
            print(f"  ✓ Saved CSV: {csv_file.name}")
            csv_saved = True
        else:
            print(f"  ✗ Failed to save CSV")
    
    return (True, sql_saved, csv_saved)


def main():
    """Main execution"""
    print("=" * 80)
    print("Couchbase IQ + Spider2-Lite Evaluation")
    print("=" * 80)
    print()
    
    # Load configuration
    config = load_config()
    print()
    
    # Extract config values
    couchbase_config = config.get("couchbase", {})
    couchbase_iq_config = config.get("couchbase_iq", {})
    eval_config = config.get("evaluation", {})
    
    query_endpoint = couchbase_config.get("query_endpoint", "http://localhost:8093/query/service")
    couchbase_user = couchbase_config.get("username", "Administrator")
    couchbase_pass = couchbase_config.get("password", "password")
    natural_cred = couchbase_iq_config.get("natural_cred", "<capella_username:password>")
    natural_orgid = couchbase_iq_config.get("natural_orgid", "<capella_orgid>")
    max_questions = eval_config.get("max_questions", None)
    save_sql = eval_config.get("save_sql", True)
    execute_sql_flag = eval_config.get("execute_sql", True)
    delay = eval_config.get("delay_between_requests", 0.5)
    
    # Create output directories
    OUTPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_SQL_DIR.mkdir(exist_ok=True)
    OUTPUT_CSV_DIR.mkdir(exist_ok=True)
    print(f"✓ Output directories created:")
    print(f"  SQL: {OUTPUT_SQL_DIR}")
    print(f"  CSV: {OUTPUT_CSV_DIR}")
    print()
    
    # Initialize Couchbase IQ API
    print("Initializing Couchbase IQ API...")
    couchbase_iq = CouchbaseIQAPI(
        query_endpoint=query_endpoint,
        natural_cred=natural_cred,
        natural_orgid=natural_orgid,
        couchbase_user=couchbase_user,
        couchbase_pass=couchbase_pass
    )
    print("✓ Couchbase IQ API initialized")
    print()
    
    # Load questions
    print("Loading Spider2-Lite questions...")
    questions = load_questions()
    total_questions = len(questions)
    
    if max_questions:
        questions = questions[:max_questions]
        print(f"✓ Loaded {total_questions} questions (processing {len(questions)})")
    else:
        print(f"✓ Loaded {total_questions} questions")
    print()
    
    # Process each question
    print("Processing questions...")
    print("-" * 80)
    
    stats = {
        'total': 0,
        'sql_generated': 0,
        'sql_saved': 0,
        'csv_saved': 0,
        'failed': 0
    }
    
    for i, item in enumerate(questions, 1):
        instance_id = item['instance_id']
        question = item['question']
        db = item['db']
        
        print(f"\n[{i}/{len(questions)}] {instance_id}")
        print(f"  Question: {question[:80]}...")
        print(f"  Database: {db}")
        
        stats['total'] += 1
        
        try:
            success, sql_saved, csv_saved = process_question(
                item=item,
                couchbase_iq=couchbase_iq,
                couchbase_user=couchbase_user,
                couchbase_pass=couchbase_pass,
                query_endpoint=query_endpoint,
                save_sql=save_sql,
                execute_sql=execute_sql_flag
            )
            
            if success:
                stats['sql_generated'] += 1
            if sql_saved:
                stats['sql_saved'] += 1
            if csv_saved:
                stats['csv_saved'] += 1
            if not success:
                stats['failed'] += 1
                
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            stats['failed'] += 1
        
        # Small delay to avoid overwhelming the API
        time.sleep(delay)
    
    # Print summary
    print()
    print("-" * 80)
    print("Summary:")
    print(f"  Total questions: {stats['total']}")
    print(f"  SQL generated: {stats['sql_generated']}")
    print(f"  SQL saved: {stats['sql_saved']}")
    print(f"  CSV saved: {stats['csv_saved']}")
    print(f"  Failed: {stats['failed']}")
    print()
    print("=" * 80)
    print("Next Steps:")
    print("=" * 80)
    print()
    print("1. Review generated files:")
    print(f"   SQL: {OUTPUT_SQL_DIR}")
    print(f"   CSV: {OUTPUT_CSV_DIR}")
    print()
    print("2. Run evaluation:")
    print(f"   # Using SQL mode:")
    print(f"   python3 evaluate.py --result_dir {OUTPUT_SQL_DIR.name} --mode sql")
    print()
    print(f"   # Using CSV mode:")
    print(f"   python3 evaluate.py --result_dir {OUTPUT_CSV_DIR.name} --mode exec_result")
    print()


if __name__ == "__main__":
    main()

