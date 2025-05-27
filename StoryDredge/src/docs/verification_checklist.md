# StoryDredge Improvements Verification Checklist

Use this checklist to verify that all the recent improvements to the StoryDredge pipeline are working correctly.

## Classification System

- [ ] Rule-based classification is used by default
  - Run: `PYTHONPATH=. python scripts/run_classification.py --issue per_atlanta-constitution_1922-01-01_54_203`
  - Verify: Classification completes in under 5 seconds for hundreds of articles

- [ ] LLM-based classification is still available when needed
  - Run: `PYTHONPATH=. python scripts/run_classification.py --issue per_atlanta-constitution_1922-01-01_54_203 --use-llm`
  - Verify: Classification uses Ollama and produces more detailed results

- [ ] Entity extraction is working correctly
  - Check: Files in `output/per_atlanta-constitution_1922-01-01_54_203/classified/` contain metadata with people, organizations, and locations

## Directory Structure

- [ ] Temporary files are stored in the temp directory
  - Run: `PYTHONPATH=. python pipeline/process_ocr.py --issue per_atlanta-constitution_1922-01-01_54_203 --output-dir output --fast-mode`
  - Verify: Files are created in `output/temp/per_atlanta-constitution_1922-01-01_54_203/`

- [ ] No "per_atlanta" directories are created in the main output directory
  - Verify: `output/per_atlanta-constitution_1922-01-01_54_203` does not exist
  - Verify: Instead, find temporary files in `output/temp/per_atlanta-constitution_1922-01-01_54_203/`

- [ ] No nested "hsa-ready" directories exist
  - Verify: `output/hsa-ready/hsa-ready` does not exist

- [ ] HSA-ready output is properly organized by date
  - Verify: HSA-ready files are in `output/hsa-ready/1922/01/01/`

## Entity Tags

- [ ] Entity tags are correctly included in HSA-ready output
  - Run: `find output/hsa-ready -name "*.json" | head -1 | xargs cat`
  - Verify: The "tags" array in the output includes entities (people, organizations, locations)

- [ ] Tags include both category and entities
  - Check: Files in `output/hsa-ready/1922/01/01/` contain tags with both category (news, sports, etc.) and entities

## Tests

- [ ] All tests pass
  - Run: `PYTHONPATH=. pytest tests/test_classifier/test_rule_based_classification.py -v`
  - Run: `PYTHONPATH=. pytest tests/test_formatter/test_entity_tag_extraction.py -v`
  - Run: `PYTHONPATH=. pytest tests/test_pipeline/test_directory_structure.py -v`
  - Verify: All tests pass without failures

## Documentation

- [ ] Documentation is up-to-date
  - Check: `docs/pipeline_improvements.md` contains details of all changes
  - Check: `docs/classification.md` properly describes the rule-based classification
  - Check: README.md includes the "Recent Improvements" section

## End-to-End Test

- [ ] Full pipeline works correctly
  - Run: `PYTHONPATH=. python pipeline/process_ocr.py --issue per_atlanta-constitution_1922-01-05_54_207 --output-dir output --fast-mode`
  - Verify: Pipeline completes without errors
  - Verify: HSA-ready output has correct structure and includes entity tags 