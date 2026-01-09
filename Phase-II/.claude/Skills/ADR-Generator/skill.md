---
name: adr-generator
description: Generate Architecture Decision Records (ADRs) for documenting significant architectural decisions. Capture context, decision rationale, alternatives considered, and consequences. Use consistent ADR template with proper structure and versioning. Use when documenting technology choices, architectural patterns, infrastructure decisions, API designs, data models, security approaches, or any significant technical decision that impacts system design. Ensures decisions are traceable, durable, and future-readable.
---

# ADR Generator

Generate clear, concise Architecture Decision Records that document significant architectural decisions and their rationale.

## What is an ADR?

An Architecture Decision Record (ADR) is a document that captures a significant architectural decision, the context in which it was made, alternatives considered, and the consequences of the decision.

**ADRs are for decisions, not documentation.** They record the "why" behind choices, not the "how" of implementation.

## When to Create an ADR

### Do Create ADRs For

**Technology Choices**
- "We chose PostgreSQL over MongoDB for our primary database"
- "We adopted TypeScript instead of JavaScript"
- "We selected AWS Lambda for serverless compute"

**Architectural Patterns**
- "We implemented event-driven architecture using message queues"
- "We adopted microservices over monolithic architecture"
- "We chose CQRS pattern for read/write separation"

**Infrastructure Decisions**
- "We deployed to Kubernetes instead of traditional VMs"
- "We selected multi-region active-active deployment"
- "We chose serverless over container-based deployment"

**API Design**
- "We standardized on REST over GraphQL"
- "We adopted OpenAPI 3.0 for API specifications"
- "We implemented JWT-based authentication"

**Data Models**
- "We normalized our database schema to 3NF"
- "We chose event sourcing for audit trail"
- "We adopted star schema for data warehouse"

**Security Approaches**
- "We implemented zero-trust network architecture"
- "We chose OAuth 2.0 with PKCE for authentication"
- "We adopted encryption at rest for all PII data"

### Do NOT Create ADRs For

**Trivial Decisions**
- Variable naming conventions (too granular)
- Minor library version updates (unless major breaking change)
- Temporary workarounds (not architectural)

**Implementation Details**
- "How to write a for loop" (not architectural)
- Code formatting rules (use linters)
- File organization within a module (too detailed)

**Speculative Decisions**
- "We might use Redis in the future" (not committed)
- "We're considering microservices" (not decided)

**Obvious Choices**
- "We use Git for version control" (industry standard)
- "We write tests" (best practice, not a decision)

## ADR Template

```markdown
# [NUMBER]. [SHORT TITLE]

Date: [YYYY-MM-DD]

## Status

[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Context

[Describe the situation that requires a decision. What problem are we solving?
What constraints exist? What are the forces at play?]

## Decision

[State the decision clearly and concisely. Use active voice and present tense.
"We will...", "We have decided to...", "We are adopting..."]

## Alternatives Considered

[List alternatives that were evaluated. For each, briefly explain why it was
NOT chosen.]

### Alternative 1: [Name]
- [Brief description]
- [Why not chosen]

### Alternative 2: [Name]
- [Brief description]
- [Why not chosen]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Trade-off 1]
- [Trade-off 2]

### Neutral
- [Impact 1]
- [Impact 2]

## Implementation Notes

[Optional: Key implementation considerations, migration path, or rollout plan]

## References

[Optional: Links to RFCs, documentation, benchmarks, or related discussions]
```

## Writing Each Section

### Title

**Format**: `[NUMBER]. [SHORT DESCRIPTIVE TITLE]`

**Good Examples**:
- `001. Use PostgreSQL as Primary Database`
- `002. Adopt Microservices Architecture`
- `003. Implement Event-Driven Communication`

**Bad Examples**:
- `Database Decision` (too vague)
- `ADR about choosing PostgreSQL over other databases we considered` (too long)
- `Tech Stack` (too broad)

### Status

