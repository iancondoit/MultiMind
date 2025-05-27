# Inter-Project Handoff Protocol

Version: 0.2.0

## Overview

This document defines the standardized protocol for handoffs between project components in the MultiMind system. Handoffs allow one component to request changes or clarifications from another component.

## Handoff File Structure

Handoffs are stored as Markdown files in the following locations:

1. **PM Handoff Directory**: `/MultiMindPM/handoffs/`
   - Contains all active handoffs
   - Named format: `YYYYMMDD-from_to-description.md`
   - Example: `20250615-project_one_project_two-schema_update.md`

2. **Output Handoff Directory**: `/output/handoffs/`
   - Used for direct project-to-project handoffs
   - Same naming convention as PM handoffs

## Handoff Document Format

Each handoff document must follow this structure:

```markdown
# Handoff: [Brief Description]

Version: 0.1.0
Status: [REQUESTED | IN_PROGRESS | COMPLETED | REJECTED]
From: [Source Project]
To: [Target Project]
Created: [YYYY-MM-DD]
Last Updated: [YYYY-MM-DD]
Due: [YYYY-MM-DD or "None"]
Priority: [HIGH | MEDIUM | LOW]

## Request

[Detailed description of what needs to be done]

## Rationale

[Why this handoff is necessary and how it benefits the overall system]

## Technical Details

[Specific implementation details, API requirements, data formats, etc.]

## Acceptance Criteria

* [Measurable criterion 1]
* [Measurable criterion 2]
...

## Dependencies

* [Dependency 1]
* [Dependency 2]
...

## Response

[To be filled by the receiving project]

## Implementation Notes

[Notes on the actual implementation by the receiving project]
```

## Handoff Process

1. **Requesting Project**
   - Creates a handoff document in `/output/handoffs/`
   - Follows the naming convention and document format
   - Sets status to REQUESTED
   - Provides clear acceptance criteria
   - Notifies the PM via a status report update

2. **Project Manager**
   - Runs `./multimind.py handoffs` to discover new handoffs
   - Reviews the handoff request
   - May add additional context or requirements
   - Ensures the handoff is properly directed

3. **Receiving Project**
   - Discovers the handoff during the next sync
   - Updates the status to IN_PROGRESS
   - Implements the requested changes
   - Documents the implementation in the "Implementation Notes" section
   - Updates the status to COMPLETED when done

4. **Verification**
   - The requesting project verifies that the implementation meets the acceptance criteria
   - PM may facilitate resolution of any discrepancies
   - Once verified, the handoff is archived

## Status Definitions

- **REQUESTED**: Initial state when the handoff is created
- **IN_PROGRESS**: Receiving project has acknowledged and started work
- **COMPLETED**: Receiving project has implemented the requested changes
- **REJECTED**: Receiving project cannot fulfill the request (with explanation)

## Priority Levels

- **HIGH**: Critical for system functionality, blocks further progress
- **MEDIUM**: Important but not blocking immediate work
- **LOW**: Nice to have, can be scheduled for later

## Tips for Effective Handoffs

1. Be specific about requirements
2. Include clear acceptance criteria
3. Provide necessary technical context
4. Indicate any dependencies
5. Set reasonable due dates based on scope
6. Reference any relevant documentation or code
7. Be available to answer questions about the handoff
8. When receiving a handoff, acknowledge it promptly

## Examples

### API Update Example

```markdown
# Handoff: Update User Authentication API

Version: 0.1.0
Status: REQUESTED
From: UserInterface
To: AuthService
Created: 2025-05-15
Last Updated: 2025-05-15
Due: 2025-05-22
Priority: HIGH

## Request

Add support for OAuth 2.0 token refresh to the authentication API.

## Rationale

Users are currently being logged out when their token expires, creating a poor user experience. Token refresh will allow for seamless user sessions.

## Technical Details

The AuthService should implement a new endpoint at `/api/v1/auth/refresh` that:
- Accepts a refresh token in the request body
- Validates the refresh token
- Issues a new access token
- Returns the new token pair (access + refresh)

JSON structure for request:
```json
{
  "refreshToken": "string"
}
```

JSON structure for response:
```json
{
  "accessToken": "string",
  "refreshToken": "string",
  "expiresIn": number
}
```

## Acceptance Criteria

* New endpoint implemented at `/api/v1/auth/refresh`
* Endpoint correctly validates refresh tokens
* Endpoint issues new access tokens when refresh is valid
* Endpoint rejects expired or invalid refresh tokens with 401 status
* Refresh tokens have a 30-day expiration
* Access tokens have a 15-minute expiration

## Dependencies

* Existing JWT implementation in AuthService
* User database for token validation

## Response

[To be filled by AuthService]

## Implementation Notes

[Notes on the actual implementation]
```

## Updating This Protocol

This protocol may be updated by the PM as the project evolves. All projects will automatically receive updates through the standard sync process. 