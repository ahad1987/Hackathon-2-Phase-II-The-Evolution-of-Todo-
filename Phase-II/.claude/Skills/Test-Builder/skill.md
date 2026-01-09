---
name: test-builder
description: Design and implement comprehensive test suites. Create unit, integration, and regression tests with clear test cases and assertions. Mock external dependencies deterministically. Validate edge cases, error paths, and failure modes. Ensure tests are isolated, repeatable, and fast. Organize tests for maintainability and high coverage. Use when building test suites, writing test cases, setting up CI/CD testing, implementing TDD/BDD, or ensuring code quality. Keeps test logic deterministic and production-safe.
---

# Test Builder

Build comprehensive, maintainable test suites with proper isolation, mocking, and coverage.

## Core Principles

**Test Independence**: Each test runs in isolation. No shared state between tests. Order doesn't matter.

**Fast Execution**: Tests run in seconds, not minutes. Mock slow dependencies (databases, APIs, file I/O).

**Clear Assertions**: One concept per test. Descriptive names. Obvious failures.

**Deterministic Results**: Same code = same result, always. No flaky tests. No random data unless seeded.

**Coverage Targets Quality**: Aim for edge cases and error paths, not just line coverage percentages.

**Maintainable Structure**: Follow consistent patterns. Easy to locate and update tests.

## Test Types

### Unit Tests

**Test individual functions/methods in isolation**.

**Characteristics**:
- Fast (milliseconds per test)
- No external dependencies
- Mock all I/O operations
- Test one unit of logic
- High volume (70-80% of test suite)

**TypeScript/Jest Example**:
```typescript
// src/utils/calculator.ts
export class Calculator {
  add(a: number, b: number): number {
    return a + b
  }
  
  divide(a: number, b: number): number {
    if (b === 0) {
      throw new Error('Cannot divide by zero')
    }
    return a / b
  }
}

// tests/utils/calculator.test.ts
import { Calculator } from '@/utils/calculator'

describe('Calculator', () => {
  let calculator: Calculator
  
  beforeEach(() => {
    calculator = new Calculator()
  })
  
  describe('add', () => {
    it('should add two positive numbers', () => {
      expect(calculator.add(2, 3)).toBe(5)
    })
    
    it('should add negative numbers', () => {
      expect(calculator.add(-2, -3)).toBe(-5)
    })
    
    it('should handle zero', () => {
      expect(calculator.add(0, 5)).toBe(5)
      expect(calculator.add(5, 0)).toBe(5)
    })
  })
  
  describe('divide', () => {
    it('should divide two numbers', () => {
      expect(calculator.divide(10, 2)).toBe(5)
    })
    
    it('should handle decimal results', () => {
      expect(calculator.divide(10, 3)).toBeCloseTo(3.333, 2)
    })
    
    it('should throw error when dividing by zero', () => {
      expect(() => calculator.divide(10, 0)).toThrow('Cannot divide by zero')
    })
  })
})
```

**Python/pytest Example**:
```python
# src/calculator.py
class Calculator:
    def add(self, a: float, b: float) -> float:
        return a + b
    
    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

# tests/test_calculator.py
import pytest
from src.calculator import Calculator

class TestCalculator:
    @pytest.fixture
    def calculator(self):
        """Create a fresh calculator for each test."""
        return Calculator()
    
    def test_add_positive_numbers(self, calculator):
        """Test adding two positive numbers."""
        assert calculator.add(2, 3) == 5
    
    def test_add_negative_numbers(self, calculator):
        """Test adding negative numbers."""
        assert calculator.add(-2, -3) == -5
    
    def test_add_with_zero(self, calculator):
        """Test addition with zero."""
        assert calculator.add(0, 5) == 5
        assert calculator.add(5, 0) == 5
    
    def test_divide_numbers(self, calculator):
        """Test dividing two numbers."""
        assert calculator.divide(10, 2) == 5
    
    def test_divide_decimal_result(self, calculator):
        """Test division with decimal result."""
        result = calculator.divide(10, 3)
        assert abs(result - 3.333) < 0.01
    
    def test_divide_by_zero_raises_error(self, calculator):
        """Test that dividing by zero raises ValueError."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            calculator.divide(10, 0)
```

### Integration Tests

**Test multiple components working together**.

**Characteristics**:
- Slower than unit tests (seconds per test)
- May use real databases (test databases)
- Test component interactions
- Fewer tests than unit tests (20-30% of suite)