**Use one of these statuses**:
- **Proposed**: Under discussion, not yet approved
- **Accepted**: Approved and being implemented
- **Deprecated**: No longer relevant but kept for history
- **Superseded by ADR-XXX**: Replaced by a newer decision

**Status Evolution**:
```
Proposed → Accepted → [Deprecated | Superseded]
```

**Never delete ADRs**. Mark them as deprecated or superseded instead.

### Context

**What to Include**:
- The problem or opportunity
- Technical constraints
- Business requirements
- Current system state
- Triggering events

**Structure**:
1. **Current Situation**: "Currently, we..."
2. **Problem**: "We face challenges with..."
3. **Requirements**: "We need to..."
4. **Constraints**: "We must consider..."

**Example - Good Context**:
```markdown
## Context

Our monolithic application currently serves 10,000 requests/minute during peak
hours. Response times have degraded to 2-3 seconds as the codebase has grown
to 500K lines of code. We have 15 developers working on the same codebase,
leading to merge conflicts and slow release cycles.

We need to:
- Reduce response times to under 500ms
- Enable independent team deployments
- Support horizontal scaling for specific high-traffic features

Constraints:
- Must maintain data consistency for financial transactions
- Cannot break existing client integrations
- Must complete migration within 6 months
```

**Example - Bad Context**:
```markdown
## Context

We need to improve the system because it's slow. Microservices are popular
and other companies use them successfully.
```
*Problem: Vague, lacks specifics, justifies by popularity rather than needs*

### Decision

**Write in active voice and present tense**:
- ✅ "We will adopt microservices architecture"
- ✅ "We are implementing event-driven communication"
- ❌ "It was decided that microservices might be good"
- ❌ "We could potentially consider microservices"

**Be Specific**:
```markdown
## Decision

We will adopt PostgreSQL 15+ as our primary relational database for all
transactional data. All new services must use PostgreSQL unless explicitly
exempted through a separate ADR.

We will:
- Use connection pooling via PgBouncer
- Implement read replicas for analytics workloads
- Store JSON data using JSONB columns where appropriate
- Use native PostgreSQL features (arrays, JSONB, full-text search) over 
  external solutions where possible
```

**Be Clear About Scope**:
```markdown
## Decision

We will migrate our user authentication system to use OAuth 2.0 with PKCE flow.

This applies to:
- Web application login
- Mobile app authentication
- API access for third-party integrations

This does NOT apply to:
- Internal admin tools (will continue using existing SSO)
- Legacy API endpoints (deprecated, will be removed in Q3)
```

### Alternatives Considered

**List 2-4 realistic alternatives**. For each, explain:
1. What it is
2. Key advantages
3. Why it wasn't chosen

**Example - Good Alternatives**:
```markdown
## Alternatives Considered

### Alternative 1: MongoDB

Document database with flexible schema and horizontal scaling.

**Advantages**:
- Flexible schema allows rapid iteration
- Built-in sharding for horizontal scaling
- Strong JSON document support

**Why not chosen**:
- Our data has clear relational structure
- ACID guarantees across documents are limited
- Team lacks MongoDB expertise
- Complex queries perform poorly compared to SQL

### Alternative 2: MySQL

Mature, widely-used relational database.

**Advantages**:
- Large community and extensive tooling
- Team has existing expertise
- Proven at scale

**Why not chosen**:
- JSON support less mature than PostgreSQL
- Full-text search capabilities inferior
- No native JSONB indexing like PostgreSQL
- We need advanced indexing (GiST, GIN) for geospatial queries

### Alternative 3: Remain with Current SQLite Setup

Keep using SQLite with manual sharding.

**Advantages**:
- No migration cost
- Simple deployment model
- Low operational overhead

**Why not chosen**:
- Cannot scale beyond single server
- Manual sharding becoming unmaintainable
- No built-in replication for high availability
- Write concurrency limitations blocking performance
```

**Example - Bad Alternatives**:
```markdown
## Alternatives Considered

### Use NoSQL
We could use NoSQL but SQL is better for our needs.

### Stay with current database
This wouldn't solve our problems.
```
*Problem: Too vague, no specific options, no real analysis*

