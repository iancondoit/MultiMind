"""
Article Splitter Component

This module contains the ArticleSplitter class which identifies and extracts
individual articles from cleaned OCR text.
"""

import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional, Union

from src.utils.errors import StoryDredgeError, IOError, ValidationError
from src.utils.config import get_config_manager
from src.utils.progress import ProgressReporter
from src.utils.common import ensure_directory


class ArticleSplitter:
    """
    Identifies and extracts individual articles from OCR-cleaned newspaper text.
    
    Features:
    - Headline detection using pattern recognition
    - Article boundary identification
    - Metadata extraction (bylines, datelines)
    - OCR quality verification
    """
    
    def __init__(self, aggressive_mode: bool = False):
        """
        Initialize the ArticleSplitter.
        
        Args:
            aggressive_mode: If True, use more aggressive methods to detect headlines
                            and article boundaries. May result in more false positives
                            but fewer missed articles.
        """
        self.logger = logging.getLogger(__name__)
        config_manager = get_config_manager()
        config_manager.load()
        self.config = config_manager.config.splitter
        self.aggressive_mode = aggressive_mode
        
        # Configuration parameters with defaults
        config_dict = self.config.model_dump()
        self.headline_threshold = config_dict.get("headline_detection_threshold", 0.7)
        self.min_article_length = config_dict.get("min_article_length", 100)
        self.max_article_length = config_dict.get("max_article_length", 10000)
        self.enable_fuzzy_boundaries = config_dict.get("enable_fuzzy_boundaries", True)
        self.remove_advertisements = config_dict.get("remove_advertisements", True)
        self.quality_threshold = config_dict.get("quality_threshold", 0.5)
        
        self.logger.debug(f"Initialized ArticleSplitter with aggressive_mode={aggressive_mode}")
    
    def detect_headlines(self, text: str) -> List[Tuple[int, int, str]]:
        """
        Detect headlines in the OCR text.
        
        Args:
            text: The OCR-cleaned text to analyze
            
        Returns:
            List of tuples (start_pos, end_pos, headline_text) for each detected headline
        """
        self.logger.debug("Detecting headlines in text")
        headlines = []
        
        # Common headline patterns
        patterns = [
            # ALL CAPS line not followed by "By" (to avoid bylines)
            r'^\s*([A-Z][A-Z\s\d.,!?:;()\'-]+)$',
            
            # Line with trailing separator (==== or ----)
            r'^\s*(.+?)\s*[=\-]{3,}\s*$',
            
            # Centered text (indented with spaces on both sides)
            r'^\s{3,}(.+?)\s{3,}$'
        ]
        
        # Add more aggressive patterns if in aggressive mode
        if self.aggressive_mode:
            patterns.extend([
                # Initial-uppercase title-like line with reasonable length
                r'^\s*([A-Z][a-zA-Z\s\d.,!?:;()\'-]{10,60})\s*$',
                
                # Any line followed by a byline (e.g. "By John Smith")
                r'^\s*(.+?)\s*$(?=\n\s*By\s+[A-Z][a-z]+\s+[A-Z][a-z]+)',
                
                # Line with trailing newlines
                r'^\s*(.+?)\s*\n\n+'
            ])
        
        # Process line by line
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if not line.strip():
                continue
                
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    headline_text = match.group(1).strip()
                    
                    # Skip if it's too short to be a headline
                    if len(headline_text) < 5:
                        continue
                        
                    # Skip if it looks like a byline or dateline
                    if re.match(r'^By\s+|^[A-Z][a-z]+\s+\d{1,2},\s+\d{4}', headline_text):
                        continue
                    
                    # Calculate start and end positions in original text
                    start_pos = text.find(line)
                    end_pos = start_pos + len(line)
                    
                    headlines.append((start_pos, end_pos, headline_text))
                    self.logger.debug(f"Detected headline: {headline_text}")
                    break
        
        # Sort by position in text
        headlines.sort(key=lambda x: x[0])
        
        self.logger.info(f"Detected {len(headlines)} headlines")
        return headlines
    
    def extract_articles(self, text: str, headlines: List[Tuple[int, int, str]]) -> List[Dict[str, Any]]:
        """
        Extract articles from the OCR text based on detected headlines.
        
        Args:
            text: The OCR-cleaned text to extract articles from
            headlines: List of (start_pos, end_pos, headline_text) tuples
            
        Returns:
            List of article dictionaries with title and raw_text
        """
        self.logger.debug(f"Extracting articles from {len(headlines)} headlines")
        
        articles = []
        
        # Handle case with no headlines - return entire text as one article
        if not headlines:
            self.logger.warning("No headlines detected, creating single article from entire text")
            title = "Untitled Article"
            article = {
                "title": title,
                "raw_text": text.strip()
            }
            if self._is_valid_article(article):
                articles.append(article)
            else:
                # Force add article even if it doesn't meet the normal criteria
                self.logger.info("Adding article despite not meeting criteria (no headlines mode)")
                articles.append(article)
            return articles
        
        # Process each headline to extract articles
        for i, (start_pos, _, headline) in enumerate(headlines):
            # Determine article boundaries
            article_start = start_pos
            
            # Find end of this article (start of next headline or end of text)
            if i < len(headlines) - 1:
                article_end = headlines[i+1][0]
            else:
                article_end = len(text)
            
            # Extract raw article text
            raw_text = text[article_start:article_end].strip()
            
            # Create article dictionary
            article = {
                "title": headline,
                "raw_text": raw_text
            }
            
            # Extract byline if present
            byline_match = re.search(r'By\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', raw_text)
            if byline_match:
                article["byline"] = byline_match.group(1)
            
            # Extract dateline if present
            dateline_match = re.search(r'([A-Z][A-Z\s]+),\s+([A-Za-z\.]+\s+\d{1,2})(?:\s*[-–—]\s*|\s+)', raw_text)
            if dateline_match:
                article["dateline"] = f"{dateline_match.group(1)}, {dateline_match.group(2)}"
            
            # Only add valid articles
            if self._is_valid_article(article):
                articles.append(article)
                self.logger.debug(f"Extracted article: {headline[:30]}...")
            else:
                self.logger.debug(f"Skipped invalid article: {headline[:30]}...")
        
        self.logger.info(f"Extracted {len(articles)} valid articles from {len(headlines)} headlines")
        return articles
    
    def _is_valid_article(self, article: Dict[str, Any]) -> bool:
        """
        Check if an article is valid based on length and content.
        
        Args:
            article: Article dictionary with title and raw_text
            
        Returns:
            True if the article is valid, False otherwise
        """
        # Check minimum length
        if len(article["raw_text"]) < self.min_article_length:
            return False
            
        # Check maximum length
        if len(article["raw_text"]) > self.max_article_length:
            return False
            
        # Skip articles that appear to be advertisements if configured to do so
        if self.remove_advertisements and self._is_advertisement(article["raw_text"]):
            return False
            
        return True
    
    def _is_advertisement(self, text: str) -> bool:
        """
        Determine if the text appears to be an advertisement.
        
        Args:
            text: The article text to check
            
        Returns:
            True if the text appears to be an advertisement, False otherwise
        """
        # Common advertisement indicators
        ad_indicators = [
            r'CLASSIFIED',
            r'ADVERTISEMENT',
            r'\bFOR SALE\b',
            r'\bHELP WANTED\b',
            r'\bWANTED\b',
            r'\bFOR RENT\b',
            r'\bSPECIAL OFFER\b',
            r'\bCALL\s+\d{3}-\d{4}\b',
            r'\$\d+\.\d{2}\b',
            r'\d{1,2}% OFF\b'
        ]
        
        # Count matches
        match_count = 0
        for pattern in ad_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                match_count += 1
                
        # Determine if it's an advertisement based on match count
        # More aggressive if in aggressive mode
        threshold = 1 if self.aggressive_mode else 2
        return match_count >= threshold
    
    def verify_ocr_quality(self, text: str) -> bool:
        """
        Verify the quality of OCR text to determine if it's good enough to process.
        
        Args:
            text: The OCR text to verify
            
        Returns:
            True if the OCR quality appears to be good enough, False otherwise
        """
        self.logger.debug("Verifying OCR quality")
        
        # If text is too short, it's probably not good quality
        if len(text) < 100:
            self.logger.warning("Text too short, OCR quality insufficient")
            return False
        
        # Check for evidence of good structure
        has_paragraphs = text.count('\n\n') > 0
        has_capitalization = re.search(r'[A-Z][a-z]', text) is not None
        has_punctuation = re.search(r'[.,;:!?]', text) is not None
        
        # Calculate a quality score (higher is better)
        quality_score = sum([
            0.4 if has_paragraphs else 0,
            0.3 if has_capitalization else 0,
            0.3 if has_punctuation else 0
        ])
        
        quality_sufficient = quality_score >= self.quality_threshold
        self.logger.debug(f"OCR quality score: {quality_score:.2f}, sufficient: {quality_sufficient}")
        
        return quality_sufficient
    
    def split_file(self, input_file: Union[str, Path], output_dir: Union[str, Path], 
                   metadata: Optional[Dict[str, str]] = None) -> List[Path]:
        """
        Process a file containing OCR-cleaned text and split it into articles.
        
        Args:
            input_file: Path to the input file
            output_dir: Directory to save the extracted articles
            metadata: Optional metadata to include with each article
            
        Returns:
            List of paths to the created article files
        """
        self.logger.info(f"Splitting file: {input_file}")
        
        # Convert to Path objects
        input_file = Path(input_file)
        output_dir = Path(output_dir)
        
        # Ensure the input file exists
        if not input_file.exists():
            self.logger.error(f"Input file does not exist: {input_file}")
            return []
        
        # Create output directory if it doesn't exist
        ensure_directory(output_dir)
        
        # Initialize progress reporting
        progress = ProgressReporter(
            total=100,
            desc="Splitting Articles"
        )
        
        try:
            # Read the input file
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            progress.update(20)  # 20% progress
            
            # Verify OCR quality
            if not self.verify_ocr_quality(text):
                self.logger.warning(f"OCR quality insufficient in {input_file}")
                if not self.aggressive_mode:
                    self.logger.info("Retrying with aggressive mode")
                    # Try again with aggressive mode for low-quality OCR
                    temp_splitter = ArticleSplitter(aggressive_mode=True)
                    return temp_splitter.split_file(input_file, output_dir, metadata)
            
            # Detect headlines
            headlines = self.detect_headlines(text)
            
            progress.update(30)  # 50% progress
            
            # Extract articles
            articles = self.extract_articles(text, headlines)
            
            # Add metadata to each article
            if metadata:
                for article in articles:
                    article.update(metadata)
            
            progress.update(20)  # 70% progress
            
            # Save articles to files
            output_files = []
            for i, article in enumerate(articles):
                # Create filename based on title or index if title not suitable for filename
                safe_title = re.sub(r'[^\w\s-]', '', article["title"][:50]).strip().replace(' ', '_')
                if not safe_title:
                    safe_title = f"article_{i+1}"
                
                output_file = output_dir / f"{safe_title}.json"
                
                # Handle duplicate filenames
                counter = 1
                original_output_file = output_file
                while output_file.exists():
                    output_file = output_dir / f"{original_output_file.stem}_{counter}{original_output_file.suffix}"
                    counter += 1
                
                # Write article to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(article, f, indent=2)
                
                output_files.append(output_file)
                
                # Update progress (remaining 30% spread across all articles)
                progress_step = 30 / max(len(articles), 1)
                progress.update(progress_step)
            
            self.logger.info(f"Split {input_file} into {len(output_files)} articles in {output_dir}")
            return output_files
            
        except Exception as e:
            self.logger.error(f"Error splitting file {input_file}: {e}")
            raise StoryDredgeError(f"Failed to split file {input_file}") from e
        
        finally:
            progress.close() 