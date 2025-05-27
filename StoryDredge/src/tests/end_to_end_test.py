#!/usr/bin/env python3
"""
End-to-end test script for StoryDredge pipeline.

This script performs an end-to-end test of the StoryDredge pipeline, processing
a small set of newspaper issues and validating the outputs at each stage.
"""

import os
import sys
import json
import time
import logging
import argparse
import tempfile
import shutil
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fetcher import ArchiveFetcher
from src.cleaner import OCRCleaner
from src.splitter import ArticleSplitter
from src.classifier import ArticleClassifier
from src.formatter import HSAFormatter
from src.pipeline.batch_processor import BatchProcessor
from src.pipeline.parallel_processor import ParallelProcessor
from src.utils.validation import validate_hsa_format


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("end_to_end_test")


class TestResult:
    """Class to track test results."""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.failures = []
    
    def success(self, test_name):
        self.tests_run += 1
        self.tests_passed += 1
        logger.info(f"✅ {test_name} - PASSED")
    
    def failure(self, test_name, error_message):
        self.tests_run += 1
        self.failures.append((test_name, error_message))
        logger.error(f"❌ {test_name} - FAILED: {error_message}")
    
    def summary(self):
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        logger.info(f"Tests run: {self.tests_run}")
        logger.info(f"Tests passed: {self.tests_passed} ({success_rate:.1f}%)")
        
        if self.failures:
            logger.error(f"Failures: {len(self.failures)}")
            for name, error in self.failures:
                logger.error(f"  - {name}: {error}")
        else:
            logger.info("All tests passed!")
        
        return self.tests_passed == self.tests_run


def test_fetcher(test_issue_id, result):
    """Test the archive.org fetcher."""
    test_name = "Fetcher Test"
    try:
        # Initialize fetcher
        fetcher = ArchiveFetcher(cache_dir="cache")
        
        # Fetch the test issue
        start_time = time.time()
        ocr_text = fetcher.fetch_issue(test_issue_id)
        elapsed_time = time.time() - start_time
        
        # Validate the result
        if not ocr_text or len(ocr_text) < 1000:
            result.failure(test_name, f"OCR text is too short: {len(ocr_text)} characters")
            return None
        
        logger.info(f"Fetched {len(ocr_text)} characters in {elapsed_time:.2f} seconds")
        result.success(test_name)
        return ocr_text
    except Exception as e:
        result.failure(test_name, str(e))
        return None


def test_cleaner(ocr_text, result):
    """Test the OCR text cleaner."""
    test_name = "Cleaner Test"
    try:
        # Initialize cleaner
        cleaner = OCRCleaner()
        
        # Clean the OCR text
        start_time = time.time()
        cleaned_text = cleaner.clean(ocr_text)
        elapsed_time = time.time() - start_time
        
        # Validate the result
        if not cleaned_text:
            result.failure(test_name, "Cleaned text is empty")
            return None
        
        if len(cleaned_text) < 0.5 * len(ocr_text):
            result.failure(test_name, f"Cleaned text is too short: {len(cleaned_text)} vs {len(ocr_text)}")
            return None
        
        logger.info(f"Cleaned text: {len(cleaned_text)} characters in {elapsed_time:.2f} seconds")
        result.success(test_name)
        return cleaned_text
    except Exception as e:
        result.failure(test_name, str(e))
        return None


def test_splitter(cleaned_text, result):
    """Test the article splitter."""
    test_name = "Splitter Test"
    try:
        # Initialize splitter
        splitter = ArticleSplitter()
        
        # Split the cleaned text into articles
        start_time = time.time()
        articles = splitter.split(cleaned_text)
        elapsed_time = time.time() - start_time
        
        # Validate the result
        if not articles:
            result.failure(test_name, "No articles found")
            return None
        
        if len(articles) < 2:
            result.failure(test_name, f"Too few articles extracted: {len(articles)}")
            return None
        
        logger.info(f"Extracted {len(articles)} articles in {elapsed_time:.2f} seconds")
        result.success(test_name)
        return articles
    except Exception as e:
        result.failure(test_name, str(e))
        return None


def test_classifier(articles, result):
    """Test the article classifier."""
    test_name = "Classifier Test"
    try:
        # Initialize classifier
        classifier = ArticleClassifier(model_name="llama2")
        
        # Classify a subset of articles (to speed up the test)
        test_articles = articles[:min(3, len(articles))]
        
        start_time = time.time()
        classified_articles = classifier.classify_batch(test_articles)
        elapsed_time = time.time() - start_time
        
        # Validate the result
        if not classified_articles:
            result.failure(test_name, "No articles classified")
            return None
        
        if len(classified_articles) != len(test_articles):
            result.failure(test_name, f"Expected {len(test_articles)} classified articles, got {len(classified_articles)}")
            return None
        
        # Check for required fields
        required_fields = ["headline", "body", "tags", "section"]
        for i, article in enumerate(classified_articles):
            for field in required_fields:
                if field not in article:
                    result.failure(test_name, f"Article {i} missing required field '{field}'")
                    return None
        
        logger.info(f"Classified {len(classified_articles)} articles in {elapsed_time:.2f} seconds")
        result.success(test_name)
        return classified_articles
    except Exception as e:
        result.failure(test_name, str(e))
        return None