### Consequences

**Organize into three categories**:
1. **Positive**: Benefits and improvements
2. **Negative**: Trade-offs and costs
3. **Neutral**: Changes without clear positive/negative impact

**Be Honest About Trade-offs**:
```markdown
## Consequences

### Positive

- **Performance**: Expected 80% reduction in query times for complex joins
  using PostgreSQL's query planner
- **Data Integrity**: Full ACID compliance ensures consistency for financial
  transactions
- **Developer Productivity**: Rich SQL feature set reduces application code
  complexity
- **Operational Maturity**: Extensive monitoring and tooling ecosystem

### Negative

- **Migration Effort**: 6-8 weeks to migrate existing 50GB SQLite database
  to PostgreSQL
- **Operational Complexity**: Requires dedicated database administration
  compared to SQLite's simplicity
- **Cost**: $2,000/month for managed PostgreSQL hosting vs $0 for SQLite
- **Learning Curve**: 2 developers need PostgreSQL training

### Neutral

- **Backup Strategy**: Must implement new backup procedures for PostgreSQL
  (shift from file-based to pg_dump)
- **Development Environment**: Docker-based PostgreSQL for local development
  instead of file-based SQLite
- **Connection Management**: Requires connection pooling layer (PgBouncer)
  for optimal performance
```

**Avoid Vague Consequences**:
- ❌ "It will be better"
- ❌ "Might improve performance"
- ❌ "Users will be happier"

**Be Specific**:
- ✅ "Query response times reduced from 2s to 200ms (measured in staging)"
- ✅ "Reduces deployment time from 2 hours to 15 minutes"
- ✅ "Increases infrastructure cost by $500/month"

### Implementation Notes (Optional)

**Use this section for**:
- Migration strategy
- Rollout phases
- Key risks and mitigations
- Timeline
- Success metrics

**Example**:
```markdown
## Implementation Notes

**Migration Plan**:

Phase 1 (Week 1-2): Setup
- Provision PostgreSQL cluster
- Set up replication and backups
- Configure monitoring

Phase 2 (Week 3-4): Data Migration
- Export SQLite data
- Transform and load into PostgreSQL
- Validate data integrity

Phase 3 (Week 5-6): Application Migration
- Update connection strings
- Deploy to staging environment
- Run integration tests
- Deploy to production with feature flag

Phase 4 (Week 7-8): Validation
- Monitor performance metrics
- Gather team feedback
- Decommission SQLite

**Rollback Plan**:
Feature flag allows instant rollback to SQLite if critical issues occur.

**Success Metrics**:
- Query response time < 500ms (p95)
- Zero data loss during migration
- No increase in error rate
- Successful completion within 8 weeks
```

### References (Optional)

**Link to supporting materials**:
- Technical RFCs
- Benchmark results
- Documentation
- Related ADRs
- Discussion threads
- External articles

**Example**:
```markdown
## References

- [PostgreSQL vs MySQL Benchmark Results](link)
- [Internal RFC-042: Database Strategy](link)
- [Related ADR-012: Data Sharding Strategy](link)
- [PostgreSQL Documentation: JSONB Indexing](link)
- [Team Discussion: Database Migration](link)
```

## ADR Organization

### File Structure

```
docs/adr/
├── README.md                    # ADR index and guidelines
├── template.md                  # ADR template
├── 0001-record-architecture-decisions.md
├── 0002-use-postgresql-database.md
├── 0003-adopt-microservices.md
├── 0004-implement-event-bus.md
└── 0005-use-jwt-authentication.md
```

### Naming Convention

**Format**: `[NNNN]-[kebab-case-title].md`

**Examples**:
- `0001-record-architecture-decisions.md`
- `0012-use-postgresql-as-primary-database.md`
- `0023-adopt-event-driven-architecture.md`

**Zero-padding**: Use 4 digits (0001, 0002, etc.) for proper sorting

### README.md Structure

