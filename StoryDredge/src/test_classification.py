#!/usr/bin/env python3
"""
Test script to demonstrate different classification methods and their performance.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any

def test_classification_methods():
    """Test different classification methods and compare their performance."""
    # Make sure we can import from the project
    sys.path.insert(0, os.path.abspath("."))
    
    # Import the classifier
    from src.classifier.article_classifier import ArticleClassifier
    
    # Create test articles
    test_articles = [
        {
            "title": "Football Game Results",
            "raw_text": """The Atlanta Falcons defeated the New Orleans Saints 28-14 in a thrilling game on Sunday. 
            Quarterback Matt Ryan threw for 3 touchdowns while the defense held the Saints to just 250 total yards. 
            Coach Smith praised the team's effort saying this was their best performance of the season so far.""",
            "source_issue": "per_atlanta-constitution_1922-01-01_54_203",
            "publication": "The Atlanta Constitution"
        },
        {
            "title": "Stock Market Report",
            "raw_text": """Wall Street saw significant gains yesterday as the Dow Jones Industrial Average rose 2.1%.
            Technology stocks led the rally with Apple and Microsoft both gaining over 3%.
            Analysts point to strong economic data and positive corporate earnings as factors driving the market higher.
            Investors remain cautious about inflation concerns, but the Federal Reserve has signaled it will maintain 
            its current policy.""",
            "source_issue": "per_atlanta-constitution_1922-01-01_54_203",
            "publication": "The Atlanta Constitution"
        },
        {
            "title": "Mayor's Address to City Council",
            "raw_text": """In his address to the city council yesterday, Mayor Johnson outlined his plans for 
            urban renewal and infrastructure improvement. The $50 million project will focus on repairing bridges, 
            upgrading water systems, and expanding public transportation. The council will vote on the proposal 
            next week, with several members already expressing support. Representatives from neighborhood associations 
            attended the meeting and raised concerns about potential disruptions during construction.""",
            "source_issue": "per_atlanta-constitution_1922-01-01_54_203",
            "publication": "The Atlanta Constitution"
        },
        {
            "title": "Editorial: The Need for Education Reform",
            "raw_text": """Our public education system is failing our children and requires immediate reform. 
            For too long, bureaucracy and outdated methods have hindered progress in our schools.
            We believe that increased funding alone is not the answer - structural changes must be made to how 
            we approach teaching and learning. Teachers should be given more autonomy in the classroom, while 
            being held accountable for results. Parents must have more choices in where and how their children 
            are educated. The time for half-measures and incremental change has passed.""",
            "source_issue": "per_atlanta-constitution_1922-01-01_54_203",
            "publication": "The Atlanta Constitution"
        }
    ]
    
    # Test 1: Rule-based classification only
    print("\n---- TEST 1: RULE-BASED CLASSIFICATION ONLY ----")
    rule_based_classifier = ArticleClassifier(skip_classification=True)
    
    # Measure time
    start_time = time.time()
    rule_results = classify_and_report(rule_based_classifier, test_articles, "Rule-based")
    rule_time = time.time() - start_time
    print(f"Total time for rule-based classification: {rule_time:.2f} seconds")
    
    # Test 2: Full LLM-based classification
    print("\n---- TEST 2: LLM CLASSIFICATION ----")
    llm_classifier = ArticleClassifier(skip_classification=False)
    
    # Clean cache to ensure fair test
    clean_cache()
    
    # Measure time
    start_time = time.time()
    llm_results = classify_and_report(llm_classifier, test_articles, "LLM-based")
    llm_time = time.time() - start_time
    print(f"Total time for LLM classification: {llm_time:.2f} seconds")
    
    # Test 3: Hybrid approach (default)
    print("\n---- TEST 3: HYBRID APPROACH (RULE-BASED + LLM WITH CACHING) ----")
    hybrid_classifier = ArticleClassifier()
    
    # Clean cache to ensure fair test
    clean_cache()
    
    # Measure time for first run (no cache)
    start_time = time.time()
    hybrid_results_1 = classify_and_report(hybrid_classifier, test_articles, "Hybrid (first run)")
    hybrid_time_1 = time.time() - start_time
    print(f"Total time for hybrid classification (first run): {hybrid_time_1:.2f} seconds")
    
    # Measure time for second run (with cache)
    start_time = time.time()
    hybrid_results_2 = classify_and_report(hybrid_classifier, test_articles, "Hybrid (cached)")
    hybrid_time_2 = time.time() - start_time
    print(f"Total time for hybrid classification (with cache): {hybrid_time_2:.2f} seconds")
    
    # Print summary
    print("\n---- PERFORMANCE SUMMARY ----")
    print(f"Rule-based only: {rule_time:.2f} seconds")
    print(f"LLM-based: {llm_time:.2f} seconds")
    print(f"Hybrid (first run): {hybrid_time_1:.2f} seconds")
    print(f"Hybrid (with cache): {hybrid_time_2:.2f} seconds")
    print(f"Speed improvement from caching: {hybrid_time_1 / hybrid_time_2:.1f}x faster")
    
    if rule_time > 0 and llm_time > 0:
        print(f"Rule-based vs LLM speedup: {llm_time / rule_time:.1f}x faster")

def classify_and_report(classifier, articles, method_name):
    """Classify articles and report results."""
    results = []
    
    print(f"\n{method_name} Classification Results:")
    print("-" * 50)
    
    for i, article in enumerate(articles):
        start_time = time.time()
        result = classifier.classify_article(article)
        duration = time.time() - start_time
        
        results.append(result)
        
        print(f"Article {i+1}: \"{article['title']}\"")
        print(f"  Category: {result.get('category', 'unknown')}")
        print(f"  Confidence: {result.get('confidence', 0):.2f}")
        print(f"  Classification time: {duration:.2f} seconds")
        print()
    
    return results

def clean_cache():
    """Clean the classification cache."""
    cache_dir = Path("cache/classifications")
    if cache_dir.exists():
        for file in cache_dir.glob("*.json"):
            try:
                file.unlink()
            except Exception as e:
                print(f"Failed to delete {file}: {e}")

if __name__ == "__main__":
    # Run the test
    test_classification_methods() 