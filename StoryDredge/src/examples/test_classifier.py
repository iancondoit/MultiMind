"""
Example script to test the ArticleClassifier with Ollama.

Make sure Ollama is running before executing this script:
1. Install Ollama from https://ollama.com/
2. Start Ollama
3. Pull a model: ollama pull llama2
4. Run this script to test the classifier
"""

import sys
import json
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from src.classifier.article_classifier import ArticleClassifier, OllamaClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_ollama_connection():
    """Test if Ollama is accessible."""
    print("Testing Ollama connection...")
    
    client = OllamaClient()
    try:
        response = client.generate(
            prompt="Hello, are you working?",
            model="llama2",
            max_tokens=20
        )
        print(f"Ollama response: {response.get('response', '')}")
        print("Ollama connection successful!")
        return True
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        print("Is Ollama running? Install from https://ollama.com/ and start it.")
        return False

def test_article_classification():
    """Test article classification with a sample article."""
    print("\nTesting article classification...")
    
    # Sample article
    article = {
        "title": "LOCAL COUNCIL APPROVES NEW BUDGET",
        "raw_text": """
        LOCAL COUNCIL APPROVES NEW BUDGET
        
        By John Smith, Staff Writer
        SAN ANTONIO, JUNE 14 — The San Antonio City Council yesterday approved a $24 million budget for the upcoming fiscal year, with increased funding for public safety and parks. Mayor Robert Johnson said the new budget reflects the city's commitment to improving quality of life while maintaining fiscal responsibility.
        
        The budget passed by a vote of 7-2, with Councilmembers Maria Rodriguez and James Wilson opposing the measure, citing concerns about insufficient funding for affordable housing initiatives.
        
        "This budget represents a balanced approach to meeting our city's needs," said Johnson during the council meeting. "We're investing in essential services while keeping tax increases minimal."
        
        The new budget includes a 5% increase for the police department, a 4% increase for parks and recreation, and a 3% increase for infrastructure maintenance. The fiscal year begins on July 1.
        
        Public reaction to the budget has been mixed, with some residents praising the focus on public safety, while others have expressed disappointment about the lack of funding for social programs.
        
        The City Council will meet again next week to discuss implementation plans for the newly approved budget.
        """
    }
    
    # Create classifier
    classifier = ArticleClassifier(model="llama2")
    
    # Classify article
    try:
        result = classifier.classify_article(article)
        
        # Print results
        print("\nClassification result:")
        print(f"Category: {result.get('category', 'Unknown')}")
        print(f"Confidence: {result.get('confidence', 0)}")
        
        if "metadata" in result:
            print("\nMetadata:")
            metadata = result["metadata"]
            print(f"Topic: {metadata.get('topic', '')}")
            print(f"People: {', '.join(metadata.get('people', []))}")
            print(f"Organizations: {', '.join(metadata.get('organizations', []))}")
            print(f"Locations: {', '.join(metadata.get('locations', []))}")
        
        # Print full result as JSON
        print("\nFull result:")
        print(json.dumps(result, indent=2))
        
        return True
    except Exception as e:
        print(f"Error classifying article: {e}")
        return False

if __name__ == "__main__":
    print("===== ArticleClassifier Test =====\n")
    
    # Test Ollama connection
    if test_ollama_connection():
        # Test article classification
        test_article_classification()
    
    print("\n===== Test Complete =====") 