```markdown
# Architecture Decision Records

## About ADRs

[Brief explanation of what ADRs are and why we use them]

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [001](0001-record-architecture-decisions.md) | Record Architecture Decisions | Accepted | 2024-01-15 |
| [002](0002-use-postgresql-database.md) | Use PostgreSQL as Primary Database | Accepted | 2024-01-20 |
| [003](0003-adopt-microservices.md) | Adopt Microservices Architecture | Accepted | 2024-02-01 |
| [004](0004-implement-event-bus.md) | Implement Event-Driven Communication | Proposed | 2024-02-15 |

## Creating New ADRs

[Instructions for creating new ADRs]
```

## Version Control

### When to Update an ADR

**Never modify an accepted ADR's decision**. Instead:
1. Create a new ADR that supersedes it
2. Update the old ADR's status to "Superseded by ADR-XXX"

**Example Update**:
```markdown
# 002. Use PostgreSQL as Primary Database

Date: 2024-01-20

## Status

Superseded by ADR-015 (Use Distributed SQL with CockroachDB)

[Rest of original ADR remains unchanged]
```

### Git Workflow

**One ADR per commit**:
```bash
git add docs/adr/0012-use-postgresql.md
git commit -m "ADR-012: Use PostgreSQL as Primary Database"
```

**Link ADRs to code changes**:
```bash
git commit -m "Implement PostgreSQL migration (ADR-012)"
```

## Complete ADR Example

