---
name: crud-builder
description: Design and implement CRUD (Create, Read, Update, Delete) functionality aligned with data models. Create consistent interfaces with clear input/output structures. Validate inputs, handle errors predictably, and enforce authorization rules. Integrate safely with database layers and APIs. Structure CRUD logic for reusability and maintainability. Use when building data access layers, REST APIs, service layers, repository patterns, or any data manipulation operations. Ensures deterministic, testable, and production-safe CRUD code.
---

# CRUD Builder

Build production-ready CRUD operations with proper validation, error handling, authorization, and maintainable architecture.

## Core Principles

**Data Model First**: CRUD operations must align exactly with your data model. Schema changes require CRUD updates.

**Interface Consistency**: All CRUD operations follow the same patterns. Users should predict behavior across entities.

**Fail Explicitly**: Validate early, fail fast with clear error messages. Never silently fail or return ambiguous results.

**Authorization Always**: Check permissions before operations. Never trust input or assume authorization.

**Transactions Matter**: Use database transactions for multi-step operations. Ensure atomicity and consistency.

**Testability**: CRUD operations should be easily testable in isolation with predictable inputs and outputs.

## CRUD Operation Patterns

### Create

**Purpose**: Insert new records into the database.

**Key Responsibilities**:
- Validate all required fields
- Check uniqueness constraints
- Set default values
- Generate IDs if needed
- Enforce authorization (can user create?)
- Return created entity with generated fields

**TypeScript Example**:
```typescript
// types/user.ts
interface UserCreateInput {
  email: string
  username: string
  password: string
  firstName: string
  lastName: string
  role?: 'user' | 'admin'
}

interface UserOutput {
  id: string
  email: string
  username: string
  firstName: string
  lastName: string
  role: string
  createdAt: Date
  updatedAt: Date
}

// services/user.service.ts
class UserService {
  async create(input: UserCreateInput, currentUser?: User): Promise<UserOutput> {
    // 1. Authorization check
    if (!this.canCreate(currentUser, input)) {
      throw new ForbiddenError('Insufficient permissions to create user')
    }
    
    // 2. Validate input
    const validationErrors = this.validateCreateInput(input)
    if (validationErrors.length > 0) {
      throw new ValidationError('Invalid input', validationErrors)
    }
    
    // 3. Check uniqueness constraints
    const existingEmail = await this.repository.findByEmail(input.email)
    if (existingEmail) {
      throw new ConflictError('Email already exists')
    }
    
    const existingUsername = await this.repository.findByUsername(input.username)
    if (existingUsername) {
      throw new ConflictError('Username already exists')
    }
    
    // 4. Hash password
    const hashedPassword = await hashPassword(input.password)
    
    // 5. Set defaults
    const userData = {
      ...input,
      password: hashedPassword,
      role: input.role || 'user',
      createdAt: new Date(),
      updatedAt: new Date()
    }
    
    // 6. Database operation
    const user = await this.repository.create(userData)
    
    // 7. Return without sensitive fields
    return this.toOutput(user)
  }
  
  private validateCreateInput(input: UserCreateInput): ValidationError[] {
    const errors: ValidationError[] = []
    
    if (!input.email || !this.isValidEmail(input.email)) {
      errors.push({ field: 'email', message: 'Valid email is required' })
    }
    
    if (!input.username || input.username.length < 3) {
      errors.push({ field: 'username', message: 'Username must be at least 3 characters' })
    }
    
    if (!input.password || input.password.length < 8) {
      errors.push({ field: 'password', message: 'Password must be at least 8 characters' })
    }
    
    return errors
  }
  
  private canCreate(currentUser: User | undefined, input: UserCreateInput): boolean {
    // Public registration allowed for 'user' role
    if (!input.role || input.role === 'user') {
      return true
    }
    
    // Only admins can create admin users
    return currentUser?.role === 'admin'
  }
  
  private toOutput(user: User): UserOutput {
    const { password, ...output } = user
    return output
  }
}
```