**Example - Testing API endpoints**:
```typescript
// tests/integration/user-api.test.ts
import request from 'supertest'
import { app } from '@/app'
import { db } from '@/database'

describe('User API Integration', () => {
  beforeAll(async () => {
    // Setup test database
    await db.migrate.latest()
  })
  
  afterAll(async () => {
    // Cleanup
    await db.destroy()
  })
  
  beforeEach(async () => {
    // Clear data before each test
    await db('users').delete()
  })
  
  describe('POST /api/users', () => {
    it('should create a new user', async () => {
      const userData = {
        email: 'test@example.com',
        username: 'testuser',
        password: 'password123'
      }
      
      const response = await request(app)
        .post('/api/users')
        .send(userData)
        .expect(201)
      
      expect(response.body).toMatchObject({
        email: userData.email,
        username: userData.username
      })
      expect(response.body).toHaveProperty('id')
      expect(response.body).not.toHaveProperty('password')
      
      // Verify in database
      const user = await db('users').where({ email: userData.email }).first()
      expect(user).toBeDefined()
      expect(user.email).toBe(userData.email)
    })
    
    it('should return 409 for duplicate email', async () => {
      // Create existing user
      await db('users').insert({
        email: 'existing@example.com',
        username: 'existing',
        password: 'hashed'
      })
      
      const response = await request(app)
        .post('/api/users')
        .send({
          email: 'existing@example.com',
          username: 'newuser',
          password: 'password123'
        })
        .expect(409)
      
      expect(response.body.error).toContain('already exists')
    })
    
    it('should return 422 for invalid email', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({
          email: 'invalid-email',
          username: 'testuser',
          password: 'password123'
        })
        .expect(422)
      
      expect(response.body.errors).toContainEqual(
        expect.objectContaining({ field: 'email' })
      )
    })
  })
  
  describe('GET /api/users/:id', () => {
    it('should retrieve user by id', async () => {
      // Setup: Create user
      const [userId] = await db('users').insert({
        email: 'test@example.com',
        username: 'testuser',
        password: 'hashed'
      }).returning('id')
      
      const response = await request(app)
        .get(`/api/users/${userId}`)
        .expect(200)
      
      expect(response.body).toMatchObject({
        id: userId,
        email: 'test@example.com',
        username: 'testuser'
      })
    })
    
    it('should return 404 for non-existent user', async () => {
      await request(app)
        .get('/api/users/999999')
        .expect(404)
    })
  })
})
```

### End-to-End (E2E) Tests

**Test complete user workflows**.

**Characteristics**:
- Slowest tests (seconds to minutes)
- Test full application stack
- Simulate real user behavior
- Fewest tests (<10% of suite)

**Playwright Example**:
```typescript
// tests/e2e/user-registration.spec.ts
import { test, expect } from '@playwright/test'

test.describe('User Registration Flow', () => {
  test('should complete full registration process', async ({ page }) => {
    // Navigate to registration page
    await page.goto('/register')
    
    // Fill in form
    await page.fill('input[name="email"]', 'newuser@example.com')
    await page.fill('input[name="username"]', 'newuser')
    await page.fill('input[name="password"]', 'SecurePass123!')
    await page.fill('input[name="confirmPassword"]', 'SecurePass123!')
    
    // Submit form
    await page.click('button[type="submit"]')
    
    // Wait for redirect to dashboard
    await page.waitForURL('/dashboard')
    
    // Verify user is logged in
    await expect(page.locator('text=Welcome, newuser')).toBeVisible()
    
    // Verify email sent (check UI message)
    await expect(page.locator('text=verification email')).toBeVisible()
  })
  
  test('should show validation errors for invalid input', async ({ page }) => {
    await page.goto('/register')
    
    // Submit empty form
    await page.click('button[type="submit"]')
    
    // Check for error messages
    await expect(page.locator('text=Email is required')).toBeVisible()
    await expect(page.locator('text=Username is required')).toBeVisible()
    await expect(page.locator('text=Password is required')).toBeVisible()
  })
  
  test('should prevent registration with existing email', async ({ page, request }) => {
    // Setup: Create existing user via API
    await request.post('/api/users', {
      data: {
        email: 'existing@example.com',
        username: 'existing',
        password: 'password123'
      }
    })
    
    // Attempt to register with same email
    await page.goto('/register')
    await page.fill('input[name="email"]', 'existing@example.com')
    await page.fill('input[name="username"]', 'newuser')
    await page.fill('input[name="password"]', 'SecurePass123!')
    await page.fill('input[name="confirmPassword"]', 'SecurePass123!')
    await page.click('button[type="submit"]')
    
    // Verify error message
    await expect(page.locator('text=Email already exists')).toBeVisible()
  })
})
```

## Test Structure

### AAA Pattern (Arrange-Act-Assert)

**Standard test structure**:

```typescript
it('should calculate total with tax', () => {
  // Arrange: Setup test data and dependencies
  const cart = new ShoppingCart()
  const product = { name: 'Book', price: 10.00 }
  const taxRate = 0.08
  
  // Act: Execute the code under test
  cart.addItem(product)
  const total = cart.calculateTotal(taxRate)
  
  // Assert: Verify the results
  expect(total).toBe(10.80)
})
```

