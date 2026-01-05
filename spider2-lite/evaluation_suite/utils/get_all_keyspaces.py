#!/usr/bin/env python3
"""
Extract all Couchbase keyspaces from JSON files in a directory
Outputs keyspaces in the format: bucket.scope.collection
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple


def get_tables_from_json(json_file_path: str) -> List[str]:
    """
    Extract table names from a JSON file
    
    Args:
        json_file_path: Path to the JSON file
        
    Returns:
        List of table names (collection names)
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tables = []
        
        if isinstance(data, dict):
            # Dictionary format - each key is a table name
            for table_name in data.keys():
                tables.append(table_name)
        elif isinstance(data, list):
            # Array format - goes to _default collection
            tables.append("_default")
        else:
            print(f"  Warning: Unknown JSON format in {json_file_path}")
            
        return tables
        
    except Exception as e:
        print(f"  Error reading {json_file_path}: {e}")
        return []


def get_all_keyspaces(
    json_directory: str,
    scope_name: str = "spider2"
) -> List[Tuple[str, str, str, str]]:
    """
    Get all keyspaces from JSON files in a directory
    
    Args:
        json_directory: Path to directory containing JSON files
        scope_name: Scope name (default: spider2)
        
    Returns:
        List of tuples: (bucket_name, scope_name, collection_name, keyspace)
    """
    json_dir = Path(json_directory)
    
    if not json_dir.exists():
        print(f"Error: Directory not found: {json_directory}")
        return []
    
    # Find all JSON files
    json_files = sorted(json_dir.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {json_directory}")
        return []
    
    print(f"Found {len(json_files)} JSON files\n")
    
    all_keyspaces = []
    
    for json_file in json_files:
        bucket_name = json_file.stem
        print(f"Processing: {json_file.name}")
        
        # Get table names from JSON
        tables = get_tables_from_json(str(json_file))
        
        if tables:
            print(f"  Found {len(tables)} collection(s)")
            for table_name in tables:
                keyspace = f"{bucket_name}.{scope_name}.{table_name}"
                all_keyspaces.append((bucket_name, scope_name, table_name, keyspace))
        else:
            print(f"  No collections found")
        
        print()
    
    return all_keyspaces


def save_keyspaces_to_file(keyspaces: List[Tuple[str, str, str, str]], output_file: str):
    """
    Save keyspaces to a text file
    
    Args:
        keyspaces: List of (bucket, scope, collection, keyspace) tuples
        output_file: Output file path
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for bucket, scope, collection, keyspace in keyspaces:
            f.write(f"{keyspace}\n")
    
    print(f"✓ Saved {len(keyspaces)} keyspaces to: {output_file}")


def print_keyspace_summary(keyspaces: List[Tuple[str, str, str, str]]):
    """
    Print a summary of keyspaces grouped by bucket
    
    Args:
        keyspaces: List of (bucket, scope, collection, keyspace) tuples
    """
    print("\n" + "="*70)
    print("KEYSPACE SUMMARY")
    print("="*70)
    
    # Group by bucket
    buckets = {}
    for bucket, scope, collection, keyspace in keyspaces:
        if bucket not in buckets:
            buckets[bucket] = []
        buckets[bucket].append((scope, collection, keyspace))
    
    # Print grouped by bucket
    for bucket in sorted(buckets.keys()):
        collections = buckets[bucket]
        print(f"\n{bucket} ({len(collections)} collections):")
        for scope, collection, keyspace in sorted(collections, key=lambda x: x[1]):
            print(f"  - {keyspace}")
    
    print(f"\n{'='*70}")
    print(f"Total Buckets:     {len(buckets)}")
    print(f"Total Collections: {len(keyspaces)}")
    print(f"{'='*70}\n")


def main():
    """Main function"""
    
    # Configuration
    JSON_DIRECTORY = "/Users/soham.sarkar/Documents/evaluations/Spider2/spider2-lite/local_sqlite_json"
    SCOPE_NAME = "spider2"
    OUTPUT_FILE = "/Users/soham.sarkar/Documents/evaluations/Spider2/spider2-lite/evaluation_suite/utils/keyspaces.txt"
    
    print("\n" + "="*70)
    print("Couchbase Keyspace Extractor")
    print("="*70)
    print(f"JSON Directory: {JSON_DIRECTORY}")
    print(f"Scope Name:     {SCOPE_NAME}")
    print(f"Output File:    {OUTPUT_FILE}")
    print("="*70 + "\n")
    
    # Get all keyspaces
    keyspaces = get_all_keyspaces(
        json_directory=JSON_DIRECTORY,
        scope_name=SCOPE_NAME
    )
    
    if not keyspaces:
        print("No keyspaces found!")
        sys.exit(1)
    
    # Print summary
    print_keyspace_summary(keyspaces)
    
    # Save to file
    save_keyspaces_to_file(keyspaces, OUTPUT_FILE)
    
    print("\nDone!")


if __name__ == "__main__":
    main()

