# Advisory: Technology Stack and Authentication Guidance

Version: 0.1.0
Status: ANSWERED
Project: MasterBus
Created: 2025-05-22
Last Updated: 2025-05-22

## Question

What technology stack should be used for MasterBus implementation? Also, what authentication mechanism should be implemented for the API?

## Context

The MasterBus status report identified these as blockers:
- Need confirmation on technology stack preferences for MasterBus
- Need to determine authentication mechanism for API

## Response

### Technology Stack

For the MasterBus implementation, use the following stack:

1. **Backend Framework**: FastAPI (Python)
   - Provides excellent performance for API development
   - Built-in OpenAPI documentation
   - Type validation with Pydantic
   - Async support for handling concurrent requests

2. **Database**: PostgreSQL
   - Consistent with Condoit's database technology
   - Use SQLAlchemy ORM for database access
   - Implement a separate schema for MasterBus data

3. **Caching**: Redis
   - For performance optimization
   - Store frequently requested data
   - Cache VoltMetrics calculation results

4. **Infrastructure**: Containerized with Docker
   - Simplifies deployment and scaling
   - Consistent environment across development and production
   - Use docker-compose for local development

### Authentication Mechanism

Implement a token-based authentication system using:

1. **JSON Web Tokens (JWT)**
   - Stateless authentication
   - Include scopes for authorization (read-only, admin, etc.)
   - 24-hour expiration with refresh token capability

2. **API Key Authentication**
   - For service-to-service communication (MasterBus ↔ VoltMetrics)
   - Required in header: `X-API-Key: [api_key]`
   - Different keys for development, testing, and production

3. **Security Requirements**
   - All endpoints except health check require authentication
   - HTTPS-only in production
   - Rate limiting for all endpoints
   - Input validation on all parameters

This authentication approach will allow secure access from ThreatMap while also enabling direct system-to-system communication with VoltMetrics.

## Resolution

[To be filled by MasterBus team after implementation] 