### Given-When-Then (BDD Style)

**Behavior-driven test structure**:

```typescript
describe('Shopping Cart', () => {
  describe('when calculating total with tax', () => {
    it('should apply tax rate to subtotal', () => {
      // Given a cart with items
      const cart = new ShoppingCart()
      cart.addItem({ name: 'Book', price: 10.00 })
      cart.addItem({ name: 'Pen', price: 2.00 })
      
      // When calculating total with 8% tax
      const total = cart.calculateTotal(0.08)
      
      // Then the total includes tax
      expect(total).toBe(12.96) // (10 + 2) * 1.08
    })
  })
})
```

### Test Organization

**Organize tests by feature or module**:

```
tests/
├── unit/
│   ├── services/
│   │   ├── user.service.test.ts
│   │   └── order.service.test.ts
│   ├── utils/
│   │   ├── validator.test.ts
│   │   └── formatter.test.ts
│   └── models/
│       └── user.model.test.ts
├── integration/
│   ├── api/
│   │   ├── users.test.ts
│   │   └── orders.test.ts
│   └── database/
│       └── repositories.test.ts
├── e2e/
│   ├── user-flows.spec.ts
│   └── checkout.spec.ts
└── fixtures/
    ├── users.ts
    └── orders.ts
```

## Mocking and Stubbing

### Mock External Dependencies

**Mock HTTP requests**:
```typescript
// tests/unit/services/api.service.test.ts
import axios from 'axios'
import { ApiService } from '@/services/api.service'

jest.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

describe('ApiService', () => {
  let apiService: ApiService
  
  beforeEach(() => {
    apiService = new ApiService()
    jest.clearAllMocks()
  })
  
  it('should fetch user data', async () => {
    // Arrange: Mock API response
    const mockUser = { id: 1, name: 'John Doe' }
    mockedAxios.get.mockResolvedValue({ data: mockUser })
    
    // Act
    const user = await apiService.getUser(1)
    
    // Assert
    expect(user).toEqual(mockUser)
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/users/1')
    expect(mockedAxios.get).toHaveBeenCalledTimes(1)
  })
  
  it('should handle API errors', async () => {
    // Mock error response
    mockedAxios.get.mockRejectedValue(new Error('Network error'))
    
    // Verify error handling
    await expect(apiService.getUser(1)).rejects.toThrow('Network error')
  })
})
```

**Mock database operations**:
```typescript
// tests/unit/repositories/user.repository.test.ts
import { UserRepository } from '@/repositories/user.repository'
import { db } from '@/database'

jest.mock('@/database')
const mockedDb = db as jest.Mocked<typeof db>

describe('UserRepository', () => {
  let repository: UserRepository
  
  beforeEach(() => {
    repository = new UserRepository()
    jest.clearAllMocks()
  })
  
  it('should find user by email', async () => {
    // Mock database query
    const mockUser = { id: 1, email: 'test@example.com' }
    mockedDb.mockReturnValue({
      where: jest.fn().mockReturnThis(),
      first: jest.fn().mockResolvedValue(mockUser)
    } as any)
    
    const user = await repository.findByEmail('test@example.com')
    
    expect(user).toEqual(mockUser)
    expect(mockedDb).toHaveBeenCalledWith('users')
  })
})
```

**Mock file system**:
```typescript
import fs from 'fs/promises'
import { FileService } from '@/services/file.service'

jest.mock('fs/promises')
const mockedFs = fs as jest.Mocked<typeof fs>

describe('FileService', () => {
  let fileService: FileService
  
  beforeEach(() => {
    fileService = new FileService()
    jest.clearAllMocks()
  })
  
  it('should read file content', async () => {
    const mockContent = 'file content'
    mockedFs.readFile.mockResolvedValue(mockContent as any)
    
    const content = await fileService.readFile('test.txt')
    
    expect(content).toBe(mockContent)
    expect(mockedFs.readFile).toHaveBeenCalledWith('test.txt', 'utf-8')
  })
  
  it('should handle file not found', async () => {
    mockedFs.readFile.mockRejectedValue(new Error('ENOENT: no such file'))
    
    await expect(fileService.readFile('missing.txt')).rejects.toThrow('no such file')
  })
})
```

### Spy on Methods

**Verify method calls without full mocks**:
```typescript
describe('UserService', () => {
  it('should call logger when creating user', async () => {
    const userService = new UserService()
    const loggerSpy = jest.spyOn(userService.logger, 'info')
    
    await userService.create({ email: 'test@example.com' })
    
    expect(loggerSpy).toHaveBeenCalledWith('User created', expect.any(Object))
    
    loggerSpy.mockRestore()
  })
})
```

