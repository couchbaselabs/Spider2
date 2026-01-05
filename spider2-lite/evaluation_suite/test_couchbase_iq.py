#!/usr/bin/env python3
"""
Process all local questions from spider2-lite.jsonl
Run SQL generation, execution, and save results to CSV
"""

import json
from pathlib import Path
from couchbase_iq_spider2_evaluator import CouchbaseIQAPI, load_config, exec_sql, json_to_csv

def load_questions():
    """Load questions from spider2-lite.jsonl"""
    spider2_file = Path(__file__).parent.parent / "spider2-lite.jsonl"
    questions = []
    
    with open(spider2_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line))
    
    return questions


def load_external_knowledge(filename):
    """Load external knowledge content from resource/documents directory"""
    if not filename:
        return None
    
    # Path to resource/documents directory
    resource_dir = Path(__file__).parent.parent / "resource" / "documents"
    knowledge_file = resource_dir / filename
    
    if not knowledge_file.exists():
        print(f"    Warning: External knowledge file not found: {filename}")
        return None
    
    try:
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"    Warning: Failed to read {filename}: {e}")
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


def process_questions():
    """Process all questions with local instance_id"""
    print("=" * 80)
    print("Processing Local Questions from spider2-lite.jsonl")
    print("=" * 80)
    print()
    
    # Load configuration
    print("Step 1: Loading configuration...")
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
    print("Step 2: Initializing CouchbaseIQ API...")
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
    
    # Load questions
    print("Step 3: Loading questions from spider2-lite.jsonl...")
    all_questions = load_questions()
    
    # Filter for local instance_id
    local_questions = [
        q for q in all_questions 
        if q.get('instance_id', '').startswith('local')
    ]
    
    print(f"✓ Loaded {len(all_questions)} total questions")
    print(f"✓ Found {len(local_questions)} questions with 'local' instance_id")
    
    if not local_questions:
        print("No matching questions found!")
        return False
    
    # Group questions by database
    from collections import defaultdict
    questions_by_db = defaultdict(list)
    for q in local_questions:
        db_name = q.get('db')
        if db_name:
            questions_by_db[db_name].append(q)
    
    print(f"✓ Found {len(questions_by_db)} databases: {', '.join(sorted(questions_by_db.keys()))}")
    print()
    
    # Create base output directory
    base_output_dir = Path(__file__).parent / "local_results"
    base_output_dir.mkdir(exist_ok=True)
    
    # Overall statistics
    overall_stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'by_database': {}
    }
    
    # Process each database
    for db_idx, (db_name, db_questions) in enumerate(sorted(questions_by_db.items()), 1):
        print("=" * 80)
        print(f"Database {db_idx}/{len(questions_by_db)}: {db_name}")
        print("=" * 80)
        print()
        
        # Get keyspaces for this database
        print(f"Step 4.{db_idx}: Loading keyspaces for {db_name}...")
        keyspaces = get_keyspaces_for_db(db_name)
        
        if not keyspaces:
            print(f"  ✗ No keyspaces found for {db_name}, skipping...")
            print()
            continue
        
        print(f"✓ Loaded {len(keyspaces)} keyspaces")
        print()
        
        # Create database-specific output directory
        db_output_dir = base_output_dir / db_name
        db_output_dir.mkdir(exist_ok=True)
        print(f"✓ Output directory: {db_output_dir}")
        print()
        
        # Process questions for this database
        print(f"Processing {len(db_questions)} questions for {db_name}")
        print("-" * 80)
        print()
        
        db_stats = {
            'total': len(db_questions),
            'success': 0,
            'failed': 0
        }
        
        for i, item in enumerate(db_questions, 1):
            instance_id = item['instance_id']
            question = item['question']
            external_knowledge_file = item.get('external_knowledge')
            
            print(f"[{i}/{len(db_questions)}] Processing: {instance_id}")
            print(f"  Question: {question[:100]}...")
            
            # Load external knowledge content if available
            external_knowledge_content = None
            if external_knowledge_file:
                print(f"  External knowledge: {external_knowledge_file}")
                external_knowledge_content = load_external_knowledge(external_knowledge_file)
                if external_knowledge_content:
                    print(f"    ✓ Loaded external knowledge ({len(external_knowledge_content)} chars)")
            
            print()
            
            try:
                # Generate SQL
                print(f"  Generating SQL...")
                generated_sql = couchbase_iq.generate_sql(
                    keyspaces=keyspaces,
                    question=question,
                    evidence=external_knowledge_content
                )
                
                if not generated_sql:
                    print(f"  ✗ Failed to generate SQL")
                    db_stats['failed'] += 1
                    print()
                    continue
                
                print(f"  ✓ SQL generated ({len(generated_sql)} chars)")
                
                # Execute SQL
                print(f"  Executing SQL...")
                results = exec_sql(
                    sql_query=generated_sql,
                    couchbase_user=couchbase_user,
                    couchbase_pass=couchbase_pass,
                    query_endpoint=query_endpoint
                )
                
                if results is None:
                    print(f"  ✗ Failed to execute SQL")
                    db_stats['failed'] += 1
                    print()
                    continue
                
                print(f"  ✓ SQL executed ({len(results)} rows)")
                
                # Save to CSV
                csv_file = db_output_dir / f"{instance_id}.csv"
                if json_to_csv(results, csv_file):
                    print(f"  ✓ Saved to: {db_name}/{csv_file.name}")
                    db_stats['success'] += 1
                else:
                    print(f"  ✗ Failed to save CSV")
                    db_stats['failed'] += 1
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                db_stats['failed'] += 1
            
            print()
        
        # Database summary
        print(f"Database {db_name} Summary:")
        print(f"  Total:      {db_stats['total']}")
        print(f"  ✓ Success:  {db_stats['success']}")
        print(f"  ✗ Failed:   {db_stats['failed']}")
        print()
        
        # Update overall stats
        overall_stats['total'] += db_stats['total']
        overall_stats['success'] += db_stats['success']
        overall_stats['failed'] += db_stats['failed']
        overall_stats['by_database'][db_name] = db_stats
    
    # Final summary
    print()
    print("=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    print(f"Total questions processed: {overall_stats['total']}")
    print(f"✓ Successful:              {overall_stats['success']}")
    print(f"✗ Failed:                  {overall_stats['failed']}")
    print()
    print("Results by Database:")
    for db_name, db_stats in sorted(overall_stats['by_database'].items()):
        print(f"  {db_name}:")
        print(f"    Total: {db_stats['total']}, Success: {db_stats['success']}, Failed: {db_stats['failed']}")
    print()
    print(f"Results saved in: {base_output_dir}")
    print("=" * 80)
    
    return overall_stats['failed'] == 0


def main():
    success = process_questions()
    
    print()
    if success:
        print("✓ ALL QUESTIONS PROCESSED SUCCESSFULLY!")
    else:
        print("✗ SOME QUESTIONS FAILED - Please check the output above")
    print()
    
    if not success:
        print("Troubleshooting tips:")
        print("1. Verify couchbase_config.json exists and has correct credentials")
        print("2. Check that Couchbase server is running and accessible")
        print("3. Verify Capella credentials (natural_cred and natural_orgid)")
        print("4. Check network connectivity to the query endpoint")
        print("5. Review the error messages for specific questions")
        print()


if __name__ == "__main__":
    main()

