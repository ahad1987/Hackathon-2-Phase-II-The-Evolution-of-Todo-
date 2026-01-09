---
name: code-reviewer
description: Review code for correctness, clarity, and maintainability. Verify alignment with architecture decisions, ADRs, and intended behavior. Identify logical errors, edge cases, security vulnerabilities, and performance issues. Distinguish blocking issues from recommendations. Propose minimal, concrete fixes with code examples. Avoid stylistic or cosmetic feedback. Use when reviewing pull requests, conducting code audits, ensuring code quality, or validating implementations. Keep reviews concise, actionable, and implementation-focused.
---

# Code Reviewer

Conduct effective code reviews that identify real issues and provide actionable feedback.

## Core Principles

**Functional First**: Does the code work correctly? Are there bugs, edge cases, or logical errors?

**Security Critical**: Security issues are always blocking. SQL injection, XSS, authentication bypass, etc.

**Architecture Alignment**: Does code follow established patterns, ADRs, and project architecture?

**Actionable Feedback**: Provide specific suggestions with code examples, not vague criticisms.

**Blocking vs. Optional**: Clearly distinguish must-fix issues from nice-to-have improvements.

**Respect Author**: Assume competence. Ask questions before assuming mistakes.

**Focus on Impact**: Prioritize issues that affect correctness, security, or maintainability.

## Review Categories

### 1. Correctness (Blocking)

**Logical errors that cause incorrect behavior**.

**❌ Bad Review**:
```
"This code doesn't look right."
```

**✅ Good Review**:
```typescript
// Code being reviewed
function calculateDiscount(price: number, percentage: number): number {
  return price * percentage  // BUG: Missing division by 100
}

// Review comment:
❌ BLOCKING: Incorrect discount calculation

The discount is not being calculated correctly. For a 20% discount, 
this returns 20 * price instead of price * 0.20.

**Fix**:
```typescript
function calculateDiscount(price: number, percentage: number): number {
  return price * (percentage / 100)
}
```

**Test case to add**:
```typescript
expect(calculateDiscount(100, 20)).toBe(20) // Should be 20, not 2000
```
```

**Example - Off-by-one error**:
```typescript
// Code
for (let i = 0; i <= arr.length; i++) {  // BUG: Should be < not <=
  console.log(arr[i])
}

// Review
❌ BLOCKING: Off-by-one error causes array out of bounds

Loop iterates one past array end. When `i === arr.length`, 
`arr[i]` is undefined.

**Fix**: Change `<=` to `<`:
```typescript
for (let i = 0; i < arr.length; i++) {
  console.log(arr[i])
}
```
```

**Example - Race condition**:
```typescript
// Code
async function updateCounter() {
  const current = await getCounter()
  await setCounter(current + 1)  // BUG: Race condition
}

// Review
❌ BLOCKING: Race condition in counter update

If two requests call this simultaneously:
1. Both read current = 5
2. Both write 6
3. Counter should be 7, but is 6 (lost update)

**Fix**: Use atomic operation:
```typescript
async function updateCounter() {
  await db.query('UPDATE counters SET count = count + 1 WHERE id = 1')
}
```

Or use optimistic locking:
```typescript
async function updateCounter() {
  const MAX_RETRIES = 3
  for (let i = 0; i < MAX_RETRIES; i++) {
    const current = await getCounter()
    const success = await setCounterIfUnchanged(current, current + 1)
    if (success) return
  }
  throw new Error('Failed to update counter after retries')
}
```
```

### 2. Security (Always Blocking)

**Vulnerabilities that expose system to attacks**.

**SQL Injection**:
```typescript
// Code
async function getUser(username: string) {
  return db.query(`SELECT * FROM users WHERE username = '${username}'`)  // CRITICAL
}

// Review
🚨 BLOCKING: SQL injection vulnerability

User input is concatenated directly into SQL query. Attacker can inject:
`'; DROP TABLE users; --`

**Fix**: Use parameterized queries:
```typescript
async function getUser(username: string) {
  return db.query('SELECT * FROM users WHERE username = ?', [username])
}
```
```

**XSS Vulnerability**:
```typescript
// Code
function displayMessage(message: string) {
  document.getElementById('output').innerHTML = message  // CRITICAL
}