### Dependency Injection for Testing

**Design for testability**:
```typescript
// src/services/order.service.ts
export class OrderService {
  constructor(
    private database: Database,
    private paymentGateway: PaymentGateway,
    private emailService: EmailService
  ) {}
  
  async createOrder(orderData: OrderData): Promise<Order> {
    const order = await this.database.orders.create(orderData)
    await this.paymentGateway.processPayment(order.total)
    await this.emailService.sendOrderConfirmation(order)
    return order
  }
}

// tests/unit/services/order.service.test.ts
class MockDatabase {
  orders = {
    create: jest.fn()
  }
}

class MockPaymentGateway {
  processPayment = jest.fn()
}

class MockEmailService {
  sendOrderConfirmation = jest.fn()
}

describe('OrderService', () => {
  let orderService: OrderService
  let mockDb: MockDatabase
  let mockPayment: MockPaymentGateway
  let mockEmail: MockEmailService
  
  beforeEach(() => {
    mockDb = new MockDatabase()
    mockPayment = new MockPaymentGateway()
    mockEmail = new MockEmailService()
    orderService = new OrderService(
      mockDb as any,
      mockPayment as any,
      mockEmail as any
    )
  })
  
  it('should create order with payment and email', async () => {
    const orderData = { userId: 1, items: [], total: 100 }
    const createdOrder = { id: 1, ...orderData }
    
    mockDb.orders.create.mockResolvedValue(createdOrder)
    mockPayment.processPayment.mockResolvedValue({ success: true })
    mockEmail.sendOrderConfirmation.mockResolvedValue(undefined)
    
    const order = await orderService.createOrder(orderData)
    
    expect(order).toEqual(createdOrder)
    expect(mockDb.orders.create).toHaveBeenCalledWith(orderData)
    expect(mockPayment.processPayment).toHaveBeenCalledWith(100)
    expect(mockEmail.sendOrderConfirmation).toHaveBeenCalledWith(createdOrder)
  })
  
  it('should not send email if payment fails', async () => {
    const orderData = { userId: 1, items: [], total: 100 }
    
    mockDb.orders.create.mockResolvedValue({ id: 1, ...orderData })
    mockPayment.processPayment.mockRejectedValue(new Error('Payment failed'))
    
    await expect(orderService.createOrder(orderData)).rejects.toThrow('Payment failed')
    
    expect(mockEmail.sendOrderConfirmation).not.toHaveBeenCalled()
  })
})
```

## Test Fixtures and Setup

### Fixture Factories

**Generate test data consistently**:
```typescript
// tests/fixtures/user.fixture.ts
import { faker } from '@faker-js/faker'

export class UserFixture {
  static create(overrides = {}) {
    return {
      id: faker.number.int({ min: 1, max: 10000 }),
      email: faker.internet.email(),
      username: faker.internet.userName(),
      firstName: faker.person.firstName(),
      lastName: faker.person.lastName(),
      createdAt: faker.date.past(),
      ...overrides
    }
  }
  
  static createMany(count: number, overrides = {}) {
    return Array.from({ length: count }, () => this.create(overrides))
  }
  
  static createAdmin(overrides = {}) {
    return this.create({
      role: 'admin',
      ...overrides
    })
  }
}

// Usage in tests
it('should filter admin users', () => {
  const users = [
    UserFixture.create(),
    UserFixture.createAdmin(),
    UserFixture.create(),
    UserFixture.createAdmin()
  ]
  
  const admins = filterAdmins(users)
  
  expect(admins).toHaveLength(2)
  expect(admins.every(u => u.role === 'admin')).toBe(true)
})
```

**Seeded random data for reproducibility**:
```typescript
import { faker } from '@faker-js/faker'

beforeAll(() => {
  // Set seed for reproducible random data
  faker.seed(123)
})

it('should generate consistent random data', () => {
  // This will generate the same data every test run
  const user = UserFixture.create()
  expect(user.email).toBe('expected@email.com') // Predictable with seed
})
```

### Setup and Teardown

**beforeEach/afterEach for test isolation**:
```typescript
describe('UserService', () => {
  let userService: UserService
  let database: Database
  
  beforeEach(async () => {
    // Setup fresh state before each test
    database = await createTestDatabase()
    userService = new UserService(database)
  })
  
  afterEach(async () => {
    // Cleanup after each test
    await database.clear()
    await database.close()
  })
  
  it('test 1', () => { /* ... */ })
  it('test 2', () => { /* ... */ })
})
```

**beforeAll/afterAll for expensive setup**:
```typescript
describe('Database Integration', () => {
  let database: Database
  
  beforeAll(async () => {
    // One-time setup for all tests
    database = await createTestDatabase()
    await database.migrate()
  })
  
  afterAll(async () => {
    // One-time cleanup
    await database.destroy()
  })
  
  beforeEach(async () => {
    // Clear data between tests (fast)
    await database.truncate()
  })
  
  it('test 1', () => { /* ... */ })
  it('test 2', () => { /* ... */ })
})
```

