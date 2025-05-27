"""
Article Extractor Module

This module extracts individual articles from OCR text.
"""

import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any

# Configure logger
logger = logging.getLogger(__name__)

class ArticleExtractor:
    """
    Extracts individual articles from OCR text.
    
    This class uses various heuristics and pattern recognition
    to identify article boundaries within OCR text from newspapers.
    """
    
    def __init__(self):
        """Initialize the article extractor."""
        self.logger = logging.getLogger(__name__)
        
        # Patterns for identifying article boundaries
        self.headline_patterns = [
            r'([A-Z][A-Z\s]{10,}[A-Z])',  # All caps text of significant length
            r'([A-Z][a-z]+\s[A-Z][a-z]+.{0,20}:)',  # Common headline format with colon
            r'(^|\n)([A-Z][A-Z\s,]{5,}[A-Z])(\n|$)',  # All caps with potential commas at line start/end
        ]
        
        # Combined headline pattern
        self.headline_pattern = '|'.join(self.headline_patterns)
        
        # Minimum article length (characters)
        self.min_article_length = 100
        
        # Maximum article length (characters)
        self.max_article_length = 5000
    
    def extract_articles(self, ocr_text: str) -> List[Dict[str, Any]]:
        """
        Extract articles from OCR text.
        
        Args:
            ocr_text: The OCR text to extract articles from
            
        Returns:
            List of article dictionaries
        """
        self.logger.info("Extracting articles from OCR text")
        
        # Clean the OCR text
        cleaned_text = self._clean_text(ocr_text)
        
        # Find potential headlines
        headlines = self._find_headlines(cleaned_text)
        self.logger.info(f"Found {len(headlines)} potential headlines")
        
        # Extract articles based on headlines
        articles = self._extract_from_headlines(cleaned_text, headlines)
        
        # Filter articles by length
        articles = [a for a in articles if len(a.get('raw_text', '')) >= self.min_article_length]
        
        # Truncate extremely long articles
        for article in articles:
            if len(article['raw_text']) > self.max_article_length:
                article['raw_text'] = article['raw_text'][:self.max_article_length] + "..."
        
        self.logger.info(f"Extracted {len(articles)} articles")
        return articles
    
    def _clean_text(self, text: str) -> str:
        """
        Clean OCR text for better article extraction.
        
        Args:
            text: The OCR text to clean
            
        Returns:
            Cleaned text
        """
        # Handle common OCR errors
        cleaned = text
        
        # Remove multiple consecutive newlines (collapse to max 2)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        # Remove page numbers and headers
        cleaned = re.sub(r'\n\d+\n', '\n', cleaned)
        
        return cleaned
    
    def _find_headlines(self, text: str) -> List[Dict[str, Any]]:
        """
        Find potential headlines in the OCR text.
        
        Args:
            text: The OCR text to search
            
        Returns:
            List of headline dictionaries with position info
        """
        headlines = []
        
        # Find headlines based on patterns
        for pattern in self.headline_patterns:
            for match in re.finditer(pattern, text):
                headline_text = match.group(0).strip()
                
                # Skip too short headlines
                if len(headline_text) < 10:
                    continue
                
                # Create headline info
                headline_info = {
                    'text': headline_text,
                    'start': match.start(),
                    'end': match.end()
                }
                
                headlines.append(headline_info)
        
        # Sort headlines by position
        headlines.sort(key=lambda h: h['start'])
        
        # Filter out overlapping headlines
        filtered_headlines = []
        prev_end = 0
        
        for headline in headlines:
            if headline['start'] >= prev_end:
                filtered_headlines.append(headline)
                prev_end = headline['end']
        
        return filtered_headlines
    
    def _extract_from_headlines(self, text: str, headlines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract articles based on headline positions.
        
        Args:
            text: The OCR text
            headlines: List of headline dictionaries
            
        Returns:
            List of article dictionaries
        """
        articles = []
        
        # Add an artificial endpoint
        text_length = len(text)
        
        # Process each headline
        for i, headline in enumerate(headlines):
            # Determine article boundaries
            start = headline['start']
            
            # End is the start of the next headline or the end of the text
            if i < len(headlines) - 1:
                end = headlines[i + 1]['start']
            else:
                end = text_length
            
            # Extract article text
            article_text = text[start:end].strip()
            
            # Skip too short articles
            if len(article_text) < self.min_article_length:
                continue
            
            # Create article dictionary
            article = {
                'title': headline['text'],
                'raw_text': article_text,
                'position': {
                    'start': start,
                    'end': end
                }
            }
            
            articles.append(article)
        
        return articles
    
    def save_article(self, article: Dict[str, Any], output_path: Path) -> bool:
        """
        Save an article to a JSON file.
        
        Args:
            article: The article to save
            output_path: Path to save the article
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(article, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving article: {e}")
            return False 