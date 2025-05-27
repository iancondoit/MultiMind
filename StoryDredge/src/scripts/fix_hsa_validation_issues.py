#!/usr/bin/env python3
"""
Fix HSA Validation Issues

This script addresses validation issues found in the HSA-ready data.
It reads the validation report, fixes the identified issues, and updates
the files in the clean directory structure.
"""

import os
import json
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("hsa_fixer")

class HSAFixer:
    """Fixes validation issues in HSA-ready data."""

    def __init__(self, base_dir="output/hsa-ready-clean", validation_report="reports/hsa_validation.json"):
        """Initialize with the base directory and validation report."""
        self.base_dir = Path(base_dir)
        self.validation_report_path = Path(validation_report)
        self.stats = {
            "total_issues": 0,
            "fixed_issues": 0,
            "failed_fixes": 0,
            "by_issue_type": {}
        }
        
    def load_validation_report(self):
        """Load the validation report JSON."""
        try:
            with open(self.validation_report_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load validation report: {e}")
            return None
            
    def fix_issues(self):
        """Fix issues identified in the validation report."""
        logger.info(f"Starting to fix HSA validation issues")
        
        report = self.load_validation_report()
        if not report:
            logger.error("Cannot proceed without validation report")
            return False
            
        errors = report.get("validation_errors", [])
        self.stats["total_issues"] = len(errors)
        
        if not errors:
            logger.info("No validation issues to fix")
            return True
            
        logger.info(f"Found {len(errors)} validation issues to fix")
        
        for error in errors:
            file_path = error.get("path")
            error_message = error.get("error", "")
            
            if not file_path:
                continue
                
            # Categorize the error
            error_type = self.categorize_error(error_message)
            
            if error_type not in self.stats["by_issue_type"]:
                self.stats["by_issue_type"][error_type] = 0
            self.stats["by_issue_type"][error_type] += 1
            
            # Fix the file
            success = self.fix_file(Path(self.base_dir) / file_path, error_type)
            
            if success:
                self.stats["fixed_issues"] += 1
            else:
                self.stats["failed_fixes"] += 1
                
        logger.info(f"Finished fixing issues. Fixed {self.stats['fixed_issues']} of {self.stats['total_issues']} issues.")
        return True
        
    def categorize_error(self, error_message):
        """Categorize the error message to determine fix strategy."""
        if "None is not of type 'string'" and "headline" in error_message:
            return "null_headline"
        elif "None is not of type 'string'" and "body" in error_message:
            return "null_body"
        elif "should be non-empty" and "body" in error_message:
            return "empty_body"
        else:
            return "unknown"
            
    def fix_file(self, file_path, error_type):
        """Fix a specific file based on error type."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Apply fixes based on error type
            if error_type == "null_headline":
                # Fix null headline
                data["headline"] = "Untitled Article"
                logger.info(f"Fixed null headline in {file_path}")
                
            elif error_type == "null_body" or error_type == "empty_body":
                # Fix null or empty body
                data["body"] = "[Content not available]"
                logger.info(f"Fixed null/empty body in {file_path}")
                
            else:
                # Unknown error type, apply generic fixes
                # Ensure all required fields have at least empty values
                for field in ["headline", "body", "section", "publication", "source_issue", "source_url"]:
                    if field not in data or data[field] is None:
                        if field in ["headline", "body"]:
                            data[field] = f"[{field.capitalize()} not available]"
                        elif field == "section":
                            data[field] = "unknown"
                        elif field == "publication":
                            data[field] = "San Antonio Express-News"
                        elif field == "source_issue":
                            # Extract from filename if possible
                            issue_date = file_path.stem.split("--")[0]
                            data[field] = f"san-antonio-express-news-{issue_date}"
                        elif field == "source_url":
                            # Create a generic URL based on issue date
                            issue_date = file_path.stem.split("--")[0]
                            data[field] = f"https://archive.org/details/san-antonio-express-news-{issue_date}"
                
                # Ensure timestamp is properly formatted
                if "timestamp" in data and not data["timestamp"].endswith("Z"):
                    if "T" not in data["timestamp"]:
                        data["timestamp"] = f"{data['timestamp']}T00:00:00.000Z"
                        
                logger.info(f"Applied generic fixes to {file_path}")
                
            # Ensure tags is an array
            if "tags" not in data or data["tags"] is None:
                data["tags"] = []
                
            # Write the fixed data back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to fix {file_path}: {e}")
            return False
            
    def generate_report(self, output_file=None):
        """Generate a report of the fix results."""
        report = {
            "base_directory": str(self.base_dir),
            "validation_report": str(self.validation_report_path),
            "summary": {
                "total_issues": self.stats["total_issues"],
                "fixed_issues": self.stats["fixed_issues"],
                "failed_fixes": self.stats["failed_fixes"],
                "success_rate": (self.stats["fixed_issues"] / self.stats["total_issues"] * 100) if self.stats["total_issues"] > 0 else 0
            },
            "by_issue_type": self.stats["by_issue_type"]
        }
        
        # Print summary to console
        logger.info(f"Fix Summary:")
        logger.info(f"  Total issues: {report['summary']['total_issues']}")
        logger.info(f"  Fixed issues: {report['summary']['fixed_issues']} ({report['summary']['success_rate']:.2f}%)")
        logger.info(f"  Failed fixes: {report['summary']['failed_fixes']}")
        logger.info(f"  Issues by type: {report['by_issue_type']}")
        
        # Output full report
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Full report written to {output_path}")
            
        return report
            
def main():
    """Main function."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Fix HSA validation issues")
    parser.add_argument("--dir", default="output/hsa-ready-clean", 
                        help="Base directory with migrated data")
    parser.add_argument("--validation-report", default="reports/hsa_validation.json", 
                        help="Validation report file")
    parser.add_argument("--output", default="reports/hsa_fix_report.json", 
                        help="Output file for fix report")
    args = parser.parse_args()
    
    fixer = HSAFixer(args.dir, args.validation_report)
    success = fixer.fix_issues()
    
    if success:
        fixer.generate_report(args.output)
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main()) 