## Edge Cases and Error Handling

### Test Boundary Conditions

```typescript
describe('StringValidator', () => {
  describe('minLength', () => {
    it('should reject empty string', () => {
      expect(validator.minLength('', 5)).toBe(false)
    })
    
    it('should reject string shorter than minimum', () => {
      expect(validator.minLength('abc', 5)).toBe(false)
    })
    
    it('should accept string at exact minimum', () => {
      expect(validator.minLength('abcde', 5)).toBe(true)
    })
    
    it('should accept string longer than minimum', () => {
      expect(validator.minLength('abcdef', 5)).toBe(true)
    })
  })
  
  describe('maxLength', () => {
    it('should accept empty string', () => {
      expect(validator.maxLength('', 5)).toBe(true)
    })
    
    it('should accept string at exact maximum', () => {
      expect(validator.maxLength('abcde', 5)).toBe(true)
    })
    
    it('should reject string longer than maximum', () => {
      expect(validator.maxLength('abcdef', 5)).toBe(false)
    })
  })
})
```

### Test Error Paths

```typescript
describe('OrderService', () => {
  describe('error handling', () => {
    it('should handle invalid product ID', async () => {
      await expect(
        orderService.addItem(-1, 1)
      ).rejects.toThrow('Invalid product ID')
    })
    
    it('should handle out of stock items', async () => {
      mockProductRepo.findById.mockResolvedValue({ id: 1, stock: 0 })
      
      await expect(
        orderService.addItem(1, 1)
      ).rejects.toThrow('Product out of stock')
    })
    
    it('should handle payment processing failures', async () => {
      mockPaymentGateway.process.mockRejectedValue(
        new Error('Payment declined')
      )
      
      const result = await orderService.checkout()
      
      expect(result.success).toBe(false)
      expect(result.error).toBe('Payment declined')
    })
    
    it('should rollback transaction on failure', async () => {
      mockPaymentGateway.process.mockRejectedValue(new Error('Failed'))
      
      await orderService.checkout().catch(() => {})
      
      // Verify order was not saved
      expect(mockOrderRepo.save).not.toHaveBeenCalled()
    })
  })
})
```

### Test Race Conditions

```typescript
describe('ConcurrencyService', () => {
  it('should handle concurrent updates correctly', async () => {
    const counter = new Counter()
    
    // Simulate 100 concurrent increments
    const promises = Array.from({ length: 100 }, () => 
      counter.increment()
    )
    
    await Promise.all(promises)
    
    // Counter should be exactly 100, not less due to race condition
    expect(counter.value).toBe(100)
  })
})
```

### Test Timeout Scenarios

```typescript
describe('ApiService', () => {
  it('should timeout slow requests', async () => {
    // Mock slow response
    mockAxios.get.mockImplementation(() => 
      new Promise(resolve => setTimeout(resolve, 10000))
    )
    
    await expect(
      apiService.getData({ timeout: 1000 })
    ).rejects.toThrow('Request timeout')
  }, 2000) // Test timeout
})
```

## Assertions and Matchers

### Common Assertions

```typescript
// Equality
expect(value).toBe(5) // Strict equality (===)
expect(object).toEqual({ a: 1 }) // Deep equality
expect(array).toStrictEqual([1, 2, 3]) // Strict deep equality

// Truthiness
expect(value).toBeTruthy()
expect(value).toBeFalsy()
expect(value).toBeDefined()
expect(value).toBeNull()
expect(value).toBeUndefined()

// Numbers
expect(value).toBeGreaterThan(10)
expect(value).toBeGreaterThanOrEqual(10)
expect(value).toBeLessThan(10)
expect(value).toBeCloseTo(3.14, 2) // Floating point comparison

// Strings
expect(string).toMatch(/pattern/)
expect(string).toContain('substring')

// Arrays
expect(array).toContain(item)
expect(array).toHaveLength(5)
expect(array).toContainEqual({ id: 1 })

// Objects
expect(object).toHaveProperty('key')
expect(object).toHaveProperty('key', 'value')
expect(object).toMatchObject({ a: 1 }) // Partial match

// Functions
expect(fn).toThrow()
expect(fn).toThrow(Error)
expect(fn).toThrow('specific message')

// Mock functions
expect(mockFn).toHaveBeenCalled()
expect(mockFn).toHaveBeenCalledTimes(3)
expect(mockFn).toHaveBeenCalledWith(arg1, arg2)
expect(mockFn).toHaveBeenLastCalledWith(arg)
```

### Custom Matchers