// Review
🚨 BLOCKING: XSS vulnerability

User input rendered as HTML without sanitization. Attacker can inject:
`<script>steal(document.cookie)</script>`

**Fix**: Use text content or sanitize:
```typescript
// Option 1: Text only
function displayMessage(message: string) {
  document.getElementById('output').textContent = message
}

// Option 2: Sanitize HTML
import DOMPurify from 'dompurify'
function displayMessage(message: string) {
  document.getElementById('output').innerHTML = DOMPurify.sanitize(message)
}
```
```

**Authentication Bypass**:
```typescript
// Code
function requireAdmin(req: Request) {
  if (req.headers['x-user-role'] === 'admin') {  // CRITICAL
    return true
  }
  throw new Error('Unauthorized')
}

// Review
🚨 BLOCKING: Authentication bypass via header manipulation

Client can set `x-user-role` header to 'admin' and bypass auth.
Never trust client-provided role information.

**Fix**: Get role from server-side session/token:
```typescript
function requireAdmin(req: Request) {
  const user = getUserFromSession(req)  // Server-side verification
  if (!user || user.role !== 'admin') {
    throw new Error('Unauthorized')
  }
  return true
}
```
```

**Exposed Secrets**:
```typescript
// Code
const apiKey = 'sk_live_abc123...'  // CRITICAL

// Review
🚨 BLOCKING: Hard-coded API key

API key committed to repository is compromised. Anyone with repo 
access can use it. Must be rotated immediately.

**Fix**:
1. Move to environment variable:
```typescript
const apiKey = process.env.API_KEY
if (!apiKey) throw new Error('API_KEY not configured')
```

2. Add to .gitignore:
```
.env
.env.local
```

3. **ACTION REQUIRED**: Rotate compromised API key immediately.
```
```

### 3. Edge Cases (Blocking)

**Unhandled scenarios that cause errors**.

**Null/Undefined Handling**:
```typescript
// Code
function getFullName(user: User) {
  return user.firstName + ' ' + user.lastName  // BUG: No null check
}

// Review
❌ BLOCKING: Missing null/undefined handling

If `user` is null/undefined, this throws TypeError.
If `firstName` or `lastName` are null, result is "null Smith" or "John null".

**Fix**:
```typescript
function getFullName(user: User | null): string {
  if (!user) return ''
  
  const first = user.firstName ?? ''
  const last = user.lastName ?? ''
  
  return `${first} ${last}`.trim()
}
```

**Test cases to add**:
```typescript
expect(getFullName(null)).toBe('')
expect(getFullName({ firstName: null, lastName: 'Doe' })).toBe('Doe')
expect(getFullName({ firstName: 'John', lastName: null })).toBe('John')
```
```

**Empty Array/Collection**:
```typescript
// Code
function getAverage(numbers: number[]) {
  return numbers.reduce((a, b) => a + b) / numbers.length  // BUG: Empty array
}

// Review
❌ BLOCKING: Division by zero for empty arrays

Calling `getAverage([])` returns `NaN` due to division by zero.

**Fix**:
```typescript
function getAverage(numbers: number[]): number {
  if (numbers.length === 0) {
    throw new Error('Cannot calculate average of empty array')
  }
  return numbers.reduce((a, b) => a + b, 0) / numbers.length
}
```

Or return a default:
```typescript
function getAverage(numbers: number[]): number | null {
  if (numbers.length === 0) return null
  return numbers.reduce((a, b) => a + b, 0) / numbers.length
}
```
```

**Integer Overflow**:
```typescript
// Code
function addDays(timestamp: number, days: number) {
  return timestamp + (days * 24 * 60 * 60 * 1000)  // BUG: Integer overflow
}

// Review
❌ BLOCKING: Integer overflow for large day values

JavaScript numbers are 64-bit floats with 53-bit precision.
Large day values cause integer overflow and incorrect results.

**Example**: `addDays(Date.now(), 10000000)` produces invalid timestamp.

**Fix**: Validate input range:
```typescript
function addDays(timestamp: number, days: number): number {
  if (days > 100000) {  // ~273 years
    throw new Error('Day value too large')
  }
  if (!Number.isSafeInteger(timestamp)) {
    throw new Error('Invalid timestamp')
  }
  return timestamp + (days * 24 * 60 * 60 * 1000)
}
```
```