**Python Example**:
```python
# models/user.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class UserCreateInput:
    email: str
    username: str
    password: str
    first_name: str
    last_name: str
    role: Optional[str] = 'user'

@dataclass
class UserOutput:
    id: str
    email: str
    username: str
    first_name: str
    last_name: str
    role: str
    created_at: datetime
    updated_at: datetime

# services/user_service.py
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    async def create(
        self, 
        input_data: UserCreateInput, 
        current_user: Optional[User] = None
    ) -> UserOutput:
        """Create a new user with validation and authorization."""
        
        # 1. Authorization check
        if not self._can_create(current_user, input_data):
            raise ForbiddenError('Insufficient permissions to create user')
        
        # 2. Validate input
        validation_errors = self._validate_create_input(input_data)
        if validation_errors:
            raise ValidationError('Invalid input', validation_errors)
        
        # 3. Check uniqueness constraints
        if await self.repository.find_by_email(input_data.email):
            raise ConflictError('Email already exists')
        
        if await self.repository.find_by_username(input_data.username):
            raise ConflictError('Username already exists')
        
        # 4. Hash password
        hashed_password = hash_password(input_data.password)
        
        # 5. Prepare user data
        user_data = {
            'email': input_data.email,
            'username': input_data.username,
            'password': hashed_password,
            'first_name': input_data.first_name,
            'last_name': input_data.last_name,
            'role': input_data.role or 'user',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # 6. Database operation
        user = await self.repository.create(user_data)
        
        # 7. Return safe output
        return self._to_output(user)
    
    def _validate_create_input(self, input_data: UserCreateInput) -> list:
        errors = []
        
        if not input_data.email or not is_valid_email(input_data.email):
            errors.append({'field': 'email', 'message': 'Valid email is required'})
        
        if not input_data.username or len(input_data.username) < 3:
            errors.append({'field': 'username', 'message': 'Username must be at least 3 characters'})
        
        if not input_data.password or len(input_data.password) < 8:
            errors.append({'field': 'password', 'message': 'Password must be at least 8 characters'})
        
        return errors
```

### Read (Single)

**Purpose**: Retrieve a single record by identifier.

**Key Responsibilities**:
- Validate identifier format
- Check record existence
- Enforce authorization (can user view?)
- Return complete or filtered data based on permissions
- Handle soft deletes if applicable

**TypeScript Example**:
```typescript
async getById(id: string, currentUser?: User): Promise<UserOutput> {
  // 1. Validate ID format
  if (!this.isValidId(id)) {
    throw new BadRequestError('Invalid user ID format')
  }
  
  // 2. Fetch from database
  const user = await this.repository.findById(id)
  
  // 3. Check existence
  if (!user) {
    throw new NotFoundError(`User with id ${id} not found`)
  }
  
  // 4. Check soft delete
  if (user.deletedAt) {
    throw new NotFoundError(`User with id ${id} not found`)
  }
  
  // 5. Authorization check
  if (!this.canView(currentUser, user)) {
    throw new ForbiddenError('Insufficient permissions to view this user')
  }
  
  // 6. Return filtered output based on permissions
  return this.toOutput(user, currentUser)
}

private canView(currentUser: User | undefined, targetUser: User): boolean {
  // Users can view their own profile
  if (currentUser?.id === targetUser.id) {
    return true
  }
  
  // Admins can view anyone
  if (currentUser?.role === 'admin') {
    return true
  }
  
  // Public profiles are viewable by all
  return targetUser.isPublic
}

private toOutput(user: User, viewer?: User): UserOutput {
  // Remove sensitive fields
  const { password, ...safeUser } = user
  
  // Hide additional fields for non-owners
  if (viewer?.id !== user.id && viewer?.role !== 'admin') {
    const { email, ...publicUser } = safeUser
    return publicUser as UserOutput
  }
  
  return safeUser
}
```

### Read (List)

**Purpose**: Retrieve multiple records with filtering, sorting, and pagination.

**Key Responsibilities**:
- Validate query parameters
- Apply authorization filters (only show accessible records)
- Implement pagination for performance
- Support filtering and sorting
- Return metadata (total count, page info)

