#!/usr/bin/env python3
"""
Diagnose Pipeline

This script analyzes the pipeline process and provides diagnostic information
about each step, from raw OCR to HSA-ready output. It can be used to identify
issues in the pipeline and understand where failures are occurring.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import argparse
import shutil

# Ensure we can import from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from src directory
from src.utils.progress import ProgressReporter
from src.utils.config import get_config_manager
from src.formatter.hsa_formatter import HSAFormatter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("diagnose_pipeline")

def count_files(directory: Path, pattern: str = "**/*") -> int:
    """Count files in a directory matching a pattern."""
    if not directory.exists():
        return 0
    
    return len(list(directory.glob(pattern)))

def get_pipeline_stats(issue_id: str, output_dir: str = "output") -> Dict[str, Any]:
    """
    Get stats for each stage of the pipeline for a specific issue.
    
    Args:
        issue_id: The issue ID to analyze
        output_dir: The output directory
        
    Returns:
        Dictionary with statistics for each pipeline stage
    """
    base_dir = Path(output_dir)
    issue_dir = base_dir / issue_id
    
    stats = {
        "issue_id": issue_id,
        "stages": {
            "raw": {
                "path": str(issue_dir / "raw.txt"),
                "exists": False,
                "size": 0,
                "line_count": 0
            },
            "articles": {
                "path": str(issue_dir / "articles"),
                "exists": False,
                "count": 0
            },
            "classified": {
                "path": str(issue_dir / "classified"),
                "exists": False,
                "count": 0
            },
            "hsa_ready": {
                "path": "varies by date",
                "exists": False,
                "count": 0,
                "samples": []
            }
        },
        "overall": {
            "complete": False,
            "bottleneck": None,
            "success_rate": 0.0
        }
    }
    
    # Check raw OCR file
    raw_path = issue_dir / "raw.txt"
    if raw_path.exists():
        stats["stages"]["raw"]["exists"] = True
        stats["stages"]["raw"]["size"] = raw_path.stat().st_size
        
        # Count lines in the file
        try:
            with open(raw_path, 'r', encoding='utf-8', errors='replace') as f:
                stats["stages"]["raw"]["line_count"] = sum(1 for _ in f)
        except Exception as e:
            logger.error(f"Error reading raw file: {e}")
    
    # Check articles directory
    articles_dir = issue_dir / "articles"
    if articles_dir.exists():
        stats["stages"]["articles"]["exists"] = True
        stats["stages"]["articles"]["count"] = count_files(articles_dir, "*.json")
    
    # Check classified directory
    classified_dir = issue_dir / "classified"
    if classified_dir.exists():
        stats["stages"]["classified"]["exists"] = True
        stats["stages"]["classified"]["count"] = count_files(classified_dir, "*.json")
    
    # Try to find HSA-ready files
    # We need to parse the issue_id to get the date for the HSA directory structure
    try:
        # Format: per_atlanta-constitution_1922-01-01_54_203
        parts = issue_id.split('_')
        if len(parts) >= 3:
            date_part = parts[2]  # e.g., 1922-01-01
            if '-' in date_part:
                year, month, day = date_part.split('-')
                hsa_dir = base_dir / "hsa-ready" / year / month / day
                
                if hsa_dir.exists():
                    stats["stages"]["hsa_ready"]["exists"] = True
                    stats["stages"]["hsa_ready"]["path"] = str(hsa_dir)
                    stats["stages"]["hsa_ready"]["count"] = count_files(hsa_dir, "*.json")
                    
                    # Get a few samples
                    samples = []
                    for file_path in list(hsa_dir.glob("*.json"))[:3]:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                sample = json.load(f)
                            
                            # Add filename and truncate body
                            sample["_filename"] = file_path.name
                            if "body" in sample and len(sample["body"]) > 100:
                                sample["body"] = sample["body"][:100] + "..."
                            
                            samples.append(sample)
                        except Exception as e:
                            logger.warning(f"Error reading sample file: {e}")
                    
                    stats["stages"]["hsa_ready"]["samples"] = samples
    except Exception as e:
        logger.error(f"Error finding HSA-ready files: {e}")
    
    # Calculate overall stats
    if stats["stages"]["raw"]["exists"]:
        if stats["stages"]["articles"]["count"] > 0:
            if stats["stages"]["classified"]["count"] > 0:
                if stats["stages"]["hsa_ready"]["count"] > 0:
                    stats["overall"]["complete"] = True
                    
                    # Calculate success rates
                    articles_to_classified = (stats["stages"]["classified"]["count"] / 
                                             stats["stages"]["articles"]["count"]) * 100
                    classified_to_hsa = (stats["stages"]["hsa_ready"]["count"] / 
                                        stats["stages"]["classified"]["count"]) * 100
                    
                    stats["overall"]["success_rate"] = {
                        "articles_to_classified": articles_to_classified,
                        "classified_to_hsa": classified_to_hsa,
                        "overall": (stats["stages"]["hsa_ready"]["count"] / 
                                   stats["stages"]["articles"]["count"]) * 100
                    }
                else:
                    stats["overall"]["bottleneck"] = "formatter"
            else:
                stats["overall"]["bottleneck"] = "classifier"
        else:
            stats["overall"]["bottleneck"] = "extractor"
    else:
        stats["overall"]["bottleneck"] = "fetcher"
    
    return stats

def attempt_fix(issue_id: str, output_dir: str = "output", fix_stage: Optional[str] = None) -> Dict[str, Any]:
    """
    Attempt to fix pipeline issues for a specific issue.
    
    Args:
        issue_id: The issue ID to fix
        output_dir: The output directory
        fix_stage: The specific stage to fix ("formatter", "classifier", "extractor", "all")
        
    Returns:
        Dictionary with results of the fix attempt
    """
    results = {
        "issue_id": issue_id,
        "attempted_fixes": [],
        "successful_fixes": [],
        "errors": []
    }
    
    base_dir = Path(output_dir)
    issue_dir = base_dir / issue_id
    
    # Get current stats to identify issues
    stats = get_pipeline_stats(issue_id, output_dir)
    
    # Fix based on the identified bottleneck or specified stage
    target_stage = fix_stage or stats["overall"]["bottleneck"]
    
    if target_stage == "formatter" or target_stage == "all":
        # Try to fix formatter issues
        try:
            logger.info(f"Attempting to fix formatter issues for {issue_id}")
            results["attempted_fixes"].append("formatter")
            
            classified_dir = issue_dir / "classified"
            if classified_dir.exists() and count_files(classified_dir, "*.json") > 0:
                formatter = HSAFormatter(output_dir=base_dir)
                
                # Force add_default_values to true
                formatter.add_default_values = True
                formatter.strict_validation = False
                
                # Process the classified articles
                formatted_files = formatter.format_issue(issue_id, classified_dir)
                
                if formatted_files:
                    results["successful_fixes"].append("formatter")
                    logger.info(f"Successfully formatted {len(formatted_files)} articles")
                else:
                    results["errors"].append("No articles were formatted successfully")
            else:
                results["errors"].append("No classified articles to format")
        except Exception as e:
            results["errors"].append(f"Error fixing formatter: {str(e)}")
    
    if target_stage == "classifier" or target_stage == "all":
        # Try to fix classifier issues
        try:
            logger.info(f"Attempting to fix classifier issues for {issue_id}")
            results["attempted_fixes"].append("classifier")
            
            # This would run the classifier again with different settings
            # Placeholder for now - would need to import and run the classifier with modified settings
            logger.warning("Classifier fix not implemented yet")
            
        except Exception as e:
            results["errors"].append(f"Error fixing classifier: {str(e)}")
    
    # Return updated stats
    updated_stats = get_pipeline_stats(issue_id, output_dir)
    results["before"] = stats
    results["after"] = updated_stats
    
    return results

def create_report(stats: Dict[str, Any], output_file: Optional[str] = None) -> None:
    """
    Create a detailed HTML report from pipeline stats.
    
    Args:
        stats: Pipeline statistics from get_pipeline_stats
        output_file: Output file for the HTML report
    """
    if output_file is None:
        output_file = f"reports/pipeline_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    
    # Create HTML report
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pipeline Diagnosis Report - {stats['issue_id']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #333; }}
            .section {{ margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; border-radius: 5px; }}
            .stage {{ margin-bottom: 15px; }}
            .success {{ color: green; }}
            .warning {{ color: orange; }}
            .error {{ color: red; }}
            .metrics {{ display: flex; flex-wrap: wrap; }}
            .metric {{ flex: 1; min-width: 200px; margin: 5px; padding: 10px; background-color: #f5f5f5; border-radius: 5px; }}
            pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 3px; overflow-x: auto; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f0f0f0; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h1>Pipeline Diagnosis Report</h1>
        <div class="section">
            <h2>Issue: {stats['issue_id']}</h2>
            <div class="metrics">
                <div class="metric">
                    <h3>Status</h3>
                    <p class="{('success' if stats['overall']['complete'] else 'error')}">
                        {('Complete' if stats['overall']['complete'] else 'Incomplete')}
                    </p>
                </div>
                <div class="metric">
                    <h3>Bottleneck</h3>
                    <p class="{('success' if not stats['overall']['bottleneck'] else 'warning')}">
                        {(stats['overall']['bottleneck'] if stats['overall']['bottleneck'] else 'None')}
                    </p>
                </div>
    """
    
    # Add success rates if available
    if isinstance(stats['overall']['success_rate'], dict):
        html += f"""
                <div class="metric">
                    <h3>Success Rates</h3>
                    <ul>
                        <li>Articles → Classified: {stats['overall']['success_rate']['articles_to_classified']:.1f}%</li>
                        <li>Classified → HSA: {stats['overall']['success_rate']['classified_to_hsa']:.1f}%</li>
                        <li>Overall: {stats['overall']['success_rate']['overall']:.1f}%</li>
                    </ul>
                </div>
        """
    
    html += """
            </div>
        </div>
    """
    
    # Pipeline Stages
    html += """
        <div class="section">
            <h2>Pipeline Stages</h2>
    """
    
    # Raw OCR
    stage = stats['stages']['raw']
    status_class = "success" if stage['exists'] else "error"
    html += f"""
            <div class="stage">
                <h3>1. Raw OCR</h3>
                <p class="{status_class}">Status: {('Complete' if stage['exists'] else 'Missing')}</p>
                <p>Path: {stage['path']}</p>
                <p>Size: {stage['size'] / 1024:.1f} KB</p>
                <p>Lines: {stage['line_count']}</p>
            </div>
    """
    
    # Articles
    stage = stats['stages']['articles']
    status_class = "success" if stage['exists'] and stage['count'] > 0 else "error"
    html += f"""
            <div class="stage">
                <h3>2. Article Extraction</h3>
                <p class="{status_class}">Status: {('Complete' if stage['exists'] and stage['count'] > 0 else 'Missing or Empty')}</p>
                <p>Path: {stage['path']}</p>
                <p>Articles: {stage['count']}</p>
            </div>
    """
    
    # Classified
    stage = stats['stages']['classified']
    status_class = "success" if stage['exists'] and stage['count'] > 0 else "error"
    html += f"""
            <div class="stage">
                <h3>3. Classification</h3>
                <p class="{status_class}">Status: {('Complete' if stage['exists'] and stage['count'] > 0 else 'Missing or Empty')}</p>
                <p>Path: {stage['path']}</p>
                <p>Classified Articles: {stage['count']}</p>
            </div>
    """
    
    # HSA Ready
    stage = stats['stages']['hsa_ready']
    status_class = "success" if stage['exists'] and stage['count'] > 0 else "error"
    html += f"""
            <div class="stage">
                <h3>4. HSA Formatting</h3>
                <p class="{status_class}">Status: {('Complete' if stage['exists'] and stage['count'] > 0 else 'Missing or Empty')}</p>
                <p>Path: {stage['path']}</p>
                <p>HSA Articles: {stage['count']}</p>
    """
    
    # Add sample HSA articles if available
    if stage['samples']:
        html += f"""
                <h4>Sample HSA Articles ({len(stage['samples'])})</h4>
                <table>
                    <tr>
                        <th>Filename</th>
                        <th>Headline</th>
                        <th>Section</th>
                        <th>Publication</th>
                        <th>Tags</th>
                    </tr>
        """
        
        for sample in stage['samples']:
            tags = ', '.join(sample.get('tags', []))
            html += f"""
                    <tr>
                        <td>{sample.get('_filename', '')}</td>
                        <td>{sample.get('headline', '')}</td>
                        <td>{sample.get('section', '')}</td>
                        <td>{sample.get('publication', '')}</td>
                        <td>{tags}</td>
                    </tr>
            """
        
        html += """
                </table>
                <h4>Sample JSON</h4>
        """
        
        if stage['samples']:
            html += f"""
                <pre>{json.dumps(stage['samples'][0], indent=2)}</pre>
            """
    
    html += """
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    logger.info(f"Report generated at {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Diagnose the pipeline process")
    parser.add_argument("--issue", required=True, help="Issue ID to diagnose")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument("--report", default=None, help="Generate HTML report")
    parser.add_argument("--fix", choices=["formatter", "classifier", "extractor", "all"], 
                        help="Attempt to fix identified issues")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info(f"Diagnosing pipeline for issue: {args.issue}")
    
    # Get pipeline stats
    stats = get_pipeline_stats(args.issue, args.output_dir)
    
    # Attempt to fix issues if requested
    if args.fix:
        logger.info(f"Attempting to fix {args.fix} issues")
        results = attempt_fix(args.issue, args.output_dir, args.fix)
        logger.info(f"Fix results: {len(results['successful_fixes'])} successful, {len(results['errors'])} errors")
        
        # Update stats after fixes
        stats = get_pipeline_stats(args.issue, args.output_dir)
    
    # Print summary
    print(f"\nPipeline Diagnostic Summary for {args.issue}:")
    print(f"Raw OCR: {'✅' if stats['stages']['raw']['exists'] else '❌'} ({stats['stages']['raw']['line_count']} lines)")
    print(f"Articles: {'✅' if stats['stages']['articles']['count'] > 0 else '❌'} ({stats['stages']['articles']['count']} articles)")
    print(f"Classified: {'✅' if stats['stages']['classified']['count'] > 0 else '❌'} ({stats['stages']['classified']['count']} articles)")
    print(f"HSA Ready: {'✅' if stats['stages']['hsa_ready']['count'] > 0 else '❌'} ({stats['stages']['hsa_ready']['count']} articles)")
    
    print(f"\nOverall Status: {'✅ Complete' if stats['overall']['complete'] else '❌ Incomplete'}")
    if stats['overall']['bottleneck']:
        print(f"Bottleneck: {stats['overall']['bottleneck']}")
    
    if isinstance(stats['overall']['success_rate'], dict):
        print(f"\nSuccess Rates:")
        print(f"  Articles → Classified: {stats['overall']['success_rate']['articles_to_classified']:.1f}%")
        print(f"  Classified → HSA: {stats['overall']['success_rate']['classified_to_hsa']:.1f}%")
        print(f"  Overall: {stats['overall']['success_rate']['overall']:.1f}%")
    
    # Generate report if requested
    if args.report is not None:
        report_path = args.report
        create_report(stats, report_path)
        print(f"\nDetailed report saved to: {report_path}")

if __name__ == "__main__":
    main() 