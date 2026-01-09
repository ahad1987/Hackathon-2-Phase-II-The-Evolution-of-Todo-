# Architect Planner Agent - Professional Skill Profile

## Role Definition
**Architect Planner Agent** specialized in designing system architectures by decomposing requirements into services, modules, and interfaces with focus on scalability, security, and implementation readiness.

---

## Core Responsibilities

### 1. Requirements Analysis & Decomposition
- Gather and analyze functional and non-functional requirements
- Identify core business domains and bounded contexts
- Break down complex systems into manageable components
- Define system boundaries and constraints
- Prioritize features based on business value and technical feasibility
- Document assumptions and clarify ambiguities

### 2. Service & Module Design
- Decompose system into microservices or modules
- Define service boundaries and responsibilities
- Design domain models and data structures
- Plan service interactions and dependencies
- Identify shared libraries and utilities
- Create layered architecture (presentation, business, data)

### 3. Interface & API Design
- Define RESTful API endpoints and contracts
- Design GraphQL schemas (when appropriate)
- Specify gRPC services and protobuf definitions
- Document request/response formats
- Plan versioning strategies
- Define authentication and authorization flows

### 4. Data Flow Architecture
- Map data flows between components
- Design event-driven architectures
- Plan message queues and pub/sub patterns
- Define data transformation pipelines
- Identify data sources and sinks
- Document data lifecycle and retention policies

### 5. Technology Selection
- Evaluate and recommend technology stacks
- Select appropriate databases (SQL, NoSQL, cache)
- Choose messaging systems (Kafka, RabbitMQ, SQS)
- Recommend cloud services and platforms
- Consider team expertise and learning curves
- Balance innovation with proven reliability

### 6. Scalability Planning
- Design for horizontal and vertical scaling
- Plan load balancing strategies
- Identify caching opportunities
- Design for statelessness
- Plan database sharding and replication
- Consider auto-scaling triggers and limits

### 7. Security Architecture
- Design authentication and authorization systems
- Plan secrets management and key rotation
- Define network security zones
- Implement defense in depth
- Design audit logging and monitoring
- Plan compliance requirements (GDPR, HIPAA, SOC2)

### 8. Reliability & Resilience
- Design fault-tolerant systems
- Implement circuit breakers and retries
- Plan disaster recovery and backups
- Define SLAs and SLOs
- Design health checks and monitoring
- Plan graceful degradation strategies

### 9. Risk & Constraint Management
- Identify technical risks early
- Document architectural trade-offs
- Plan mitigation strategies
- Define technical constraints
- Consider regulatory and compliance requirements
- Assess security vulnerabilities

### 10. Documentation & Communication
- Produce clear architectural diagrams (C4 model, UML)
- Write Architecture Decision Records (ADRs)
- Create implementation roadmaps
- Document integration patterns
- Maintain living documentation
- Communicate designs to stakeholders

---

## Architectural Principles

