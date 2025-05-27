# StoryDredge v1.0.0 Release Checklist

This checklist covers the steps required to prepare and publish a new StoryDredge release.

## Pre-Release Steps

- [x] Update version in `src/version.py` to 1.0.0
- [x] Update CHANGELOG.md with details of changes
- [x] Create comprehensive documentation (`docs/pipeline_improvements.md`)
- [x] Develop test suite for new features
- [x] Verify all tests are passing
- [x] Run the verification checklist (`docs/verification_checklist.md`)
- [x] Update README.md with version information

## Release Preparation

- [x] Generate version information: `python scripts/show_version.py`
- [x] Create release artifacts: `python scripts/prepare_release.py`
- [x] Review release notes in `dist/RELEASE_NOTES_1.0.0.md`
- [ ] Commit all changes: `git commit -am "Prepare v1.0.0 release"`
- [ ] Tag the release: `./scripts/tag_release.sh`
- [ ] Push release tag to origin

## Post-Release Steps

- [ ] Verify the release artifacts in `dist/` directory
- [ ] Update documentation site (if applicable)
- [ ] Test installation from the release package
- [ ] Prepare development environment for next version

## Release Artifacts

The release preparation process generates the following artifacts in the `dist/` directory:

- `storydredge-1.0.0-<timestamp>.zip`: Complete source code package
- `manifest.json`: Release metadata
- `RELEASE_NOTES_1.0.0.md`: Detailed release notes

## Features in v1.0.0

This release includes:

1. **Fast Rule-based Classification**: Articles are classified using a high-performance rule-based system by default, processing hundreds of articles in under a second.

2. **Enhanced Entity Extraction**: The system extracts people, organizations, and locations from articles and adds them to the tags array in the HSA-ready output.

3. **Improved Directory Structure**: The pipeline uses a cleaner directory structure with temporary files stored in a dedicated temp directory and final output in the properly organized hsa-ready folder.

4. **Comprehensive Testing**: New test scripts verify all aspects of the pipeline, including directory structure, rule-based classification, and entity tag extraction.

5. **Detailed Documentation**: New and updated documentation covers all improvements and provides verification steps.

## Next Development Cycle

After this release, development will focus on:

- Improving OCR text cleaning for better article extraction
- Adding support for additional newspaper sources
- Enhancing visualization tools for processed articles
- Developing a web interface for pipeline management 