# PM Advisory Templates

Version: 1.0.0
Created: 2025-05-23
Updated: 2025-05-23

## Overview

This document provides standardized templates for Project Manager advisories in different scenarios. Use these templates as starting points when responding to project questions and blockers.

## Technology Selection Advisory Template

```markdown
# Advisory: [Technology Area] Selection Guidance

Version: 1.0.0
Status: ANSWERED
Project: [Project Name]
Created: [YYYY-MM-DD]
Last Updated: [YYYY-MM-DD]

## Question

We need guidance on selecting [technology/framework/library] for [specific purpose].
Specific options we're considering include:
1. [Option A]
2. [Option B]
3. [Option C]

## Context

We need to implement [describe functionality] as part of Phase [X]. The selected technology will need to [describe requirements].

## Response

After evaluating the options against our project requirements, I recommend [selected option] for the following reasons:

1. **Alignment with Project Needs**:
   - [How the selected option meets specific project requirements]
   - [Performance/scalability/maintainability considerations]

2. **Integration Considerations**:
   - [How it integrates with existing components]
   - [Any dependency or compatibility issues]

3. **Learning Curve and Team Expertise**:
   - [Ease of adoption considerations]
   - [Available resources and documentation]

4. **Implementation Approach**:
   - [Recommended implementation strategy]
   - [Key features to utilize]
   - [Potential pitfalls to avoid]

5. **Comparison with Alternatives**:
   - [Brief comparison with rejected alternatives]
   - [Why they were not selected]

## Resolution

The team should:
1. Adopt [selected technology] for [specific purpose]
2. Follow the implementation approach outlined above
3. Document the decision and reasoning in the architecture documentation
4. Ensure test coverage for all components using this technology
```

## Integration Advisory Template

```markdown
# Advisory: Integration Between [System A] and [System B]

Version: 1.0.0
Status: ANSWERED
Project: [Project Name]
Created: [YYYY-MM-DD]
Last Updated: [YYYY-MM-DD]

## Question

We need guidance on implementing the integration between [System A] and [System B], specifically:
1. What communication patterns should we use?
2. What authentication mechanism is appropriate?
3. How should we handle data transfer between systems?

## Context

As part of Phase [X], we need to establish a reliable integration between these systems to enable [specific functionality].

## Response

### 1. Communication Patterns

I recommend implementing a [synchronous/asynchronous/hybrid] approach:

- **API Design**:
  - [REST/GraphQL/gRPC/etc.] for [specific use cases]
  - Endpoint structure: [suggested structure]
  - Rate limiting considerations: [recommendations]

- **Data Flow**:
  - [Push/pull/event-driven model details]
  - [Batch vs. real-time considerations]
  - [Error handling approach]

### 2. Authentication and Security

- **Authentication Mechanism**:
  - Use [JWT/API keys/OAuth/etc.]
  - Implementation details: [specific implementation guidance]
  - Token management: [expiration, refresh strategy, etc.]

- **Security Considerations**:
  - Transport layer security requirements
  - Data protection measures
  - Access control model

### 3. Data Format and Validation

- **Schema Definition**:
  ```json
  {
    "example_field": "Example value",
    "nested_object": {
      "property": "value"
    }
  }
  ```

- **Validation Rules**:
  - Required fields: [list fields]
  - Type constraints: [data type requirements]
  - Business rule validation: [business-specific rules]

### 4. Error Handling and Resilience

- **Error Response Format**:
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human-readable message",
      "details": {}
    }
  }
  ```

- **Retry Strategy**:
  - Exponential backoff with [specific parameters]
  - Circuit breaker pattern implementation
  - Fallback mechanisms

### 5. Implementation Timeline

- Week 1: Implement authentication mechanism
- Week 2: Develop core API endpoints
- Week 3: Implement data validation and error handling
- Week 4: Testing and refining

## Resolution

Both teams should:
1. Implement the integration according to the specifications above
2. Schedule weekly sync meetings during implementation
3. Develop comprehensive integration tests
4. Document the final integration pattern for future reference
```

## Architecture Advisory Template

```markdown
# Advisory: Architecture Guidance for [Feature/Component]

Version: 1.0.0
Status: ANSWERED
Project: [Project Name]
Created: [YYYY-MM-DD]
Last Updated: [YYYY-MM-DD]

## Question

We need architecture guidance for [feature/component], specifically:
1. How should we structure the component?
2. What patterns should we apply?
3. How should this component interact with [related components]?

## Context

We're implementing [feature/component] which needs to [describe requirements]. We want to ensure this design aligns with the overall system architecture.

## Response

### 1. Component Structure

I recommend a [microservice/layered/modular/etc.] architecture:

```
[ASCII/text diagram of component structure]
```

Key components:
- **[Component A]**: Responsible for [functionality]
- **[Component B]**: Handles [functionality]
- **[Component C]**: Manages [functionality]

### 2. Design Patterns

Apply the following patterns:

- **[Pattern A]**:
  - Purpose: [Why this pattern is appropriate]
  - Implementation details: [How to implement]
  - Example: [Code snippet or diagram]

- **[Pattern B]**:
  - Purpose: [Why this pattern is appropriate]
  - Implementation details: [How to implement]
  - Example: [Code snippet or diagram]

### 3. Data Management

- **Data Flow**:
  - [Describe how data flows through the component]
  - [Identify potential bottlenecks]
  - [Suggest optimizations]

- **State Management**:
  - [Recommendations for managing state]
  - [Caching strategy]
  - [Persistence considerations]

### 4. Performance Considerations

- **Scalability**:
  - [Vertical/horizontal scaling approach]
  - [Load balancing strategy]
  - [Resource requirements]

