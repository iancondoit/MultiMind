"""
Tests for the ArticleClassifier class.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.classifier.article_classifier import ArticleClassifier, OllamaClient


class TestArticleClassifier:
    """Test cases for ArticleClassifier."""
    
    def test_init(self):
        """Test initialization of ArticleClassifier."""
        with patch('src.classifier.article_classifier.get_config_manager') as mock_config:
            # Mock the configuration
            mock_config.return_value.config.classifier.model_dump.return_value = {
                "model_name": "llama2",
                "batch_size": 10,
                "concurrency": 2,
                "confidence_threshold": 0.6,
                "fallback_section": "miscellaneous",
                "prompt_template": "article_classification"
            }
            mock_config.return_value.load = MagicMock()
            
            classifier = ArticleClassifier()
            assert classifier.model == "llama2"  # Default model
            
            classifier = ArticleClassifier(model="llama3")
            assert classifier.model == "llama3"
    
    @patch('src.classifier.article_classifier.OllamaClient.generate')
    def test_classify_article(self, mock_generate):
        """Test classification of a single article."""
        # Setup mock response
        mock_response = {
            "model": "llama2",
            "response": json.dumps({
                "category": "News",
                "confidence": 0.95,
                "metadata": {
                    "topic": "Local Government",
                    "people": ["John Smith"],
                    "organizations": ["San Antonio City Council"],
                    "locations": ["San Antonio"]
                }
            }),
            "done": True
        }
        
        mock_generate.return_value = mock_response
        
        # Create classifier and article
        with patch('src.classifier.article_classifier.get_config_manager') as mock_config:
            mock_config.return_value.config.classifier.model_dump.return_value = {}
            mock_config.return_value.load = MagicMock()
            
            classifier = ArticleClassifier()
            article = {
                "title": "LOCAL COUNCIL APPROVES NEW BUDGET",
                "raw_text": "The San Antonio City Council yesterday approved..."
            }
            
            # Test classification
            result = classifier.classify_article(article)
            
            # Verify result
            assert result["category"] == "News"
            assert result["confidence"] == 0.95
            assert result["metadata"]["topic"] == "Local Government"
            assert "John Smith" in result["metadata"]["people"]
            assert "San Antonio City Council" in result["metadata"]["organizations"]
            assert "San Antonio" in result["metadata"]["locations"]
            
            # Verify original article data is preserved
            assert result["title"] == "LOCAL COUNCIL APPROVES NEW BUDGET"
            assert result["raw_text"] == "The San Antonio City Council yesterday approved..."
            
            # Verify ollama client was called with proper args
            mock_generate.assert_called_once()
            args, kwargs = mock_generate.call_args
            assert kwargs["model"] == "llama2"
            assert "The San Antonio City Council" in kwargs["prompt"]
    
    @patch('src.classifier.article_classifier.OllamaClient.generate')
    def test_classify_article_error(self, mock_generate):
        """Test handling of classifier errors."""
        mock_generate.side_effect = Exception("Ollama error")
        
        # Create classifier and article
        with patch('src.classifier.article_classifier.get_config_manager') as mock_config:
            mock_config.return_value.config.classifier.model_dump.return_value = {
                "fallback_section": "unknown"
            }
            mock_config.return_value.load = MagicMock()
            
            classifier = ArticleClassifier()
            article = {
                "title": "TEST",
                "raw_text": "Test content"
            }
            
            # Should handle errors gracefully
            result = classifier.classify_article(article)
            
            # Should return original article with default values
            assert result["title"] == "TEST"
            assert result["raw_text"] == "Test content"
            assert result["category"] == "unknown"  # Default value
            assert result["confidence"] == 0.0
    
    @patch('src.classifier.article_classifier.OllamaClient.generate')
    def test_classify_batch(self, mock_generate):
        """Test batch classification of multiple articles."""
        # Setup mock responses
        mock_responses = [
            {
                "model": "llama2",
                "response": json.dumps({
                    "category": "News",
                    "confidence": 0.95,
                    "metadata": {
                        "topic": "Article 1 Topic",
                        "people": ["Person 1"],
                        "organizations": [],
                        "locations": []
                    }
                }),
                "done": True
            },
            {
                "model": "llama2",
                "response": json.dumps({
                    "category": "Opinion",
                    "confidence": 0.9,
                    "metadata": {
                        "topic": "Article 2 Topic", 
                        "people": [],
                        "organizations": ["Org 1"],
                        "locations": []
                    }
                }),
                "done": True
            }
        ]
        
        mock_generate.side_effect = mock_responses
        
        # Create classifier and articles
        with patch('src.classifier.article_classifier.get_config_manager') as mock_config:
            mock_config.return_value.config.classifier.model_dump.return_value = {}
            mock_config.return_value.load = MagicMock()
            
            # Mock progress reporter
            with patch('src.classifier.article_classifier.ProgressReporter') as mock_progress:
                mock_progress_instance = MagicMock()
                mock_progress.return_value = mock_progress_instance
                
                classifier = ArticleClassifier()
                articles = [
                    {"title": "A1", "raw_text": "Article 1 content"},
                    {"title": "A2", "raw_text": "Article 2 content"}
                ]
                
                # Test batch classification
                results = classifier.classify_batch(articles)
                
                # Verify results
                assert len(results) == 2
                assert results[0]["category"] == "News"
                assert results[0]["title"] == "A1"
                assert results[1]["category"] == "Opinion"
                assert results[1]["title"] == "A2"
                
                # Verify ollama was called twice (once per article)
                assert mock_generate.call_count == 2
    
    def test_parse_response(self):
        """Test parsing of LLM response."""
        with patch('src.classifier.article_classifier.get_config_manager') as mock_config:
            mock_config.return_value.config.classifier.model_dump.return_value = {}
            mock_config.return_value.load = MagicMock()
            
            classifier = ArticleClassifier()
            
            # Test valid JSON response
            response = {
                "response": '{"category": "News", "confidence": 0.95, "metadata": {"topic": "Test"}}'
            }
            original_article = {"title": "Original"}
            
            result = classifier._parse_response(response, original_article)
            
            assert result["category"] == "News"
            assert result["confidence"] == 0.95
            assert result["title"] == "Original"
            
            # Test invalid JSON with text before/after
            messy_response = {
                "response": 'Here is the result:\n{"category": "News", "confidence": 0.95}\nEnd of response'
            }
            result = classifier._parse_response(messy_response, {"title": "Original"})
            
            assert result["category"] == "News"  # Should extract the JSON part
            assert result["title"] == "Original"
            
            # Test completely invalid response
            invalid_response = {
                "response": "This is not JSON at all"
            }
            result = classifier._parse_response(invalid_response, {"title": "Original"})
            
            assert result["title"] == "Original"  # Should fall back to original
            assert "category" in result  # Should add default fields
    
    def test_create_prompt(self):
        """Test prompt creation for classification."""
        with patch('src.classifier.article_classifier.get_config_manager') as mock_config:
            mock_config.return_value.config.classifier.model_dump.return_value = {}
            mock_config.return_value.load = MagicMock()
            
            # Mock template
            with patch('src.classifier.article_classifier.PromptTemplates') as mock_templates:
                mock_templates_instance = MagicMock()
                mock_templates.return_value = mock_templates_instance
                mock_templates_instance.format_template.return_value = "Test prompt for article: {article_text}"
                
                classifier = ArticleClassifier()
                
                prompt = classifier._create_prompt("Article content goes here")
                
                # Verify prompt creation
                mock_templates_instance.format_template.assert_called_once()
                assert mock_templates_instance.format_template.call_args[1]["article_text"] == "Article content goes here"
                
                # Test error handling - simulate a template error
                mock_templates_instance.format_template.side_effect = Exception("Template error")
                
                # The fallback should work
                mock_templates_instance.get_template.return_value = "Fallback template: {article_text}"
                
                prompt = classifier._create_prompt("Fallback content")
                assert "Fallback template: Fallback content" == prompt
                
                # Test double failure - both primary and fallback fail
                mock_templates_instance.get_template.side_effect = Exception("Fallback error too")
                
                prompt = classifier._create_prompt("Last resort content")
                assert "Last resort content" in prompt
                assert "expert newspaper article classifier" in prompt.lower()
    
    def test_extract_structured_data(self):
        """Test extraction of structured data from text."""
        with patch('src.classifier.article_classifier.get_config_manager') as mock_config:
            mock_config.return_value.config.classifier.model_dump.return_value = {
                "fallback_section": "unknown"
            }
            mock_config.return_value.load = MagicMock()
            
            classifier = ArticleClassifier()
            
            # Test with well-formatted data
            text = """
            The category is: News
            confidence: 0.95
            topic: "Local Government"
            people: ["John Smith", "Jane Doe"]
            organizations: ["City Council"]
            locations: ["San Antonio"]
            """
            
            result = classifier._extract_structured_data(text)
            
            assert result["category"] == "News"
            assert result["confidence"] == 0.95
            assert result["metadata"]["topic"] == "Local Government"
            assert "John Smith" in result["metadata"]["people"]
            assert "City Council" in result["metadata"]["organizations"]
    
    def test_validate_result(self):
        """Test validation of classification results."""
        with patch('src.classifier.article_classifier.get_config_manager') as mock_config:
            mock_config.return_value.config.classifier.model_dump.return_value = {
                "confidence_threshold": 0.6
            }
            mock_config.return_value.load = MagicMock()
            
            classifier = ArticleClassifier()
            
            # Valid result with high confidence
            valid_result = {
                "category": "News",
                "confidence": 0.8
            }
            assert classifier._validate_result(valid_result) is True
            
            # Valid result with low confidence
            low_confidence = {
                "category": "News",
                "confidence": 0.5
            }
            assert classifier._validate_result(low_confidence) is False
            
            # Missing category
            missing_category = {
                "confidence": 0.9
            }
            assert classifier._validate_result(missing_category) is False 