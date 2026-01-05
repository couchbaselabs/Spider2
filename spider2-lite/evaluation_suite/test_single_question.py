#!/usr/bin/env python3
"""
Test a single question from spider2-lite.jsonl
Run SQL generation, execution, and save results to CSV
"""

import json
import sys
from pathlib import Path
from couchbase_iq_spider2_evaluator import CouchbaseIQAPI, load_config, exec_sql, json_to_csv


def load_question_by_id(instance_id):
    """Load a specific question by instance_id from spider2-lite.jsonl"""
    spider2_file = Path(__file__).parent.parent / "spider2-lite.jsonl"
    
    with open(spider2_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                question = json.loads(line)
                if question.get('instance_id') == instance_id:
                    return question
    
    return None


def load_external_knowledge(filename):
    """Load external knowledge content from resource/documents directory"""
    if not filename:
        return None
    
    # Path to resource/documents directory
    resource_dir = Path(__file__).parent.parent / "resource" / "documents"
    knowledge_file = resource_dir / filename
    
    if not knowledge_file.exists():
        print(f"  ✗ Warning: External knowledge file not found: {filename}")
        return None
    
    try:
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"  ✗ Warning: Failed to read {filename}: {e}")
        return None


def get_keyspaces_for_db(database_name):
    """Get keyspaces for a specific database from keyspaces.txt"""
    keyspaces_file = Path(__file__).parent / "utils" / "keyspaces.txt"
    keyspaces = []
    
    prefix = f"{database_name}.spider2."
    
    with open(keyspaces_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith(prefix):
                keyspaces.append(line)
    
    return keyspaces


def test_single_question(instance_id):
    """Test a single question by instance_id"""
    print("=" * 80)
    print(f"Testing Single Question: {instance_id}")
    print("=" * 80)
    print()
    
    # Load question
    print("Step 1: Loading question...")
    question_data = load_question_by_id(instance_id)
    
    if not question_data:
        print(f"✗ ERROR: Question '{instance_id}' not found in spider2-lite.jsonl")
        return False
    
    print(f"✓ Question loaded")
    print(f"  Instance ID: {question_data['instance_id']}")
    print(f"  Database: {question_data.get('db', 'N/A')}")
    print(f"  Question: {question_data['question'][:100]}...")
    if question_data.get('external_knowledge'):
        print(f"  External knowledge: {question_data['external_knowledge']}")
    print()
    
    # Load configuration
    print("Step 2: Loading configuration...")
    config = load_config()
    
    couchbase_config = config.get("couchbase", {})
    couchbase_iq_config = config.get("couchbase_iq", {})
    
    query_endpoint = couchbase_config.get("query_endpoint", "http://localhost:8093/query/service")
    couchbase_user = couchbase_config.get("username", "Administrator")
    couchbase_pass = couchbase_config.get("password", "password")
    natural_cred = couchbase_iq_config.get("natural_cred", "<capella_username:password>")
    natural_orgid = couchbase_iq_config.get("natural_orgid", "<capella_orgid>")
    
    print(f"✓ Configuration loaded")
    print(f"  Query endpoint: {query_endpoint}")
    print(f"  Username: {couchbase_user}")
    print()
    
    # Check credentials
    if natural_cred == "<capella_username:password>" or natural_orgid == "<capella_orgid>":
        print("✗ ERROR: Couchbase IQ credentials not configured!")
        print("  Please update couchbase_config.json with your Capella credentials")
        return False
    
    # Initialize API
    print("Step 3: Initializing CouchbaseIQ API...")
    try:
        couchbase_iq = CouchbaseIQAPI(
            query_endpoint=query_endpoint,
            natural_cred=natural_cred,
            natural_orgid=natural_orgid,
            couchbase_user=couchbase_user,
            couchbase_pass=couchbase_pass
        )
        print("✓ API initialized successfully")
        print()
    except Exception as e:
        print(f"✗ Failed to initialize API: {e}")
        return False
    
    # Get keyspaces for the database
    db_name = question_data.get('db')
    if not db_name:
        print("✗ ERROR: No database specified in question data")
        return False
    
    print(f"Step 4: Loading keyspaces for {db_name}...")
    keyspaces = get_keyspaces_for_db(db_name)
    
    if not keyspaces:
        print(f"✗ ERROR: No keyspaces found for database '{db_name}'")
        print("  Make sure the database is imported and keyspaces.txt is up to date")
        return False
    
    print(f"✓ Loaded {len(keyspaces)} keyspaces:")
    for ks in keyspaces[:5]:  # Show first 5
        print(f"  - {ks}")
    if len(keyspaces) > 5:
        print(f"  ... and {len(keyspaces) - 5} more")
    print()
    
    # Load external knowledge if available
    external_knowledge_content = None
    external_knowledge_file = question_data.get('external_knowledge')
    if external_knowledge_file:
        print(f"Step 5: Loading external knowledge: {external_knowledge_file}")
        external_knowledge_content = load_external_knowledge(external_knowledge_file)
        if external_knowledge_content:
            print(f"✓ Loaded external knowledge ({len(external_knowledge_content)} chars)")
            print(f"  Preview: {external_knowledge_content[:150]}...")
        else:
            print(f"⚠ Could not load external knowledge")
        print()
    
    # Generate SQL
    step_num = 6 if external_knowledge_file else 5
    print(f"Step {step_num}: Generating SQL...")
    print(f"  Question: {question_data['question']}")
    print()

    external_knowledge_content = external_knowledge_content+"Use window functions to answer complicated calculation questions." if external_knowledge_content else None
    
    try:
        generated_sql = couchbase_iq.generate_sql(
            keyspaces=keyspaces,
            question=question_data['question'],
            evidence=external_knowledge_content
        )
        
        if not generated_sql:
            print(f"✗ Failed to generate SQL")
            return False
        
        print(f"✓ SQL generated successfully")
        print()
        print("Generated SQL:")
        print("-" * 80)
        print(generated_sql)
        print("-" * 80)
        print()
        
    except Exception as e:
        print(f"✗ Error generating SQL: {e}")
        return False
    
    # Execute SQL
    step_num += 1
    print(f"Step {step_num}: Executing SQL...")
    try:
        results = exec_sql(
            sql_query=generated_sql,
            couchbase_user=couchbase_user,
            couchbase_pass=couchbase_pass,
            query_endpoint=query_endpoint
        )
        
        if results is None:
            print(f"✗ Failed to execute SQL")
            return False
        
        print(f"✓ SQL executed successfully")
        print(f"  Rows returned: {len(results)}")
        print()
        
        # Show preview of results
        if results:
            print("Result preview (first 3 rows):")
            print("-" * 80)
            for i, row in enumerate(results[:3], 1):
                print(f"Row {i}: {row}")
            if len(results) > 3:
                print(f"... and {len(results) - 3} more rows")
            print("-" * 80)
            print()
        else:
            print("No rows returned")
            print()
        
    except Exception as e:
        print(f"✗ Error executing SQL: {e}")
        return False
    
    # Save to CSV
    step_num += 1
    print(f"Step {step_num}: Saving results to CSV...")
    
    # Create output directory
    output_dir = Path(__file__).parent / "local_results" / db_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    csv_file = output_dir / f"{instance_id}.csv"
    
    if json_to_csv(results, csv_file):
        print(f"✓ Results saved to: {csv_file}")
        print()
    else:
        print(f"✗ Failed to save results to CSV")
        return False
    
    # Summary
    print()
    print("=" * 80)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print(f"Instance ID: {instance_id}")
    print(f"Database: {db_name}")
    print(f"Rows returned: {len(results)}")
    print(f"Output file: {csv_file}")
    print("=" * 80)
    print()
    
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_single_question.py <instance_id>")
        print()
        print("Example:")
        print("  python test_single_question.py local_001")
        print()
        print("To see available instance IDs, check spider2-lite.jsonl")
        sys.exit(1)
    
    instance_id = sys.argv[1]
    success = test_single_question(instance_id)
    
    if not success:
        print()
        print("✗ TEST FAILED")
        print()
        print("Troubleshooting tips:")
        print("1. Verify the instance_id exists in spider2-lite.jsonl")
        print("2. Check that couchbase_config.json has correct credentials")
        print("3. Ensure Couchbase server is running and accessible")
        print("4. Verify the database has been imported to Couchbase")
        print("5. Check that keyspaces.txt contains entries for the database")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()

