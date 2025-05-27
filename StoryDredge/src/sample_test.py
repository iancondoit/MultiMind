#!/usr/bin/env python3
"""
Simple test script for checking article format without classification.
"""

import sys
import json
from pathlib import Path

def test_byline_handling():
    """Test the formatting of articles with bylines without running classification."""
    # Import just the formatter
    from src.formatter.hsa_formatter import HSAFormatter
    
    # Create sample test articles
    sample_articles = [
        {
            "title": "BY HENSON TATUM",
            "raw_text": "BUILDING BOOM CONTINUES\n\nDuring an unprecedented building boom in Atlanta, contractors report...",
            "section": "news",
            "source_issue": "per_atlanta-constitution_1922-01-01_54_203",
            "publication": "The Atlanta Constitution"
        },
        {
            "headline": "MAYOR'S ADDRESS TO COUNCIL",
            "byline": "Special Correspondent",
            "raw_text": "The mayor addressed the city council yesterday regarding...",
            "section": "politics",
            "source_issue": "per_atlanta-constitution_1922-01-01_54_203",
            "publication": "The Atlanta Constitution"
        },
        {
            "title": "STOCK MARKETS IN DECLINE",
            "raw_text": "BY FINANCIAL REPORTER\n\nStock markets showed significant decline yesterday as investors...",
            "section": "business",
            "source_issue": "per_atlanta-constitution_1922-01-01_54_203",
            "publication": "The Atlanta Constitution"
        }
    ]
    
    # Initialize formatter
    formatter = HSAFormatter()
    
    # Process each article
    formatted_articles = []
    for i, article in enumerate(sample_articles):
        print(f"\nProcessing test article {i+1}:")
        
        # Skip classification, just format directly
        formatted = formatter.format_article(article)
        formatted_articles.append(formatted)
        
        # Show key fields
        print(f"  Original title: {article.get('title', article.get('headline', 'None'))}")
        print(f"  Formatted headline: {formatted['headline']}")
        print(f"  Formatted byline: {formatted['byline']}")
        
    # Save the formatted articles
    output_dir = Path("examples/sample_articles")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    for i, article in enumerate(formatted_articles):
        output_file = output_dir / f"article_{i+1}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(article, f, indent=2)
    
    print(f"\nSaved {len(formatted_articles)} formatted articles to {output_dir}")
    
    # Print formatted JSON for the first article
    print("\nExample formatted article (JSON):")
    print(json.dumps(formatted_articles[0], indent=2))
    
    return True

if __name__ == "__main__":
    # Make sure we can import from the project
    import os
    sys.path.insert(0, os.path.abspath("."))
    
    # Run the test
    test_byline_handling() 