#!/usr/bin/env python3
"""
Script to check the size of JSON files in the local_sqlite_json directory
"""

import os
from pathlib import Path

def format_size(size_bytes):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def main():
    # Directory containing JSON files
    json_dir = Path("/Users/soham.sarkar/Documents/evaluations/Spider2/spider2-lite/local_sqlite_json")
    
    if not json_dir.exists():
        print(f"Error: Directory not found: {json_dir}")
        return
    
    # Get all JSON files
    json_files = sorted(json_dir.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {json_dir}")
        return
    
    print(f"Found {len(json_files)} JSON files in {json_dir.name}/")
    print("=" * 70)
    print(f"{'File Name':<40} {'Size':>15} {'Size (bytes)':>15}")
    print("=" * 70)
    
    total_size = 0
    
    for json_file in json_files:
        size = json_file.stat().st_size
        total_size += size
        print(f"{json_file.name:<40} {format_size(size):>15} {size:>15,}")
    
    print("=" * 70)
    print(f"{'TOTAL':<40} {format_size(total_size):>15} {total_size:>15,}")
    print("=" * 70)

if __name__ == "__main__":
    main()

