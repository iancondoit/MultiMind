"""
Integration tests for the complete StoryDredge pipeline.
"""

import pytest
from pathlib import Path
import json
from unittest.mock import patch, MagicMock

# Import the pipeline components we'll test together
# from pipeline.main import process_issue
# from src.fetcher.archive_fetcher import ArchiveFetcher
# from src.cleaner.ocr_cleaner import OCRCleaner
# from src.splitter.article_splitter import ArticleSplitter
# from src.classifier.llama_classifier import LlamaClassifier
# from src.formatter.hsa_formatter import HSAFormatter


class TestPipeline:
    """Integration tests for the complete pipeline."""
    
    @patch('src.fetcher.archive_fetcher.ArchiveFetcher')
    @patch('src.cleaner.ocr_cleaner.OCRCleaner')
    @patch('src.splitter.article_splitter.ArticleSplitter')
    @patch('src.classifier.llama_classifier.LlamaClassifier')
    @patch('src.formatter.hsa_formatter.HSAFormatter')
    def test_process_single_issue(self, mock_formatter, mock_classifier, 
                                mock_splitter, mock_cleaner, mock_fetcher,
                                temp_dir, sample_newspaper_metadata):
        """Test processing of a single newspaper issue through the full pipeline."""
        # Setup mocks
        # archive_id = sample_newspaper_metadata["archive_id"]
        # date = sample_newspaper_metadata["date"]
        # 
        # # Mock fetcher
        # mock_fetcher_instance = mock_fetcher.return_value
        # mock_fetcher_instance.fetch_issue.return_value = temp_dir / f"{archive_id}.txt"
        # 
        # # Mock cleaner
        # mock_cleaner_instance = mock_cleaner.return_value
        # mock_cleaner_instance.process_file.return_value = temp_dir / f"{archive_id}-clean.txt"
        # 
        # # Mock splitter
        # mock_splitter_instance = mock_splitter.return_value
        # article_paths = [
        #     temp_dir / f"{date}--article-1.json",
        #     temp_dir / f"{date}--article-2.json",
        #     temp_dir / f"{date}--article-3.json"
        # ]
        # mock_splitter_instance.split_file.return_value = article_paths
        # 
        # # Create sample articles
        # articles = []
        # for i, path in enumerate(article_paths):
        #     article = {
        #         "title": f"Article {i+1}",
        #         "raw_text": f"Content for article {i+1}"
        #     }
        #     articles.append(article)
        #     path.parent.mkdir(parents=True, exist_ok=True)
        #     with open(path, 'w') as f:
        #         json.dump(article, f)
        # 
        # # Mock classifier
        # mock_classifier_instance = mock_classifier.return_value
        # classified_articles = [
        #     {
        #         "headline": f"Article {i+1}",
        #         "body": f"Content for article {i+1}",
        #         "section": "news",
        #         "tags": ["test"]
        #     }
        #     for i in range(3)
        # ]
        # mock_classifier_instance.classify_batch.return_value = classified_articles
        # 
        # # Mock formatter
        # mock_formatter_instance = mock_formatter.return_value
        # output_paths = [
        #     temp_dir / "hsa-ready" / "1977" / "06" / "14" / f"{date}--article-{i+1}.json"
        #     for i in range(3)
        # ]
        # mock_formatter_instance.process_batch.return_value = output_paths
        # 
        # # Run the pipeline
        # output_files = process_issue(archive_id, output_dir=temp_dir)
        # 
        # # Verify the pipeline flow
        # mock_fetcher.assert_called_once()
        # mock_fetcher_instance.fetch_issue.assert_called_once_with(archive_id)
        # 
        # mock_cleaner.assert_called_once()
        # mock_cleaner_instance.process_file.assert_called_once()
        # 
        # mock_splitter.assert_called_once()
        # mock_splitter_instance.split_file.assert_called_once()
        # 
        # mock_classifier.assert_called_once()
        # mock_classifier_instance.classify_batch.assert_called_once()
        # 
        # mock_formatter.assert_called_once()
        # mock_formatter_instance.process_batch.assert_called_once()
        # 
        # # Verify output
        # assert output_files == output_paths
        # assert len(output_files) == 3
        pass
    
    @patch('src.fetcher.archive_fetcher.ArchiveFetcher')
    @patch('pipeline.main.process_issue')
    def test_process_multiple_issues(self, mock_process_issue, mock_fetcher, temp_dir):
        """Test processing multiple issues in parallel."""
        # # Setup
        # issues = [
        #     {"archive_id": "newspaper-1977-06-14", "date": "1977-06-14"},
        #     {"archive_id": "newspaper-1977-06-15", "date": "1977-06-15"},
        #     {"archive_id": "newspaper-1977-06-16", "date": "1977-06-16"}
        # ]
        # 
        # # Mock individual issue processing
        # mock_process_issue.side_effect = [
        #     [temp_dir / f"output-{i}.json"] for i in range(3)
        # ]
        # 
        # # Run the batch process
        # from pipeline.main import process_issues_batch
        # results = process_issues_batch(issues, parallel=2, output_dir=temp_dir)
        # 
        # # Verify
        # assert len(results) == 3
        # assert mock_process_issue.call_count == 3
        pass
    
    def test_end_to_end(self, temp_dir, test_data_dir):
        """
        Full end-to-end test with real components.
        
        This test uses the actual components (not mocks) but with a controlled
        small test file. It processes a sample newspaper OCR file through all
        steps of the pipeline, verifying the output at each stage.
        """
        # # Copy test data to temp dir for processing
        # import shutil
        # test_file = test_data_dir / "sample_ocr.txt"
        # input_file = temp_dir / "san-antonio-express-news-1977-06-14.txt"
        # shutil.copy(test_file, input_file)
        # 
        # # Create test metadata
        # metadata = {
        #     "archive_id": "san-antonio-express-news-1977-06-14",
        #     "date": "1977-06-14", 
        #     "publication": "San Antonio Express-News",
        #     "source_url": "https://archive.org/details/san-antonio-express-news-1977-06-14"
        # }
        # 
        # # Create all component instances
        # from pipeline.main import process_issue_with_components
        # from src.fetcher.archive_fetcher import ArchiveFetcher
        # from src.cleaner.ocr_cleaner import OCRCleaner
        # from src.splitter.article_splitter import ArticleSplitter
        # from src.classifier.llama_classifier import LlamaClassifier
        # from src.formatter.hsa_formatter import HSAFormatter
        # 
        # fetcher = ArchiveFetcher(cache_dir=temp_dir)
        # cleaner = OCRCleaner()
        # splitter = ArticleSplitter()
        # classifier = LlamaClassifier()
        # formatter = HSAFormatter(output_dir=temp_dir / "hsa-ready")
        # 
        # # Disable actual Ollama calls for testing
        # with patch.object(classifier, '_run_ollama') as mock_run_ollama:
        #     # Mock Ollama output
        #     mock_run_ollama.side_effect = lambda article: {
        #         "headline": article.get("title", "Sample Headline"),
        #         "body": article.get("raw_text", "")[:100],  # Truncate for test
        #         "section": "news",
        #         "tags": ["local", "test"],
        #         "byline": "By John Smith",
        #         "dateline": "SAN ANTONIO, JUNE 14"
        #     }
        #     
        #     # Process the issue
        #     results = process_issue_with_components(
        #         metadata["archive_id"],
        #         fetcher=fetcher,
        #         cleaner=cleaner,
        #         splitter=splitter,
        #         classifier=classifier,
        #         formatter=formatter,
        #         use_cache=True
        #     )
        # 
        # # Verify results
        # assert len(results) > 0
        # 
        # # Check a sample output file
        # sample_file = results[0]
        # assert sample_file.exists()
        # 
        # with open(sample_file, 'r') as f:
        #     article = json.load(f)
        #     assert "headline" in article
        #     assert "body" in article
        #     assert "section" in article
        #     assert article["section"] == "news"
        #     assert "tags" in article
        #     assert "timestamp" in article
        #     assert "publication" in article
        #     assert article["publication"] == "San Antonio Express-News"
        pass 