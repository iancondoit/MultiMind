#!/usr/bin/env python3
"""
Update the Atlanta Constitution summary file with statistics about the additional processed issues
"""

import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("summary_updater")

def count_articles_by_year_month(output_dir="output/atlanta-constitution"):
    """
    Count the number of articles by year and month
    
    Args:
        output_dir: Root directory containing processed articles
    
    Returns:
        Dictionary with counts by year, month, and day
    """
    root_dir = Path(output_dir) / "atlanta-constitution"
    
    if not root_dir.exists():
        logger.error(f"Directory not found: {root_dir}")
        return {}
    
    stats = {}
    
    # Count by year
    for year_dir in sorted(root_dir.glob("*")):
        if not year_dir.is_dir():
            continue
        
        year = year_dir.name
        if not year.isdigit():
            continue
            
        stats[year] = {"total": 0, "months": {}}
        
        # Count by month
        for month_dir in sorted(year_dir.glob("*")):
            if not month_dir.is_dir():
                continue
                
            month = month_dir.name
            if not month.isdigit():
                continue
                
            stats[year]["months"][month] = {"total": 0, "days": {}}
            
            # Count by day
            for day_dir in sorted(month_dir.glob("*")):
                if not day_dir.is_dir():
                    continue
                    
                day = day_dir.name
                if not day.isdigit():
                    continue
                
                # Count articles in this day
                article_count = len(list(day_dir.glob("*.json")))
                
                stats[year]["months"][month]["days"][day] = article_count
                stats[year]["months"][month]["total"] += article_count
                stats[year]["total"] += article_count
    
    return stats

def count_total_articles(output_dir="output/atlanta-constitution"):
    """
    Count the total number of processed articles
    
    Args:
        output_dir: Root directory containing processed articles
    
    Returns:
        Total number of articles
    """
    root_dir = Path(output_dir) / "atlanta-constitution"
    
    if not root_dir.exists():
        logger.error(f"Directory not found: {root_dir}")
        return 0
    
    # Count all JSON files recursively
    return len(list(root_dir.glob("**/*.json")))

def count_issues(output_dir="output/atlanta-constitution"):
    """
    Count the number of processed issues
    
    Args:
        output_dir: Root directory containing processed articles
    
    Returns:
        Number of issues (days)
    """
    root_dir = Path(output_dir) / "atlanta-constitution"
    
    if not root_dir.exists():
        logger.error(f"Directory not found: {root_dir}")
        return 0
    
    # Count day directories
    issue_count = 0
    for year_dir in root_dir.glob("*"):
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue
        for month_dir in year_dir.glob("*"):
            if not month_dir.is_dir() or not month_dir.name.isdigit():
                continue
            for day_dir in month_dir.glob("*"):
                if not day_dir.is_dir() or not day_dir.name.isdigit():
                    continue
                # Make sure it has at least one article
                if list(day_dir.glob("*.json")):
                    issue_count += 1
    
    return issue_count

def update_summary_markdown(summary_file="atlanta_constitution_summary.md"):
    """
    Update the summary markdown file with the latest stats
    
    Args:
        summary_file: Path to the summary markdown file
    """
    logger.info(f"Updating summary file: {summary_file}")
    
    # Get the latest stats
    total_articles = count_total_articles()
    total_issues = count_issues()
    stats_by_year = count_articles_by_year_month()
    
    # Read the current summary file
    try:
        with open(summary_file, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        logger.error(f"Summary file not found: {summary_file}")
        return
    
    # Find year ranges
    years = sorted(stats_by_year.keys())
    date_range = f"{years[0]}-{years[-1]}" if years else "N/A"
    
    # Update the content
    new_lines = []
    section = None
    
    for line in lines:
        if re.match(r"^## \w+", line):
            section = line.strip()[3:].lower()
            new_lines.append(line)
        elif section == "data details" and "**date range**" in line.lower():
            new_lines.append(f"- **Date Range**: {date_range}\n")
        elif section == "data details" and "**total issues processed**" in line.lower():
            new_lines.append(f"- **Total Issues Processed**: {total_issues}\n")
        elif section == "data details" and "**total articles extracted**" in line.lower():
            new_lines.append(f"- **Total Articles Extracted**: {total_articles:,}\n")
        elif section == "data breakdown":
            if re.match(r"- \d{4} issues", line.lower()):
                continue  # Skip existing year breakdown lines
            elif "## " in line or line.strip() == "":
                # Before adding a new section or blank line, add our year breakdown
                if "## " in line and not any(re.match(r"- \d{4} issues", l.lower()) for l in new_lines[-5:]):
                    # Add year breakdown before the next section
                    for year in sorted(stats_by_year.keys()):
                        new_lines.append(f"- {year} Issues: {len(stats_by_year[year]['months']):,} months, {stats_by_year[year]['total']:,} articles\n")
                new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Write the updated content
    with open(summary_file, "w") as f:
        f.writelines(new_lines)
    
    logger.info(f"Summary updated: {total_issues} issues, {total_articles} articles")

def main():
    update_summary_markdown()

if __name__ == "__main__":
    main() 