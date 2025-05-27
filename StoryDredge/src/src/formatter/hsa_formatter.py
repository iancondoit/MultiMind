"""
HSA Formatter Module

This module transforms classified articles into HSA-ready JSON format,
validates them against the required schema, and organizes them into
the appropriate directory structure.

Features:
- Article validation against HSA schema
- Timestamp formatting standardization
- Output organization by date (YYYY/MM/DD)
- Proper field mapping from classified articles to HSA format
- Extraction of metadata (topic, people, organizations, locations) as tags
- Intelligent mapping of categories to sections
- JSON output formatting with configurable pretty printing
"""

import os
import json
import logging
import traceback
from typing import Dict, List, Tuple, Any, Optional, Set
from pathlib import Path
from datetime import datetime

from src.utils.errors import ValidationError
from src.utils.config import get_config_manager
from src.utils.date_utils import extract_date_from_archive_id, format_iso_date, get_current_timestamp


class HSAFormatter:
    """
    Formats classified articles into HSA-ready JSON format.
    
    This class handles the final stage of the pipeline, transforming
    classified articles into the format required by the Human Story
    Atlas (HSA) system and organizing them by date.
    
    Features:
    - Extracts metadata from classified articles (topic, people, organizations, 
      locations) and adds them as tags
    - Maps article category to the most appropriate HSA section
    - Formats timestamps to ISO 8601 standard
    - Creates a directory structure organized by date (YYYY/MM/DD)
    - Validates articles against HSA requirements
    - Extracts dates from archive.org identifiers like per_atlanta-constitution_1922-01-01_54_203
    """
    
    # Define the required fields for HSA output
    REQUIRED_FIELDS = {
        "headline", "body", "tags", "section", "timestamp",
        "publication", "source_issue", "source_url"
    }
    
    # Optional fields that should be included when available
    OPTIONAL_FIELDS = {
        "byline", "dateline"
    }
    
    # Define valid section values
    VALID_SECTIONS = {
        "news", "sports", "business", "entertainment", "opinion",
        "local", "national", "international", "politics", "science",
        "health", "technology", "education", "weather", "obituaries",
        "lifestyle", "culture", "arts", "food", "travel", "other"
    }
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the HSAFormatter.
        
        Args:
            output_dir: Directory for storing HSA-ready output. If None,
                        defaults to "output/hsa-ready"
        """
        # Set up a dedicated formatter logger
        self.logger = logging.getLogger("formatter")
        
        # Create a file handler if it doesn't exist
        if not self.logger.handlers:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(log_dir / "formatter.log")
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(file_handler)
            
            # Add console handler for INFO and above
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(logging.Formatter(
                '%(levelname)s - %(message)s'
            ))
            self.logger.addHandler(console_handler)
            
            self.logger.setLevel(logging.DEBUG)
        
        # Default configuration
        self.pretty_print = True
        self.strict_validation = False  # New option to control validation strictness
        self.add_default_values = True  # New option to add default values for missing fields
        
        # Try to load configuration if available
        try:
            config_manager = get_config_manager()
            config_manager.load()
                
            # The config might be a dict or an object with attributes
            if hasattr(config_manager.config, 'formatter'):
                formatter_config = config_manager.config.formatter
                if hasattr(formatter_config, 'pretty_print'):
                    self.pretty_print = formatter_config.pretty_print
                if hasattr(formatter_config, 'strict_validation'):
                    self.strict_validation = formatter_config.strict_validation
                if hasattr(formatter_config, 'add_default_values'):
                    self.add_default_values = formatter_config.add_default_values
            elif isinstance(config_manager.config, dict) and 'formatter' in config_manager.config:
                formatter_config = config_manager.config['formatter']
                if isinstance(formatter_config, dict):
                    if 'pretty_print' in formatter_config:
                        self.pretty_print = formatter_config['pretty_print']
                    if 'strict_validation' in formatter_config:
                        self.strict_validation = formatter_config['strict_validation']
                    if 'add_default_values' in formatter_config:
                        self.add_default_values = formatter_config['add_default_values']
        except Exception as e:
            # If configuration loading fails, use defaults
            self.logger.warning(f"Failed to load configuration: {e}. Using defaults.")
        
        # Set output directory
        base_output_dir = Path(output_dir) if output_dir else Path("output")
        
        # Check if the output_dir already ends with 'hsa-ready'
        if base_output_dir.name == "hsa-ready":
            self.output_dir = base_output_dir
        else:
            self.output_dir = base_output_dir / "hsa-ready"
            
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        self.logger.info(f"HSA Formatter initialized with output directory: {self.output_dir}")
        self.logger.info(f"Configuration: pretty_print={self.pretty_print}, strict_validation={self.strict_validation}, add_default_values={self.add_default_values}")
    
    def validate_article(self, article: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate an article against HSA requirements.
        
        Args:
            article: The article to validate
            
        Returns:
            A tuple containing:
            - bool: True if valid, False otherwise
            - List[str]: List of error messages if invalid
        """
        errors = []
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in article:
                errors.append(f"Missing required field: {field}")
            elif article[field] is None or article[field] == "":
                if field != "byline":  # byline can be empty
                    errors.append(f"Required field is empty: {field}")
        
        # Log the validation process for debugging
        self.logger.debug(f"Validating article with headline: {article.get('headline', 'UNKNOWN')}")
        self.logger.debug(f"Fields present: {', '.join(article.keys())}")
        
        # Validate section if present
        if "section" in article and article["section"] not in self.VALID_SECTIONS:
            errors.append(f"Invalid section: {article['section']}. Must be one of: {', '.join(self.VALID_SECTIONS)}")
        
        # Validate tags if present
        if "tags" in article:
            if not isinstance(article["tags"], list):
                errors.append("Tags must be a list")
            elif len(article["tags"]) == 0:
                self.logger.warning("Tags list is empty, should have at least one tag")
        
        # Validate timestamp if present
        if "timestamp" in article:
            try:
                # Just test if it can be formatted
                formatted_timestamp = self.format_timestamp(article["timestamp"])
                if formatted_timestamp != article["timestamp"]:
                    self.logger.debug(f"Timestamp reformatted: {article['timestamp']} -> {formatted_timestamp}")
            except ValueError as e:
                errors.append(f"Invalid timestamp format: {article['timestamp']} - {str(e)}")
        
        if errors:
            self.logger.warning(f"Article validation errors: {'; '.join(errors)}")
        
        return len(errors) == 0, errors
    
    def format_timestamp(self, timestamp: str) -> str:
        """
        Format the timestamp in ISO 8601 format with UTC timezone.
        
        Args:
            timestamp: The timestamp string to format
            
        Returns:
            Formatted timestamp string in the format "YYYY-MM-DDTHH:MM:SS.000Z"
        """
        # Handle already correctly formatted timestamps
        if timestamp.endswith("Z") and "T" in timestamp:
            return timestamp
        
        try:
            # Try to parse the timestamp
            if " " in timestamp:
                # Assume format is "YYYY-MM-DD HH:MM:SS"
                dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            else:
                # Assume format is "YYYY-MM-DD"
                dt = datetime.strptime(timestamp, "%Y-%m-%d")
            
            # Format in ISO 8601 format
            return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            
        except ValueError as e:
            # If parsing fails, try to extract year-month-day from the timestamp string
            self.logger.warning(f"Invalid timestamp format: {timestamp}, attempting to extract date")
            
            # Try to extract a date using regular expressions or other methods
            try:
                # Extract from source_issue if available
                if hasattr(self, "current_article") and "source_issue" in self.current_article:
                    source_issue = self.current_article["source_issue"]
                    date_str = extract_date_from_archive_id(source_issue)
                    if date_str:
                        self.logger.info(f"Extracted date from source_issue: {date_str}")
                        return f"{date_str}T00:00:00.000Z"
            except Exception:
                pass
            
            # Use current date as a last resort
            current_date = get_current_timestamp()
            self.logger.warning(f"Using current date as fallback: {current_date}")
            return current_date
    
    def get_output_path(self, article: Dict[str, Any]) -> Path:
        """
        Determine the output path for an article based on its timestamp.
        
        Args:
            article: The article to get the path for
            
        Returns:
            Path object for where the article should be saved
        """
        # Format timestamp if not already in the right format
        if "timestamp" not in article:
            self.logger.warning("Article has no timestamp, using default")
            timestamp = get_current_timestamp()
        else:
            timestamp = self.format_timestamp(article["timestamp"])
        
        # Extract date components from timestamp
        try:
            date_part = timestamp.split("T")[0]
            year, month, day = date_part.split("-")
            
            # Create directory structure: YYYY/MM/DD/
            output_dir = self.output_dir / year / month / day
            output_dir.mkdir(exist_ok=True, parents=True)
            
            # Create a unique filename based on headline and timestamp
            headline = article.get("headline", "untitled")
            # Sanitize headline for filename
            sanitized_headline = "".join(c if c.isalnum() or c in " -_" else "_" for c in headline)
            sanitized_headline = sanitized_headline.strip().lower().replace(" ", "_")[:50]
            
            # Add a timestamp component to ensure uniqueness
            timestamp_part = datetime.now().strftime("%H%M%S")
            filename = f"{sanitized_headline}_{timestamp_part}.json"
            
            return output_dir / filename
            
        except Exception as e:
            self.logger.error(f"Error creating output path: {e}")
            self.logger.error(f"Timestamp: {timestamp}")
            
            # Fallback to a default path
            fallback_dir = self.output_dir / "fallback"
            fallback_dir.mkdir(exist_ok=True, parents=True)
            
            # Use a timestamp-based filename
            fallback_filename = f"article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            self.logger.warning(f"Using fallback path: {fallback_dir / fallback_filename}")
            return fallback_dir / fallback_filename
    
    def format_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format an article for HSA output.
        
        Args:
            article: The article to format
            
        Returns:
            The formatted article
        """
        self.current_article = article  # Store the current article for reference in other methods
        
        # Log the input article for debugging
        self.logger.debug(f"Formatting article: {article.get('title', article.get('headline', 'UNKNOWN'))}")
        
        # Create a new dictionary for the formatted article
        formatted = {}
        
        # Map fields from the input article to the HSA format
        
        # 1. Handle headline (might be in 'title' or 'headline')
        if "headline" in article:
            formatted["headline"] = article["headline"]
        elif "title" in article:
            formatted["headline"] = article["title"]
        else:
            formatted["headline"] = "Untitled Article"
            self.logger.warning("Article has no headline or title, using default")
        
        # 2. Handle body (might be in 'body', 'raw_text', or 'content')
        if "body" in article:
            formatted["body"] = article["body"]
        elif "raw_text" in article:
            formatted["body"] = article["raw_text"]
        elif "content" in article:
            formatted["body"] = article["content"]
        elif "text" in article:
            formatted["body"] = article["text"]
        else:
            formatted["body"] = "No content available"
            self.logger.warning("Article has no body content, using default")
        
        # 3. Extract tags from various metadata fields
        tags = set()
        
        # First, copy any existing tags
        if "tags" in article and isinstance(article["tags"], list):
            tags.update(article["tags"])
        
        # Add section/category as a tag if available
        if "section" in article and article["section"]:
            tags.add(article["section"])
        elif "category" in article and article["category"]:
            tags.add(article["category"])
        
        # Add other metadata as tags
        meta_fields = ["topic", "people", "organizations", "locations", "keywords"]
        for field in meta_fields:
            # Check if the field exists directly in the article
            if field in article:
                if isinstance(article[field], list):
                    tags.update(article[field])
                elif isinstance(article[field], str) and article[field]:
                    tags.add(article[field])
            
            # Also check if the field exists in the metadata structure
            if "metadata" in article and isinstance(article["metadata"], dict) and field in article["metadata"]:
                if isinstance(article["metadata"][field], list):
                    tags.update(article["metadata"][field])
                elif isinstance(article["metadata"][field], str) and article["metadata"][field]:
                    tags.add(article["metadata"][field])
        
        # Also check for tags in the metadata structure
        if "metadata" in article and isinstance(article["metadata"], dict) and "tags" in article["metadata"]:
            if isinstance(article["metadata"]["tags"], list):
                tags.update(article["metadata"]["tags"])
            elif isinstance(article["metadata"]["tags"], str) and article["metadata"]["tags"]:
                tags.add(article["metadata"]["tags"])
        
        # If no tags were found, add a default tag
        if not tags and "section" in formatted:
            tags.add(formatted["section"])
        elif not tags:
            tags.add("news")  # Default tag
        
        formatted["tags"] = list(tags)
        
        # 4. Map or guess section
        if "section" in article and article["section"]:
            section = article["section"]
        elif "category" in article and article["category"]:
            section = self._map_category_to_section(article["category"])
        else:
            # Try to guess section from tags
            for tag in tags:
                section = self._map_category_to_section(tag)
                if section:
                    break
            else:
                section = "news"  # Default section
        
        # Ensure section is valid
        if section in self.VALID_SECTIONS:
            formatted["section"] = section
        else:
            formatted["section"] = "other"
            self.logger.warning(f"Invalid section: {section}, using 'other'")
        
        # 5. Handle timestamp
        if "timestamp" in article and article["timestamp"]:
            # Format the timestamp
            formatted["timestamp"] = self.format_timestamp(article["timestamp"])
        elif "date" in article and article["date"]:
            # Format the date
            formatted["timestamp"] = self.format_timestamp(article["date"])
        elif "source_issue" in article:
            # Try to extract date from source_issue
            try:
                date_str = extract_date_from_archive_id(article["source_issue"])
                if date_str:
                    formatted["timestamp"] = f"{date_str}T00:00:00.000Z"
                else:
                    formatted["timestamp"] = get_current_timestamp()
                    self.logger.warning("Could not extract date from source_issue, using current date")
            except Exception as e:
                formatted["timestamp"] = get_current_timestamp()
                self.logger.warning(f"Error extracting date: {e}, using current date")
        else:
            # Use current date as fallback
            formatted["timestamp"] = get_current_timestamp()
            self.logger.warning("No date or timestamp found, using current date")
        
        # 6. Handle publication
        if "publication" in article and article["publication"]:
            formatted["publication"] = article["publication"]
        elif "source_issue" in article:
            # Try to extract publication from source_issue
            try:
                # Example: per_atlanta-constitution_1922-01-01_54_203 → Atlanta Constitution
                parts = article["source_issue"].split('_')
                if len(parts) > 1:
                    publication_part = parts[1].replace('-', ' ').title()
                    formatted["publication"] = publication_part
                else:
                    formatted["publication"] = "Unknown Publication"
                    self.logger.warning("Could not extract publication from source_issue")
            except Exception:
                formatted["publication"] = "Unknown Publication"
                self.logger.warning("Error extracting publication from source_issue")
        else:
            formatted["publication"] = "Unknown Publication"
            self.logger.warning("No publication information found")
        
        # 7. Handle source_issue
        if "source_issue" in article:
            formatted["source_issue"] = article["source_issue"]
        else:
            formatted["source_issue"] = "unknown_source"
            self.logger.warning("No source_issue found")
        
        # 8. Handle source_url
        if "source_url" in article:
            formatted["source_url"] = article["source_url"]
        elif "source_issue" in article:
            # Construct a URL from the source_issue
            formatted["source_url"] = f"https://archive.org/details/{article['source_issue']}"
        else:
            formatted["source_url"] = "https://archive.org"
            self.logger.warning("No source_url or source_issue found")
        
        # 9. Handle byline
        if "byline" in article:
            formatted["byline"] = article["byline"]
        elif "author" in article:
            formatted["byline"] = article["author"]
        else:
            # Check if the headline contains a byline pattern like "BY JOHN SMITH"
            headline = formatted.get("headline", "")
            if headline.upper().startswith("BY "):
                formatted["byline"] = headline[3:].strip()
                # Update the headline to remove the byline part
                if " " in formatted["byline"] and len(formatted["byline"].split()) >= 2:
                    self.logger.info(f"Extracted byline from headline: {formatted['byline']}")
                    # Find the first actual sentence in the body to use as headline
                    body = formatted.get("body", "")
                    sentences = body.split('.')
                    if sentences and len(sentences[0]) > 10:
                        formatted["headline"] = sentences[0].strip()
                        self.logger.info(f"Replaced headline with first sentence: {formatted['headline']}")
            else:
                formatted["byline"] = ""
        
        # 10. Handle dateline (optional)
        if "dateline" in article:
            formatted["dateline"] = article["dateline"]
        
        # Log the formatted article
        self.logger.debug(f"Formatted article: {formatted['headline']}")
        
        return formatted
    
    def _map_category_to_section(self, category: str) -> Optional[str]:
        """
        Map a category string to a valid HSA section.
        
        Args:
            category: The category string from classification
            
        Returns:
            A valid section name or None if no mapping is found
        """
        # Lowercase and strip the category
        category = category.lower().strip()
        
        # Direct mappings
        direct_mappings = {
            "news": "news",
            "sports": "sports",
            "opinion": "opinion", 
            "business": "business",
            "entertainment": "entertainment",
            "editorial": "opinion",
            "politics": "politics",
            "technology": "technology",
            "science": "science",
            "health": "health",
            "education": "education",
            "local": "local",
            "national": "national",
            "international": "international",
            "weather": "weather",
            "obituaries": "obituaries",
            "lifestyle": "lifestyle",
            "culture": "culture",
            "arts": "arts",
            "food": "food",
            "travel": "travel"
        }
        
        if category in direct_mappings:
            return direct_mappings[category]
            
        # Partial matching for complex categories
        if "sport" in category:
            return "sports"
        elif "opin" in category or "editor" in category:
            return "opinion"
        elif "business" in category or "finance" in category:
            return "business"
        elif "entertainment" in category or "movie" in category or "film" in category:
            return "entertainment"
        elif "world" in category or "global" in category or "foreign" in category:
            return "international"
        elif "tech" in category:
            return "technology"
        elif "health" in category or "medical" in category:
            return "health"
        elif "edu" in category or "school" in category:
            return "education"
        elif "art" in category:
            return "arts"
        elif "food" in category or "recipe" in category or "dining" in category:
            return "food"
        elif "travel" in category or "vacation" in category or "tourism" in category:
            return "travel"
        elif "polit" in category or "election" in category or "government" in category:
            return "politics"
        elif "local" in category or "community" in category:
            return "local"
        elif "nation" in category:
            return "national"
            
        # No mapping found
        self.logger.debug(f"No section mapping found for category: {category}")
        return "news"  # Default to news instead of None
    
    def save_article(self, article: Dict[str, Any]) -> Optional[Path]:
        """
        Save an article to its appropriate output location.
        
        Args:
            article: The article to save
            
        Returns:
            Path to the saved file, or None if validation failed
        """
        # First, format the article
        try:
            formatted_article = self.format_article(article)
            
            # Validate the formatted article
            valid, errors = self.validate_article(formatted_article)
            
            if not valid and self.strict_validation:
                error_msg = "; ".join(errors)
                self.logger.error(f"Article validation failed (strict mode): {error_msg}")
                return None
            elif not valid:
                self.logger.warning(f"Article validation issues (non-strict mode): {'; '.join(errors)}")
                
                # Try to fix missing fields
                if self.add_default_values:
                    for field in self.REQUIRED_FIELDS:
                        if field not in formatted_article or not formatted_article[field]:
                            if field == "headline":
                                formatted_article["headline"] = "Untitled Article"
                            elif field == "body":
                                formatted_article["body"] = "No content available"
                            elif field == "tags":
                                formatted_article["tags"] = ["news"]
                            elif field == "section":
                                formatted_article["section"] = "news"
                            elif field == "timestamp":
                                formatted_article["timestamp"] = get_current_timestamp()
                            elif field == "publication":
                                formatted_article["publication"] = "Unknown Publication"
                            elif field == "source_issue":
                                formatted_article["source_issue"] = "unknown_source"
                            elif field == "source_url":
                                formatted_article["source_url"] = "https://archive.org"
                    
                    self.logger.info("Added default values for missing fields")
            
            # Determine output path
            output_path = self.get_output_path(formatted_article)
            
            # Save the article
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    if self.pretty_print:
                        json.dump(formatted_article, f, indent=2, ensure_ascii=False)
                    else:
                        json.dump(formatted_article, f, ensure_ascii=False)
                
                self.logger.info(f"Saved article to {output_path}")
                return output_path
            
            except Exception as e:
                self.logger.error(f"Error saving article: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error formatting article: {e}")
            self.logger.error(traceback.format_exc())
            return None
    
    def process_batch(self, articles: List[Dict[str, Any]]) -> List[Path]:
        """
        Process a batch of articles.
        
        Args:
            articles: List of articles to process
            
        Returns:
            List of paths to the saved files (successful saves only)
        """
        self.logger.info(f"Processing batch of {len(articles)} articles")
        
        results = []
        for i, article in enumerate(articles):
            try:
                self.logger.debug(f"Processing article {i+1}/{len(articles)}")
                result = self.save_article(article)
                if result:
                    results.append(result)
                    if (i + 1) % 100 == 0:
                        self.logger.info(f"Processed {i+1}/{len(articles)} articles ({len(results)} successful)")
            except Exception as e:
                self.logger.error(f"Error processing article {i+1}: {e}")
        
        self.logger.info(f"Successfully processed {len(results)} of {len(articles)} articles")
        return results
    
    def process_directory(self, input_dir: str, recursive: bool = False) -> List[Path]:
        """
        Process all JSON files in a directory.
        
        Args:
            input_dir: Directory containing article JSON files
            recursive: Whether to recursively process subdirectories
            
        Returns:
            List of paths to the saved files (successful saves only)
        """
        input_path = Path(input_dir)
        if not input_path.exists() or not input_path.is_dir():
            self.logger.error(f"Invalid input directory: {input_dir}")
            return []
        
        self.logger.info(f"Processing articles from directory: {input_dir}")
        
        results = []
        pattern = "**/*.json" if recursive else "*.json"
        
        file_paths = list(input_path.glob(pattern))
        self.logger.info(f"Found {len(file_paths)} JSON files")
        
        for i, file_path in enumerate(file_paths):
            if file_path.is_file():
                try:
                    self.logger.debug(f"Processing file {i+1}/{len(file_paths)}: {file_path}")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        article = json.load(f)
                    
                    result = self.save_article(article)
                    if result:
                        results.append(result)
                        
                    if (i + 1) % 100 == 0:
                        self.logger.info(f"Processed {i+1}/{len(file_paths)} files ({len(results)} successful)")
                
                except json.JSONDecodeError:
                    self.logger.error(f"Invalid JSON in file {file_path}")
                except Exception as e:
                    self.logger.error(f"Error processing file {file_path}: {e}")
        
        self.logger.info(f"Successfully processed {len(results)} articles from {input_dir}")
        return results
    
    def format_issue(self, issue_id: str, classified_dir: Path) -> List[Path]:
        """
        Process all classified articles from an issue and format them for HSA output.
        
        Args:
            issue_id: The archive.org identifier for the issue
            classified_dir: Directory containing classified article JSON files
            
        Returns:
            List of paths to the saved files (successful saves only)
        """
        self.logger.info(f"Formatting articles from issue {issue_id}")
        
        if not classified_dir.exists() or not classified_dir.is_dir():
            self.logger.error(f"Invalid classified directory: {classified_dir}")
            return []
        
        # Get all JSON files in the classified directory
        article_files = list(classified_dir.glob("*.json"))
        self.logger.info(f"Found {len(article_files)} classified articles")
        
        results = []
        for i, article_file in enumerate(article_files):
            try:
                # Read the classified article
                with open(article_file, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                
                # Add source information if not already present
                if "source_issue" not in article:
                    article["source_issue"] = issue_id
                
                # Extract publication from issue_id if not present
                if "publication" not in article:
                    # Example: per_atlanta-constitution_1922-01-01_54_203 → The Atlanta Constitution
                    parts = issue_id.split('_')
                    if len(parts) > 1:
                        publication_part = parts[1].replace('-', ' ').title()
                        article["publication"] = publication_part
                
                # Format and save the article
                result = self.save_article(article)
                if result:
                    results.append(result)
                    if (i + 1) % 50 == 0:
                        self.logger.info(f"Processed {i+1}/{len(article_files)} articles from issue")
                
            except json.JSONDecodeError:
                self.logger.error(f"Invalid JSON in file {article_file}")
            except Exception as e:
                self.logger.error(f"Error processing file {article_file}: {e}")
                self.logger.debug(traceback.format_exc())
        
        success_rate = (len(results) / len(article_files)) * 100 if article_files else 0
        self.logger.info(f"Successfully formatted {len(results)} of {len(article_files)} articles from issue {issue_id} ({success_rate:.1f}%)")
        return results 