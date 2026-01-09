---
name: sql-schema-builder
description: Design SQL data models and database schemas with proper structure and relationships. Define tables, columns, data types, primary keys, foreign keys, indexes, and constraints. Apply normalization principles and clear naming conventions. Model entities to support efficient queries and data integrity. Plan schema evolution with safe migrations. Use when designing databases, creating tables, defining relationships, optimizing queries, or planning schema changes. Ensures consistent, performant, and production-ready database schemas.
---

# SQL Model Schema Builder

Design robust, normalized SQL database schemas with proper relationships, constraints, and performance optimization.

## Core Principles

**Normalization First**: Design schemas in normalized form (3NF minimum), then denormalize strategically for performance only when needed.

**Explicit Constraints**: Use database-level constraints (NOT NULL, UNIQUE, CHECK, FOREIGN KEY) to enforce data integrity, not just application code.

**Naming Consistency**: Follow clear naming conventions across all database objects. Names should be self-documenting.

**Index Strategically**: Index columns used in WHERE, JOIN, and ORDER BY clauses. Balance query performance with write overhead.

**Plan for Change**: Design schemas that can evolve. Use migrations for all changes. Never modify production schemas manually.

**Data Types Matter**: Choose appropriate data types. They affect storage, performance, and data integrity.

## Table Design

### Basic Table Structure

```sql
-- Example: Users table
CREATE TABLE users (
    -- Primary key
    id BIGSERIAL PRIMARY KEY,
    
    -- Unique identifiers
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    
    -- Required fields
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    
    -- Hashed password (never store plain text)
    password_hash VARCHAR(255) NOT NULL,
    
    -- Optional fields
    phone VARCHAR(20),
    avatar_url TEXT,
    bio TEXT,
    
    -- Enums or constrained values
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    
    -- Metadata
    email_verified_at TIMESTAMP,
    last_login_at TIMESTAMP,
    
    -- Audit fields (always include these)
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,  -- Soft delete support
    
    -- Constraints
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT users_status_check CHECK (status IN ('active', 'inactive', 'suspended', 'deleted')),
    CONSTRAINT users_role_check CHECK (role IN ('user', 'admin', 'moderator'))
);

-- Indexes for common queries
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_username ON users(username) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_status ON users(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_created_at ON users(created_at DESC);
CREATE INDEX idx_users_deleted_at ON users(deleted_at) WHERE deleted_at IS NOT NULL;

-- Add comment for documentation
COMMENT ON TABLE users IS 'Stores user account information and authentication credentials';
COMMENT ON COLUMN users.password_hash IS 'BCrypt hashed password - never store plain text passwords';
COMMENT ON COLUMN users.deleted_at IS 'Soft delete timestamp - NULL means not deleted';
```

### Naming Conventions

**Tables**: Plural nouns, lowercase with underscores
- ✅ `users`, `products`, `order_items`, `user_preferences`
- ❌ `User`, `tblProducts`, `OrderItem`

**Columns**: Lowercase with underscores, descriptive
- ✅ `first_name`, `created_at`, `is_active`, `total_amount`
- ❌ `FirstName`, `createdAt`, `active`, `amt`

**Primary Keys**: Use `id` as the standard name
- ✅ `id BIGSERIAL PRIMARY KEY`
- ❌ `user_id`, `pk_users`, `userId`

**Foreign Keys**: Use `{referenced_table}_id` format
- ✅ `user_id`, `product_id`, `category_id`
- ❌ `userId`, `prod_id`, `cat`

**Indexes**: Prefix with `idx_`, include table and columns
- ✅ `idx_users_email`, `idx_orders_user_id_created_at`
- ❌ `index1`, `email_idx`, `users_idx`

**Constraints**: Prefix with table name and type
- ✅ `users_email_check`, `orders_total_check`, `fk_orders_user_id`
- ❌ `chk1`, `email_constraint`, `FK_Orders_Users`

**Boolean Columns**: Prefix with `is_`, `has_`, `can_`
- ✅ `is_active`, `has_avatar`, `can_post`
- ❌ `active`, `avatar`, `posting`

## Data Types

### Choosing the Right Type

