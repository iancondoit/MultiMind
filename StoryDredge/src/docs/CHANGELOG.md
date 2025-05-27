# Changelog

## 1.0.0 - 2023-10-24

### Official Release
- First stable release of StoryDredge with improved pipeline

### Performance Improvements
- Rule-based classification processes hundreds of articles in less than a second
- Entity extraction is integrated into the rule-based classifier for better performance
- Directory structure improvements reduce disk usage

### Added
- New comprehensive test suite for rule-based classification and directory structure
- Added documentation in `docs/pipeline_improvements.md` detailing all recent improvements
- Enhanced entity extraction that includes people, organizations, and locations in HSA tags
- Verification checklist for testing all improvements

### Changed
- Default classification now uses fast rule-based system instead of LLM
- Improved directory structure with temporary files stored in a dedicated temp directory
- Fixed issue with nested "hsa-ready" directories
- Updated HSA formatter to properly include entity tags

### Fixed
- Fixed issue with article metadata not appearing in tags
- Fixed directory duplication bug where "per_atlanta" directories were created
- Fixed slow classification by defaulting to rule-based instead of LLM
- Fixed LLM template handling to be more robust

## Pre-Release Changes (2023-10-24)

### Added
- New comprehensive test suite for rule-based classification and directory structure
- Added documentation in `docs/pipeline_improvements.md` detailing all recent improvements
- Enhanced entity extraction that includes people, organizations, and locations in HSA tags

### Changed
- Default classification now uses fast rule-based system instead of LLM
- Improved directory structure with temporary files stored in a dedicated temp directory
- Fixed issue with nested "hsa-ready" directories
- Updated HSA formatter to properly include entity tags

### Fixed
- Fixed issue with article metadata not appearing in tags
- Fixed directory duplication bug where "per_atlanta" directories were created
- Fixed slow classification by defaulting to rule-based instead of LLM
- Fixed LLM template handling to be more robust

## Performance Improvements
- Classification now processes hundreds of articles in less than a second
- Entity extraction is integrated into the rule-based classifier for better performance
- Directory structure improvements reduce disk usage 