#!/usr/bin/env python3
"""
Analyze JSON files to find columns with mixed types.
This helps identify SQLite type affinity issues where NUMERIC columns
may contain empty strings instead of NULL or numeric values.

Can also clean JSON files by replacing empty strings with NULL in numeric columns.
"""

import json
import os
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Any, Tuple


def get_value_type(value: Any) -> str:
    """Get the type name of a value, handling None specially."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        if value == "":
            return "empty_string"
        return "string"
    return str(type(value).__name__)


def analyze_column_types(table_data: List[Dict]) -> Dict[str, Set[str]]:
    """Analyze all columns in a table and return types found in each column."""
    column_types = defaultdict(set)
    
    if not table_data:
        return column_types
    
    # Get all column names from first row
    all_columns = set()
    for row in table_data:
        all_columns.update(row.keys())
    
    # Analyze each column
    for column in all_columns:
        for row in table_data:
            if column in row:
                value_type = get_value_type(row[column])
                column_types[column].add(value_type)
    
    return column_types


def is_mixed_type(types: Set[str]) -> bool:
    """Check if a column has mixed types (excluding null)."""
    # Remove null from consideration as it's usually acceptable
    non_null_types = types - {"null"}
    
    if len(non_null_types) <= 1:
        return False
    
    # Check for problematic type mixing
    numeric_types = {"int", "float"}
    text_types = {"string", "empty_string"}
    
    has_numeric = bool(non_null_types & numeric_types)
    has_text = bool(non_null_types & text_types)
    
    # Mixing numeric and text is problematic
    if has_numeric and has_text:
        return True
    
    # Mixing int and float is usually okay, but we'll report it
    if "int" in non_null_types and "float" in non_null_types:
        return True
    
    # Mixing empty_string with non-empty string is worth noting
    if "empty_string" in non_null_types and "string" in non_null_types:
        # This is less problematic, but still mixed
        return len(non_null_types) > 2  # Only report if there are other types too
    
    return False


def analyze_json_file(json_path: Path) -> Dict[str, Dict[str, Set[str]]]:
    """Analyze a single JSON file and return mixed type columns."""
    results = {}
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for table_name, table_data in data.items():
            if not isinstance(table_data, list):
                continue
            
            column_types = analyze_column_types(table_data)
            mixed_columns = {}
            
            for column, types in column_types.items():
                if is_mixed_type(types):
                    mixed_columns[column] = types
            
            if mixed_columns:
                results[table_name] = mixed_columns
    
    except Exception as e:
        print(f"Error processing {json_path.name}: {e}")
    
    return results


def format_type_set(types: Set[str]) -> str:
    """Format a set of types for display."""
    # Sort for consistent output
    sorted_types = sorted(types)
    return ", ".join(sorted_types)


def is_numeric_column(column_types: Set[str]) -> bool:
    """Check if a column is numeric (contains int or float types)."""
    numeric_types = {"int", "float"}
    non_null_types = column_types - {"null"}
    return bool(non_null_types & numeric_types)


def clean_json_file(json_path: Path, dry_run: bool = False) -> Dict[str, int]:
    """
    Clean a JSON file by replacing empty strings with NULL in numeric columns.
    
    Args:
        json_path: Path to the JSON file
        dry_run: If True, only report what would be changed without making changes
        
    Returns:
        Dictionary with cleaning statistics: {'tables_processed': int, 'columns_cleaned': int, 'values_replaced': int}
    """
    stats = {
        'tables_processed': 0,
        'columns_cleaned': 0,
        'values_replaced': 0
    }
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified = False
        
        for table_name, table_data in data.items():
            if not isinstance(table_data, list) or not table_data:
                continue
            
            stats['tables_processed'] += 1
            
            # Analyze column types to identify numeric columns
            column_types_map = analyze_column_types(table_data)
            
            # Find numeric columns that have empty strings
            numeric_columns_to_clean = []
            for column, types in column_types_map.items():
                if is_numeric_column(types) and "empty_string" in types:
                    numeric_columns_to_clean.append(column)
            
            if not numeric_columns_to_clean:
                continue
            
            # Clean the data
            for row in table_data:
                for column in numeric_columns_to_clean:
                    if column in row and row[column] == "":
                        if not dry_run:
                            row[column] = None
                        stats['values_replaced'] += 1
                        modified = True
            
            if numeric_columns_to_clean:
                stats['columns_cleaned'] += len(numeric_columns_to_clean)
        
        # Save the cleaned data
        if modified and not dry_run:
            # Create backup
            backup_path = json_path.with_suffix('.json.backup')
            if not backup_path.exists():
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Write cleaned data
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    except Exception as e:
        print(f"Error cleaning {json_path.name}: {e}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Analyze and clean JSON files for mixed type columns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze only (default)
  python find_mixed_type_columns.py
  
  # Clean JSON files (replace empty strings with NULL in numeric columns)
  python find_mixed_type_columns.py --clean
  
  # Dry run - see what would be cleaned without making changes
  python find_mixed_type_columns.py --clean --dry-run
        """
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean JSON files by replacing empty strings with NULL in numeric columns'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes (requires --clean)'
    )
    
    args = parser.parse_args()
    
    json_dir = Path(__file__).parent.parent.parent / "local_sqlite_json"
    
    if not json_dir.exists():
        print(f"Directory not found: {json_dir}")
        return
    
    if args.clean:
        # Cleaning mode
        if args.dry_run:
            print("DRY RUN MODE: No changes will be made to JSON files\n")
        
        print("Cleaning JSON files (replacing empty strings with NULL in numeric columns)...")
        print("=" * 80)
        
        json_files = sorted(json_dir.glob("*.json"))
        total_files = len(json_files)
        total_stats = {
            'tables_processed': 0,
            'columns_cleaned': 0,
            'values_replaced': 0,
            'files_modified': 0
        }
        
        for json_file in json_files:
            print(f"\nProcessing: {json_file.name}")
            stats = clean_json_file(json_file, dry_run=args.dry_run)
            
            if stats['values_replaced'] > 0:
                total_stats['files_modified'] += 1
                total_stats['tables_processed'] += stats['tables_processed']
                total_stats['columns_cleaned'] += stats['columns_cleaned']
                total_stats['values_replaced'] += stats['values_replaced']
                
                if args.dry_run:
                    print(f"  Would replace {stats['values_replaced']} empty strings in {stats['columns_cleaned']} columns")
                else:
                    print(f"  ✓ Replaced {stats['values_replaced']} empty strings with NULL in {stats['columns_cleaned']} columns")
            else:
                print(f"  ✓ No empty strings found in numeric columns")
        
        # Summary
        print("\n" + "=" * 80)
        print("CLEANING SUMMARY")
        print("=" * 80)
        print(f"Total files processed: {total_files}")
        print(f"Files modified: {total_stats['files_modified']}")
        print(f"Total values replaced: {total_stats['values_replaced']}")
        print(f"Total columns cleaned: {total_stats['columns_cleaned']}")
        print(f"Total tables processed: {total_stats['tables_processed']}")
        
        if args.dry_run:
            print("\n(DRY RUN - No files were actually modified)")
        else:
            print("\n✓ Cleaning complete! Backup files saved with .backup extension")
    
    else:
        # Analysis mode (default)
        all_results = {}
        total_files = 0
        files_with_issues = 0
        
        print("Analyzing JSON files for mixed type columns...")
        print("=" * 80)
        
        # Process all JSON files
        json_files = sorted(json_dir.glob("*.json"))
        total_files = len(json_files)
        
        for json_file in json_files:
            print(f"\nProcessing: {json_file.name}")
            results = analyze_json_file(json_file)
            
            if results:
                files_with_issues += 1
                all_results[json_file.name] = results
                
                for table_name, mixed_columns in results.items():
                    print(f"  Table: {table_name}")
                    for column, types in mixed_columns.items():
                        print(f"    - {column}: {format_type_set(types)}")
            else:
                print(f"  ✓ No mixed type columns found")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total files analyzed: {total_files}")
        print(f"Files with mixed type columns: {files_with_issues}")
        
        if all_results:
            print("\nDetailed breakdown:")
            
            # Count by type combination
            type_combinations = defaultdict(int)
            for file_results in all_results.values():
                for table_results in file_results.values():
                    for types in table_results.values():
                        type_key = format_type_set(types)
                        type_combinations[type_key] += 1
            
            print("\nType combinations found:")
            for combo, count in sorted(type_combinations.items(), key=lambda x: -x[1]):
                print(f"  {combo}: {count} columns")
            
            # Save detailed report
            report_path = json_dir.parent / "mixed_type_columns_report.txt"
            with open(report_path, 'w') as f:
                f.write("MIXED TYPE COLUMNS REPORT\n")
                f.write("=" * 80 + "\n\n")
                
                for filename, file_results in sorted(all_results.items()):
                    f.write(f"File: {filename}\n")
                    f.write("-" * 80 + "\n")
                    
                    for table_name, mixed_columns in sorted(file_results.items()):
                        f.write(f"\n  Table: {table_name}\n")
                        for column, types in sorted(mixed_columns.items()):
                            f.write(f"    Column: {column}\n")
                            f.write(f"      Types: {format_type_set(types)}\n")
                    
                    f.write("\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("SUMMARY\n")
                f.write("=" * 80 + "\n")
                f.write(f"Total files with issues: {files_with_issues}\n")
                f.write(f"Total files analyzed: {total_files}\n")
            
            print(f"\nDetailed report saved to: {report_path}")
        else:
            print("\n✓ No mixed type columns found in any file!")


if __name__ == "__main__":
    main()