**TypeScript Example**:
```typescript
interface ListOptions {
  page?: number
  pageSize?: number
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
  filters?: Record<string, any>
}

interface ListResult<T> {
  data: T[]
  pagination: {
    page: number
    pageSize: number
    totalItems: number
    totalPages: number
  }
}

async list(
  options: ListOptions = {},
  currentUser?: User
): Promise<ListResult<UserOutput>> {
  // 1. Validate and set defaults
  const page = Math.max(1, options.page || 1)
  const pageSize = Math.min(100, Math.max(1, options.pageSize || 20))
  const sortBy = options.sortBy || 'createdAt'
  const sortOrder = options.sortOrder || 'desc'
  
  // 2. Validate sort field
  const allowedSortFields = ['createdAt', 'username', 'email']
  if (!allowedSortFields.includes(sortBy)) {
    throw new BadRequestError(`Invalid sort field: ${sortBy}`)
  }
  
  // 3. Build query with authorization filters
  const query = this.buildAuthorizedQuery(options.filters, currentUser)
  
  // 4. Calculate pagination
  const skip = (page - 1) * pageSize
  
  // 5. Fetch data and count
  const [users, totalItems] = await Promise.all([
    this.repository.find({
      where: query,
      skip,
      take: pageSize,
      orderBy: { [sortBy]: sortOrder }
    }),
    this.repository.count({ where: query })
  ])
  
  // 6. Transform to output
  const data = users.map(user => this.toOutput(user, currentUser))
  
  // 7. Build response with pagination metadata
  return {
    data,
    pagination: {
      page,
      pageSize,
      totalItems,
      totalPages: Math.ceil(totalItems / pageSize)
    }
  }
}

private buildAuthorizedQuery(
  filters: Record<string, any> = {},
  currentUser?: User
): any {
  const query: any = { ...filters }
  
  // Exclude soft-deleted records
  query.deletedAt = null
  
  // Non-admins can only see public profiles and their own
  if (currentUser?.role !== 'admin') {
    query.OR = [
      { isPublic: true },
      { id: currentUser?.id }
    ]
  }
  
  return query
}
```

### Update

**Purpose**: Modify existing record fields.

**Key Responsibilities**:
- Validate identifier and input
- Check record existence
- Enforce authorization (can user update?)
- Validate partial updates (only changed fields)
- Check uniqueness constraints for changed fields
- Update timestamps
- Return updated entity

**TypeScript Example**:
```typescript
interface UserUpdateInput {
  email?: string
  username?: string
  firstName?: string
  lastName?: string
  isPublic?: boolean
}

async update(
  id: string,
  input: UserUpdateInput,
  currentUser?: User
): Promise<UserOutput> {
  // 1. Validate ID
  if (!this.isValidId(id)) {
    throw new BadRequestError('Invalid user ID format')
  }
  
  // 2. Fetch existing record
  const existingUser = await this.repository.findById(id)
  
  if (!existingUser) {
    throw new NotFoundError(`User with id ${id} not found`)
  }
  
  if (existingUser.deletedAt) {
    throw new NotFoundError(`User with id ${id} not found`)
  }
  
  // 3. Authorization check
  if (!this.canUpdate(currentUser, existingUser)) {
    throw new ForbiddenError('Insufficient permissions to update this user')
  }
  
  // 4. Validate input (only provided fields)
  const validationErrors = this.validateUpdateInput(input)
  if (validationErrors.length > 0) {
    throw new ValidationError('Invalid input', validationErrors)
  }
  
  // 5. Check uniqueness constraints for changed fields
  if (input.email && input.email !== existingUser.email) {
    const emailExists = await this.repository.findByEmail(input.email)
    if (emailExists) {
      throw new ConflictError('Email already exists')
    }
  }
  
  if (input.username && input.username !== existingUser.username) {
    const usernameExists = await this.repository.findByUsername(input.username)
    if (usernameExists) {
      throw new ConflictError('Username already exists')
    }
  }
  
  // 6. Prepare update data
  const updateData = {
    ...input,
    updatedAt: new Date()
  }
  
  // 7. Perform update
  const updatedUser = await this.repository.update(id, updateData)
  
  // 8. Return safe output
  return this.toOutput(updatedUser)
}

private validateUpdateInput(input: UserUpdateInput): ValidationError[] {
  const errors: ValidationError[] = []
  
  if (input.email !== undefined && !this.isValidEmail(input.email)) {
    errors.push({ field: 'email', message: 'Invalid email format' })
  }
  
  if (input.username !== undefined && input.username.length < 3) {
    errors.push({ field: 'username', message: 'Username must be at least 3 characters' })
  }
  
  return errors
}

private canUpdate(currentUser: User | undefined, targetUser: User): boolean {
  // Users can update their own profile
  if (currentUser?.id === targetUser.id) {
    return true
  }
  
  // Admins can update anyone
  return currentUser?.role === 'admin'
}
```