### 4. Performance (Blocking if Severe)

**Inefficiencies that cause production issues**.

**N+1 Query Problem**:
```typescript
// Code
async function getUsersWithPosts() {
  const users = await db.query('SELECT * FROM users')
  
  for (const user of users) {
    user.posts = await db.query(
      'SELECT * FROM posts WHERE user_id = ?',
      [user.id]
    )  // BUG: N+1 queries
  }
  
  return users
}

// Review
❌ BLOCKING: N+1 query problem

For 100 users, this executes 101 database queries (1 + 100).
With many users, this causes severe performance degradation.

**Fix**: Use JOIN or batch query:
```typescript
// Option 1: JOIN
async function getUsersWithPosts() {
  return db.query(`
    SELECT 
      u.*,
      json_agg(json_build_object('id', p.id, 'title', p.title)) as posts
    FROM users u
    LEFT JOIN posts p ON p.user_id = u.id
    GROUP BY u.id
  `)
}

// Option 2: Batch query
async function getUsersWithPosts() {
  const users = await db.query('SELECT * FROM users')
  const userIds = users.map(u => u.id)
  
  const posts = await db.query(
    'SELECT * FROM posts WHERE user_id IN (?)',
    [userIds]
  )
  
  // Group posts by user
  const postsByUser = posts.reduce((acc, post) => {
    acc[post.user_id] = acc[post.user_id] || []
    acc[post.user_id].push(post)
    return acc
  }, {})
  
  return users.map(user => ({
    ...user,
    posts: postsByUser[user.id] || []
  }))
}
```

**Performance impact**: Reduces from O(n) queries to O(1) queries.
```

**Inefficient Algorithm**:
```typescript
// Code
function findDuplicates(arr: number[]): number[] {
  const duplicates = []
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (arr[i] === arr[j]) {  // BUG: O(n²) complexity
        duplicates.push(arr[i])
      }
    }
  }
  return duplicates
}

// Review
⚠️ BLOCKING if used on large arrays: O(n²) algorithm

Current implementation has quadratic time complexity.
For 10,000 elements, this performs 50 million comparisons.

**Fix**: Use Set for O(n) complexity:
```typescript
function findDuplicates(arr: number[]): number[] {
  const seen = new Set<number>()
  const duplicates = new Set<number>()
  
  for (const num of arr) {
    if (seen.has(num)) {
      duplicates.add(num)
    } else {
      seen.add(num)
    }
  }
  
  return Array.from(duplicates)
}
```

**Performance**: O(n²) → O(n), 100x faster for 10,000 elements.
```

**Memory Leak**:
```typescript
// Code
class EventManager {
  private listeners: Map<string, Function[]> = new Map()
  
  subscribe(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event)!.push(callback)  // BUG: No cleanup
  }
}

// Review
❌ BLOCKING: Memory leak - listeners never removed

Subscribers accumulate indefinitely without cleanup mechanism.
Long-running application will exhaust memory.

**Fix**: Add unsubscribe method:
```typescript
class EventManager {
  private listeners: Map<string, Set<Function>> = new Map()
  
  subscribe(event: string, callback: Function): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(callback)
    
    // Return unsubscribe function
    return () => {
      this.listeners.get(event)?.delete(callback)
    }
  }
}

// Usage:
const unsubscribe = manager.subscribe('event', callback)
unsubscribe()  // Clean up when done
```
```

### 5. Error Handling (Blocking)

**Missing or incorrect error handling**.

**Unhandled Promise Rejection**:
```typescript
// Code
async function processOrder(orderId: string) {
  const order = await fetchOrder(orderId)  // BUG: No error handling
  await chargePayment(order)
  await sendConfirmation(order)
}

// Review
❌ BLOCKING: Unhandled promise rejections

If any operation fails, promise rejection crashes Node.js process
or leaves system in inconsistent state (payment charged but no confirmation).

**Fix**: Add proper error handling:
```typescript
async function processOrder(orderId: string): Promise<void> {
  try {
    const order = await fetchOrder(orderId)
    
    try {
      await chargePayment(order)
    } catch (error) {
      await logPaymentFailure(orderId, error)
      throw new Error(`Payment failed for order ${orderId}`)
    }
    
    try {
      await sendConfirmation(order)
    } catch (error) {
      // Payment succeeded but email failed - log but don't fail
      await logEmailFailure(orderId, error)
    }
  } catch (error) {
    await logError('processOrder', error)
    throw error
  }
}
```
```

