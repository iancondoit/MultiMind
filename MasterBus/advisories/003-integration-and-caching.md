# Advisory: VoltMetrics Integration, Caching, and Error Handling

Version: 1.0.0
Status: ANSWERED
Project: MasterBus
Created: 2025-05-23
Last Updated: 2025-05-23

## Question

We need guidance on:
1. VoltMetrics API documentation for implementing integration
2. Determining an appropriate cache invalidation strategy for risk calculations
3. Finalizing error handling standards for API responses

## Context

As we move into Phase 3 which focuses on integration with VoltMetrics, we need to understand their API structure. Additionally, we need to determine how to handle caching of calculation results and standardize our error handling approach across the API.

## Response

### 1. VoltMetrics API Integration

The VoltMetrics team is preparing their integration endpoints simultaneously with your Phase 3 work. Rather than waiting for their complete documentation, we'll establish a contract-first approach:

#### Core Integration Endpoints

VoltMetrics will expose these primary endpoints:

- `POST /api/v1/calculations/risk` - Submit equipment/facility data for risk calculation
- `GET /api/v1/calculations/{job_id}` - Check calculation status and retrieve results
- `GET /api/v1/equipment/{equipment_id}/risk` - Get cached risk calculation for specific equipment
- `GET /api/v1/facilities/{facility_id}/risk` - Get aggregated risk data for a facility
- `GET /api/v1/compliance/nfpa70b/{facility_id}` - Get NFPA 70B compliance metrics
- `GET /api/v1/compliance/nfpa70e/{facility_id}` - Get NFPA 70E compliance metrics

#### Authentication

VoltMetrics will use JWT tokens compatible with your existing auth system. The same tokens you issue for ThreatMap can be used for VoltMetrics access.

#### Asynchronous Processing

For calculation jobs that may take time, VoltMetrics will:
1. Accept data and return a job ID immediately
2. Process the calculation asynchronously
3. Provide status updates via the job status endpoint
4. Issue a webhook callback to MasterBus when complete (you'll need to implement a receiver)

### 2. Cache Invalidation Strategy

Implement a hybrid approach for caching risk calculations:

1. **Time-Based Expiration**:
   - Set base TTL of 24 hours for all risk calculations
   - Set shorter TTL (1 hour) for aggregated facility metrics

2. **Event-Based Invalidation**:
   - Invalidate equipment risk cache when equipment data changes
   - Invalidate facility risk cache when any related equipment changes
   - Propagate invalidations up the hierarchy (equipment → panel → facility)

3. **Versioned Cache Keys**:
   - Include algorithm version in cache keys (e.g., `risk:v1.2:equipment:123`)
   - This allows transparent updates when risk algorithms change

4. **Soft Invalidation**:
   - When data changes, mark cache as "stale" but still serve it
   - Trigger background refresh rather than forcing users to wait
   - Use cache-control headers to indicate freshness to clients

### 3. API Error Handling Standards

Standardize error responses across all endpoints:

1. **Response Structure**:
```json
{
  "error": {
    "code": "ERROR_CODE_STRING",
    "message": "Human-readable error message",
    "details": {
      "field_name": "Specific error about this field",
      "additional_info": "Any other relevant details"
    },
    "request_id": "unique-request-id-for-tracing"
  }
}
```

2. **HTTP Status Codes**:
   - 400: Bad Request (invalid input)
   - 401: Unauthorized (missing authentication)
   - 403: Forbidden (authenticated but not authorized)
   - 404: Not Found (resource doesn't exist)
   - 409: Conflict (e.g., version conflicts)
   - 422: Unprocessable Entity (validation errors)
   - 429: Too Many Requests (rate limiting)
   - 500: Internal Server Error (unexpected errors)
   - 503: Service Unavailable (maintenance or overload)

3. **Error Codes**:
   - Format: `CATEGORY_SPECIFIC_ERROR`
   - Examples: `AUTH_INVALID_TOKEN`, `DATA_NOT_FOUND`, `VALIDATION_REQUIRED_FIELD`

4. **Localization**:
   - Include error codes that can be mapped to localized messages by the front-end
   - Keep messages clear and consistent across the API

5. **Validation Errors**:
   - For field validation failures, include the field name and specific error
   - Use consistent naming for validation error codes

6. **Logging**:
   - Log all errors with request IDs for correlation
   - Include additional context not sent to clients for debugging

## Resolution

The MasterBus team should:
1. Begin implementing the VoltMetrics integration using the contract described above
2. Schedule weekly sync meetings with VoltMetrics team during Phase 3 to align on interface details
3. Implement the cache invalidation strategy and error handling standards
4. Create a webhook receiver endpoint for VoltMetrics to notify on calculation completion 