### Delete

**Purpose**: Remove records from the database.

**Key Responsibilities**:
- Support both soft delete (mark as deleted) and hard delete (permanent removal)
- Validate identifier
- Check record existence
- Enforce authorization (can user delete?)
- Handle cascading deletes or relationships
- Return success confirmation

**TypeScript Example**:
```typescript
// Soft Delete (Recommended)
async softDelete(id: string, currentUser?: User): Promise<void> {
  // 1. Validate ID
  if (!this.isValidId(id)) {
    throw new BadRequestError('Invalid user ID format')
  }
  
  // 2. Fetch existing record
  const user = await this.repository.findById(id)
  
  if (!user) {
    throw new NotFoundError(`User with id ${id} not found`)
  }
  
  if (user.deletedAt) {
    throw new ConflictError('User is already deleted')
  }
  
  // 3. Authorization check
  if (!this.canDelete(currentUser, user)) {
    throw new ForbiddenError('Insufficient permissions to delete this user')
  }
  
  // 4. Perform soft delete
  await this.repository.update(id, {
    deletedAt: new Date(),
    updatedAt: new Date()
  })
  
  // 5. Log deletion for audit trail
  await this.auditLog.log({
    action: 'USER_DELETED',
    userId: id,
    performedBy: currentUser?.id,
    timestamp: new Date()
  })
}

// Hard Delete (Use with caution)
async hardDelete(id: string, currentUser?: User): Promise<void> {
  // 1-3. Same validation and authorization as soft delete
  const user = await this.validateAndAuthorizeDelete(id, currentUser)
  
  // 4. Check for dependencies
  const hasActiveData = await this.checkDependencies(id)
  if (hasActiveData) {
    throw new ConflictError(
      'Cannot delete user with active data. Consider soft delete instead.'
    )
  }
  
  // 5. Use transaction for cascading deletes
  await this.database.transaction(async (tx) => {
    // Delete related data
    await tx.userSessions.deleteMany({ where: { userId: id } })
    await tx.userPreferences.deleteMany({ where: { userId: id } })
    
    // Delete main record
    await tx.users.delete({ where: { id } })
  })
  
  // 6. Log deletion
  await this.auditLog.log({
    action: 'USER_HARD_DELETED',
    userId: id,
    performedBy: currentUser?.id,
    timestamp: new Date()
  })
}

private async checkDependencies(userId: string): Promise<boolean> {
  const [orderCount, postCount] = await Promise.all([
    this.repository.countUserOrders(userId),
    this.repository.countUserPosts(userId)
  ])
  
  return orderCount > 0 || postCount > 0
}

private canDelete(currentUser: User | undefined, targetUser: User): boolean {
  // Users can delete their own account
  if (currentUser?.id === targetUser.id) {
    return true
  }
  
  // Only admins can delete other users
  return currentUser?.role === 'admin'
}
```

## Repository Pattern

**Separate data access logic from business logic**. Repositories handle database operations.

```typescript
// repositories/user.repository.ts
interface IUserRepository {
  create(data: any): Promise<User>
  findById(id: string): Promise<User | null>
  findByEmail(email: string): Promise<User | null>
  findByUsername(username: string): Promise<User | null>
  find(options: FindOptions): Promise<User[]>
  count(options: CountOptions): Promise<number>
  update(id: string, data: any): Promise<User>
  delete(id: string): Promise<void>
}

class UserRepository implements IUserRepository {
  constructor(private db: Database) {}
  
  async create(data: any): Promise<User> {
    return await this.db.users.create({ data })
  }
  
  async findById(id: string): Promise<User | null> {
    return await this.db.users.findUnique({ where: { id } })
  }
  
  async findByEmail(email: string): Promise<User | null> {
    return await this.db.users.findUnique({ where: { email } })
  }
  
  async find(options: FindOptions): Promise<User[]> {
    return await this.db.users.findMany(options)
  }
  
  async count(options: CountOptions): Promise<number> {
    return await this.db.users.count(options)
  }
  
  async update(id: string, data: any): Promise<User> {
    return await this.db.users.update({
      where: { id },
      data
    })
  }
  
  async delete(id: string): Promise<void> {
    await this.db.users.delete({ where: { id } })
  }
}
```

