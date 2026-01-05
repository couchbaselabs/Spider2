#!/bin/bash

# Script to delete all non-local files from the exec_result directory
# Keeps only files starting with "local*.csv"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set the exec_result directory path
EXEC_RESULT_DIR="$SCRIPT_DIR/../gold/exec_result"

# Check if directory exists
if [ ! -d "$EXEC_RESULT_DIR" ]; then
    echo "Error: Directory $EXEC_RESULT_DIR does not exist"
    exit 1
fi

# Count files before deletion
TOTAL_FILES=$(find "$EXEC_RESULT_DIR" -maxdepth 1 -type f | wc -l)
LOCAL_FILES=$(find "$EXEC_RESULT_DIR" -maxdepth 1 -type f -name 'local*.csv' | wc -l)
TO_DELETE=$((TOTAL_FILES - LOCAL_FILES))

echo "Files in $EXEC_RESULT_DIR:"
echo "  Total files: $TOTAL_FILES"
echo "  Local files: $LOCAL_FILES"
echo "  Files to delete: $TO_DELETE"

# Ask for confirmation
read -p "Do you want to delete $TO_DELETE non-local files? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Delete all files that don't start with "local"
    cd "$EXEC_RESULT_DIR"
    find . -maxdepth 1 -type f ! -name 'local*.csv' -delete
    
    REMAINING=$(find . -maxdepth 1 -type f | wc -l)
    echo "✓ Deletion complete!"
    echo "  Remaining files: $REMAINING (all local files)"
else
    echo "Operation cancelled."
    exit 0
fi