**Swallowing Errors**:
```typescript
// Code
try {
  await saveToDatabase(data)
} catch (error) {
  console.log('Save failed')  // BUG: Error swallowed
}

// Review
❌ BLOCKING: Error swallowed without proper handling

Error is logged but not propagated. Caller thinks save succeeded 
when it actually failed, leading to data inconsistency.

**Fix**: Re-throw or handle explicitly:
```typescript
try {
  await saveToDatabase(data)
} catch (error) {
  logger.error('Database save failed', { error, data })
  throw new DatabaseError('Failed to save data', { cause: error })
}
```

Or handle with fallback:
```typescript
try {
  await saveToDatabase(data)
} catch (error) {
  logger.error('Primary database failed, using backup', { error })
  await saveToBackupDatabase(data)
}
```
```

### 6. Architecture Violations (Blocking)

**Code that violates project architecture or ADRs**.

**Bypassing Established Patterns**:
```typescript
// Code (violates repository pattern)
async function getUserOrders(userId: string) {
  const orders = await db.query(
    'SELECT * FROM orders WHERE user_id = ?',
    [userId]
  )  // BUG: Direct database access in service layer
  return orders
}

// Review
❌ BLOCKING: Architecture violation - bypassing repository layer

Per ADR-023, all database access must go through repository layer.
Direct queries in services bypass:
- Query centralization
- Caching strategy
- Audit logging

**Fix**: Use existing repository:
```typescript
async function getUserOrders(userId: string) {
  return orderRepository.findByUserId(userId)
}
```

If repository method doesn't exist, add it to repository:
```typescript
// repositories/order.repository.ts
class OrderRepository {
  async findByUserId(userId: string): Promise<Order[]> {
    return db.query('SELECT * FROM orders WHERE user_id = ?', [userId])
  }
}
```

**Reference**: See ADR-023: Repository Pattern for Data Access
```

**Inconsistent Error Handling**:
```typescript
// Code (inconsistent with project standard)
if (!user) {
  return { error: 'User not found' }  // BUG: Wrong error pattern
}

// Review
❌ BLOCKING: Inconsistent error handling

Project standard (per ADR-015) is to throw exceptions, not return error objects.
This creates inconsistent error handling across codebase.

**Fix**: Follow project pattern:
```typescript
if (!user) {
  throw new NotFoundError('User not found')
}
```

**Reference**: See ADR-015: Error Handling Strategy
```

### 7. Maintainability (Recommendation)

**Code that's hard to understand or modify**.

**Complex Nested Logic**:
```typescript
// Code
function processPayment(order: Order) {
  if (order.total > 0) {
    if (order.paymentMethod === 'credit_card') {
      if (order.card && order.card.isValid) {
        if (order.user.hasPaymentProfile) {
          // Process payment...
        }
      }
    }
  }
}

// Review
💡 RECOMMENDATION: Simplify nested conditions

Deep nesting makes code hard to follow. Consider early returns.

**Suggestion**:
```typescript
function processPayment(order: Order) {
  if (order.total <= 0) return
  if (order.paymentMethod !== 'credit_card') return
  if (!order.card || !order.card.isValid) {
    throw new Error('Invalid card')
  }
  if (!order.user.hasPaymentProfile) {
    throw new Error('User has no payment profile')
  }
  
  // Process payment...
}
```

Not blocking, but improves readability.
```

**Magic Numbers**:
```typescript
// Code
if (user.age < 18) {  // What's special about 18?
  return false
}

if (items.length > 50) {  // Why 50?
  throw new Error('Too many items')
}

// Review
💡 RECOMMENDATION: Extract magic numbers to named constants

**Suggestion**:
```typescript
const MINIMUM_AGE = 18
const MAX_ITEMS_PER_ORDER = 50

if (user.age < MINIMUM_AGE) {
  return false
}