## Error Handling

**Define clear error hierarchy** for different failure scenarios.

```typescript
// errors/base.error.ts
export class AppError extends Error {
  constructor(
    public message: string,
    public statusCode: number,
    public code: string
  ) {
    super(message)
    this.name = this.constructor.name
    Error.captureStackTrace(this, this.constructor)
  }
}

// errors/domain.errors.ts
export class NotFoundError extends AppError {
  constructor(message: string) {
    super(message, 404, 'NOT_FOUND')
  }
}

export class ValidationError extends AppError {
  constructor(message: string, public errors: any[]) {
    super(message, 422, 'VALIDATION_ERROR')
  }
}

export class ConflictError extends AppError {
  constructor(message: string) {
    super(message, 409, 'CONFLICT')
  }
}

export class ForbiddenError extends AppError {
  constructor(message: string) {
    super(message, 403, 'FORBIDDEN')
  }
}

export class BadRequestError extends AppError {
  constructor(message: string) {
    super(message, 400, 'BAD_REQUEST')
  }
}

// middleware/error-handler.ts
export function errorHandler(err: Error, req: Request, res: Response, next: NextFunction) {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      success: false,
      error: {
        code: err.code,
        message: err.message,
        ...(err instanceof ValidationError && { errors: err.errors })
      }
    })
  }
  
  // Unexpected errors
  console.error('Unexpected error:', err)
  return res.status(500).json({
    success: false,
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred'
    }
  })
}
```

## Input Validation

**Validate at multiple layers** for defense in depth.

```typescript
// validators/user.validator.ts
import * as yup from 'yup'

export const createUserSchema = yup.object({
  email: yup
    .string()
    .email('Invalid email format')
    .required('Email is required'),
  username: yup
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(30, 'Username must not exceed 30 characters')
    .matches(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores')
    .required('Username is required'),
  password: yup
    .string()
    .min(8, 'Password must be at least 8 characters')
    .matches(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .matches(/[0-9]/, 'Password must contain at least one number')
    .required('Password is required'),
  firstName: yup
    .string()
    .required('First name is required'),
  lastName: yup
    .string()
    .required('Last name is required'),
  role: yup
    .string()
    .oneOf(['user', 'admin'], 'Invalid role')
    .optional()
})

export const updateUserSchema = yup.object({
  email: yup
    .string()
    .email('Invalid email format')
    .optional(),
  username: yup
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(30, 'Username must not exceed 30 characters')
    .matches(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores')
    .optional(),
  firstName: yup
    .string()
    .optional(),
  lastName: yup
    .string()
    .optional(),
  isPublic: yup
    .boolean()
    .optional()
})

// Usage in service
async create(input: UserCreateInput, currentUser?: User): Promise<UserOutput> {
  // Validate with schema
  try {
    await createUserSchema.validate(input, { abortEarly: false })
  } catch (err) {
    if (err instanceof yup.ValidationError) {
      const errors = err.inner.map(e => ({
        field: e.path,
        message: e.message
      }))
      throw new ValidationError('Validation failed', errors)
    }
    throw err
  }
  
  // Continue with business logic...
}
```

## Authorization Strategies

### Role-Based Access Control (RBAC)

```typescript
// auth/rbac.ts
enum Permission {
  USER_CREATE = 'user:create',
  USER_READ_OWN = 'user:read:own',
  USER_READ_ANY = 'user:read:any',
  USER_UPDATE_OWN = 'user:update:own',
  USER_UPDATE_ANY = 'user:update:any',
  USER_DELETE_OWN = 'user:delete:own',
  USER_DELETE_ANY = 'user:delete:any'
}

const rolePermissions: Record<string, Permission[]> = {
  user: [
    Permission.USER_READ_OWN,
    Permission.USER_UPDATE_OWN,
    Permission.USER_DELETE_OWN
  ],
  admin: [
    Permission.USER_CREATE,
    Permission.USER_READ_ANY,
    Permission.USER_UPDATE_ANY,
    Permission.USER_DELETE_ANY
  ]
}

function hasPermission(user: User | undefined, permission: Permission): boolean {
  if (!user) return false
  const permissions = rolePermissions[user.role] || []
  return permissions.includes(permission)
}

// Usage in service
private canDelete(currentUser: User | undefined, targetUser: User): boolean {
  // Check if user can delete any user
  if (hasPermission(currentUser, Permission.USER_DELETE_ANY)) {
    return true
  }
  
  // Check if user can delete their own account
  if (currentUser?.id === targetUser.id && 
      hasPermission(currentUser, Permission.USER_DELETE_OWN)) {
    return true
  }
  
  return false
}
```