**Integers**:
```sql
-- Use appropriate size based on expected range
SMALLINT      -- -32,768 to 32,767 (2 bytes)
INTEGER       -- -2 billion to 2 billion (4 bytes)
BIGINT        -- -9 quintillion to 9 quintillion (8 bytes)

-- Auto-incrementing primary keys
SERIAL        -- Auto-incrementing INTEGER
BIGSERIAL     -- Auto-incrementing BIGINT (recommended for PKs)

-- Examples
age SMALLINT CHECK (age >= 0 AND age <= 150)
quantity INTEGER NOT NULL DEFAULT 0
user_id BIGINT NOT NULL REFERENCES users(id)
```

**Decimals and Money**:
```sql
-- Use NUMERIC for exact precision (money, percentages)
price NUMERIC(10, 2)  -- 10 total digits, 2 after decimal (e.g., 12345678.90)
tax_rate NUMERIC(5, 4)  -- e.g., 0.0825 (8.25%)
balance NUMERIC(15, 2)  -- For account balances

-- NEVER use FLOAT or REAL for money (rounding errors)
-- ❌ price FLOAT
-- ✅ price NUMERIC(10, 2)
```

**Strings**:
```sql
-- Fixed length (padded with spaces)
country_code CHAR(2)  -- e.g., 'US', 'UK'
postal_code CHAR(5)   -- For fixed-length US zip codes

-- Variable length (most common)
email VARCHAR(255)     -- Standard email length
username VARCHAR(50)   -- Short user-facing strings
title VARCHAR(200)     -- Article/product titles
description TEXT       -- Unlimited length for long content

-- Guidelines:
-- - Use VARCHAR with limit for validated fields
-- - Use TEXT for unlimited user-generated content
-- - NEVER use VARCHAR without a length limit
```

**Dates and Times**:
```sql
-- Date only (no time)
birth_date DATE

-- Time only (no date)
opening_time TIME

-- Timestamp without timezone (avoid in most cases)
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP

-- Timestamp with timezone (RECOMMENDED - always use for events)
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
event_start_at TIMESTAMPTZ NOT NULL

-- Intervals
rental_duration INTERVAL  -- e.g., '7 days', '2 hours 30 minutes'

-- Always use TIMESTAMPTZ for timestamps to avoid timezone issues
```

**Boolean**:
```sql
is_active BOOLEAN NOT NULL DEFAULT TRUE
is_verified BOOLEAN NOT NULL DEFAULT FALSE
can_edit BOOLEAN

-- Don't use VARCHAR or INTEGER for true/false values
```

**JSON**:
```sql
-- JSON data (stored as text, parsed on retrieval)
metadata JSON

-- JSONB (binary JSON, supports indexing, recommended)
preferences JSONB DEFAULT '{}'::JSONB
settings JSONB NOT NULL DEFAULT '{}'::JSONB

-- Create indexes on JSONB fields
CREATE INDEX idx_preferences_language ON users((preferences->>'language'));
CREATE INDEX idx_settings_gin ON users USING GIN (settings);
```

**Arrays**:
```sql
-- PostgreSQL arrays (use sparingly, prefer normalized tables)
tags TEXT[]
allowed_ips INET[]

-- Better approach: separate table for many-to-many relationships
-- Use arrays only for small, fixed lists
```

**Enums**:
```sql
-- PostgreSQL custom types
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    status order_status NOT NULL DEFAULT 'pending'
);

-- Alternatively, use CHECK constraints (easier to modify)
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    CONSTRAINT orders_status_check CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled'))
);
```

## Relationships

### One-to-Many

**Most common relationship type**. One record in table A relates to many records in table B.

```sql
-- Example: One user has many posts

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_posts_user_id 
        FOREIGN KEY (user_id) 
        REFERENCES users(id)
        ON DELETE CASCADE  -- Delete posts when user is deleted
        ON UPDATE CASCADE  -- Update posts if user.id changes
);

-- Index foreign key for join performance
CREATE INDEX idx_posts_user_id ON posts(user_id);

-- Query: Get all posts by a user
SELECT p.* 
FROM posts p
WHERE p.user_id = 123
ORDER BY p.created_at DESC;

-- Query: Get users with their post count
SELECT u.*, COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON p.user_id = u.id
GROUP BY u.id;
```