```typescript
// tests/matchers/toBeValidEmail.ts
expect.extend({
  toBeValidEmail(received: string) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    const pass = emailRegex.test(received)
    
    return {
      pass,
      message: () => 
        pass
          ? `Expected ${received} not to be a valid email`
          : `Expected ${received} to be a valid email`
    }
  }
})

// Usage
expect('test@example.com').toBeValidEmail()
expect('invalid-email').not.toBeValidEmail()
```

## Test Coverage

### Measure Coverage

```bash
# Jest
npm test -- --coverage

# Coverage report shows:
# - Line coverage: % of lines executed
# - Branch coverage: % of branches taken
# - Function coverage: % of functions called
# - Statement coverage: % of statements executed
```

**Coverage Configuration**:
```javascript
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{js,ts}',
    '!src/**/*.test.{js,ts}',
    '!src/**/*.spec.{js,ts}',
    '!src/index.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
}
```

### Coverage Best Practices

**Focus on critical paths**:
```typescript
// High priority for coverage
describe('PaymentProcessor', () => {
  it('should process valid payment', () => { /* ... */ })
  it('should decline invalid card', () => { /* ... */ })
  it('should handle network errors', () => { /* ... */ })
  it('should retry failed transactions', () => { /* ... */ })
})

// Lower priority
describe('ButtonComponent', () => {
  it('should render correctly', () => { /* ... */ })
})
```

**Don't chase 100% coverage**:
- 80-90% is excellent
- Some code is hard to test (UI, timing, random)
- Focus on business logic, not getters/setters

## Snapshot Testing

**Test complex output structures**:
```typescript
describe('UserProfile', () => {
  it('should render user profile correctly', () => {
    const user = UserFixture.create()
    const profile = renderProfile(user)
    
    // Snapshot captures entire output
    expect(profile).toMatchSnapshot()
  })
  
  it('should render admin profile with badge', () => {
    const admin = UserFixture.createAdmin()
    const profile = renderProfile(admin)
    
    expect(profile).toMatchSnapshot()
  })
})

// Update snapshots when intentional changes occur:
// npm test -- -u
```

**Inline snapshots**:
```typescript
it('should format user object', () => {
  const user = { id: 1, name: 'John' }
  const formatted = formatUser(user)
  
  expect(formatted).toMatchInlineSnapshot(`
    {
      "displayName": "John",
      "userId": 1,
    }
  `)
})
```

## Parameterized Tests

**Test multiple scenarios efficiently**:
```typescript
// Jest with test.each
describe('Calculator', () => {
  test.each([
    [1, 1, 2],
    [1, 2, 3],
    [2, 2, 4],
    [-1, 1, 0],
    [0, 0, 0]
  ])('add(%i, %i) should return %i', (a, b, expected) => {
    expect(calculator.add(a, b)).toBe(expected)
  })
  
  test.each([
    { a: 10, b: 0, error: 'Cannot divide by zero' },
    { a: 10, b: 5, result: 2 },
    { a: -10, b: 2, result: -5 }
  ])('divide($a, $b)', ({ a, b, error, result }) => {
    if (error) {
      expect(() => calculator.divide(a, b)).toThrow(error)
    } else {
      expect(calculator.divide(a, b)).toBe(result)
    }
  })
})
```

**Python pytest parametrize**:
```python
import pytest

@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (1, 2, 3),
    (2, 2, 4),
    (-1, 1, 0),
    (0, 0, 0),
])
def test_add(calculator, a, b, expected):
    """Test addition with multiple input combinations."""
    assert calculator.add(a, b) == expected

@pytest.mark.parametrize("a,b,error", [
    (10, 0, "Cannot divide by zero"),
    (5, 0, "Cannot divide by zero"),
])
def test_divide_by_zero(calculator, a, b, error):
    """Test division by zero raises error."""
    with pytest.raises(ValueError, match=error):
        calculator.divide(a, b)
```

## Test Doubles

### Types of Test Doubles

**Dummy**: Passed but never used
```typescript
it('should create user without calling logger', () => {
  const dummyLogger = {} as Logger // Never called
  const service = new UserService(dummyLogger)
  
  service.create({ email: 'test@example.com' })
})
```

**Stub**: Returns predefined values
```typescript
const stubDatabase = {
  findUser: () => ({ id: 1, name: 'John' })
}
```

**Spy**: Records how it was called
```typescript
const spy = jest.fn()
service.on('event', spy)
service.triggerEvent()
expect(spy).toHaveBeenCalledTimes(1)
```

**Mock**: Pre-programmed with expectations
```typescript
const mock = jest.fn()
  .mockReturnValueOnce('first call')
  .mockReturnValueOnce('second call')
```