```markdown
# 003. Adopt Microservices Architecture

Date: 2024-02-01

## Status

Accepted

## Context

Our monolithic e-commerce application currently serves 50,000 orders per day
with a codebase of 800K lines. We face several critical challenges:

**Performance Issues**:
- Average response time: 2.5 seconds (target: < 500ms)
- Database locks during checkout causing order failures
- Cannot scale individual features independently

**Development Bottlenecks**:
- 25 developers working in single codebase
- Average 15 merge conflicts per day
- Release cycle: 2 weeks (target: daily deploys)
- 45-minute test suite blocking CI/CD pipeline

**Business Requirements**:
- Black Friday traffic expected to 10x (500K orders/day)
- Launch marketplace feature requiring third-party integrations
- International expansion requiring regional data compliance

**Technical Constraints**:
- Must maintain 99.9% uptime during migration
- Cannot break existing mobile app clients (v1.2+)
- PCI DSS compliance for payment processing
- Budget: $200K for migration over 6 months

## Decision

We will decompose our monolithic application into microservices using a
domain-driven design approach. 

**Service Boundaries** (initial phase):
1. **User Service**: Authentication, profiles, preferences
2. **Product Catalog Service**: Products, inventory, search
3. **Order Service**: Cart, checkout, order management
4. **Payment Service**: Payment processing, PCI-compliant zone
5. **Notification Service**: Email, SMS, push notifications

**Technical Approach**:
- Kubernetes for orchestration
- gRPC for inter-service communication
- PostgreSQL per service (database-per-service pattern)
- Redis for distributed caching
- RabbitMQ for asynchronous events
- Kong API Gateway for external traffic

**Migration Strategy**:
- Strangler Fig pattern: gradually extract services
- API Gateway routes traffic to monolith or services
- Maintain monolith in maintenance mode during migration
- Complete migration in 3 phases over 6 months

## Alternatives Considered

### Alternative 1: Optimize Monolith

Keep monolithic architecture but optimize performance through caching,
database tuning, and code refactoring.

**Advantages**:
- No architectural complexity
- Simpler deployment and operations
- Lower upfront cost (~$50K)
- Faster to implement (2 months)

**Why not chosen**:
- Does not solve team scalability (25 developers in one codebase)
- Cannot independently scale high-traffic features
- Single point of failure remains
- Technical debt continues to accumulate
- Does not enable international data residency requirements

### Alternative 2: Modular Monolith

Restructure codebase into modules with clear boundaries but keep single
deployment unit.

**Advantages**:
- Simpler operations than microservices
- Modules enforce boundaries
- Single database simplifies transactions
- Lower infrastructure cost

**Why not chosen**:
- Cannot independently scale modules
- Modules cannot be deployed independently
- Risk of boundary violations over time
- Does not solve 45-minute test suite problem
- Cannot isolate failures (one module crash affects all)

### Alternative 3: Serverless Functions

Rewrite application as AWS Lambda functions with API Gateway.

**Advantages**:
- Zero server management
- Automatic scaling
- Pay-per-invocation pricing

**Why not chosen**:
- Cold start latency unacceptable for e-commerce (>1s)
- Complex state management for checkout flow
- Vendor lock-in to AWS
- Limited control over infrastructure
- Team lacks serverless expertise
- Higher latency for inter-function communication

## Consequences

### Positive

- **Independent Scaling**: Can scale Product Catalog independently during
  traffic spikes (reduce costs by 40% vs scaling entire monolith)
- **Team Autonomy**: 5 teams can work independently with reduced merge
  conflicts (estimated 80% reduction)
- **Faster Deployments**: Services can deploy independently, enabling daily
  releases (vs 2-week cycles)
- **Failure Isolation**: Payment service failure doesn't affect product
  browsing (improved uptime SLA from 99.5% to 99.9%)
- **Technology Flexibility**: Can use optimal technology per service (e.g.,
  Elasticsearch for search, Redis for sessions)
- **Regional Deployment**: Can deploy services in EU region for GDPR
  compliance

### Negative

- **Increased Complexity**: 5 services vs 1 application increases operational
  overhead
- **Distributed Transactions**: Cannot use database transactions across
  services, must implement saga pattern
- **Network Latency**: Inter-service calls add 10-20ms overhead per hop
- **Infrastructure Cost**: Estimated $15K/month vs $5K/month for monolith
  (3x increase)
- **Monitoring Complexity**: Requires distributed tracing (Jaeger) to debug
  issues across services
- **Team Learning Curve**: 3-4 weeks training on Kubernetes, gRPC, distributed
  systems patterns
- **Data Consistency**: Eventual consistency between services requires careful
  design

### Neutral

- **Development Environment**: Developers need Docker + Kubernetes locally
  (existing workflow)
- **Testing Strategy**: Shift from integration tests to contract tests
  between services
- **Deployment Pipeline**: Need separate CI/CD pipeline per service (6 total)
- **Documentation**: Must document service APIs (OpenAPI/Protobuf specs)

## Implementation Notes

**Phase 1: Foundation (Months 1-2)**
- Set up Kubernetes cluster (AWS EKS)
- Deploy API Gateway (Kong)
- Implement monitoring (Prometheus, Grafana, Jaeger)
- Extract User Service (lowest risk)
- Set up CI/CD pipelines

**Phase 2: Core Services (Months 3-4)**
- Extract Product Catalog Service
- Extract Order Service
- Implement event bus (RabbitMQ)
- Migrate 20% of traffic through API Gateway

**Phase 3: Critical Services (Months 5-6)**
- Extract Payment Service (PCI compliance zone)
- Extract Notification Service
- Migrate 100% of traffic
- Decommission monolith (maintenance mode)

**Risk Mitigation**:
- API Gateway routes enable gradual rollout and instant rollback
- Feature flags for service-by-service activation
- Parallel run: services mirror monolith for 2 weeks before cutover
- Load testing at each phase (simulate Black Friday traffic)

**Success Metrics**:
- Average response time < 500ms (p95)
- Zero downtime during migration
- Deploy frequency: 5+ deploys/week per service
- Merge conflicts reduced by 70%
- Cost increase < 2x current spend

**Rollback Plan**:
- API Gateway can route traffic back to monolith
- Keep monolith running for 3 months after full migration
- Database replication allows reverting data changes

## References

- [RFC-043: Microservices Migration Strategy](link)
- [Load Testing Results: Monolith vs Microservices](link)
- [Team Survey: Developer Pain Points](link)
- [AWS Well-Architected Framework: Microservices](link)
- [Related ADR-002: Use PostgreSQL](0002-use-postgresql.md)
- [Related ADR-004: Event-Driven Communication](0004-event-bus.md)
```

