#!/usr/bin/env python3
"""
HSA-Ready Directory Analysis Script

This script analyzes the current structure of the hsa-ready directory,
identifies all publications, validates JSON files, and generates a report
to inform the restructuring process.
"""

import os
import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("hsa_analyzer")

# Required fields for HSA files
REQUIRED_FIELDS = [
    "headline", 
    "body", 
    "section", 
    "timestamp", 
    "publication",
    "source_issue",
    "source_url"
]

class HSAAnalyzer:
    """Analyzes the HSA-ready directory structure and content."""

    def __init__(self, base_dir="output/hsa-ready"):
        """Initialize with the base directory."""
        self.base_dir = Path(base_dir)
        self.stats = {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "publications": Counter(),
            "years": Counter(),
            "files_by_year_month": defaultdict(Counter),
            "missing_fields": defaultdict(int),
            "file_issues": [],
            "unique_sections": set()
        }
        
    def analyze(self):
        """Perform full analysis of the HSA-ready directory."""
        logger.info(f"Starting analysis of {self.base_dir}")
        
        if not self.base_dir.exists():
            logger.error(f"Directory {self.base_dir} does not exist")
            return False
            
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
                self.analyze_file(file_path)
                
        logger.info(f"Analysis complete. Found {self.stats['total_files']} JSON files.")
        return True
        
    def analyze_file(self, file_path):
        """Analyze a single JSON file."""
        relative_path = file_path.relative_to(self.base_dir)
        self.stats["total_files"] += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Check for required fields
            missing_fields = [field for field in REQUIRED_FIELDS if field not in data]
            
            if missing_fields:
                self.stats["invalid_files"] += 1
                for field in missing_fields:
                    self.stats["missing_fields"][field] += 1
                self.stats["file_issues"].append({
                    "path": str(relative_path),
                    "issue": f"Missing fields: {', '.join(missing_fields)}"
                })
            else:
                self.stats["valid_files"] += 1
                
                # Record publication
                publication = data.get("publication", "Unknown")
                self.stats["publications"][publication] += 1
                
                # Record section
                if "section" in data:
                    self.stats["unique_sections"].add(data["section"])
                
                # Extract year and month from timestamp
                if "timestamp" in data:
                    try:
                        # Handle different timestamp formats
                        timestamp = data["timestamp"]
                        # Try ISO format first (YYYY-MM-DDTHH:MM:SS.sssZ)
                        if "T" in timestamp:
                            date_part = timestamp.split("T")[0]
                        else:
                            date_part = timestamp
                            
                        # Extract year, month
                        parts = date_part.split("-")
                        if len(parts) >= 2:
                            year = parts[0]
                            month = parts[1]
                            
                            self.stats["years"][year] += 1
                            self.stats["files_by_year_month"][(year, month)] += 1
                    except Exception as e:
                        self.stats["file_issues"].append({
                            "path": str(relative_path),
                            "issue": f"Invalid timestamp format: {timestamp}"
                        })
                
        except json.JSONDecodeError:
            self.stats["invalid_files"] += 1
            self.stats["file_issues"].append({
                "path": str(relative_path),
                "issue": "Invalid JSON format"
            })
        except Exception as e:
            self.stats["invalid_files"] += 1
            self.stats["file_issues"].append({
                "path": str(relative_path),
                "issue": f"Error processing file: {str(e)}"
            })
            
    def generate_report(self, output_file=None):
        """Generate a report of the analysis results."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "base_directory": str(self.base_dir),
            "summary": {
                "total_files": self.stats["total_files"],
                "valid_files": self.stats["valid_files"],
                "invalid_files": self.stats["invalid_files"],
                "percent_valid": (self.stats["valid_files"] / self.stats["total_files"] * 100) if self.stats["total_files"] > 0 else 0
            },
            "publications": dict(self.stats["publications"]),
            "years": dict(self.stats["years"]),
            "monthly_distribution": {f"{year}-{month}": count for (year, month), count in self.stats["files_by_year_month"].items()},
            "missing_fields": dict(self.stats["missing_fields"]),
            "unique_sections": list(self.stats["unique_sections"]),
            "file_issues": self.stats["file_issues"][:100]  # Limit to first 100 issues
        }
        
        # Print summary to console
        logger.info(f"Analysis Summary:")
        logger.info(f"  Total JSON files: {report['summary']['total_files']}")
        logger.info(f"  Valid files: {report['summary']['valid_files']} ({report['summary']['percent_valid']:.2f}%)")
        logger.info(f"  Invalid files: {report['summary']['invalid_files']}")
        logger.info(f"  Publications found: {len(report['publications'])}")
        logger.info(f"  Years covered: {list(sorted(report['years'].keys()))}")
        
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
    parser = argparse.ArgumentParser(description="Analyze HSA-ready directory structure and content")
    parser.add_argument("--dir", default="output/hsa-ready", help="Base directory to analyze")
    parser.add_argument("--output", default="reports/hsa_analysis.json", help="Output file for full report")
    args = parser.parse_args()
    
    analyzer = HSAAnalyzer(args.dir)
    success = analyzer.analyze()
    
    if success:
        analyzer.generate_report(args.output)
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main()) 