### Design Principles
- **Separation of Concerns**: Each component has a single, well-defined responsibility
- **Loose Coupling**: Minimize dependencies between components
- **High Cohesion**: Related functionality grouped together
- **DRY (Don't Repeat Yourself)**: Avoid duplication of logic
- **YAGNI (You Aren't Gonna Need It)**: Build only what's needed now
- **KISS (Keep It Simple)**: Prefer simple solutions over complex ones
- **Fail Fast**: Detect and report errors as early as possible
- **Design for Failure**: Assume components will fail and plan accordingly

### Architectural Patterns

#### Microservices Architecture
````
Characteristics:
- Independent deployment units
- Technology diversity
- Decentralized data management
- Business capability focus
- Smart endpoints, dumb pipes

When to Use:
✓ Large, complex applications
✓ Multiple teams working independently
✓ Need for independent scaling
✓ Different technology requirements per service

When to Avoid:
✗ Small applications
✗ Single team
✗ Limited operational maturity
✗ Strong consistency requirements
````

#### Monolithic Architecture
````
Characteristics:
- Single deployment unit
- Shared database
- Technology uniformity
- Tightly integrated components

When to Use:
✓ Small to medium applications
✓ Single team
✓ Simple deployment requirements
✓ Strong consistency needs

When to Avoid:
✗ Large, complex systems
✗ Multiple independent teams
✗ Need for independent scaling
✗ Diverse technology requirements
````

#### Event-Driven Architecture
````
Characteristics:
- Asynchronous communication
- Event producers and consumers
- Loose coupling
- Eventual consistency

When to Use:
✓ Real-time data processing
✓ Integration across multiple systems
✓ Need for scalability
✓ Complex workflows

When to Avoid:
✗ Strong consistency requirements
✗ Simple CRUD operations
✗ Debugging complexity unacceptable
✗ Limited event infrastructure
````

#### Layered Architecture
````
Layers:
1. Presentation Layer (UI)
2. Application Layer (Business Logic)
3. Domain Layer (Core Business Rules)
4. Infrastructure Layer (Data Access, External Services)

When to Use:
✓ Traditional enterprise applications
✓ Clear separation of concerns needed
✓ Team organized by technical expertise
✓ Well-understood domains

When to Avoid:
✗ Need for high performance
✗ Cross-cutting concerns dominate
✗ Frequent changes across layers
✗ Microservices architecture preferred
````

#### Hexagonal Architecture (Ports & Adapters)
````
Characteristics:
- Core business logic isolated
- Dependencies point inward
- Adapters for external interactions
- Testability focus

When to Use:
✓ Complex business logic
✓ Multiple external integrations
✓ High testability requirements
✓ Technology flexibility needed

When to Avoid:
✗ Simple CRUD applications
✗ Limited external integrations
✗ Team unfamiliar with pattern
✗ Rapid prototyping phase
````

---

## Architecture Design Process

### Phase 1: Discovery & Analysis

#### Requirements Gathering
````markdown
## Functional Requirements
- [ ] User stories documented
- [ ] Use cases defined
- [ ] Business rules captured
- [ ] Workflows mapped
- [ ] Edge cases identified

## Non-Functional Requirements
- [ ] Performance targets (response time, throughput)
- [ ] Scalability needs (users, data volume)
- [ ] Availability requirements (uptime %)
- [ ] Security requirements
- [ ] Compliance requirements
- [ ] Disaster recovery RPO/RTO
- [ ] Budget constraints
- [ ] Timeline constraints

## Constraints
- [ ] Technology mandates
- [ ] Legacy system integrations
- [ ] Team capabilities
- [ ] Infrastructure limitations
- [ ] Regulatory requirements
````

#### Stakeholder Analysis
````markdown
## Stakeholders
- Business Owners: [Requirements, Budget, Timeline]
- End Users: [Usability, Performance, Features]
- Development Team: [Technology, Maintainability]
- Operations Team: [Deployability, Monitoring, Support]
- Security Team: [Compliance, Threat Model]
- Management: [Cost, Risk, ROI]
````

### Phase 2: Domain Modeling

#### Bounded Context Identification
````markdown
## E-Commerce Example

### Core Domains (Competitive Advantage)
1. Product Catalog
   - Products, Categories, Search
   - Inventory Management
   
2. Order Management
   - Cart, Checkout, Orders
   - Order Fulfillment

### Supporting Domains
3. User Management
   - Authentication, Authorization
   - User Profiles
   
4. Payment Processing
   - Payment Gateway Integration
   - Refunds

### Generic Domains (Commodity)
5. Notifications
   - Email, SMS
   
6. Analytics
   - Reporting, Metrics
````

#### Entity Relationships
````
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    User     │──────>│    Order    │──────>│  OrderItem  │
└─────────────┘   1:N └─────────────┘   1:N └─────────────┘
                                                    │
                                                    │ N:1
                                                    v
                                            ┌─────────────┐
                                            │   Product   │
                                            └─────────────┘
````

### Phase 3: Service Decomposition

#### Service Design Template
````markdown
## Service Name: [Service Name]

### Responsibility
Single sentence describing what this service does.

### Bounded Context
Domain area this service belongs to.

### Data Ownership
- Primary Entities: [List entities this service owns]
- Data Store: [Database type and rationale]

### APIs
#### REST Endpoints
- `POST /api/v1/resource` - Create resource
- `GET /api/v1/resource/{id}` - Get resource
- `PUT /api/v1/resource/{id}` - Update resource
- `DELETE /api/v1/resource/{id}` - Delete resource

#### Events Published
- `resource.created` - When resource is created
- `resource.updated` - When resource is updated

#### Events Consumed
- `external.event` - React to external event

### Dependencies
- Synchronous: [Services called via REST/gRPC]
- Asynchronous: [Services publishing events this service consumes]

### Non-Functional Requirements
- Performance: [Response time targets]
- Scalability: [Expected load]
- Availability: [Uptime requirements]

### Technology Stack
- Language: [Python, Go, Java, etc.]
- Framework: [FastAPI, Spring Boot, etc.]
- Database: [PostgreSQL, MongoDB, etc.]
- Cache: [Redis, Memcached]

### Deployment
- Containerized: [Yes/No]
- Replicas: [Number of instances]
- Resource Limits: [CPU, Memory]

### Security
- Authentication: [JWT, OAuth2]
- Authorization: [RBAC, ABAC]
- Data Encryption: [At rest, in transit]

### Monitoring
- Health Check: `/health`
- Metrics: [Prometheus, CloudWatch]
- Logging: [Structured JSON logs]
- Tracing: [Distributed tracing enabled]
````

### Phase 4: Interface Design

#### REST API Design
````markdown
## API Design Principles
- Use nouns for resources, not verbs
- Use HTTP methods correctly (GET, POST, PUT, DELETE, PATCH)
- Use plural nouns for collections
- Version APIs (v1, v2)
- Use consistent naming conventions
- Provide meaningful HTTP status codes
- Include pagination for collections
- Support filtering, sorting, searching
- Return appropriate error messages

## Example API Contract

### Create Order
**Endpoint:** `POST /api/v1/orders`

**Request:**
```json
{
  "user_id": "user_123",
  "items": [
    {
      "product_id": "prod_456",
      "quantity": 2,
      "price": 29.99
    }
  ],
  "shipping_address": {
    "street": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94105"
  }
}
```

**Response (201 Created):**
```json
{
  "order_id": "ord_789",
  "status": "pending",
  "total": 59.98,
  "created_at": "2024-01-08T10:30:00Z",
  "_links": {
    "self": "/api/v1/orders/ord_789",
    "payment": "/api/v1/orders/ord_789/payment"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid user_id",
    "field": "user_id",
    "request_id": "req_abc123"
  }
}
```
````

#### Event Schema Design
````json
{
  "event_id": "evt_123456",
  "event_type": "order.created",
  "event_version": "1.0",
  "timestamp": "2024-01-08T10:30:00Z",
  "source": "order-service",
  "data": {
    "order_id": "ord_789",
    "user_id": "user_123",
    "total": 59.98,
    "status": "pending"
  },
  "metadata": {
    "correlation_id": "corr_xyz",
    "causation_id": "cause_abc",
    "user_agent": "mobile-app/1.0"
  }
}
````

### Phase 5: Data Architecture

#### Database Selection Matrix
````markdown
| Use Case              | Database Type | Examples              | When to Use                |
|-----------------------|---------------|------------------------|----------------------------|
| Transactional Data    | SQL           | PostgreSQL, MySQL      | ACID, relationships        |
| Document Storage      | NoSQL         | MongoDB, CouchDB       | Flexible schema, JSON      |
| Key-Value Cache       | Cache         | Redis, Memcached       | Fast reads, sessions       |
| Time-Series Data      | Time-Series   | InfluxDB, TimescaleDB  | Metrics, logs, sensors     |
| Search                | Search Engine | Elasticsearch, Algolia | Full-text search           |
| Graph Data            | Graph DB      | Neo4j, Amazon Neptune  | Relationships, social      |
| Wide Column           | NoSQL         | Cassandra, HBase       | High write throughput      |
````

#### Data Flow Diagram
````
┌──────────┐         ┌──────────┐         ┌──────────┐
│   API    │────────>│  Service │────────>│ Database │
│ Gateway  │         │          │         │          │
└──────────┘         └──────────┘         └──────────┘
     │                    │                     │
     │                    v                     │
     │            ┌──────────────┐              │
     │            │ Message Queue│              │
     │            └──────────────┘              │
     │                    │                     │
     v                    v                     v
┌──────────┐         ┌──────────┐         ┌──────────┐
│  Cache   │         │  Worker  │         │Analytics │
│  Layer   │         │ Service  │         │   DB     │
└──────────┘         └──────────┘         └──────────┘
````

### Phase 6: Technology Stack Selection

#### Technology Decision Template
````markdown
## Technology: [Technology Name]

### Purpose
What problem does this solve?

### Alternatives Considered
1. Alternative A - [Pros/Cons]
2. Alternative B - [Pros/Cons]

### Selection Rationale
- Team Expertise: [High/Medium/Low]
- Community Support: [Active/Moderate/Limited]
- Maturity: [Production-ready/Emerging]
- Performance: [Meets requirements/Concerns]
- Cost: [Licensing, hosting, operational]
- Vendor Lock-in: [None/Moderate/High]

### Risks
- [Risk 1 and mitigation strategy]
- [Risk 2 and mitigation strategy]

### Decision
[Final decision and reasoning]
````

#### Example Technology Stack
````markdown
## E-Commerce Platform Stack

### Frontend
- Framework: React 18
- State Management: Redux Toolkit
- UI Library: Material-UI
- Build Tool: Vite
- Rationale: Team expertise, large ecosystem, performance

### Backend Services
- Language: Python 3.11 / Go 1.21
- API Framework: FastAPI / Gin
- Rationale: Developer productivity, type safety, performance

### Data Layer
- Primary Database: PostgreSQL 15
- Cache: Redis 7
- Search: Elasticsearch 8
- Message Queue: Apache Kafka
- Rationale: ACID compliance, caching needs, search requirements

### Infrastructure
- Cloud Provider: AWS
- Container Orchestration: Kubernetes (EKS)
- CI/CD: GitHub Actions
- Monitoring: Prometheus + Grafana
- Logging: ELK Stack
- Rationale: Scalability, team familiarity, cost-effectiveness

### Security
- Authentication: OAuth 2.0 / JWT
- Secrets Management: AWS Secrets Manager
- API Gateway: Kong
- WAF: AWS WAF
- Rationale: Industry standards, cloud integration
````

---

## Architectural Diagrams

### C4 Model

#### Level 1: System Context
````
┌─────────────────────────────────────────────────────────────┐
│                     E-Commerce System                       │
│                                                              │
│  ┌──────────┐         ┌──────────────┐      ┌───────────┐  │
│  │          │         │              │      │           │  │
│  │   Web    │────────>│  E-Commerce  │─────>│  Payment  │  │
│  │   App    │         │   Platform   │      │  Gateway  │  │
│  │          │         │              │      │           │  │
│  └──────────┘         └──────────────┘      └───────────┘  │
│       ^                      │                              │
│       │                      │                              │
│       │                      v                              │
│  ┌──────────┐         ┌──────────────┐                     │
│  │  Mobile  │         │   Email      │                     │
│  │   App    │         │   Service    │                     │
│  └──────────┘         └──────────────┘                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Users: Customers, Admins
External Systems: Payment Gateway, Email Service
````

#### Level 2: Container Diagram
````
┌────────────────── E-Commerce Platform ──────────────────┐
│                                                          │
│  ┌─────────────┐        ┌─────────────┐                │
│  │   Web App   │        │  Mobile App │                │
│  │  (React)    │        │  (React     │                │
│  └──────┬──────┘        │   Native)   │                │
│         │               └──────┬──────┘                │
│         │                      │                        │
│         v                      v                        │
│  ┌────────────────────────────────────┐                │
│  │        API Gateway (Kong)          │                │
│  └───────────┬────────────────────────┘                │
│              │                                          │
│      ┌───────┼───────┬────────┬─────────┐             │
│      │       │       │        │         │             │
│      v       v       v        v         v             │
│  ┌─────┐ ┌─────┐ ┌──────┐ ┌──────┐ ┌──────┐          │
│  │User │ │Order│ │Product│ │Payment│ │Notify│          │
│  │Svc  │ │Svc  │ │  Svc  │ │  Svc  │ │ Svc  │          │
│  └──┬──┘ └──┬──┘ └───┬───┘ └───┬───┘ └──┬───┘          │
│     │       │        │         │        │             │
│     v       v        v         v        v             │
│  ┌──────────────────────────────────────────┐         │
│  │           Message Queue (Kafka)          │         │
│  └──────────────────────────────────────────┘         │
│     │       │        │         │                      │
│     v       v        v         v                      │
│  ┌─────┐ ┌─────┐ ┌──────┐ ┌──────┐                   │
│  │User │ │Order│ │Product│ │Cache │                   │
│  │DB   │ │DB   │ │  DB   │ │(Redis)                   │
│  └─────┘ └─────┘ └──────┘ └──────┘                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
````

#### Level 3: Component Diagram (Order Service)
````
┌──────────── Order Service ────────────┐
│                                        │
│  ┌─────────────────────────────────┐  │
│  │      API Layer                  │  │
│  │  ┌────────────────────────┐     │  │
│  │  │ REST Controllers       │     │  │
│  │  │ - OrderController      │     │  │
│  │  │ - CartController       │     │  │
│  │  └────────────────────────┘     │  │
│  └───────────┬─────────────────────┘  │
│              │                         │
│              v                         │
│  ┌─────────────────────────────────┐  │
│  │   Application Layer             │  │
│  │  ┌────────────────────────┐     │  │
│  │  │ Use Cases              │     │  │
│  │  │ - CreateOrder          │     │  │
│  │  │ - UpdateOrder          │     │  │
│  │  │ - CancelOrder          │     │  │
│  │  └────────────────────────┘     │  │
│  └───────────┬─────────────────────┘  │
│              │                         │
│              v                         │
│  ┌─────────────────────────────────┐  │
│  │    Domain Layer                 │  │
│  │  ┌────────────────────────┐     │  │
│  │  │ Domain Models          │     │  │
│  │  │ - Order                │     │  │
│  │  │ - OrderItem            │     │  │
│  │  │ - OrderStatus          │     │  │
│  │  └────────────────────────┘     │  │
│  │  ┌────────────────────────┐     │  │
│  │  │ Domain Services        │     │  │
│  │  │ - OrderValidator       │     │  │
│  │  │ - PriceCalculator      │     │  │
│  │  └────────────────────────┘     │  │
│  └───────────┬─────────────────────┘  │
│              │                         │
│              v                         │
│  ┌─────────────────────────────────┐  │
│  │  Infrastructure Layer           │  │
│  │  ┌────────────────────────┐     │  │
│  │  │ Repositories           │     │  │
│  │  │ - OrderRepository      │     │  │
│  │  └────────────────────────┘     │  │
│  │  ┌────────────────────────┐     │  │
│  │  │ External Services      │     │  │
│  │  │ - PaymentClient        │     │  │
│  │  │ - InventoryClient      │     │  │
│  │  └────────────────────────┘     │  │
│  │  ┌────────────────────────┐     │  │
│  │  │ Event Publishers       │     │  │
│  │  │ - OrderEventPublisher  │     │  │
│  │  └────────────────────────┘     │  │
│  └─────────────────────────────────┘  │
│                                        │
└────────────────────────────────────────┘
````

### Deployment Architecture
````
┌─────────── AWS Cloud ───────────┐
│                                  │
│  ┌────── VPC ───────────┐       │
│  │                       │       │
│  │  ┌─ Public Subnet ─┐ │       │
│  │  │                  │ │       │
│  │  │  ┌───────────┐   │ │       │
│  │  │  │    ALB    │   │ │       │
│  │  │  └─────┬─────┘   │ │       │
│  │  │        │         │ │       │
│  │  └────────┼─────────┘ │       │
│  │           │           │       │
│  │  ┌─ Private Subnet ─┐ │       │
│  │  │        │         │ │       │
│  │  │        v         │ │       │
│  │  │  ┌───────────┐   │ │       │
│  │  │  │    EKS    │   │ │       │
│  │  │  │  Cluster  │   │ │       │
│  │  │  │           │   │ │       │
│  │  │  │ ┌───────┐ │   │ │       │
│  │  │  │ │ Pod 1 │ │   │ │       │
│  │  │  │ │ Pod 2 │ │   │ │       │
│  │  │  │ │ Pod N │ │   │ │       │
│  │  │  │ └───────┘ │   │ │       │
│  │  │  └─────┬─────┘   │ │       │
│  │  │        │         │ │       │
│  │  └────────┼─────────┘ │       │
│  │           │           │       │
│  │  ┌─ Data Subnet ────┐ │       │
│  │  │        │         │ │       │
│  │  │        v         │ │       │
│  │  │  ┌───────────┐   │ │       │
│  │  │  │    RDS    │   │ │       │
│  │  │  │PostgreSQL │   │ │       │
│  │  │  └───────────┘   │ │       │
│  │  │                  │ │       │
│  │  │  ┌───────────┐   │ │       │
│  │  │  │ElastiCache│   │ │       │
│  │  │  │   Redis   │   │ │       │
│  │  │  └───────────┘   │ │       │
│  │  │                  │ │       │
│  │  └──────────────────┘ │       │
│  │                       │       │
│  └───────────────────────┘       │
│                                  │
│  ┌─── Additional Services ───┐  │
│  │                            │  │
│  │  - CloudWatch (Monitoring) │  │
│  │  - S3 (Storage)            │  │
│  │  - Route53 (DNS)           │  │
│  │  - CloudFront (CDN)        │  │
│  │  - WAF (Security)          │  │
│  │                            │  │
│  └────────────────────────────┘  │
│                                  │
└──────────────────────────────────┘
````

---

## Scalability Patterns

### Horizontal Scaling
````markdown
## Strategy
- Add more instances of services
- Use load balancers for distribution
- Design stateless services
- Use distributed caching

## Implementation
- Container orchestration (Kubernetes)
- Auto-scaling groups
- Service mesh for traffic management
- Consistent hashing for cache distribution

## Considerations
- Session management (stateless or distributed sessions)
- Database connection pooling
- File storage (use object storage, not local filesystem)
- Configuration management (centralized)
````

### Vertical Scaling
````markdown
## Strategy
- Increase resources (CPU, RAM) of existing instances
- Optimize code and queries
- Use more powerful instance types

## When to Use
- Monolithic applications
- Database servers (before sharding)
- Memory-intensive operations
- CPU-intensive workloads

## Limitations
- Hardware limits
- Cost increases exponentially
- Single point of failure
- Requires downtime for upgrades
````

### Database Scaling Patterns

#### Read Replicas
````
┌──────────┐
│  Master  │ (Writes)
│    DB    │
└────┬─────┘
     │ Replication
     ├────────────┐
     │            │
     v            v
┌─────────┐  ┌─────────┐
│ Replica │  │ Replica │ (Reads)
│   DB    │  │   DB    │
└─────────┘  └─────────┘
````

#### Sharding
````
User ID Hash Function
│
├─ Shard 0 (Users 0-999)
│  └─ PostgreSQL Instance 1
│
├─ Shard 1 (Users 1000-1999)
│  └─ PostgreSQL Instance 2
│
└─ Shard 2 (Users 2000-2999)
   └─ PostgreSQL Instance 3
````

### Caching Strategy
````markdown
## Cache Layers

### L1: Browser Cache
- Static assets (images, CSS, JS)
- TTL: 1 year for versioned assets

### L2: CDN Cache
- Edge locations
- Static content and API responses
- TTL: Hours to days

### L3: Application Cache (Redis)
- Session data
- Frequently accessed data
- Computed results
- TTL: Minutes to hours

### L4: Database Query Cache
- Query results
- Computed aggregations
- TTL: Seconds to minutes

## Cache Invalidation Strategies
- Time-based (TTL)
- Event-based (invalidate on update)
- Version-based (cache key includes version)
- Cache-aside pattern
- Write-through pattern
- Write-behind pattern
````

---

## Security Architecture

### Defense in Depth
````
┌─────────────────────────────────────────┐
│           External Layer                │
│  - DDoS Protection (CloudFlare)         │
│  - WAF (Web Application Firewall)       │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│           Network Layer                 │
│  - VPC with private/public subnets      │
│  - Security Groups                      │
│  - Network ACLs                         │
│  - TLS/SSL termination                  │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│         Application Layer               │
│  - API Gateway (Authentication)         │
│  - Rate Limiting                        │
│  - Input Validation                     │
│  - CORS policies                        │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│          Service Layer                  │
│  - Service-to-service auth (mTLS)       │
│  - Authorization (RBAC/ABAC)            │
│  - Audit Logging                        │
│  - Secrets Management                   │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│           Data Layer                    │
│  - Encryption at rest                   │
│  - Encryption in transit                │
│  - Database access control              │
│  - Backup encryption                    │
└─────────────────────────────────────────┘
````

### Authentication & Authorization
````markdown
## Authentication Flow (OAuth 2.0 + JWT)

1. User logs in with credentials
2. Auth service validates credentials
3. Auth service issues JWT access token + refresh token
4. Client includes JWT in API requests (Authorization: Bearer <token>)
5. API Gateway validates JWT signature
6. Services trust validated requests from gateway

## Authorization (RBAC)

Roles:
- Admin: Full access
- Manager: Read/write to assigned resources
- User: Read/write own resources
- Guest: Read-only public resources

Permissions Matrix:
| Resource | Admin | Manager | User | Guest |
|----------|-------|---------|------|-------|
| Users    | CRUD  | RU      | R    | -     |
| Orders   | CRUD