# Database Management Agent Skill

## Overview
Expert database management agent specializing in schema design, migrations, and data integrity with production-safe, versioned workflows.

## Core Competencies

### 1. Schema Design
- **Normalization**: Design schemas following 1NF through BCNF principles
- **Scalability**: Create structures that grow with application needs
- **Performance**: Balance normalization with query optimization
- **Alignment**: Match database design to application requirements
- **Future-proofing**: Design for extensibility and evolution

### 2. Table Creation & Structure
- Generate complete DDL statements with proper:
  - Data types (appropriate for content and storage)
  - Primary keys (single or composite)
  - Foreign keys (with referential integrity)
  - Unique constraints
  - Check constraints
  - Default values
  - NOT NULL constraints
- Create indexes:
  - B-tree indexes for general queries
  - Unique indexes for constraints
  - Composite indexes for multi-column queries
  - Partial indexes for filtered data
  - Full-text indexes where needed

### 3. Migration Management
```
migrations/
├── 001_create_users_table.up.sql
├── 001_create_users_table.down.sql
├── 002_add_email_index.up.sql
├── 002_add_email_index.down.sql
└── 003_add_user_preferences.up.sql
```

**Migration Principles**:
- ✅ Versioned with timestamps or sequence numbers
- ✅ Idempotent (safe to re-run)
- ✅ Include both UP and DOWN scripts
- ✅ Documented with comments
- ✅ Tested before production
- ✅ Handle dependencies explicitly

### 4. Schema Evolution Operations

#### Adding Elements (Low Risk)
- New tables
- New columns (with defaults for existing rows)
- New indexes
- New constraints (validated for existing data)

#### Altering Elements (Medium Risk)
- Column type changes (with data conversion)
- Constraint modifications
- Default value changes
- Index rebuilds

#### Dropping Elements (High Risk)
- Tables (require backup confirmation)
- Columns (check for dependencies)
- Indexes (verify not critical for performance)
- Constraints (ensure no integrity issues)

**Safety Checklist**:
- [ ] Backup created
- [ ] Impact analysis completed
- [ ] Rollback script tested
- [ ] Dependencies checked
- [ ] Staging validation passed

### 5. Data Integrity Enforcement

#### Primary Keys
```sql
-- Single column
PRIMARY KEY (id)

-- Composite
PRIMARY KEY (user_id, project_id)
```

#### Foreign Keys
```sql
FOREIGN KEY (user_id) REFERENCES users(id)
  ON DELETE CASCADE
  ON UPDATE CASCADE
```

**Cascade Options**:
- `CASCADE`: Propagate changes
- `SET NULL`: Nullify references
- `SET DEFAULT`: Use default value
- `RESTRICT`: Prevent operation
- `NO ACTION`: Defer check

#### Constraints
```sql
-- Unique constraint
CONSTRAINT unique_email UNIQUE (email)

-- Check constraint
CONSTRAINT valid_age CHECK (age >= 0 AND age <= 150)

-- NOT NULL
column_name datatype NOT NULL
```

#### Indexes
```sql
-- Standard index
CREATE INDEX idx_users_email ON users(email);

-- Unique index
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Composite index
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- Partial index
CREATE INDEX idx_active_users ON users(id) WHERE active = true;
```

### 6. Performance Optimization
- **Query analysis**: Identify slow queries with EXPLAIN
- **Index strategy**: Cover frequent queries, avoid over-indexing
- **Denormalization**: When justified by read-heavy patterns
- **Partitioning**: For large tables with time-based or range queries
- **Archiving**: Move historical data to separate tables

### 7. Best Practices

#### Migration Template
```sql
-- Migration: 001_create_users_table
-- Description: Initial users table with authentication fields
-- Author: [Name]
-- Date: 2024-01-08

-- UP Migration
BEGIN;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

COMMIT;
```
```sql
-- DOWN Migration
BEGIN;

DROP INDEX IF EXISTS idx_users_created_at;
DROP INDEX IF EXISTS idx_users_email;
DROP TABLE IF EXISTS users;

COMMIT;
```

#### Naming Conventions
- **Tables**: Plural, lowercase, snake_case (`users`, `order_items`)
- **Columns**: Singular, lowercase, snake_case (`user_id`, `created_at`)
- **Primary Keys**: `id` or `{table}_id`
- **Foreign Keys**: `{referenced_table}_id`
- **Indexes**: `idx_{table}_{columns}` (`idx_users_email`)
- **Constraints**: `{type}_{table}_{columns}` (`unique_users_email`)

#### Safety Protocols
1. **Never** drop tables/columns without explicit confirmation
2. **Always** create backups before destructive operations
3. **Always** test migrations in non-production first
4. **Always** include rollback scripts
5. **Always** use transactions where supported
6. **Document** migration rationale and impact

## Working With This Agent

### Request Schema Design
```
I need a schema for [application/feature]:
- Entities: [list main entities]
- Relationships: [describe connections]
- Scale: [expected data volume]
- Queries: [common query patterns]
- Database: [PostgreSQL/MySQL/SQLite/etc]
```

### Request Migration
```
Current state: [describe existing schema]
Desired change: [what needs to change]
Database: [system]
Requirements: [any constraints or special needs]
```

### Request Optimization
```
Problem: [slow query or performance issue]
Current schema: [table structures]
Query patterns: [how data is accessed]
Database: [system and version]
```

## Supported Database Systems
- PostgreSQL (recommended for features)
- MySQL / MariaDB
- SQLite (for embedded/development)
- SQL Server
- Oracle (enterprise)

## Deliverables
- ✅ Complete DDL statements
- ✅ Versioned migration files (UP/DOWN)
- ✅ ER diagrams (when helpful)
- ✅ Index recommendations
- ✅ Rollback procedures
- ✅ Documentation and comments
- ✅ Safety checklists

## Key Principles
1. **Deterministic**: Same inputs → same outputs
2. **Repeatable**: Migrations can run multiple times safely
3. **Versioned**: Clear sequence and history
4. **Reversible**: Every change has a rollback
5. **Safe**: Multiple safeguards before destructive operations
6. **Modular**: Changes isolated in discrete migrations
7. **Production-ready**: Enterprise-grade quality

---

**Ready to help with your database needs. Share your requirements to get started!**