#!/usr/bin/env python3
"""
HSA-Ready Data Validation Script

This script validates the migrated HSA-ready data against schema requirements.
It ensures all files have required fields, proper formatting, and consistent structure.
It also generates a validation report with any issues found.
"""

import os
import json
import sys
import re
from pathlib import Path
from datetime import datetime
import logging
from jsonschema import validate, ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("hsa_validator")

# HSA JSON Schema
HSA_SCHEMA = {
    "type": "object",
    "required": [
        "headline",
        "body",
        "section",
        "timestamp",
        "publication",
        "source_issue",
        "source_url"
    ],
    "properties": {
        "headline": {
            "type": "string",
            "minLength": 1
        },
        "byline": {
            "type": ["string", "null"]
        },
        "dateline": {
            "type": ["string", "null"]
        },
        "body": {
            "type": "string",
            "minLength": 1
        },
        "section": {
            "type": "string",
            "enum": ["news", "editorial", "sports", "business", "entertainment", "lifestyle", "other", "unknown"]
        },
        "tags": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "timestamp": {
            "type": "string",
            "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}:[0-9]{2}(\\.[0-9]+)?Z)?$"
        },
        "publication": {
            "type": "string",
            "minLength": 1
        },
        "source_issue": {
            "type": "string"
        },
        "source_url": {
            "type": "string"
        }
    }
}

class HSAValidator:
    """Validates HSA-ready data against schema and organizational requirements."""

    def __init__(self, base_dir="output/hsa-ready-clean"):
        """Initialize with the base directory."""
        self.base_dir = Path(base_dir)
        self.stats = {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "validation_errors": [],
            "publications": set(),
            "by_publication": {},
            "organizational_issues": []
        }
        
    def validate(self):
        """Perform full validation of the HSA-ready directory."""
        logger.info(f"Starting validation of {self.base_dir}")
        
        if not self.base_dir.exists():
            logger.error(f"Directory {self.base_dir} does not exist")
            return False
            
        # Check organizational structure
        self.validate_organization()
            
        # Walk through all files
        for root, dirs, files in os.walk(self.base_dir):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                # Skip hidden files
                if file.startswith('.'):
                    continue
                    
                # Only process JSON files
                if not file.endswith('.json'):
                    continue
                    
                file_path = Path(root) / file
                self.validate_file(file_path)
                
        logger.info(f"Validation complete. {self.stats['valid_files']} of {self.stats['total_files']} files are valid.")
        return True
        
    def validate_organization(self):
        """Validate the organizational structure of the directories."""
        # Check if there are publication directories
        if not any(d.is_dir() for d in self.base_dir.iterdir() if not d.name.startswith('.')):
            self.stats["organizational_issues"].append("No publication directories found")
            return
            
        # Check each publication directory
        for pub_dir in [d for d in self.base_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]:
            self.stats["publications"].add(pub_dir.name)
            pub_issues = []
            
            # Publication should have year directories
            if not any(d.is_dir() for d in pub_dir.iterdir() if d.name.isdigit()):
                pub_issues.append(f"No year directories found in {pub_dir.name}")
                
            # Check each year directory
            for year_dir in [d for d in pub_dir.iterdir() if d.is_dir() and d.name.isdigit()]:
                year_issues = []
                
                # Year should have month directories
                if not any(d.is_dir() for d in year_dir.iterdir() if d.name.isdigit() and 1 <= int(d.name) <= 12):
                    year_issues.append(f"No month directories found in {year_dir.name}")
                    
                # Check each month directory
                for month_dir in [d for d in year_dir.iterdir() if d.is_dir() and d.name.isdigit()]:
                    # Month should have day directories
                    if not any(d.is_dir() for d in month_dir.iterdir() if d.name.isdigit() and 1 <= int(d.name) <= 31):
                        year_issues.append(f"No day directories found in {year_dir.name}/{month_dir.name}")
                
                if year_issues:
                    pub_issues.extend(year_issues)
            
            if pub_issues:
                self.stats["organizational_issues"].append({
                    "publication": pub_dir.name,
                    "issues": pub_issues
                })
                
            self.stats["by_publication"][pub_dir.name] = {
                "years": [d.name for d in pub_dir.iterdir() if d.is_dir() and d.name.isdigit()]
            }
        
    def validate_file(self, file_path):
        """Validate a single HSA-ready file."""
        relative_path = file_path.relative_to(self.base_dir)
        self.stats["total_files"] += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Validate against schema
            try:
                validate(instance=data, schema=HSA_SCHEMA)
                self.stats["valid_files"] += 1
            except ValidationError as e:
                self.stats["invalid_files"] += 1
                self.stats["validation_errors"].append({
                    "path": str(relative_path),
                    "error": str(e)
                })
                
        except json.JSONDecodeError as e:
            self.stats["invalid_files"] += 1
            self.stats["validation_errors"].append({
                "path": str(relative_path),
                "error": f"Invalid JSON format: {str(e)}"
            })
        except Exception as e:
            self.stats["invalid_files"] += 1
            self.stats["validation_errors"].append({
                "path": str(relative_path),
                "error": f"Error validating file: {str(e)}"
            })
            
    def generate_report(self, output_file=None):
        """Generate a report of the validation results."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "base_directory": str(self.base_dir),
            "summary": {
                "total_files": self.stats["total_files"],
                "valid_files": self.stats["valid_files"],
                "invalid_files": self.stats["invalid_files"],
                "percent_valid": (self.stats["valid_files"] / self.stats["total_files"] * 100) if self.stats["total_files"] > 0 else 0
            },
            "publications": list(self.stats["publications"]),
            "by_publication": self.stats["by_publication"],
            "organizational_issues": self.stats["organizational_issues"],
            "validation_errors": self.stats["validation_errors"][:100]  # Limit to first 100 errors
        }
        
        # Print summary to console
        logger.info(f"Validation Summary:")
        logger.info(f"  Total JSON files: {report['summary']['total_files']}")
        logger.info(f"  Valid files: {report['summary']['valid_files']} ({report['summary']['percent_valid']:.2f}%)")
        logger.info(f"  Invalid files: {report['summary']['invalid_files']}")
        logger.info(f"  Publications found: {', '.join(report['publications'])}")
        
        if report["organizational_issues"]:
            logger.warning(f"  Organizational issues found: {len(report['organizational_issues'])}")
        
        if report["validation_errors"]:
            logger.warning(f"  Validation errors found: {len(report['validation_errors'])}")
        
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
    parser = argparse.ArgumentParser(description="Validate HSA-ready data")
    parser.add_argument("--dir", default="output/hsa-ready-clean", help="Base directory to validate")
    parser.add_argument("--output", default="reports/hsa_validation.json", help="Output file for validation report")
    args = parser.parse_args()
    
    validator = HSAValidator(args.dir)
    success = validator.validate()
    
    if success:
        validator.generate_report(args.output)
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main()) 