### Attribute-Based Access Control (ABAC)

```typescript
// auth/abac.ts
interface AccessContext {
  user: User
  resource: any
  action: string
  environment: {
    time: Date
    ipAddress: string
  }
}

class AccessControl {
  canAccess(context: AccessContext): boolean {
    // Check ownership
    if (context.resource.ownerId === context.user.id) {
      return true
    }
    
    // Check admin role
    if (context.user.role === 'admin') {
      return true
    }
    
    // Check resource visibility
    if (context.action === 'read' && context.resource.isPublic) {
      return true
    }
    
    // Check team membership
    if (context.user.teamId === context.resource.teamId) {
      return this.checkTeamPermission(context)
    }
    
    return false
  }
  
  private checkTeamPermission(context: AccessContext): boolean {
    const teamRole = context.user.teamRole
    const requiredRole = this.getRequiredRole(context.action)
    
    return this.roleHierarchy[teamRole] >= this.roleHierarchy[requiredRole]
  }
}
```

## Transaction Management

**Use transactions for multi-step operations** to ensure data consistency.

```typescript
// services/order.service.ts
async createOrder(
  input: OrderCreateInput,
  currentUser: User
): Promise<OrderOutput> {
  // Use database transaction
  return await this.database.transaction(async (tx) => {
    // 1. Create order
    const order = await tx.orders.create({
      data: {
        userId: currentUser.id,
        status: 'pending',
        total: input.total
      }
    })
    
    // 2. Create order items
    await tx.orderItems.createMany({
      data: input.items.map(item => ({
        orderId: order.id,
        productId: item.productId,
        quantity: item.quantity,
        price: item.price
      }))
    })
    
    // 3. Update product inventory
    for (const item of input.items) {
      const product = await tx.products.findUnique({
        where: { id: item.productId }
      })
      
      if (!product || product.stock < item.quantity) {
        throw new ConflictError(`Insufficient stock for product ${item.productId}`)
      }
      
      await tx.products.update({
        where: { id: item.productId },
        data: { stock: product.stock - item.quantity }
      })
    }
    
    // 4. Create payment record
    await tx.payments.create({
      data: {
        orderId: order.id,
        amount: input.total,
        status: 'pending'
      }
    })
    
    return order
  })
}
```

## Testing CRUD Operations

### Unit Tests