**Fake**: Working implementation (simplified)
```typescript
class FakeDatabase {
  private data = new Map()
  
  save(key: string, value: any) {
    this.data.set(key, value)
  }
  
  find(key: string) {
    return this.data.get(key)
  }
}
```

## Async Testing

### Testing Promises

```typescript
describe('Async Operations', () => {
  it('should fetch user data', async () => {
    const user = await userService.getUser(1)
    expect(user.id).toBe(1)
  })
  
  it('should handle rejection', async () => {
    await expect(userService.getUser(-1)).rejects.toThrow('Invalid ID')
  })
  
  it('should timeout long operations', async () => {
    await expect(
      slowOperation()
    ).rejects.toThrow('Timeout')
  }, 5000) // Test timeout in ms
})
```

### Testing Callbacks

```typescript
it('should call callback with result', (done) => {
  asyncFunction((error, result) => {
    expect(error).toBeNull()
    expect(result).toBe('success')
    done() // Signal test completion
  })
})
```

### Testing Event Emitters

```typescript
it('should emit event on completion', (done) => {
  const emitter = new EventEmitter()
  
  emitter.on('complete', (data) => {
    expect(data).toBe('finished')
    done()
  })
  
  emitter.start()
})
```

## Common Patterns

### Testing Authentication

```typescript
describe('Protected Routes', () => {
  it('should require authentication', async () => {
    const response = await request(app)
      .get('/api/protected')
      .expect(401)
    
    expect(response.body.error).toBe('Unauthorized')
  })
  
  it('should allow access with valid token', async () => {
    const token = generateTestToken({ userId: 1 })
    
    const response = await request(app)
      .get('/api/protected')
      .set('Authorization', `Bearer ${token}`)
      .expect(200)
    
    expect(response.body).toHaveProperty('data')
  })
  
  it('should reject expired token', async () => {
    const expiredToken = generateTestToken(
      { userId: 1 },
      { expiresIn: '-1h' }
    )
    
    await request(app)
      .get('/api/protected')
      .set('Authorization', `Bearer ${expiredToken}`)
      .expect(401)
  })
})
```

### Testing Pagination

```typescript
describe('List Users with Pagination', () => {
  beforeEach(async () => {
    // Create 25 test users
    await db('users').insert(UserFixture.createMany(25))
  })
  
  it('should return first page with default page size', async () => {
    const response = await request(app)
      .get('/api/users')
      .expect(200)
    
    expect(response.body.data).toHaveLength(20) // Default page size
    expect(response.body.pagination).toMatchObject({
      page: 1,
      pageSize: 20,
      totalItems: 25,
      totalPages: 2
    })
  })
  
  it('should return second page', async () => {
    const response = await request(app)
      .get('/api/users?page=2&pageSize=20')
      .expect(200)
    
    expect(response.body.data).toHaveLength(5) // Remaining items
    expect(response.body.pagination.page).toBe(2)
  })
  
  it('should handle out of range page', async () => {
    const response = await request(app)
      .get('/api/users?page=999')
      .expect(200)
    
    expect(response.body.data).toHaveLength(0)
  })
})
```

### Testing File Uploads

```typescript
describe('File Upload', () => {
  it('should upload valid image', async () => {
    const response = await request(app)
      .post('/api/upload')
      .attach('file', 'tests/fixtures/test-image.jpg')
      .expect(200)
    
    expect(response.body).toHaveProperty('url')
    expect(response.body.size).toBeGreaterThan(0)
  })
  
  it('should reject invalid file type', async () => {
    const response = await request(app)
      .post('/api/upload')
      .attach('file', 'tests/fixtures/test.txt')
      .expect(400)
    
    expect(response.body.error).toContain('Invalid file type')
  })
  
  it('should reject file exceeding size limit', async () => {
    // Create large buffer (11MB)
    const largeBuffer = Buffer.alloc(11 * 1024 * 1024)
    
    const response = await request(app)
      .post('/api/upload')
      .attach('file', largeBuffer, 'large.jpg')
      .expect(413)
    
    expect(response.body.error).toContain('File too large')
  })
})
```

### Testing Webhooks

```typescript
describe('Webhook Handler', () => {
  it('should process valid webhook payload', async () => {
    const payload = {
      event: 'payment.success',
      data: { orderId: 123, amount: 100 }
    }
    
    const signature = generateWebhookSignature(payload)
    
    const response = await request(app)
      .post('/webhooks/payment')
      .set('X-Webhook-Signature', signature)
      .send(payload)
      .expect(200)
    
    expect(response.body.status).toBe('processed')
  })
  
  it('should reject webhook with invalid signature', async () => {
    const payload = { event: 'payment.success' }
    
    await request(app)
      .post('/webhooks/payment')
      .set('X-Webhook-Signature', 'invalid')
      .send(payload)
      .expect(401)
  })
})
```

## Test Performance