## Common Mistakes to Avoid

### Mistake 1: Too Much Detail

❌ **Bad**: 15-page ADR with UML diagrams and complete API specifications

✅ **Good**: 2-page ADR that captures decision and rationale, linking to detailed design docs

**Rule**: ADR is not design documentation. Keep it concise.

### Mistake 2: No Real Alternatives

❌ **Bad**:
```markdown
## Alternatives Considered

We considered other options but they weren't suitable.
```

✅ **Good**: List specific alternatives with real pros/cons analysis

### Mistake 3: Vague Context

❌ **Bad**: "We need to improve performance"

✅ **Good**: "Response times are 2.5s with 10K users. We need < 500ms for 50K users by Q3"

### Mistake 4: Missing Consequences

❌ **Bad**: Only listing positive outcomes

✅ **Good**: Honest assessment of trade-offs, costs, and risks

### Mistake 5: Premature ADRs

❌ **Bad**: Creating ADR before decision is actually made

✅ **Good**: Create ADR when decision is committed, not during exploration

### Mistake 6: Modifying Accepted ADRs

❌ **Bad**: Editing an accepted ADR when decision changes

✅ **Good**: Create new ADR that supersedes the old one

### Mistake 7: ADRs for Non-Decisions

❌ **Bad**: "ADR: We will follow coding standards"

✅ **Good**: "ADR: We will use TypeScript instead of JavaScript"

## Quick Reference

### ADR Creation Checklist

- [ ] Significant architectural decision (not trivial)
- [ ] Title is clear and descriptive
- [ ] Context explains the problem and constraints
- [ ] Decision is stated clearly in active voice
- [ ] 2-4 realistic alternatives are analyzed
- [ ] Consequences include positive, negative, and neutral impacts
- [ ] All sections are concise (aim for 2-3 pages total)
- [ ] References link to supporting materials
- [ ] File follows naming convention (NNNN-kebab-case.md)
- [ ] Status is appropriate (Proposed, Accepted, etc.)
- [ ] Date is included

### Red Flags

Stop and reconsider if:
- ADR is > 5 pages (probably too detailed)
- No alternatives considered (incomplete analysis)
- Only positive consequences listed (unrealistic)
- Context is vague or missing (lacks foundation)
- Decision could change next week (not architectural)
- Trivial decision that doesn't need documentation

## First ADR

Every project should start with this ADR:

```markdown
# 001. Record Architecture Decisions

Date: 2024-01-15

## Status

Accepted

## Context

We need to document architectural decisions to help current and future team
members understand why we made specific technical choices.

## Decision

We will use Architecture Decision Records (ADRs) to document significant
architectural decisions.

An ADR is a short text file describing a decision, its context, alternatives
considered, and consequences.

## Alternatives Considered

### Alternative 1: Wiki Documentation

Maintain architectural decisions in team wiki.

**Why not chosen**:
- Disconnected from code
- No version control
- Often becomes outdated

### Alternative 2: No Formal Documentation

Rely on tribal knowledge and code comments.

**Why not chosen**:
- Knowledge is lost when team members leave
- No historical context for decisions
- New team members lack context

## Consequences

### Positive

- Decisions are documented and searchable
- Future team members understand rationale
- Prevents rehashing old decisions
- Creates shared understanding

### Negative

- Requires discipline to maintain
- Small overhead for each decision

## References

- [ADR GitHub Repository](https://github.com/joelparkerhenderson/architecture-decision-record)
```

## Summary

**ADRs capture the "why" behind architectural decisions**. Keep them:
- **Concise**: 2-3 pages maximum
- **Focused**: One decision per ADR
- **Honest**: Document trade-offs
- **Durable**: Never delete, only supersede
- **Traceable**: Link to code and docs

**Good ADRs help teams**:
- Understand past decisions
- Avoid rehashing old discussions
- Onboard new members faster
- Make consistent future decisions