def test_formatter(classified_articles, test_issue_id, result):
    """Test the HSA formatter."""
    test_name = "Formatter Test"
    try:
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize formatter
            formatter = HSAFormatter(output_dir=temp_dir)
            
            # Format the classified articles
            start_time = time.time()
            formatted_articles = formatter.format_batch(classified_articles, source_issue=test_issue_id)
            elapsed_time = time.time() - start_time
            
            # Validate the result
            if not formatted_articles:
                result.failure(test_name, "No articles formatted")
                return None
            
            # Check output files
            output_files = list(Path(temp_dir).glob("**/*.json"))
            if not output_files:
                result.failure(test_name, "No output files generated")
                return None
            
            # Validate HSA format
            for output_file in output_files:
                with open(output_file, 'r') as f:
                    try:
                        article_data = json.load(f)
                        validation_result = validate_hsa_format(article_data)
                        if not validation_result['valid']:
                            result.failure(test_name, f"HSA format validation failed: {validation_result['errors']}")
                            return None
                    except json.JSONDecodeError:
                        result.failure(test_name, f"Invalid JSON in output file: {output_file}")
                        return None
            
            logger.info(f"Formatted {len(formatted_articles)} articles in {elapsed_time:.2f} seconds")
            logger.info(f"Generated {len(output_files)} output files")
            result.success(test_name)
            return formatted_articles
    except Exception as e:
        result.failure(test_name, str(e))
        return None


def test_pipeline_integration(test_issue_ids, result):
    """Test the full pipeline integration."""
    test_name = "Pipeline Integration Test"
    try:
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize the batch processor
            processor = BatchProcessor(output_dir=temp_dir)
            
            # Process the test issues
            start_time = time.time()
            process_results = processor.process_batch(test_issue_ids)
            elapsed_time = time.time() - start_time
            
            # Validate the results
            if process_results['successful'] == 0:
                result.failure(test_name, "No issues were processed successfully")
                return False
            
            # Check output files
            output_files = list(Path(temp_dir).glob("**/*.json"))
            if not output_files:
                result.failure(test_name, "No output files generated")
                return False
            
            logger.info(f"Processed {process_results['successful']} of {len(test_issue_ids)} issues in {elapsed_time:.2f} seconds")
            logger.info(f"Generated {len(output_files)} output files")
            result.success(test_name)
            return True
    except Exception as e:
        result.failure(test_name, str(e))
        return False


def test_parallel_processing(test_issue_ids, result):
    """Test parallel processing."""
    test_name = "Parallel Processing Test"
    try:
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize the parallel processor
            processor = ParallelProcessor(output_dir=temp_dir, max_workers=2)
            
            # Process the test issues
            start_time = time.time()
            process_results = processor.process_batch(test_issue_ids)
            elapsed_time = time.time() - start_time
            
            # Validate the results
            if process_results['successful'] == 0:
                result.failure(test_name, "No issues were processed successfully")
                return False
            
            # Check output files
            output_files = list(Path(temp_dir).glob("**/*.json"))
            if not output_files:
                result.failure(test_name, "No output files generated")
                return False
            
            logger.info(f"Parallel processed {process_results['successful']} of {len(test_issue_ids)} issues in {elapsed_time:.2f} seconds")
            logger.info(f"Generated {len(output_files)} output files")
            result.success(test_name)
            return True
    except Exception as e:
        result.failure(test_name, str(e))
        return False


def run_all_tests():
    """Run all end-to-end tests."""
    result = TestResult()
    
    # Test issue IDs - use known good issues for testing
    test_issue_ids = [
        "sn84026749-19220101",
        "sn84026749-19220102"
    ]
    
    # Run individual component tests
    logger.info("=== Component Tests ===")
    
    # Fetcher test
    ocr_text = test_fetcher(test_issue_ids[0], result)
    if not ocr_text:
        logger.error("Fetcher test failed, cannot continue with cleaner test")
    else:
        # Cleaner test
        cleaned_text = test_cleaner(ocr_text, result)
        if not cleaned_text:
            logger.error("Cleaner test failed, cannot continue with splitter test")
        else:
            # Splitter test
            articles = test_splitter(cleaned_text, result)
            if not articles:
                logger.error("Splitter test failed, cannot continue with classifier test")
            else:
                # Classifier test
                classified_articles = test_classifier(articles, result)
                if not classified_articles:
                    logger.error("Classifier test failed, cannot continue with formatter test")
                else:
                    # Formatter test
                    test_formatter(classified_articles, test_issue_ids[0], result)
    
    # Run integration tests
    logger.info("\n=== Integration Tests ===")
    
    # Pipeline integration test
    pipeline_success = test_pipeline_integration(test_issue_ids, result)
    
    # Parallel processing test - only if we have multiple test issues
    if len(test_issue_ids) > 1:
        parallel_success = test_parallel_processing(test_issue_ids, result)
    
    # Print summary
    logger.info("\n=== Test Summary ===")
    all_passed = result.summary()
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run end-to-end tests for StoryDredge")
    args = parser.parse_args()
    
    # Run the tests
    sys.exit(run_all_tests()) 