### Keep Tests Fast

```typescript
// ❌ Slow: Real database
describe('UserService', () => {
  it('should create user', async () => {
    await db.connect() // Slow
    const user = await userService.create(userData)
    expect(user).toBeDefined()
  })
})

// ✅ Fast: Mocked database
describe('UserService', () => {
  it('should create user', async () => {
    mockDb.create.mockResolvedValue(userData)
    const user = await userService.create(userData)
    expect(user).toBeDefined()
  })
})
```

### Parallel Test Execution

```javascript
// jest.config.js
module.exports = {
  maxWorkers: '50%', // Use 50% of CPU cores
  testTimeout: 5000,  // 5 second timeout per test
}
```

### Avoid Sleep/Delays in Tests

```typescript
// ❌ Bad: Using sleep
it('should update after delay', async () => {
  service.updateAsync()
  await sleep(1000) // Slow and unreliable
  expect(service.isUpdated()).toBe(true)
})

// ✅ Good: Wait for actual condition
it('should update after delay', async () => {
  await service.updateAsync()
  expect(service.isUpdated()).toBe(true)
})

// ✅ Good: Use fake timers
it('should update after delay', () => {
  jest.useFakeTimers()
  
  service.updateAsync()
  
  jest.runAllTimers()
  
  expect(service.isUpdated()).toBe(true)
  
  jest.useRealTimers()
})
```

## Test Maintenance

### DRY Principle in Tests

**Extract common setup**:
```typescript
// tests/helpers/test-helpers.ts
export function createAuthenticatedRequest(app: Application, userId: number) {
  const token = generateTestToken({ userId })
  return request(app).set('Authorization', `Bearer ${token}`)
}

export function expectSuccessResponse(response: any) {
  expect(response.body.success).toBe(true)
  expect(response.body).toHaveProperty('data')
}

// Usage in tests
it('should get user profile', async () => {
  const response = await createAuthenticatedRequest(app, 1)
    .get('/api/profile')
    .expect(200)
  
  expectSuccessResponse(response)
})
```

### Avoid Test Interdependence

```typescript
// ❌ Bad: Tests depend on each other
describe('User CRUD', () => {
  let userId: number
  
  it('should create user', async () => {
    const user = await userService.create(userData)
    userId = user.id // Shared state
  })
  
  it('should update user', async () => {
    await userService.update(userId, { name: 'New Name' }) // Depends on previous test
  })
})

// ✅ Good: Independent tests
describe('User CRUD', () => {
  it('should create user', async () => {
    const user = await userService.create(userData)
    expect(user).toHaveProperty('id')
  })
  
  it('should update user', async () => {
    // Setup own data
    const user = await userService.create(userData)
    await userService.update(user.id, { name: 'New Name' })
    
    const updated = await userService.getById(user.id)
    expect(updated.name).toBe('New Name')
  })
})
```

## Production Checklist

Before merging code:

- [ ] **All Tests Pass**: Green CI pipeline
- [ ] **No Flaky Tests**: Tests pass consistently (run 10+ times)
- [ ] **Fast Execution**: Unit tests < 100ms, integration tests < 5s
- [ ] **Good Coverage**: 80%+ coverage on critical paths
- [ ] **Clear Test Names**: Descriptive, follows convention
- [ ] **Independent Tests**: No shared state, can run in any order
- [ ] **Mocked Dependencies**: No external API calls in unit tests
- [ ] **Edge Cases Covered**: Boundaries, errors, null/undefined
- [ ] **No Console Warnings**: Clean test output
- [ ] **Documentation**: Complex test scenarios explained
- [ ] **Deterministic**: No random data without seeds
- [ ] **CI/CD Integration**: Tests run on every commit

## Quick Reference

### Test Type Breakdown

| Type | Speed | Dependencies | Coverage | Purpose |
|------|-------|--------------|----------|---------|
| Unit | Fast (<100ms) | Mocked | 70-80% | Individual functions |
| Integration | Medium (1-5s) | Real DB, test APIs | 20-30% | Component interaction |
| E2E | Slow (10s-1min) | Full stack | <10% | User workflows |

### Common Commands

```bash
# Run all tests
npm test

# Run specific test file
npm test -- user.test.ts

# Run tests in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage

# Update snapshots
npm test -- -u

# Run tests matching pattern
npm test -- --testNamePattern="should create user"

# Run only changed tests
npm test -- --onlyChanged
```

### Test Smells (Red Flags)

- Tests fail intermittently (flaky)
- Tests take too long (>5s for unit tests)
- Tests share state between runs
- Tests test implementation, not behavior
- Test names don't describe what's being tested
- One test asserts too many things
- Tests require manual setup/cleanup
- Tests depend on execution order

Build test suites that are **fast, reliable, and maintainable**.