### Many-to-Many

**Requires junction table**. Many records in table A relate to many records in table B.

```sql
-- Example: Users can enroll in many courses, courses have many students

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE courses (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE
);

-- Junction table
CREATE TABLE enrollments (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    course_id BIGINT NOT NULL,
    
    -- Additional data about the relationship
    enrolled_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    grade NUMERIC(3, 2),  -- e.g., 3.75 GPA
    
    -- Foreign keys
    CONSTRAINT fk_enrollments_user_id 
        FOREIGN KEY (user_id) 
        REFERENCES users(id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_enrollments_course_id 
        FOREIGN KEY (course_id) 
        REFERENCES courses(id)
        ON DELETE CASCADE,
    
    -- Ensure user can't enroll in same course twice
    CONSTRAINT enrollments_user_course_unique 
        UNIQUE (user_id, course_id)
);

-- Composite index for common queries
CREATE INDEX idx_enrollments_user_id ON enrollments(user_id);
CREATE INDEX idx_enrollments_course_id ON enrollments(course_id);

-- Query: Get all courses for a user
SELECT c.*, e.enrolled_at, e.grade
FROM courses c
INNER JOIN enrollments e ON e.course_id = c.id
WHERE e.user_id = 123;

-- Query: Get all students in a course
SELECT u.*, e.enrolled_at
FROM users u
INNER JOIN enrollments e ON e.user_id = u.id
WHERE e.course_id = 456;
```

### One-to-One

**Rare relationship**. One record in table A relates to exactly one record in table B. Often used for table splitting.

```sql
-- Example: User has one profile with extended information

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Separate table for infrequently accessed data
CREATE TABLE user_profiles (
    user_id BIGINT PRIMARY KEY,  -- PK and FK combined
    bio TEXT,
    website VARCHAR(255),
    location VARCHAR(100),
    birth_date DATE,
    
    -- Foreign key with one-to-one constraint
    CONSTRAINT fk_user_profiles_user_id 
        FOREIGN KEY (user_id) 
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- Query: Get user with profile
SELECT u.*, p.*
FROM users u
LEFT JOIN user_profiles p ON p.user_id = u.id
WHERE u.id = 123;
```

### Self-Referencing

**Table references itself**. Common for hierarchical data.

```sql
-- Example: Organizational hierarchy

CREATE TABLE employees (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    manager_id BIGINT,  -- References another employee
    
    CONSTRAINT fk_employees_manager_id 
        FOREIGN KEY (manager_id) 
        REFERENCES employees(id)
        ON DELETE SET NULL  -- If manager is deleted, set to NULL
);

CREATE INDEX idx_employees_manager_id ON employees(manager_id);

-- Query: Get all direct reports for a manager
SELECT e.*
FROM employees e
WHERE e.manager_id = 123;

-- Recursive query: Get entire reporting chain
WITH RECURSIVE employee_hierarchy AS (
    -- Anchor: Start with specific employee
    SELECT id, name, manager_id, 1 as level
    FROM employees
    WHERE id = 123
    
    UNION ALL
    
    -- Recursive: Join to get reports
    SELECT e.id, e.name, e.manager_id, eh.level + 1
    FROM employees e
    INNER JOIN employee_hierarchy eh ON e.manager_id = eh.id
)
SELECT * FROM employee_hierarchy;
```

## Normalization

### First Normal Form (1NF)

**Rule**: Each column contains atomic (indivisible) values. No repeating groups.

**❌ Violation**:
```sql
CREATE TABLE customers (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100),
    phone_numbers VARCHAR(255)  -- '555-1234, 555-5678, 555-9012'
);
```

**✅ Normalized**:
```sql
CREATE TABLE customers (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE customer_phones (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    phone_type VARCHAR(20) NOT NULL,  -- 'mobile', 'home', 'work'
    
    CONSTRAINT fk_customer_phones_customer_id 
        FOREIGN KEY (customer_id) 
        REFERENCES customers(id)
        ON DELETE CASCADE
);
```

### Second Normal Form (2NF)

**Rule**: Must be in 1NF, and all non-key columns must depend on the entire primary key (no partial dependencies).

