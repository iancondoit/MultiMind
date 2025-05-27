# Status Report Format Guidelines

Version: 0.1.0

## Overview

This document defines the standardized format for all status reports in the MultiMind system. All subprojects must follow this format when updating their `status.md` files.

## Required Sections

Each status report must include the following sections in this order:

1. **Title and Version**
   ```markdown
   # [Project Name] Status Report
   
   Version: [version]
   ```

2. **Last Update**
   ```markdown
   ## Last Update
   
   [YYYY-MM-DD]
   ```

3. **Current Progress**
   ```markdown
   ## Current Progress
   
   * [Completed item 1]
   * [Completed item 2]
   * [In-progress item (XX% complete)]
   ```

4. **Blockers**
   ```markdown
   ## Blockers
   
   * [Blocker 1 with details]
   * [Blocker 2 with details]
   * None at this time
   ```

5. **Next Steps**
   ```markdown
   ## Next Steps
   
   * [Action item 1]
   * [Action item 2]
   ```

6. **API/Integration Updates** (if applicable)
   ```markdown
   ## API/Integration Updates
   
   * [API change 1]
   * [New requirement for other components]
   ```

## Example Status Report

```markdown
# ProjectOne Status Report

Version: 0.1.0

## Last Update

2023-06-15

## Current Progress

* Project structure has been initialized
* Working on data processor implementation (70% complete)
* Initial JSON schema defined

## Blockers

* Need clarification on handling edge cases

## Next Steps

* Complete data processing logic
* Implement JSON validation
* Create basic test suite

## API/Integration Updates

* Data JSON schema now includes "metadata" array field
* ProjectTwo will need to handle this field in processing
```

## Submission Process

1. Update your project's `reports/status.md` file
2. Ensure it follows this format exactly
3. The MultiMind PM will run `gather` to collect these reports
4. Do not modify the collected reports in the PM directory 