```typescript
// tests/user.service.test.ts
import { UserService } from '../services/user.service'
import { UserRepository } from '../repositories/user.repository'
import { NotFoundError, ConflictError, ForbiddenError } from '../errors'

describe('UserService', () => {
  let service: UserService
  let repository: jest.Mocked<UserRepository>
  
  beforeEach(() => {
    repository = {
      create: jest.fn(),
      findById: jest.fn(),
      findByEmail: jest.fn(),
      findByUsername: jest.fn(),
      update: jest.fn(),
      delete: jest.fn()
    } as any
    
    service = new UserService(repository)
  })
  
  describe('create', () => {
    it('should create user with valid input', async () => {
      const input = {
        email: 'test@example.com',
        username: 'testuser',
        password: 'Password123',
        firstName: 'Test',
        lastName: 'User'
      }
      
      repository.findByEmail.mockResolvedValue(null)
      repository.findByUsername.mockResolvedValue(null)
      repository.create.mockResolvedValue({
        id: '1',
        ...input,
        role: 'user',
        createdAt: new Date(),
        updatedAt: new Date()
      } as any)
      
      const result = await service.create(input)
      
      expect(result).toHaveProperty('id')
      expect(result).not.toHaveProperty('password')
      expect(repository.create).toHaveBeenCalledTimes(1)
    })
    
    it('should throw ConflictError if email exists', async () => {
      const input = {
        email: 'existing@example.com',
        username: 'testuser',
        password: 'Password123',
        firstName: 'Test',
        lastName: 'User'
      }
      
      repository.findByEmail.mockResolvedValue({ id: '1' } as any)
      
      await expect(service.create(input)).rejects.toThrow(ConflictError)
      expect(repository.create).not.toHaveBeenCalled()
    })
  })
  
  describe('getById', () => {
    it('should return user if exists', async () => {
      const user = {
        id: '1',
        email: 'test@example.com',
        username: 'testuser',
        firstName: 'Test',
        lastName: 'User',
        role: 'user',
        deletedAt: null
      }
      
      repository.findById.mockResolvedValue(user as any)
      
      const result = await service.getById('1')
      
      expect(result.id).toBe('1')
      expect(result).not.toHaveProperty('password')
    })
    
    it('should throw NotFoundError if user does not exist', async () => {
      repository.findById.mockResolvedValue(null)
      
      await expect(service.getById('999')).rejects.toThrow(NotFoundError)
    })
  })
  
  describe('update', () => {
    it('should update user with valid input', async () => {
      const existing = {
        id: '1',
        email: 'old@example.com',
        username: 'olduser',
        deletedAt: null
      }
      
      const input = {
        email: 'new@example.com'
      }
      
      repository.findById.mockResolvedValue(existing as any)
      repository.findByEmail.mockResolvedValue(null)
      repository.update.mockResolvedValue({
        ...existing,
        ...input
      } as any)
      
      const currentUser = { id: '1', role: 'user' } as User
      const result = await service.update('1', input, currentUser)
      
      expect(result.email).toBe('new@example.com')
      expect(repository.update).toHaveBeenCalledWith('1', expect.objectContaining(input))
    })
    
    it('should throw ForbiddenError if user cannot update', async () => {
      const existing = { id: '1', deletedAt: null }
      const currentUser = { id: '2', role: 'user' } as User
      
      repository.findById.mockResolvedValue(existing as any)
      
      await expect(service.update('1', {}, currentUser)).rejects.toThrow(ForbiddenError)
    })
  })
})
```

### Integration Tests

```typescript
// tests/integration/user.api.test.ts
import request from 'supertest'
import { app } from '../app'
import { database } from '../database'

describe('User API Integration Tests', () => {
  beforeAll(async () => {
    await database.connect()
  })
  
  afterAll(async () => {
    await database.disconnect()
  })
  
  beforeEach(async () => {
    await database.users.deleteMany()
  })
  
  describe('POST /api/users', () => {
    it('should create user with valid data', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({
          email: 'test@example.com',
          username: 'testuser',
          password: 'Password123',
          firstName: 'Test',
          lastName: 'User'
        })
        .expect(201)
      
      expect(response.body.success).toBe(true)
      expect(response.body.data).toHaveProperty('id')
      expect(response.body.data.email).toBe('test@example.com')
      expect(response.body.data).not.toHaveProperty('password')
    })
    
    it('should return 409 for duplicate email', async () => {
      await database.users.create({
        data: {
          email: 'existing@example.com',
          username: 'existing',
          password: 'hashed'
        }
      })
      
      const response = await request(app)
        .post('/api/users')
        .send({
          email: 'existing@example.com',
          username: 'newuser',
          password: 'Password123',
          firstName: 'New',
          lastName: 'User'
        })
        .expect(409)
      
      expect(response.body.success).toBe(false)
      expect(response.body.error.message).toContain('Email already exists')
    })
  })
})
```

## Production Best Practices

### Audit Logging

```typescript
// services/audit.service.ts
interface AuditLog {
  action: string
  resourceType: string
  resourceId: string
  userId?: string
  changes?: any
  timestamp: Date
  ipAddress?: string
}

class AuditService {
  async log(entry: AuditLog): Promise<void> {
    await this.repository.create({
      ...entry,
      timestamp: entry.timestamp || new Date()
    })
  }
}

// Usage in CRUD operations
async update(id: string, input: UserUpdateInput, currentUser?: User): Promise<UserOutput> {
  const existingUser = await this.repository.findById(id)
  
  // ... validation and authorization ...
  
  const updatedUser = await this.repository.update(id, input)
  
  // Log the change
  await this.auditLog.log({
    action: 'USER_UPDATED',
    resourceType: 'user',
    resourceId: id,
    userId: currentUser?.id,
    changes: {
      before: existingUser,
      after: updatedUser
    },
    timestamp: new Date()
  })
  
  return this.toOutput(updatedUser)
}
```