**❌ Violation**:
```sql
-- Composite primary key with partial dependency
CREATE TABLE order_items (
    order_id BIGINT,
    product_id BIGINT,
    product_name VARCHAR(200),  -- Depends only on product_id, not full key
    product_price NUMERIC(10, 2),  -- Depends only on product_id
    quantity INTEGER NOT NULL,
    
    PRIMARY KEY (order_id, product_id)
);
```

**✅ Normalized**:
```sql
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price NUMERIC(10, 2) NOT NULL
);

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,  -- Capture price at time of order
    
    CONSTRAINT fk_order_items_order_id 
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_order_items_product_id 
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);
```

### Third Normal Form (3NF)

**Rule**: Must be in 2NF, and no transitive dependencies (non-key columns depend only on primary key, not other non-key columns).

**❌ Violation**:
```sql
CREATE TABLE employees (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_name VARCHAR(100),  -- Depends on department_id
    department_location VARCHAR(100),  -- Depends on department_id (transitive)
    department_id BIGINT NOT NULL
);
```

**✅ Normalized**:
```sql
CREATE TABLE departments (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id BIGINT NOT NULL,
    
    CONSTRAINT fk_employees_department_id 
        FOREIGN KEY (department_id) 
        REFERENCES departments(id)
        ON DELETE RESTRICT
);
```

### Strategic Denormalization

**When to denormalize** (after measuring performance issues):

**1. Frequently Computed Aggregates**:
```sql
-- Store computed values to avoid expensive aggregations
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    post_count INTEGER NOT NULL DEFAULT 0,  -- Denormalized
    follower_count INTEGER NOT NULL DEFAULT 0  -- Denormalized
);

-- Update with triggers
CREATE FUNCTION update_user_post_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE users SET post_count = post_count + 1 WHERE id = NEW.user_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE users SET post_count = post_count - 1 WHERE id = OLD.user_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_post_count
AFTER INSERT OR DELETE ON posts
FOR EACH ROW EXECUTE FUNCTION update_user_post_count();
```

**2. Expensive Joins**:
```sql
-- Store commonly accessed related data
CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    product_name VARCHAR(200) NOT NULL,  -- Denormalized from products
    unit_price NUMERIC(10, 2) NOT NULL,  -- Capture at order time
    quantity INTEGER NOT NULL
);

-- This avoids JOIN with products table for order history queries
```

## Constraints

### Primary Keys

**Every table must have a primary key**.

```sql
-- Auto-incrementing surrogate key (recommended)
id BIGSERIAL PRIMARY KEY

-- Natural key (use when appropriate)
email VARCHAR(255) PRIMARY KEY
country_code CHAR(2) PRIMARY KEY

-- Composite primary key
PRIMARY KEY (user_id, course_id)

-- Named constraint
CONSTRAINT pk_users PRIMARY KEY (id)
```

### Foreign Keys

**Enforce referential integrity at database level**.

```sql
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    
    -- Basic foreign key
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- With ON DELETE and ON UPDATE actions
CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    
    CONSTRAINT fk_comments_post_id 
        FOREIGN KEY (post_id) 
        REFERENCES posts(id)
        ON DELETE CASCADE      -- Delete comments when post is deleted
        ON UPDATE CASCADE,     -- Update if post.id changes
    
    CONSTRAINT fk_comments_user_id 
        FOREIGN KEY (user_id) 
        REFERENCES users(id)
        ON DELETE SET NULL     -- Set to NULL if user is deleted
        ON UPDATE CASCADE
);

-- ON DELETE options:
-- CASCADE: Delete dependent rows
-- SET NULL: Set foreign key to NULL (requires nullable column)
-- SET DEFAULT: Set foreign key to default value
-- RESTRICT: Prevent deletion if dependent rows exist (default)
-- NO ACTION: Similar to RESTRICT but can be deferred
```

### Unique Constraints

**Ensure column or combination of columns is unique**.

```sql
-- Single column unique
email VARCHAR(255) NOT NULL UNIQUE

-- Named constraint
username VARCHAR(50) NOT NULL,
CONSTRAINT users_username_unique UNIQUE (username)

-- Composite unique (combination must be unique)
CONSTRAINT enrollments_user_course_unique UNIQUE (user_id, course_id)

-- Partial unique index (PostgreSQL)
CREATE UNIQUE INDEX idx_users_email_active 
    ON users(email) 
    WHERE deleted_at IS NULL;  -- Email only unique for active users
```