if (items.length > MAX_ITEMS_PER_ORDER) {
  throw new Error('Too many items')
}
```

Improves maintainability - easy to find and update limits.
```

**Missing Documentation**:
```typescript
// Code
function calculateShipping(weight: number, distance: number, zone: string) {
  const base = weight * 0.05
  const zoneMultiplier = zone === 'A' ? 1.0 : zone === 'B' ? 1.5 : 2.0
  const distanceFactor = Math.log(distance) * 0.1
  return base * zoneMultiplier + distanceFactor
}

// Review
💡 RECOMMENDATION: Add documentation for complex calculation

Complex business logic formula should be documented.

**Suggestion**:
```typescript
/**
 * Calculate shipping cost based on package weight, delivery distance, and zone.
 * 
 * Formula:
 * - Base cost: $0.05 per unit weight
 * - Zone multipliers: A (1.0x), B (1.5x), C (2.0x)
 * - Distance factor: logarithmic scaling to favor longer distances
 * 
 * @param weight - Package weight in pounds
 * @param distance - Delivery distance in miles
 * @param zone - Delivery zone (A, B, or C)
 * @returns Shipping cost in dollars
 * 
 * @example
 * calculateShipping(10, 500, 'B') // Returns ~15.80
 */
function calculateShipping(weight: number, distance: number, zone: string): number {
  const base = weight * 0.05
  const zoneMultiplier = zone === 'A' ? 1.0 : zone === 'B' ? 1.5 : 2.0
  const distanceFactor = Math.log(distance) * 0.1
  return base * zoneMultiplier + distanceFactor
}
```
```

## Review Template

**Effective Review Structure**:

```markdown
## Summary
[High-level overview of changes and overall assessment]

## Blocking Issues
[Issues that MUST be fixed before merge]

### 1. [Issue Category]: [Brief description]
**Location**: [File and line number]
**Impact**: [What breaks or security risk]
**Fix**: [Specific code change needed]

### 2. ...

## Recommendations
[Nice-to-have improvements, not blocking]

### 1. [Category]: [Brief description]
**Suggestion**: [Proposed improvement]
**Benefit**: [Why this helps]

## Questions
[Clarifications needed from author]

1. [Question about design decision]
2. [Question about intended behavior]

## Positive Feedback
[What was done well - reinforces good practices]

- Clear naming conventions
- Good test coverage
- Proper error handling in X

## Approval Status
- [ ] Approved (no blocking issues)
- [ ] Approved with recommendations (non-blocking improvements suggested)
- [ ] Changes requested (blocking issues must be addressed)
```

## Review Example

**Pull Request**: Add user email verification feature

```markdown
## Summary
Adds email verification flow for new user registrations. Overall structure 
is good, but found one critical security issue and one logical error that 
need fixing.

## Blocking Issues

### 1. Security: Verification token predictable
**Location**: `services/email-verification.service.ts:15`
**Impact**: Attacker can predict verification tokens and verify arbitrary emails

```typescript
// Current (VULNERABLE):
function generateToken(email: string): string {
  return Buffer.from(email).toString('base64')  // Predictable!
}
```

**Fix**: Use cryptographically secure random token:
```typescript
import crypto from 'crypto'

function generateToken(): string {
  return crypto.randomBytes(32).toString('hex')
}
```

Store token in database with email association rather than encoding email in token.

---

### 2. Logical Error: Token expiration not checked
**Location**: `controllers/verify-email.controller.ts:28`
**Impact**: Expired tokens still work, allowing verification weeks after registration

```typescript
// Current (BUG):
const token = await db.verificationTokens.findOne({ token: req.params.token })
if (token) {
  await verifyUser(token.userId)  // No expiration check!
}
```

**Fix**: Check expiration:
```typescript
const token = await db.verificationTokens.findOne({ token: req.params.token })

if (!token) {
  throw new NotFoundError('Invalid token')
}

if (token.expiresAt < new Date()) {
  throw new ExpiredTokenError('Verification link expired')
}

await verifyUser(token.userId)
```

---

## Recommendations

### 1. Consider adding rate limiting
**Location**: `routes/verification.routes.ts`

**Suggestion**: Add rate limiting to prevent email bombing:
```typescript
import rateLimit from 'express-rate-limit'

const verificationLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 3, // 3 verification emails per window
  message: 'Too many verification attempts'
})

router.post('/resend', verificationLimiter, resendVerificationEmail)
```

**Benefit**: Prevents abuse of verification email system.

---

### 2. Add test for expired token scenario
**Location**: `tests/email-verification.test.ts`

**Suggestion**: Add test case:
```typescript
it('should reject expired verification token', async () => {
  const expiredToken = await createExpiredToken(user.id)
  
  await expect(
    verifyEmail(expiredToken)
  ).rejects.toThrow(ExpiredTokenError)
})
```

---

## Questions

1. Should verification tokens be single-use (invalidated after first use)?
2. What's the intended token expiration time? (Suggest 24 hours)
3. Should we send email notification when token expires?

## Positive Feedback

- Excellent test coverage for happy path scenarios
- Clear separation of concerns between service and controller layers
- Good error messages that help users understand issues

## Approval Status
- [ ] Approved
- [ ] Approved with recommendations
- [x] Changes requested (blocking security and logical issues)
```

## What NOT to Review

**Avoid nitpicking or style-only feedback**:

### ❌ Bad Reviews (Don't Do This)

```
"Use const instead of let here"
[If code works correctly and let is valid]

"This function could be one line"
[If current version is clear and readable]

"I prefer different naming"
[If name is clear and follows conventions]

"Add more comments"
[If code is self-explanatory]

"Reformat this section"
[If formatting follows project style guide]
```

### ✅ Good Reviews (Do This)

```
Focus on:
- Functional correctness
- Security vulnerabilities  
- Performance issues
- Architecture violations
- Missing error handling
- Edge cases
```

## Review Checklist

### Functional Review
- [ ] Does code do what it claims to do?
- [ ] Are all edge cases handled?
- [ ] Are error cases handled appropriately?
- [ ] Are there logical errors or bugs?
- [ ] Is null/undefined handling correct?
- [ ] Are async operations handled properly?

### Security Review
- [ ] No SQL injection vulnerabilities?
- [ ] No XSS vulnerabilities?
- [ ] Authentication properly implemented?
- [ ] Authorization checks present?
- [ ] Secrets not hard-coded?
- [ ] User input validated and sanitized?
- [ ] No sensitive data logged?

### Performance Review
- [ ] No N+1 query problems?
- [ ] Algorithms efficient for expected data size?
- [ ] No memory leaks?
- [ ] Database queries indexed appropriately?
- [ ] Large operations paginated?
- [ ] Resources cleaned up properly?

### Architecture Review
- [ ] Follows established patterns?
- [ ] Consistent with existing code?
- [ ] Aligns with ADRs?
- [ ] Proper separation of concerns?
- [ ] Dependencies injected, not hard-coded?

### Testing Review
- [ ] Tests cover new functionality?
- [ ] Tests cover edge cases?
- [ ] Tests cover error paths?
- [ ] Tests are independent and isolated?
- [ ] No flaky tests?

## Common Patterns

### API Endpoint Review

**Check for**:
- Input validation
- Authentication/authorization
- Error handling
- Proper status codes
- Response structure consistency
- Rate limiting (if needed)

```typescript
// Review this endpoint
router.post('/api/users', async (req, res) => {
  const user = await createUser(req.body)
  res.json(user)
})

// Issues to flag:
// ❌ No input validation
// ❌ No authentication check
// ❌ No error handling
// ❌ Wrong status code (should be 201)
// ❌ May return sensitive data (password hash)

// Improved version:
router.post('/api/users',
  authenticate,
  validateRequest(createUserSchema),
  async (req, res, next) => {
    try {
      const user = await createUser(req.body)
      const safeUser = { ...user }
      delete safeUser.passwordHash
      res.status(201).json(safeUser)
    } catch (error) {
      next(error)
    }
  }
)
```

### Database Query Review

**Check for**:
- SQL injection
- N+1 queries
- Missing indexes
- Transactions where needed
- Connection cleanup

