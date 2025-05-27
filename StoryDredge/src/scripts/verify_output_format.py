#!/usr/bin/env python3
"""
Verify HSA Output Format

This script verifies that output files in the HSA-ready directory match
the expected format with all required fields.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Ensure we can import from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("verify_output_format")

# Required fields for HSA output
REQUIRED_FIELDS = [
    "headline", "body", "tags", "section", "timestamp",
    "publication", "source_issue", "source_url"
]

# Optional fields for HSA output
OPTIONAL_FIELDS = ["byline", "dateline"]

def verify_file(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Verify that a file matches the expected HSA format.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            article = json.load(f)
        
        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in article:
                errors.append(f"Missing required field: {field}")
            elif article[field] == "":
                errors.append(f"Required field is empty: {field}")
        
        # Check tags structure
        if "tags" in article and not isinstance(article["tags"], list):
            errors.append("Tags field must be a list")
        
        # Check timestamp format
        if "timestamp" in article and not article["timestamp"].endswith("Z"):
            errors.append(f"Invalid timestamp format: {article['timestamp']}")
        
        return len(errors) == 0, errors
    
    except json.JSONDecodeError:
        return False, ["Invalid JSON format"]
    except Exception as e:
        return False, [f"Error verifying file: {str(e)}"]

def verify_directory(directory: Path, recursive: bool = True) -> Dict[str, Any]:
    """
    Verify all JSON files in a directory.
    
    Args:
        directory: Directory containing HSA-ready files
        recursive: Whether to recursively search subdirectories
        
    Returns:
        Dictionary with verification statistics
    """
    if not directory.exists():
        logger.error(f"Directory does not exist: {directory}")
        return {
            "valid_files": 0,
            "invalid_files": 0,
            "errors": [f"Directory does not exist: {directory}"]
        }
    
    valid_files = 0
    invalid_files = 0
    error_files = []
    
    pattern = "**/*.json" if recursive else "*.json"
    
    for file_path in directory.glob(pattern):
        if file_path.is_file():
            is_valid, errors = verify_file(file_path)
            
            if is_valid:
                valid_files += 1
            else:
                invalid_files += 1
                error_files.append({
                    "file": str(file_path),
                    "errors": errors
                })
    
    return {
        "valid_files": valid_files,
        "invalid_files": invalid_files,
        "error_files": error_files
    }

def print_sample_output():
    """Print a sample of the expected HSA output format."""
    sample = {
        "headline": "AND SAVE MONEY",
        "body": "AND SAVE MONEY. \nSANTA CLAUS left another carload of oil \nstocks in your chimney...",
        "tags": ["news"],
        "section": "news",
        "timestamp": "1922-01-01T00:00:00.000Z",
        "publication": "Atlanta Constitution",
        "source_issue": "per_atlanta-constitution_1922-01-01_54_203",
        "source_url": "https://archive.org/details/per_atlanta-constitution_1922-01-01",
        "byline": ""
    }
    
    print("\nExpected HSA Output Format:")
    print(json.dumps(sample, indent=2))

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify HSA output format")
    parser.add_argument("--dir", default="output/hsa-ready", help="Directory containing HSA-ready files")
    parser.add_argument("--recursive", action="store_true", help="Recursively search subdirectories")
    parser.add_argument("--output", help="Output file for verification results")
    parser.add_argument("--sample", action="store_true", help="Print a sample of the expected format")
    
    args = parser.parse_args()
    
    if args.sample:
        print_sample_output()
        return
    
    logger.info(f"Verifying HSA output format in {args.dir}")
    
    results = verify_directory(Path(args.dir), args.recursive)
    
    logger.info(f"Verification completed: {results['valid_files']} valid files, {results['invalid_files']} invalid files")
    
    if results["invalid_files"] > 0:
        logger.warning("Some files have validation errors")
        
        for i, error_file in enumerate(results["error_files"][:10]):  # Show first 10 error files
            logger.warning(f"File {i+1}: {error_file['file']}")
            for error in error_file["errors"]:
                logger.warning(f"  - {error}")
        
        if len(results["error_files"]) > 10:
            logger.warning(f"... and {len(results['error_files']) - 10} more files with errors")
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {args.output}")

if __name__ == "__main__":
    main() 