### Rate Limiting

```typescript
// middleware/rate-limit.ts
import rateLimit from 'express-rate-limit'

export const createRateLimit = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 requests per window
  message: 'Too many accounts created, please try again later',
  standardHeaders: true,
  legacyHeaders: false
})

export const readRateLimit = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 100, // 100 requests per window
  message: 'Too many requests, please try again later'
})

// Usage in routes
router.post('/users', createRateLimit, userController.create)
router.get('/users', readRateLimit, userController.list)
```

### Caching

```typescript
// middleware/cache.ts
class CacheService {
  constructor(private redis: Redis) {}
  
  async get<T>(key: string): Promise<T | null> {
    const cached = await this.redis.get(key)
    return cached ? JSON.parse(cached) : null
  }
  
  async set(key: string, value: any, ttl: number = 3600): Promise<void> {
    await this.redis.setex(key, ttl, JSON.stringify(value))
  }
  
  async invalidate(pattern: string): Promise<void> {
    const keys = await this.redis.keys(pattern)
    if (keys.length > 0) {
      await this.redis.del(...keys)
    }
  }
}

// Usage in service
async getById(id: string, currentUser?: User): Promise<UserOutput> {
  // Try cache first
  const cacheKey = `user:${id}`
  const cached = await this.cache.get<UserOutput>(cacheKey)
  
  if (cached) {
    return cached
  }
  
  // Fetch from database
  const user = await this.repository.findById(id)
  
  if (!user) {
    throw new NotFoundError(`User with id ${id} not found`)
  }
  
  const output = this.toOutput(user)
  
  // Cache for 1 hour
  await this.cache.set(cacheKey, output, 3600)
  
  return output
}

async update(id: string, input: UserUpdateInput, currentUser?: User): Promise<UserOutput> {
  // ... validation and update logic ...
  
  const updatedUser = await this.repository.update(id, input)
  
  // Invalidate cache
  await this.cache.invalidate(`user:${id}`)
  
  return this.toOutput(updatedUser)
}
```

## CRUD Checklist

Before deploying CRUD operations:

- [ ] **Data Model Alignment**: Operations match database schema exactly
- [ ] **Input Validation**: All inputs validated with clear error messages
- [ ] **Authorization**: Permission checks on all operations
- [ ] **Error Handling**: Specific errors for each failure scenario
- [ ] **Idempotency**: Operations produce same result when repeated (where applicable)
- [ ] **Transactions**: Multi-step operations wrapped in transactions
- [ ] **Soft Deletes**: Prefer soft delete over hard delete
- [ ] **Audit Logging**: Critical operations logged for compliance
- [ ] **Rate Limiting**: Protection against abuse
- [ ] **Caching**: Read operations cached where appropriate
- [ ] **Pagination**: List operations return paginated results
- [ ] **Testing**: Unit and integration tests cover main scenarios
- [ ] **Documentation**: API documentation generated and accurate

## Quick Reference

### Operation Summary

| Operation | HTTP Method | Authorization | Validation | Returns |
|-----------|-------------|---------------|------------|---------|
| Create | POST | Can create? | Full input | Created entity |
| Read (Single) | GET | Can view? | ID only | Single entity |
| Read (List) | GET | Filter by permission | Query params | Array + pagination |
| Update | PUT/PATCH | Can update? | Partial input | Updated entity |
| Delete | DELETE | Can delete? | ID only | Success confirmation |

### Common Patterns

**Create**: Validate → Check uniqueness → Set defaults → Insert → Return
**Read**: Validate ID → Check existence → Check permission → Return
**Update**: Validate ID → Check existence → Check permission → Validate changes → Check uniqueness → Update → Return
**Delete**: Validate ID → Check existence → Check permission → Check dependencies → Delete → Return

### Error Status Codes

- **400 Bad Request**: Invalid input format
- **401 Unauthorized**: Not authenticated
- **403 Forbidden**: Not authorized for this operation
- **404 Not Found**: Resource does not exist
- **409 Conflict**: Uniqueness constraint violation
- **422 Unprocessable Entity**: Validation failed
- **500 Internal Server Error**: Unexpected error

Keep CRUD operations **simple, predictable, and secure**.