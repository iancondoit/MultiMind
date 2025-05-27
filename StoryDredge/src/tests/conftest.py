"""
conftest.py - Shared pytest fixtures for StoryDredge tests
"""

import os
import shutil
import pytest
from pathlib import Path


@pytest.fixture
def test_data_dir():
    """Fixture providing path to test data directory."""
    return Path("tests/test_data")


@pytest.fixture(scope="function")
def temp_dir(tmp_path):
    """Fixture providing a temporary directory that's cleaned up after each test."""
    yield tmp_path
    # Cleanup happens automatically with pytest's tmp_path


@pytest.fixture
def sample_ocr_text():
    """Fixture providing a sample OCR text for testing."""
    return """
THE SAN ANTONIO EXPRESS
JUNE 14, 1977                                                                                PAGE 12

LOCAL COUNCIL APPROVES NEW BUDGET

By John Smith
Staff Writer

The San Antonio City Council yesterday approved a
$24 million budget for the upcoming fiscal year, with
increased funding for public safety and parks.

Mayor Robert Johnson said the new budget reflects
the city's commitment to improving quality of life
while maintaining fiscal responsibility.

"We're making investments in critical areas while
still keeping tax rates stable," Johnson said during
the council meeting.

The budget includes $8 million for the police
department, a 5% increase from last year, and
$3.5 million for parks and recreation.

Councilwoman Maria Garcia, who represents the
west side, praised the budget's focus on
infrastructure improvements in underserved areas.

The budget will take effect on July 1.

===========================================

WEATHER FORECAST

Partly cloudy with a chance of afternoon
showers. High of 92 degrees. Low tonight
around 75. South winds 5-10 mph.

===========================================

CLASSIFIED ADVERTISEMENTS

FOR SALE: 1975 Ford Mustang, excellent condition,
low mileage, $3,200. Call 555-7890.

HELP WANTED: Full-time secretary needed for
downtown law office. Typing and shorthand required.
Call 555-1234 for interview.

APARTMENTS FOR RENT: 2BR, 1BA, near downtown.
$225/month plus utilities. No pets. 555-6789.
    """


@pytest.fixture
def sample_newspaper_metadata():
    """Fixture providing sample newspaper metadata for testing."""
    return {
        "archive_id": "san-antonio-express-news-1977-06-14",
        "date": "1977-06-14",
        "publication": "San Antonio Express-News",
        "source_url": "https://archive.org/details/san-antonio-express-news-1977-06-14"
    }


@pytest.fixture
def mock_archive_response():
    """Fixture providing mock archive.org response data."""
    return {
        "response": {
            "numFound": 3,
            "start": 0,
            "docs": [
                {
                    "identifier": "san-antonio-express-news-1977-06-14",
                    "title": "San Antonio Express-News (1977-06-14)",
                    "date": "1977-06-14T00:00:00Z",
                    "mediatype": "texts"
                },
                {
                    "identifier": "san-antonio-express-news-1977-06-15",
                    "title": "San Antonio Express-News (1977-06-15)",
                    "date": "1977-06-15T00:00:00Z",
                    "mediatype": "texts"
                },
                {
                    "identifier": "san-antonio-express-news-1977-06-16",
                    "title": "San Antonio Express-News (1977-06-16)",
                    "date": "1977-06-16T00:00:00Z",
                    "mediatype": "texts"
                }
            ]
        }
    } 