### Check Constraints

**Validate data values at database level**.

```sql
-- Simple range check
age INTEGER CHECK (age >= 0 AND age <= 150)

-- Named constraint
price NUMERIC(10, 2),
CONSTRAINT products_price_check CHECK (price >= 0)

-- Multiple conditions
quantity INTEGER,
status VARCHAR(20),
CONSTRAINT orders_quantity_status_check 
    CHECK (
        (status = 'pending' AND quantity > 0) OR
        (status IN ('cancelled', 'completed'))
    )

-- Enum-like constraint
status VARCHAR(20) NOT NULL DEFAULT 'active',
CONSTRAINT users_status_check 
    CHECK (status IN ('active', 'inactive', 'suspended', 'deleted'))

-- Date validation
start_date DATE,
end_date DATE,
CONSTRAINT events_date_check CHECK (end_date >= start_date)

-- Email format (PostgreSQL regex)
email VARCHAR(255),
CONSTRAINT users_email_check 
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
```

### NOT NULL Constraints

**Prevent NULL values in critical columns**.

```sql
-- Always NOT NULL
email VARCHAR(255) NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP

-- NOT NULL with DEFAULT
status VARCHAR(20) NOT NULL DEFAULT 'active'
is_verified BOOLEAN NOT NULL DEFAULT FALSE

-- Optional fields (nullable)
phone VARCHAR(20)  -- NULL allowed
middle_name VARCHAR(50)
```

## Indexes

### When to Create Indexes

**Index columns used in**:
- Primary keys (automatic)
- Foreign keys (CREATE INDEX manually)
- WHERE clause filters
- JOIN conditions
- ORDER BY clauses
- UNIQUE constraints (automatic)

**Don't index**:
- Small tables (< 1000 rows)
- Columns with low cardinality (few distinct values)
- Columns that are frequently updated
- Wide columns (TEXT, JSONB) without specific needs

### Index Types

**B-tree (default, most common)**:
```sql
-- Simple index
CREATE INDEX idx_users_email ON users(email);

-- Composite index (order matters!)
CREATE INDEX idx_posts_user_created ON posts(user_id, created_at DESC);

-- Use composite index for queries filtering on both columns
-- Index on (user_id, created_at) can be used for:
-- - WHERE user_id = 123
-- - WHERE user_id = 123 AND created_at > '2024-01-01'
-- - WHERE user_id = 123 ORDER BY created_at DESC
-- But NOT for:
-- - WHERE created_at > '2024-01-01' (doesn't start with user_id)
```

**Partial Index** (PostgreSQL):
```sql
-- Index only subset of rows
CREATE INDEX idx_users_active ON users(email) 
    WHERE deleted_at IS NULL;

CREATE INDEX idx_orders_pending ON orders(created_at) 
    WHERE status = 'pending';

-- Smaller, faster, more efficient than full index
```

**Unique Index**:
```sql
-- Enforce uniqueness
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- Partial unique
CREATE UNIQUE INDEX idx_users_username_active 
    ON users(username) 
    WHERE deleted_at IS NULL;
```

**GIN Index** (for full-text search, JSONB, arrays):
```sql
-- JSONB indexing
CREATE INDEX idx_users_preferences ON users USING GIN (preferences);

-- Query: WHERE preferences @> '{"theme": "dark"}'

-- Full-text search
CREATE INDEX idx_posts_content_search ON posts 
    USING GIN (to_tsvector('english', content));

-- Query: WHERE to_tsvector('english', content) @@ to_tsquery('search & terms')
```

**Expression Index**:
```sql
-- Index on computed value
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- Query: WHERE LOWER(email) = 'user@example.com'

CREATE INDEX idx_users_full_name ON users((first_name || ' ' || last_name));

-- Query: WHERE first_name || ' ' || last_name = 'John Doe'
```

### Index Maintenance

