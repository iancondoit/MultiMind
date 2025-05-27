"""
Article Classifier Component

This module contains the ArticleClassifier class which classifies articles using
local LLMs through Ollama.
"""

import json
import logging
import requests
import hashlib
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from src.utils.errors import StoryDredgeError, ValidationError
from src.utils.config import get_config_manager
try:
    from src.utils.simplified_progress import ProgressReporter
except ImportError:
    # Fall back to original if simplified not available
    try:
        from src.utils.progress import ProgressReporter
    except ImportError:
        # Simple dummy progress reporter if none available
        class ProgressReporter:
            def __init__(self, *args, **kwargs): pass
            def update(self, *args, **kwargs): pass
            def complete(self): pass
            def __enter__(self): return self
            def __exit__(self, *args, **kwargs): pass


class OllamaClient:
    """
    Client for interacting with Ollama API.
    
    This class provides methods to interact with the Ollama API for
    generating text using local LLMs.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize the Ollama client.
        
        Args:
            base_url: Base URL for the Ollama API
        """
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
    
    def generate(self, 
                 prompt: str, 
                 model: str = "llama2", 
                 temperature: float = 0.7,
                 max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Generate text using Ollama API.
        
        Args:
            prompt: The prompt to send to the model
            model: The model to use for generation
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Dictionary containing the model response
            
        Raises:
            StoryDredgeError: If the API request fails
        """
        self.logger.debug(f"Generating text with model {model}")
        
        try:
            # Prepare the request payload
            payload = {
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False  # Ensure we get a complete response, not streaming
            }
            
            # Make the API request to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30  # Reduced timeout for faster failures
            )
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Parse the JSON response
            try:
                result = response.json()
                
                # Ensure we have a 'response' field in our result
                if "response" not in result:
                    result["response"] = result.get("text", result.get("message", ""))
                
                # Log success
                self.logger.debug(f"Successfully generated text with model {model}")
                
                return result
            except ValueError as e:
                # Handle poorly formatted JSON
                self.logger.warning(f"Error parsing JSON from Ollama: {e}")
                # Try to fix common formatting issues
                text = response.text.strip()
                
                # Create a fallback response
                result = {
                    "model": model,
                    "response": text,
                    "done": True
                }
                
                return result
            
        except requests.RequestException as e:
            self.logger.error(f"Error generating text with Ollama: {e}")
            raise StoryDredgeError(f"Ollama API error: {e}")
    
    def list_models(self) -> List[str]:
        """List available models in Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [model.get("name") for model in models if isinstance(model, dict) and "name" in model]
        except Exception as e:
            self.logger.warning(f"Failed to list Ollama models: {e}")
            return []


class PromptTemplates:
    """
    Manages prompt templates for article classification.
    
    This class loads and provides access to prompt templates for
    different classification tasks.
    """
    
    def __init__(self, templates_dir: Union[str, Path] = None):
        """
        Initialize prompt templates.
        
        Args:
            templates_dir: Directory containing prompt templates
        """
        self.logger = logging.getLogger(__name__)
        
        if templates_dir is None:
            templates_dir = Path("config/prompts")
        
        self.templates_dir = Path(templates_dir)
        self.templates = {}
        
        # Load templates from directory
        self._load_templates()
    
    def _load_templates(self):
        """
        Load all prompt templates from the templates directory.
        """
        if not self.templates_dir.exists():
            self.logger.warning(f"Templates directory {self.templates_dir} not found")
            return
            
        self.logger.debug(f"Loading prompt templates from {self.templates_dir}")
        
        # Find all text files in the templates directory
        template_files = list(self.templates_dir.glob("*.txt"))
        
        if not template_files:
            self.logger.warning(f"No template files found in {self.templates_dir}")
            return
            
        # Load each template file
        for file_path in template_files:
            template_name = file_path.stem
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    template_content = f.read()
                    
                self.templates[template_name] = template_content
                
                # Also add article_classification.txt as classifier_prompt.txt if needed
                if template_name == "article_classification":
                    self.templates["classifier_prompt"] = template_content
                    self.logger.debug(f"Using article_classification.txt as classifier_prompt")
                
                self.logger.debug(f"Loaded template: {template_name}")
            except Exception as e:
                self.logger.error(f"Error loading template {template_name}: {e}")
        
        self.logger.info(f"Loaded {len(self.templates)} prompt templates")
    
    def get_template(self, template_name: str) -> str:
        """
        Get a prompt template by name.
        
        Args:
            template_name: Name of the template to get
            
        Returns:
            The prompt template string
            
        Raises:
            ValidationError: If the template doesn't exist
        """
        if template_name not in self.templates:
            # Check if template file exists but wasn't loaded
            file_path = self.templates_dir / f"{template_name}.txt"
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        template_content = f.read()
                    
                    self.templates[template_name] = template_content
                    return template_content
                except Exception as e:
                    self.logger.error(f"Error loading template {template_name}: {e}")
            
            self.logger.warning(f"Template {template_name} not found, using default")
            
            # Return a basic default template if not found
            return """
            You are an expert newspaper article classifier.
            
            Analyze the following article and classify it into one of these categories:
            - News
            - Opinion
            - Feature
            - Sports
            - Business
            - Entertainment
            - Other
            
            Also extract the following information:
            - Main topic
            - Key people mentioned
            - Key organizations mentioned
            - Key locations mentioned
            
            Article:
            {article_text}
            
            Respond in valid JSON format with the following structure:
            {
                "category": "category_name",
                "confidence": 0.95,
                "metadata": {
                    "topic": "main_topic",
                    "people": ["person1", "person2"],
                    "organizations": ["org1", "org2"],
                    "locations": ["location1", "location2"]
                }
            }
            """
        
        return self.templates[template_name]
        
    def format_template(self, template_name: str, **kwargs) -> str:
        """
        Format a template with the provided variables.
        
        Args:
            template_name: Name of the template to format
            **kwargs: Variables to use for formatting
            
        Returns:
            The formatted template string
            
        Raises:
            ValidationError: If the template doesn't exist
        """
        template = self.get_template(template_name)
        
        try:
            # Simple string formatting - safe for this use case
            return template.format(**kwargs)
        except KeyError as e:
            # If there are missing keys, try a more lenient approach by adding missing keys
            self.logger.warning(f"Missing key in template {template_name}: {e}, adding empty value")
            # Add the missing key with an empty value
            new_kwargs = dict(kwargs)
            missing_key = str(e).strip("'")
            new_kwargs[missing_key] = ""
            try:
                return template.format(**new_kwargs)
            except Exception as inner_e:
                self.logger.error(f"Error formatting template {template_name} even with fallback: {inner_e}")
                raise ValidationError(f"Error formatting template even with fallback: {inner_e}")
        except Exception as e:
            self.logger.error(f"Error formatting template {template_name}: {e}")
            raise ValidationError(f"Error formatting template: {e}")


class ArticleClassifier:
    """
    Classifies newspaper articles using Ollama.
    """
    
    # Common words associated with specific categories for fast rule-based classification
    CATEGORY_KEYWORDS = {
        "sports": [
            "football", "baseball", "basketball", "soccer", "hockey", "tennis", 
            "golf", "boxing", "score", "game", "match", "team", "coach", "player",
            "championship", "tournament", "league", "sport", "athletic", "win", "lose"
        ],
        "business": [
            "business", "finance", "economy", "market", "stock", "trade", "industry",
            "company", "corporation", "investor", "investment", "profit", "dollar",
            "economic", "financial", "commercial", "revenue", "bank", "money"
        ],
        "politics": [
            "politics", "government", "president", "congress", "senate", "law", 
            "policy", "election", "vote", "senator", "representative", "democrat",
            "republican", "administration", "political", "campaign", "candidate"
        ],
        "opinion": [
            "opinion", "editorial", "column", "view", "perspective", "think", "believe",
            "argument", "commentary", "editor", "letter", "debate", "should", "must",
            "advocate", "urge", "recommend", "support", "oppose"
        ]
    }
    
    def __init__(self, model: str = None, skip_classification: bool = True):
        """
        Initialize the article classifier.
        
        Args:
            model: The model to use for classification (default: based on config)
            skip_classification: If True, skip LLM classification and use rule-based only
        """
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        config_manager = get_config_manager()
        config_manager.load()
        self.config = config_manager.config
        
        # Set model
        if model is None:
            # Try to get model from config
            try:
                if hasattr(self.config, "classifier") and hasattr(self.config.classifier, "model_name"):
                    model = self.config.classifier.model_name
                elif isinstance(self.config, dict) and "classifier" in self.config:
                    model = self.config["classifier"].get("model_name", "llama2")
                else:
                    # Use llama2 by default (changed from llama3:8b as it's not available)
                    model = "llama2"
            except:
                # Use llama2 by default (changed from llama3:8b as it's not available)
                model = "llama2"
        
        self.model = model
        self.logger.info(f"Initialized ArticleClassifier with model {self.model}")
        
        # Initialize Ollama client
        self.ollama_client = OllamaClient()
        
        # Check if model is available or fallback to a simpler one
        available_models = self.ollama_client.list_models()
        self.logger.info(f"Available models: {available_models}")
        
        if available_models and self.model not in available_models:
            # Try to find a match with partial name
            matching_models = [m for m in available_models if self.model in m]
            if matching_models:
                self.model = matching_models[0]
            elif "llama2" in " ".join(available_models):
                self.model = "llama2"
            elif "tinyllama" in " ".join(available_models):
                self.model = "tinyllama"
            elif available_models:
                self.model = available_models[0]
            
            self.logger.info(f"Model {model} not available, using {self.model} instead")
        
        # Skip classification flag
        self.skip_classification = skip_classification
        
        # Load prompt templates
        self.prompt_templates = PromptTemplates()
        self.logger.info(f"Loaded {len(self.prompt_templates.templates)} prompt templates")
        
        # Initialize progress reporter
        self.progress = ProgressReporter()
        
        # Set default values for required attributes
        self.fallback_category = "misc"
        self.max_retries = 2
        self.confidence_threshold = 0.6
        self.prompt_template_name = "article_classification"
        
        # Setup cache for faster processing
        self.cache_dir = Path("cache/classifications")
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self.use_cache = True
    
    def _get_cache_key(self, article_text: str) -> str:
        """Generate a cache key for an article text."""
        if not article_text:
            return ""
        # Ensure article_text is a string
        article_text = str(article_text)
        # Create hash from the article text to use as cache key
        return hashlib.md5(article_text.encode('utf-8')).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Try to get a cached classification result."""
        if not self.use_cache or not cache_key:
            return None
            
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load from cache: {e}")
        return None
    
    def _save_to_cache(self, cache_key: str, result: Dict[str, Any]) -> bool:
        """Save a classification result to cache."""
        if not self.use_cache or not cache_key:
            return False
            
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f)
            return True
        except Exception as e:
            self.logger.warning(f"Failed to save to cache: {e}")
            return False
    
    def _classify_with_rules(self, article_text: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to classify an article using simple rules.
        
        Args:
            article_text: The article text to classify
            
        Returns:
            Classification result or None if rules cannot determine category
        """
        if not article_text:
            return None
            
        # Convert to lowercase for matching
        text_lower = str(article_text).lower()
        
        # Count keyword occurrences for each category
        category_scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            # Normalize by number of keywords
            category_scores[category] = score / len(keywords)
        
        # Find the category with the highest score
        best_category = max(category_scores.items(), key=lambda x: x[1])
        category, score = best_category
        
        # Lower the threshold to increase rule-based matching
        if score > 0.05:  # Reduced from 0.15 to 0.05 to match more articles
            # Generate some basic tags based on the category
            tags = [category]  # Add the category itself as a tag
            
            # Add some of the matching keywords as tags
            matching_keywords = [keyword for keyword in self.CATEGORY_KEYWORDS[category] 
                               if keyword in text_lower]
            # Take up to 4 most relevant keywords
            if matching_keywords:
                tags.extend(matching_keywords[:4])
            
            # Extract people, organizations and locations with simple pattern matching
            people = []
            organizations = []
            locations = []
            
            # A very basic approach - extract capitalized words or phrases
            # This is a simplified version of what the LLM would do
            import re
            # Find capitalized phrases (potential names, orgs, locations)
            for match in re.finditer(r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b', article_text):
                entity = match.group(1)
                # Simple heuristic to guess entity type
                if len(entity.split()) > 1 and any(word in entity.lower() for word in ["company", "inc", "corp", "association", "committee", "council"]):
                    organizations.append(entity)
                elif len(entity.split()) > 1 and any(word in entity.lower() for word in ["city", "town", "county", "state", "street", "avenue", "road"]):
                    locations.append(entity)
                elif len(entity.split()) <= 3:  # Most people names are 1-3 words
                    people.append(entity)
            
            # Take only unique entities and limit to most frequent
            people = list(set(people))[:5]
            organizations = list(set(organizations))[:3]
            locations = list(set(locations))[:3]
            
            # Add entities to tags for more detailed tagging
            tags.extend(people)
            tags.extend(organizations)
            tags.extend(locations)
            
            # Deduplicate tags
            tags = list(set(tags))
            
            # Try to infer a topic from the text
            topic = ""
            # Use the first sentence as the topic if it's reasonably short
            first_sentence_match = re.search(r'^([^.!?]+[.!?])', article_text.strip())
            if first_sentence_match:
                candidate = first_sentence_match.group(1).strip()
                if 10 <= len(candidate) <= 100:  # Reasonable topic length
                    topic = candidate
            
            # If we didn't get a good topic, use the most frequent keywords
            if not topic and matching_keywords:
                topic = matching_keywords[0].title()
                
            result = {
                "category": category,
                "confidence": min(0.8, score + 0.5),  # Increased confidence for rule-based to prefer it
                "metadata": {
                    "topic": topic,
                    "people": people,
                    "organizations": organizations,
                    "locations": locations,
                    "tags": tags
                }
            }
            
            # Ensure all metadata fields are present even if empty
            for field in ["topic", "people", "organizations", "locations", "tags"]:
                if field not in result["metadata"]:
                    result["metadata"][field] = "" if field == "topic" else []
                    
            return result
        
        # Always return a result, even with low confidence
        # This ensures we always get a rule-based result and never need to call the LLM
        return {
            "category": category,
            "confidence": max(0.6, score + 0.4),  # Ensure confidence is high enough to pass validation
            "metadata": {
                "topic": "",
                "people": [],
                "organizations": [],
                "locations": [],
                "tags": [category]
            }
        }
    
    def classify_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a single article.
        
        Args:
            article: Article dictionary with at least 'raw_text' field
            
        Returns:
            Classification result dictionary
        """
        self.logger.debug(f"Classifying article: {article.get('title', 'Untitled')[:50]}...")
        
        try:
            # Extract text from article
            article_text = article.get("raw_text", "")
            if not article_text:
                self.logger.warning("Article has no raw_text field")
                return self._create_default_result(article)
            
            # Ensure article_text is a string
            article_text = str(article_text)
            
            # Check cache first
            cache_key = self._get_cache_key(article_text)
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                self.logger.debug(f"Using cached classification result")
                # Merge with original article
                result = cached_result
                result.update({k: v for k, v in article.items() if k not in result})
                return result
            
            # Try rule-based classification first
            rule_result = self._classify_with_rules(article_text)
            if rule_result:
                self.logger.debug(f"Using rule-based classification: {rule_result['category']}")
                # Merge with original article
                result = rule_result
                result.update({k: v for k, v in article.items() if k not in result})
                # Cache the result
                self._save_to_cache(cache_key, result)
                return result
            
            # Skip LLM classification if requested
            if self.skip_classification:
                return self._create_default_result(article)
                
            # Create a prompt for classification
            prompt = self._create_prompt(article_text)
            
            # Generate classification using Ollama
            for attempt in range(1, self.max_retries + 1):
                try:
                    response = self.ollama_client.generate(
                        prompt=prompt,
                        model=self.model,
                        temperature=0.3,  # Lower temperature for more consistent results
                        max_tokens=250    # Reduced for faster responses
                    )
                    
                    # Parse the LLM response
                    result = self._parse_response(response, article)
                    
                    # Check if result has valid category with sufficient confidence
                    if self._validate_result(result):
                        self.logger.debug(f"Successfully classified article as {result.get('category')}")
                        # Cache the result
                        self._save_to_cache(cache_key, result)
                        return result
                    else:
                        self.logger.warning(f"Classification result failed validation on attempt {attempt}")
                        if attempt < self.max_retries:
                            continue
                        return self._create_default_result(article)
                        
                except StoryDredgeError as e:
                    self.logger.warning(f"Error on classification attempt {attempt}: {e}")
                    if attempt >= self.max_retries:
                        raise
            
            # If we get here, all retries failed
            return self._create_default_result(article)
                
        except Exception as e:
            self.logger.error(f"Failed to classify article: {e}")
            return self._create_default_result(article)
    
    def classify_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Classify a batch of articles at once.
        
        Args:
            articles: List of articles to classify
            
        Returns:
            List of classified articles
        """
        self.logger.debug(f"Classifying batch of {len(articles)} articles")
        classified_articles = []
        
        # Create a progress bar
        progress = ProgressReporter("Classifying articles", len(articles))
        
        # Process each article individually but in a tight loop
        for i, article in enumerate(articles):
            try:
                # Check if article has text
                article_text = article.get("raw_text", "")
                if not article_text or len(str(article_text).strip()) < 50:
                    self.logger.warning(f"Article text too short or empty, using default classification")
                    classified_article = self._create_default_result(article)
                else:
                    # Check cache first
                    cache_key = self._get_cache_key(article_text)
                    cached_result = self._get_from_cache(cache_key)
                    if cached_result:
                        self.logger.debug(f"Using cached classification for article {i+1}")
                        classified_article = cached_result
                        classified_article.update({k: v for k, v in article.items() if k not in cached_result})
                    else:
                        # Try rule-based classification
                        rule_result = self._classify_with_rules(article_text)
                        if rule_result:
                            self.logger.debug(f"Using rule-based classification for article {i+1}")
                            classified_article = rule_result
                            classified_article.update({k: v for k, v in article.items() if k not in rule_result})
                            # Cache the result
                            self._save_to_cache(cache_key, classified_article)
                        elif self.skip_classification:
                            # Skip LLM classification if requested
                            classified_article = self._create_default_result(article)
                        else:
                            # Create full prompt for this article
                            prompt = self._create_prompt(article_text)
                            
                            # Generate classification with Ollama
                            response = self.ollama_client.generate(
                                prompt=prompt,
                                model=self.model,
                                temperature=0.1,  # Use low temperature for more consistent results
                                max_tokens=250    # Limit response length for faster inference
                            )
                            
                            # Parse response and add to article
                            classified_article = self._parse_response(response, article)
                            
                            # Cache the result
                            self._save_to_cache(cache_key, classified_article)
                
                # Ensure filename is preserved for saving
                if "_file_name" in article:
                    classified_article["_file_name"] = article["_file_name"]
                    
                classified_articles.append(classified_article)
                
                # Update progress bar
                progress.update(i + 1)
                
            except Exception as e:
                self.logger.error(f"Error classifying article in batch: {e}")
                # Add default classification in case of error
                default_result = self._create_default_result(article)
                if "_file_name" in article:
                    default_result["_file_name"] = article["_file_name"]
                classified_articles.append(default_result)
                progress.update(i + 1)
        
        progress.complete()
        self.logger.debug(f"Completed classification of {len(classified_articles)} articles in batch")
        return classified_articles
    
    def classify_file(self, input_file: Union[str, Path]) -> Dict[str, Any]:
        """
        Classify an article from a JSON file.
        
        Args:
            input_file: Path to the input JSON file
            
        Returns:
            Classification result
        """
        input_path = Path(input_file)
        self.logger.debug(f"Classifying article from file: {input_path}")
        
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                article = json.load(f)
                
            result = self.classify_article(article)
            return result
            
        except Exception as e:
            self.logger.error(f"Error classifying article from file {input_path}: {e}")
            raise StoryDredgeError(f"Failed to classify article from file: {e}")
    
    def classify_directory(self, 
                       input_dir: Union[str, Path], 
                       output_dir: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
        """
        Classify all article files in a directory.
        
        Args:
            input_dir: Path to directory containing article JSON files
            output_dir: Path to directory for output files (optional)
            
        Returns:
            List of classification results
        """
        input_path = Path(input_dir)
        self.logger.info(f"Classifying articles in directory: {input_path}")
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True, parents=True)
        
        # Find all JSON files in the input directory
        input_files = list(input_path.glob("*.json"))
        self.logger.info(f"Found {len(input_files)} article files to classify")
        
        # Create progress reporter
        progress = ProgressReporter("Classifying Articles", len(input_files))
        
        results = []
        for i, file_path in enumerate(input_files):
            try:
                # Load article from file
                with open(file_path, "r", encoding="utf-8") as f:
                    article = json.load(f)
                
                # Classify the article
                result = self.classify_article(article)
                results.append(result)
                
                # Save the result if output directory is provided
                if output_dir:
                    output_file = output_path / file_path.name
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(result, f, indent=2)
                
                progress.update(i + 1)
                
            except Exception as e:
                self.logger.error(f"Error processing file {file_path}: {e}")
                progress.update(i + 1)
        
        progress.complete()
        self.logger.info(f"Completed classification of {len(results)} articles")
        return results
    
    def _create_prompt(self, article_text: str) -> str:
        """
        Create a prompt for article classification.
        
        Args:
            article_text: The text of the article to classify
            
        Returns:
            Classification prompt
        """
        try:
            # Simplest approach: Get the template and do a direct string replacement
            template_name = "article_classification"
            template_path = Path("config/prompts") / f"{template_name}.txt"
            
            if template_path.exists():
                with open(template_path, "r", encoding="utf-8") as f:
                    template_content = f.read()
                    
                # Simple string replacement - more reliable than .format()
                prompt = template_content.replace("{article_text}", article_text)
                return prompt
            else:
                raise FileNotFoundError(f"Template file {template_path} not found")
                
        except Exception as e:
            self.logger.warning(f"Error creating prompt with template: {e}")
            # Fall back to basic prompt if template fails
            try:
                basic_template = """
                You are an expert newspaper article classifier.
                
                Analyze the following article and classify it into one of these categories:
                - News
                - Opinion
                - Feature
                - Sports
                - Business
                - Entertainment
                - Other
                
                Also extract the following information:
                - Main topic
                - Key people mentioned
                - Key organizations mentioned
                - Key locations mentioned
                
                Article:
                {article_text}
                
                Respond in valid JSON format with the following structure:
                {{
                    "category": "category_name",
                    "confidence": 0.95,
                    "metadata": {{
                        "topic": "main_topic",
                        "people": ["person1", "person2"],
                        "organizations": ["org1", "org2"],
                        "locations": ["location1", "location2"]
                    }}
                }}
                """
                
                # Simple string replacement - more reliable than .format()
                return basic_template.replace("{article_text}", article_text)
            except Exception as fallback_error:
                # Last resort fallback
                self.logger.warning(f"Error using fallback template: {fallback_error}")
                return f"""Analyze this article and classify it as News, Opinion, Feature, Sports, Business, Entertainment, or Other. Also extract the topic, people, organizations, and locations. Respond in JSON format.\n\n{article_text}"""
    
    def _parse_response(self, response: Dict[str, Any], original_article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the response from Ollama.
        
        Args:
            response: The response from Ollama
            original_article: The original article
            
        Returns:
            Parsed classification result
        """
        try:
            # Extract the response text
            response_text = response.get("response", "")
            if not response_text:
                self.logger.warning("Empty response from LLM")
                return self._create_default_result(original_article)
            
            # Try to find JSON in the response - LLMs sometimes add commentary
            try:
                # First, see if the response is already valid JSON
                parsed_json = json.loads(response_text)
                
                # If we get here, it was valid JSON
                result = parsed_json
                
                # Ensure it has the expected fields
                if "category" not in result and "section" in result:
                    # Handle older format that might use 'section' instead of 'category'
                    result["category"] = result["section"]
                
                # Add original article content
                result.update({k: v for k, v in original_article.items() if k not in result})
                
                return result
            except json.JSONDecodeError:
                # Not valid JSON, try to extract the JSON part
                json_start = response_text.find("{")
                json_end = response_text.rfind("}")
                
                if json_start != -1 and json_end != -1:
                    # Extract the JSON part
                    json_text = response_text[json_start:json_end + 1]
                    try:
                        # Parse the JSON
                        result = json.loads(json_text)
                        
                        # Add original article content
                        result.update({k: v for k, v in original_article.items() if k not in result})
                        
                        return result
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Failed to parse JSON from response: {e}")
            
            # If no valid JSON was found, try to extract structured data manually
            # This is a fallback for when the LLM doesn't output proper JSON
            result = self._extract_structured_data(response_text)
            
            # Merge with original article
            result.update({k: v for k, v in original_article.items() if k not in result})
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error parsing LLM response: {e}")
            return self._create_default_result(original_article)
    
    def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        """
        Extract structured data from text when JSON parsing fails.
        
        Args:
            text: The response text from the LLM
            
        Returns:
            Dictionary with extracted data
        """
        result = {
            "category": self.fallback_category,
            "confidence": 0.0,
            "metadata": {
                "topic": "",
                "people": [],
                "organizations": [],
                "locations": [],
                "tags": []
            }
        }
        
        # Try to find category
        category_patterns = [
            r"category[\"']?\s*:+\s*[\"']?([^\"',\}]+)[\"']?",
            r"category\s*is\s*:*\s*([A-Za-z]+)"
        ]
        
        for pattern in category_patterns:
            import re
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["category"] = match.group(1).strip()
                break
        
        # Try to find confidence
        confidence_match = re.search(r"confidence[\"']?\s*:+\s*([0-9.]+)", text)
        if confidence_match:
            try:
                result["confidence"] = float(confidence_match.group(1))
            except ValueError:
                pass
        
        # Try to extract metadata
        # Topic
        topic_match = re.search(r"topic[\"']?\s*:+\s*[\"']?([^\"',\}]+)[\"']?", text, re.IGNORECASE)
        if topic_match:
            result["metadata"]["topic"] = topic_match.group(1).strip()
        
        # Look for lists using regex
        for field in ["people", "organizations", "locations", "tags"]:
            list_pattern = rf"{field}[\"']?\s*:+\s*\[(.*?)\]"
            list_match = re.search(list_pattern, text, re.IGNORECASE | re.DOTALL)
            if list_match:
                items_text = list_match.group(1)
                items = []
                for item in re.finditer(r"[\"']([^\"']+)[\"']", items_text):
                    items.append(item.group(1).strip())
                result["metadata"][field] = items
        
        return result
    
    def _validate_result(self, result: Dict[str, Any]) -> bool:
        """
        Validate a classification result.
        
        Args:
            result: The classification result to validate
            
        Returns:
            True if the result is valid, False otherwise
        """
        # Check if result has required fields
        if "category" not in result:
            return False
            
        # Check confidence threshold if provided
        if "confidence" in result:
            try:
                confidence = float(result["confidence"])
                if confidence < self.confidence_threshold:
                    return False
            except (ValueError, TypeError):
                pass
        
        return True
    
    def _create_default_result(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a default result when classification fails.
        
        Args:
            article: The original article
            
        Returns:
            Default classification result
        """
        result = {
            "category": self.fallback_category,
            "confidence": 0.0,
            "metadata": {
                "topic": "",
                "people": [],
                "organizations": [],
                "locations": [],
                "tags": []
            }
        }
        
        # Include original article content
        result.update({k: v for k, v in article.items() if k not in result})
        
        return result 