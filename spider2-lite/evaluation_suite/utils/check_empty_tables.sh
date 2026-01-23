#!/bin/bash

# Script to find and optionally remove all empty tables in SQLite databases
# Usage: 
#   ./check_empty_tables.sh [directory_path]           # List empty tables only
#   ./check_empty_tables.sh --cleanup [directory_path] # Remove empty tables

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default path is relative to script location (../../local_sqlite)
DEFAULT_DB_DIR="$(cd "$SCRIPT_DIR/../../local_sqlite" && pwd)"

# Parse arguments
CLEANUP=false
DB_DIR=""

for arg in "$@"; do
  case $arg in
    --cleanup)
      CLEANUP=true
      ;;
    *)
      DB_DIR="$arg"
      ;;
  esac
done

# Use default if no directory specified
DB_DIR="${DB_DIR:-$DEFAULT_DB_DIR}"

if [ "$CLEANUP" = true ]; then
  echo "Mode: CLEANUP (will remove empty tables)"
else
  echo "Mode: CHECK ONLY (use --cleanup flag to remove empty tables)"
fi
echo "Scanning SQLite databases in: $DB_DIR"
echo ""

total_empty=0

for db in "$DB_DIR"/*.sqlite; do
  dbname=$(basename "$db")
  echo ""
  echo "========================================"
  echo "DATABASE: $dbname"
  echo "========================================"
  
  # Get all table names (excluding SQLite internal tables)
  sqlite3 "$db" "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';" | while read table; do
    if [ -n "$table" ]; then
      count=$(sqlite3 "$db" "SELECT COUNT(*) FROM \"$table\";" 2>/dev/null)
      if [ "$count" = "0" ]; then
        if [ "$CLEANUP" = true ]; then
          echo "  Dropping empty table: $table"
          sqlite3 "$db" "DROP TABLE IF EXISTS \"$table\";" 2>/dev/null
          if [ $? -eq 0 ]; then
            echo "    ✓ Removed successfully"
          else
            echo "    ✗ Failed to remove"
          fi
        else
          echo "  EMPTY TABLE: $table"
        fi
      fi
    fi
  done
done

echo ""
echo "========================================"
if [ "$CLEANUP" = true ]; then
  echo "Cleanup complete!"
else
  echo "Scan complete! Run with --cleanup flag to remove empty tables."
fi
echo "========================================"