```sql
-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- Drop unused indexes (idx_scan = 0)
DROP INDEX idx_unused_index;

-- Rebuild index (PostgreSQL)
REINDEX INDEX idx_users_email;
REINDEX TABLE users;
```

## Schema Evolution & Migrations

### Migration Principles

**1. Never modify production schema directly**
**2. All changes through version-controlled migrations**
**3. Test migrations in staging first**
**4. Always provide rollback (down migration)**
**5. Make migrations idempotent when possible**

### Adding Columns

```sql
-- Safe: Add nullable column
ALTER TABLE users 
ADD COLUMN phone VARCHAR(20);

-- Safe: Add column with default
ALTER TABLE users 
ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT FALSE;

-- Risky: Add NOT NULL without default
-- ❌ Don't do this on large tables
ALTER TABLE users 
ADD COLUMN middle_name VARCHAR(50) NOT NULL;

-- ✅ Better: Add as nullable, backfill, then add constraint
ALTER TABLE users ADD COLUMN middle_name VARCHAR(50);
UPDATE users SET middle_name = '' WHERE middle_name IS NULL;
ALTER TABLE users ALTER COLUMN middle_name SET NOT NULL;
```

### Removing Columns

```sql
-- Migration up: Drop column
ALTER TABLE users DROP COLUMN middle_name;

-- Migration down: Add column back
ALTER TABLE users ADD COLUMN middle_name VARCHAR(50);

-- Safe approach for large tables:
-- 1. Deploy code that ignores column
-- 2. Wait for all servers to update
-- 3. Drop column in separate migration
```

### Renaming

```sql
-- Rename table
ALTER TABLE old_name RENAME TO new_name;

-- Rename column
ALTER TABLE users RENAME COLUMN old_name TO new_name;

-- Warning: Breaks queries using old name
-- Use views as compatibility layer if needed
CREATE VIEW old_name AS SELECT * FROM new_name;
```

### Modifying Columns

```sql
-- Change data type (safe if compatible)
ALTER TABLE users 
ALTER COLUMN age TYPE INTEGER;

-- Change nullable constraint
ALTER TABLE users 
ALTER COLUMN email SET NOT NULL;

ALTER TABLE users 
ALTER COLUMN phone DROP NOT NULL;

-- Change default value
ALTER TABLE users 
ALTER COLUMN status SET DEFAULT 'active';

ALTER TABLE users 
ALTER COLUMN status DROP DEFAULT;

-- Increase VARCHAR length (safe)
ALTER TABLE users 
ALTER COLUMN username TYPE VARCHAR(100);

-- Decrease VARCHAR length (risky - may fail if data exceeds new length)
-- Better: Check data first
SELECT MAX(LENGTH(username)) FROM users;  -- Check current max length
ALTER TABLE users 
ALTER COLUMN username TYPE VARCHAR(30);
```

### Adding Constraints

```sql
-- Add foreign key
ALTER TABLE posts 
ADD CONSTRAINT fk_posts_user_id 
    FOREIGN KEY (user_id) 
    REFERENCES users(id)
    ON DELETE CASCADE;

-- Add check constraint
ALTER TABLE products 
ADD CONSTRAINT products_price_check 
    CHECK (price >= 0);

-- Add unique constraint
ALTER TABLE users 
ADD CONSTRAINT users_email_unique 
    UNIQUE (email);

-- For large tables: Use NOT VALID then VALIDATE
-- (PostgreSQL - doesn't lock table for existing rows)
ALTER TABLE posts 
ADD CONSTRAINT fk_posts_user_id 
    FOREIGN KEY (user_id) 
    REFERENCES users(id)
    NOT VALID;

-- Validate in separate transaction
ALTER TABLE posts 
VALIDATE CONSTRAINT fk_posts_user_id;
```

### Migration File Template

```sql
-- migrations/20240108_001_create_users_table.sql

-- ============================================
-- Migration: Create users table
-- Description: Initial users table with authentication
-- Author: Your Name
-- Date: 2024-01-08
-- ============================================

-- ==== UP ====

BEGIN;

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT users_status_check 
        CHECK (status IN ('active', 'inactive', 'suspended'))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);

COMMENT ON TABLE users IS 'User accounts and authentication';

COMMIT;

-- ==== DOWN ====

BEGIN;

DROP TABLE IF EXISTS users CASCADE;

COMMIT;
```