- **Optimizations**:
  - [Specific optimization techniques]
  - [Performance targets]
  - [Monitoring approach]

### 5. Integration Points

- **Interfaces**:
  - [Define interfaces with other components]
  - [Communication protocols]
  - [Contract definitions]

## Resolution

The team should:
1. Implement the architecture as outlined above
2. Create detailed design documentation
3. Validate the design with performance testing
4. Review the implementation after completing key milestones
```

## Timeline/Scope Advisory Template

```markdown
# Advisory: Timeline and Scope Adjustment for [Feature/Phase]

Version: 1.0.0
Status: ANSWERED
Project: [Project Name]
Created: [YYYY-MM-DD]
Last Updated: [YYYY-MM-DD]

## Question

We need guidance on adjusting the timeline and scope for [feature/phase] due to [challenges encountered].

## Context

We've encountered [specific challenges] while implementing [feature/phase]. Our current timeline estimated completion by [original date], but we now anticipate needing [additional time].

## Response

### 1. Timeline Assessment

Based on your report and the challenges encountered, I agree that the timeline needs adjustment:

- **Original Timeline**: [Original timeline]
- **Revised Timeline**: [New timeline]
- **Critical Path Impact**: [How this affects other components/projects]

### 2. Scope Recommendations

To accommodate the timeline constraints, I recommend the following scope adjustments:

- **Priority Features**:
  - [Feature A]: Essential for [reason]
  - [Feature B]: Critical for [reason]
  - [Feature C]: Required for [reason]

- **Deferrable Features**:
  - [Feature D]: Can be moved to Phase [X+1]
  - [Feature E]: Can be simplified to [alternative approach]
  - [Feature F]: Can be descoped entirely

### 3. Risk Mitigation

- **Identified Risks**:
  - [Risk A]: [Probability and impact]
  - [Risk B]: [Probability and impact]

- **Mitigation Strategies**:
  - [Strategy for Risk A]
  - [Strategy for Risk B]
  - [General risk management approach]

### 4. Dependency Management

- **Impact on Dependent Projects**:
  - [Project X]: [Specific impact and mitigation]
  - [Project Y]: [Specific impact and mitigation]

- **Communication Plan**:
  - [How to communicate changes to stakeholders]
  - [Coordination meetings needed]

## Resolution

The team should:
1. Adjust the project plan according to the revised timeline
2. Implement the suggested scope modifications
3. Document the scope changes in the project documentation
4. Provide weekly status updates focusing on risk areas
5. Coordinate with affected teams to manage dependencies
```

## Performance Optimization Advisory Template

```markdown
# Advisory: Performance Optimization for [Component/Feature]

Version: 1.0.0
Status: ANSWERED
Project: [Project Name]
Created: [YYYY-MM-DD]
Last Updated: [YYYY-MM-DD]

## Question

We need guidance on addressing performance issues with [component/feature], specifically:
1. [Performance issue A]
2. [Performance issue B]
3. [Performance issue C]

## Context

Our current implementation of [component/feature] is experiencing [specific performance issues] under [conditions]. We're targeting [performance goals].

## Response

### 1. Diagnosis Summary

Based on the performance data provided, the key bottlenecks are:

- **[Bottleneck A]**:
  - Current performance: [metrics]
  - Impact: [description of impact]
  - Root cause: [analysis of cause]

- **[Bottleneck B]**:
  - Current performance: [metrics]
  - Impact: [description of impact]
  - Root cause: [analysis of cause]

### 2. Optimization Recommendations

#### High Priority Optimizations

1. **[Optimization A]**:
   - Approach: [detailed description]
   - Expected improvement: [percentage or metrics]
   - Implementation complexity: [low/medium/high]
   - Code example:
     ```
     [Code snippet demonstrating the optimization]
     ```

2. **[Optimization B]**:
   - Approach: [detailed description]
   - Expected improvement: [percentage or metrics]
   - Implementation complexity: [low/medium/high]
   - Code example:
     ```
     [Code snippet demonstrating the optimization]
     ```

#### Medium Priority Optimizations

3. **[Optimization C]**:
   - Approach: [detailed description]
   - Expected improvement: [percentage or metrics]
   - Implementation complexity: [low/medium/high]

4. **[Optimization D]**:
   - Approach: [detailed description]
   - Expected improvement: [percentage or metrics]
   - Implementation complexity: [low/medium/high]

### 3. Architectural Considerations

- **Caching Strategy**:
  - [Recommendations for caching]
  - [Cache invalidation approach]
  - [Technology suggestions]

- **Concurrency Model**:
  - [Thread/process model recommendations]
  - [Resource utilization strategy]
  - [Locking and synchronization guidance]

### 4. Testing and Validation

- **Performance Benchmarking**:
  - [Benchmark methodology]
  - [Key metrics to measure]
  - [Success criteria]

- **Load Testing**:
  - [Testing scenarios]
  - [Tool recommendations]
  - [Test data requirements]

## Resolution

The team should:
1. Implement the high-priority optimizations first
2. Measure performance impact after each change
3. Proceed with medium-priority optimizations if needed
4. Document optimization techniques for future reference
5. Incorporate performance testing into the CI/CD pipeline
```

## How to Use These Templates

1. Select the most appropriate template for the advisory situation
2. Customize the template with project-specific details
3. Be specific in your recommendations and include examples when possible
4. Ensure the "Resolution" section provides clear next steps
5. Review the advisory for clarity, completeness, and actionability before finalizing

Always adapt these templates to the specific needs of the project and the nature of the question or blocker being addressed. 