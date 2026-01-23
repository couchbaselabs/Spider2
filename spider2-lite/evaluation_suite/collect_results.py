#!/usr/bin/env python3
"""
Script to collect all CSV files from subdirectories in local_results/ 
and copy them to a flat final_results/ folder for evaluation.
"""

import os
import shutil
from pathlib import Path


def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.resolve()
    
    # Source and destination directories
    local_results_dir = script_dir / "local_results"
    final_results_dir = script_dir / "final_results"
    
    # Create final_results directory (clean start)
    if final_results_dir.exists():
        shutil.rmtree(final_results_dir)
    final_results_dir.mkdir(parents=True)
    
    # Collect all CSV files from subdirectories
    csv_files_copied = 0
    
    for subdir in local_results_dir.iterdir():
        if subdir.is_dir():
            for csv_file in subdir.glob("*.csv"):
                dest_path = final_results_dir / csv_file.name
                
                # Check for duplicate filenames
                if dest_path.exists():
                    print(f"Warning: Duplicate file {csv_file.name} found in {subdir.name}, skipping...")
                    continue
                
                shutil.copy2(csv_file, dest_path)
                csv_files_copied += 1
                print(f"Copied: {subdir.name}/{csv_file.name} -> final_results/{csv_file.name}")
    
    print(f"\n✅ Done! Copied {csv_files_copied} CSV files to {final_results_dir}")


if __name__ == "__main__":
    main()