## Performance Optimization

### Query Patterns

**1. Use EXPLAIN ANALYZE**:
```sql
EXPLAIN ANALYZE
SELECT u.*, COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON p.user_id = u.id
WHERE u.status = 'active'
GROUP BY u.id
ORDER BY post_count DESC
LIMIT 20;

-- Look for:
-- - Seq Scan on large tables (add index)
-- - High cost operations
-- - Nested loops on large datasets
```

**2. Avoid N+1 Queries**:
```sql
-- ❌ Bad: N+1 queries (1 for users + N for each user's posts)
SELECT * FROM users;
-- Then for each user:
SELECT * FROM posts WHERE user_id = ?;

-- ✅ Good: Single query with JOIN
SELECT 
    u.*,
    json_agg(json_build_object(
        'id', p.id,
        'title', p.title,
        'created_at', p.created_at
    )) as posts
FROM users u
LEFT JOIN posts p ON p.user_id = u.id
GROUP BY u.id;
```

**3. Pagination**:
```sql
-- ❌ Bad: OFFSET becomes slow on large offsets
SELECT * FROM posts
ORDER BY created_at DESC
LIMIT 20 OFFSET 10000;  -- Scans and discards 10,000 rows

-- ✅ Good: Cursor-based pagination
SELECT * FROM posts
WHERE created_at < '2024-01-01 12:00:00'  -- Last seen timestamp
ORDER BY created_at DESC
LIMIT 20;

-- Or with ID for uniqueness
WHERE (created_at, id) < ('2024-01-01 12:00:00', 12345)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

**4. Covering Indexes**:
```sql
-- Include commonly selected columns in index
CREATE INDEX idx_posts_user_covering 
    ON posts(user_id, created_at) 
    INCLUDE (title, status);