```typescript
// Review this function
async function getUserOrders(userId: string) {
  const user = await db.query(`SELECT * FROM users WHERE id = ${userId}`)  // ❌ SQL injection
  
  for (const order of user.orders) {
    order.items = await db.query(
      `SELECT * FROM order_items WHERE order_id = ${order.id}`  // ❌ SQL injection + N+1
    )
  }
  
  return user
}

// Issues:
// 🚨 BLOCKING: SQL injection in both queries
// ❌ BLOCKING: N+1 query problem
// ❌ BLOCKING: No error handling
```

### React Component Review

**Check for**:
- Proper hooks usage
- Key prop in lists
- Memory leaks (cleanup in useEffect)
- Unnecessary re-renders
- Accessibility

```typescript
// Review this component
function UserList({ users }) {
  const [filter, setFilter] = useState('')
  
  useEffect(() => {
    const interval = setInterval(() => {
      fetchUsers()
    }, 1000)
    // ❌ No cleanup - memory leak
  }, [])
  
  return (
    <div>
      {users.filter(u => u.name.includes(filter)).map(user => (
        <div>{user.name}</div>  // ❌ Missing key prop
      ))}
    </div>
  )
}

// Issues:
// ❌ BLOCKING: Memory leak - interval not cleaned up
// ❌ BLOCKING: Missing key prop in list
// 💡 RECOMMENDATION: Consider debouncing filter
```

## Severity Levels

### 🚨 Critical (Block Immediately)
- Security vulnerabilities
- Data loss bugs
- Authentication/authorization bypass
- SQL injection, XSS
- Hard-coded secrets

### ❌ Blocking (Must Fix Before Merge)
- Logical errors causing incorrect behavior
- Unhandled error cases
- Memory leaks
- Severe performance issues (O(n²) on large data)
- Architecture violations
- Missing critical tests

### ⚠️ Warning (Should Fix, Can Merge)
- Minor performance issues
- Missing edge case handling (if rare)
- Incomplete error messages
- Missing non-critical tests

### 💡 Recommendation (Nice to Have)
- Code clarity improvements
- Documentation additions
- Refactoring suggestions
- Additional test coverage
- Minor optimizations

## Response to Feedback

**How to Handle Author Responses**:

### Author Disagrees
```
Author: "I don't think this is a bug, it's intentional."

Good Response:
"Thanks for clarifying. Can you help me understand the scenario where 
null is the expected input? Looking at the caller in line 45, it seems 
to always pass a defined user object. If null is possible, we should 
add a test case to document this behavior."
```

### Author Provides Context
```
Author: "This query optimization was measured and only saves 50ms."

Good Response:
"Appreciate the data. 50ms for this code path is acceptable. 
Approved - no changes needed here."
```

### Author Has Alternative Solution
```
Author: "Instead of early return, I prefer guard clauses at the top."

Good Response:
"Both approaches work. Since the project already uses early returns 
in similar files (see user.service.ts:45, order.service.ts:78), 
let's maintain consistency. But functionally both are fine."
```

## Review Timing

**When to Review**:
- ✅ Within 24 hours of PR creation
- ✅ After author responds to feedback
- ✅ Before merge (final approval)

**How Long to Spend**:
- Small PR (<100 lines): 5-10 minutes
- Medium PR (100-500 lines): 15-30 minutes
- Large PR (500+ lines): 30-60 minutes
- Suggest splitting if >1000 lines

## Quick Reference

### Review Priority Order
1. **Security** - Always review first
2. **Correctness** - Does it work?
3. **Architecture** - Does it fit?
4. **Performance** - Is it fast enough?
5. **Maintainability** - Can we maintain it?
6. **Style** - Only if egregious

### Feedback Formula
```
[Severity]: [Brief description]
Location: [Where]
Impact: [Why it matters]
Fix: [Specific solution with code]
```

### Tone Guidelines
- ✅ "Consider...", "Suggest...", "What if..."
- ✅ "This could cause X if Y happens"
- ✅ "Per ADR-023, we should..."
- ❌ "This is wrong"
- ❌ "Why didn't you..."
- ❌ "Obviously this won't work"

### Approval Criteria
**Approve if**:
- No blocking issues
- All security concerns addressed
- Tests cover new functionality
- Follows architecture

**Request changes if**:
- Blocking issues present
- Security vulnerabilities
- Missing critical error handling
- Architecture violations

Conduct code reviews that are **thorough, actionable, and respectful**.