-- Query can be satisfied entirely from index
SELECT title, status, created_at
FROM posts
WHERE user_id = 123
ORDER BY created_at DESC;
```

### Table Design for Performance

**1. Partitioning** (for very large tables):
```sql
-- Partition by date range
CREATE TABLE events (
    id BIGSERIAL,
    user_id BIGINT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    data JSONB
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE events_2024_01 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE events_2024_02 PARTITION OF events
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Queries automatically use relevant partition
SELECT * FROM events 
WHERE created_at >= '2024-01-15' AND created_at < '2024-01-20';
```

**2. Materialized Views** (for expensive queries):
```sql
-- Create materialized view
CREATE MATERIALIZED VIEW user_stats AS
SELECT 
    u.id,
    u.username,
    COUNT(DISTINCT p.id) as post_count,
    COUNT(DISTINCT c.id) as comment_count,
    MAX(p.created_at) as last_post_at
FROM users u
LEFT JOIN posts p ON p.user_id = u.id
LEFT JOIN comments c ON c.user_id = u.id
GROUP BY u.id;

-- Create index on materialized view
CREATE INDEX idx_user_stats_post_count ON user_stats(post_count DESC);

-- Refresh periodically
REFRESH MATERIALIZED VIEW CONCURRENTLY user_stats;
```

## Common Patterns

### Soft Deletes

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    deleted_at TIMESTAMPTZ,  -- NULL = not deleted
    
    -- Unique only for non-deleted
    CONSTRAINT users_email_unique UNIQUE (email, deleted_at)
);

CREATE INDEX idx_users_deleted_at 
    ON users(deleted_at) 
    WHERE deleted_at IS NOT NULL;

-- Query active users
SELECT * FROM users WHERE deleted_at IS NULL;

-- Soft delete
UPDATE users SET deleted_at = CURRENT_TIMESTAMP WHERE id = 123;

-- Restore
UPDATE users SET deleted_at = NULL WHERE id = 123;

-- Hard delete (permanently remove)
DELETE FROM users WHERE deleted_at < CURRENT_TIMESTAMP - INTERVAL '90 days';
```

### Audit Trail

```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id BIGINT NOT NULL,
    action VARCHAR(20) NOT NULL,  -- 'INSERT', 'UPDATE', 'DELETE'
    old_values JSONB,
    new_values JSONB,
    changed_by BIGINT,  -- user_id
    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT audit_logs_action_check 
        CHECK (action IN ('INSERT', 'UPDATE', 'DELETE'))
);

CREATE INDEX idx_audit_logs_table_record 
    ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_logs_changed_at 
    ON audit_logs(changed_at DESC);

-- Trigger function for automatic auditing
CREATE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (table_name, record_id, action, new_values)
        VALUES (TG_TABLE_NAME, NEW.id, 'INSERT', row_to_json(NEW));
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_values, new_values)
        VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE', row_to_json(OLD), row_to_json(NEW));
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_values)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', row_to_json(OLD));
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables
CREATE TRIGGER users_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
```

### Optimistic Locking (Version Column)

```sql
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,  -- Version number
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Update with version check
UPDATE products
SET 
    price = 29.99,
    version = version + 1,
    updated_at = CURRENT_TIMESTAMP
WHERE id = 123 
  AND version = 5;  -- Only update if version matches

-- If 0 rows affected, someone else updated it (conflict)
```

### Hierarchical Data (Nested Sets)

```sql
-- Store tree structure efficiently
CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    lft INTEGER NOT NULL,
    rgt INTEGER NOT NULL,
    
    CONSTRAINT categories_lft_rgt_check CHECK (lft < rgt)
);

CREATE INDEX idx_categories_lft ON categories(lft);
CREATE INDEX idx_categories_rgt ON categories(rgt);

-- Query: Get all descendants of node
SELECT * FROM categories
WHERE lft > 10 AND rgt < 20
ORDER BY lft;

-- Query: Get path to node
SELECT * FROM categories c1
WHERE c1.lft <= 15 AND c1.rgt >= 15
ORDER BY c1.lft;
```

## Production Checklist

Before deploying schema:

- [ ] **Primary Keys**: Every table has a primary key
- [ ] **Foreign Keys**: All relationships have foreign key constraints
- [ ] **Indexes**: Foreign keys, frequently queried columns indexed
- [ ] **NOT NULL**: Required columns marked NOT NULL
- [ ] **Defaults**: Sensible defaults for optional columns
- [ ] **Check Constraints**: Data validation at database level
- [ ] **Audit Fields**: created_at, updated_at on all tables
- [ ] **Soft Deletes**: deleted_at column if needed
- [ ] **Naming**: Consistent, clear naming conventions
- [ ] **Normalization**: At least 3NF (unless intentionally denormalized)
- [ ] **Comments**: Tables and complex columns documented
- [ ] **Migrations**: All changes version-controlled
- [ ] **Rollback**: Down migrations prepared
- [ ] **Performance**: EXPLAIN ANALYZE on key queries
- [ ] **Backups**: Backup strategy in place

## Quick Reference

### Data Type Cheatsheet

| Use Case | Type | Example |
|----------|------|---------|
| Primary Key | BIGSERIAL | `id BIGSERIAL PRIMARY KEY` |
| Foreign Key | BIGINT | `user_id BIGINT NOT NULL` |
| Money | NUMERIC | `price NUMERIC(10, 2)` |
| Email | VARCHAR(255) | `email VARCHAR(255) NOT NULL` |
| Short Text | VARCHAR(50-200) | `username VARCHAR(50)` |
| Long Text | TEXT | `description TEXT` |
| Boolean | BOOLEAN | `is_active BOOLEAN NOT NULL DEFAULT TRUE` |
| Timestamp | TIMESTAMPTZ | `created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP` |
| JSON | JSONB | `metadata JSONB DEFAULT '{}'` |

### Foreign Key Actions

| Action | Effect |
|--------|--------|
| CASCADE | Delete/update dependent rows |
| SET NULL | Set foreign key to NULL |
| SET DEFAULT | Set foreign key to default value |
| RESTRICT | Prevent if dependent rows exist |
| NO ACTION | Similar to RESTRICT (can be deferred) |

### Index Types

| Type | Use Case |
|------|----------|
| B-tree | Most queries (default) |
| GIN | JSONB, arrays, full-text search |
| GIST | Geospatial, ranges |
| HASH | Exact equality only (rarely used) |

Design schemas that are **normalized, constrained, indexed, and maintainable**.
