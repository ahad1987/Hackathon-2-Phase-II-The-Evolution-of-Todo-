# Auth Agent Skill - Complete Documentation

This is the complete Auth Agent skill for implementing secure authentication systems using Better Auth.

---

## SKILL.md

```markdown
---
name: auth-agent
description: Implement secure authentication systems using Better Auth with expertise in password hashing, JWT access/refresh token management, session validation, and OWASP security best practices. Use when building or modifying authentication flows (signup, signin, signout), implementing token-based auth, protecting routes with middleware, managing environment secrets, or designing auth logic for React/Next.js applications. Covers credential storage, token expiration/revocation, and modular framework-compatible patterns.
---

# Auth Agent

Implement secure, production-ready authentication using Better Auth for React and Next.js applications.

## Quick Start

For a basic Better Auth setup in Next.js:

\`\`\`typescript
// lib/auth.ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  database: {
    provider: "postgresql",
    url: process.env.DATABASE_URL!,
  },
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 12,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },
});
\`\`\`

## Core Authentication Flows

### Signup Flow

Implement secure user registration with proper validation:

\`\`\`typescript
// app/api/auth/signup/route.ts
import { auth } from "@/lib/auth";
import { hash } from "bcrypt";

export async function POST(request: Request) {
  const { email, password, name } = await request.json();
  
  // Validate input
  if (!email || !password || password.length < 12) {
    return Response.json({ error: "Invalid input" }, { status: 400 });
  }
  
  // Use Better Auth's built-in signup
  const result = await auth.api.signUpEmail({
    body: { email, password, name },
  });
  
  return Response.json(result);
}
\`\`\`

### Signin Flow with Session Management

\`\`\`typescript
// app/api/auth/signin/route.ts
export async function POST(request: Request) {
  const { email, password } = await request.json();
  
  const session = await auth.api.signInEmail({
    body: { email, password },
  });
  
  if (!session) {
    return Response.json({ error: "Invalid credentials" }, { status: 401 });
  }
  
  return Response.json({ session });
}
\`\`\`

### Signout with Token Revocation

\`\`\`typescript
// app/api/auth/signout/route.ts
export async function POST(request: Request) {
  const token = request.headers.get("authorization")?.split(" ")[1];
  
  await auth.api.signOut({
    headers: { authorization: \`Bearer \${token}\` },
  });
  
  return Response.json({ success: true });
}
\`\`\`

## JWT Token Management

### Access & Refresh Token Pattern

Better Auth handles tokens automatically, but for custom implementations:

\`\`\`typescript
// lib/jwt.ts
import jwt from "jsonwebtoken";

const ACCESS_TOKEN_SECRET = process.env.ACCESS_TOKEN_SECRET!;
const REFRESH_TOKEN_SECRET = process.env.REFRESH_TOKEN_SECRET!;

export function generateAccessToken(userId: string) {
  return jwt.sign({ userId }, ACCESS_TOKEN_SECRET, { expiresIn: "15m" });
}

export function generateRefreshToken(userId: string) {
  return jwt.sign({ userId }, REFRESH_TOKEN_SECRET, { expiresIn: "7d" });
}

export function verifyAccessToken(token: string) {
  try {
    return jwt.verify(token, ACCESS_TOKEN_SECRET);
  } catch {
    return null;
  }
}
\`\`\`

### Token Refresh Endpoint

\`\`\`typescript
// app/api/auth/refresh/route.ts
export async function POST(request: Request) {
  const { refreshToken } = await request.json();
  
  const session = await auth.api.refreshSession({
    body: { refreshToken },
  });
  
  return Response.json(session);
}
\`\`\`

## Route Protection

### Middleware for Protected Routes

\`\`\`typescript
// middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function middleware(request: NextRequest) {
  const token = request.cookies.get("better-auth.session_token")?.value;
  
  if (!token) {
    return NextResponse.redirect(new URL("/signin", request.url));
  }
  
  // Validate session
  const session = await auth.api.getSession({
    headers: { authorization: \`Bearer \${token}\` },
  });
  
  if (!session) {
    return NextResponse.redirect(new URL("/signin", request.url));
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/api/protected/:path*"],
};
\`\`\`

### Server Component Auth Check

\`\`\`typescript
// app/dashboard/page.tsx
import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { redirect } from "next/navigation";

export default async function Dashboard() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });
  
  if (!session) {
    redirect("/signin");
  }
  
  return <div>Protected Dashboard</div>;
}
\`\`\`

## Client-Side Integration

### React Hook for Authentication

\`\`\`typescript
// hooks/use-auth.ts
import { useSession } from "better-auth/react";

export function useAuth() {
  const { data: session, isPending } = useSession();
  
  return {
    user: session?.user,
    isAuthenticated: !!session,
    isLoading: isPending,
  };
}
\`\`\`

### Protected Client Component

\`\`\`typescript
// components/protected-content.tsx
"use client";
import { useAuth } from "@/hooks/use-auth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export function ProtectedContent({ children }) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/signin");
    }
  }, [isAuthenticated, isLoading, router]);
  
  if (isLoading) return <div>Loading...</div>;
  if (!isAuthenticated) return null;
  
  return <>{children}</>;
}
\`\`\`

## Security Best Practices

### Environment Variables Management

Never expose secrets. Use \`.env.local\`:

\`\`\`bash
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=<generate-with-openssl-rand-base64-32>
BETTER_AUTH_URL=http://localhost:3000
ACCESS_TOKEN_SECRET=<generate-with-openssl-rand-base64-32>
REFRESH_TOKEN_SECRET=<generate-with-openssl-rand-base64-32>
\`\`\`

### Password Requirements

Enforce strong passwords:

\`\`\`typescript
const passwordRequirements = {
  minLength: 12,
  requireUppercase: true,
  requireLowercase: true,
  requireNumbers: true,
  requireSpecialChars: true,
};

function validatePassword(password: string): boolean {
  if (password.length < passwordRequirements.minLength) return false;
  if (requireUppercase && !/[A-Z]/.test(password)) return false;
  if (requireLowercase && !/[a-z]/.test(password)) return false;
  if (requireNumbers && !/\\d/.test(password)) return false;
  if (requireSpecialChars && !/[!@#$%^&*]/.test(password)) return false;
  return true;
}
\`\`\`

### Rate Limiting

Prevent brute force attacks:

\`\`\`typescript
// lib/rate-limit.ts
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(5, "1 m"), // 5 requests per minute
});

export async function checkRateLimit(identifier: string) {
  const { success } = await ratelimit.limit(identifier);
  return success;
}
\`\`\`

## Advanced Features

For detailed implementation of:
- **OAuth social providers** - See [references/oauth-patterns.md](references/oauth-patterns.md)
- **Email verification** - See [references/email-verification.md](references/email-verification.md)
- **Two-factor authentication** - See [references/2fa-implementation.md](references/2fa-implementation.md)
- **Role-based access control** - See [references/rbac-patterns.md](references/rbac-patterns.md)
- **OWASP security checklist** - See [references/owasp-checklist.md](references/owasp-checklist.md)

## Helper Scripts

Use bundled scripts for common tasks:
- \`scripts/generate-secrets.py\` - Generate secure secrets for environment variables
- \`scripts/validate-auth-config.py\` - Validate Better Auth configuration
- \`scripts/test-token-flow.py\` - Test JWT token generation and validation

## Configuration Templates

Find ready-to-use configuration in \`assets/\`:
- \`assets/auth-config-template.ts\` - Complete Better Auth configuration
- \`assets/env-template.txt\` - Environment variables template
- \`assets/middleware-template.ts\` - Route protection middleware
```

---

## Bundled Resources

### Scripts

#### 1. `scripts/generate-secrets.py`
Generates cryptographically secure secrets for environment variables.

#### 2. `scripts/validate-auth-config.py`
Validates Better Auth configuration for security best practices.

#### 3. `scripts/test-token-flow.py`
Tests JWT token generation, validation, and expiration.

### References

#### 1. `references/oauth-patterns.md`
Complete guide for implementing OAuth authentication with Google, GitHub, Discord, Microsoft, and other providers.

#### 2. `references/email-verification.md`
Email verification implementation guide including verification flows, email templates, and testing strategies.

#### 3. `references/2fa-implementation.md`
Two-factor authentication implementation using TOTP, backup codes, and trusted devices.

#### 4. `references/rbac-patterns.md`
Role-based access control patterns including roles, permissions, middleware protection, and React hooks.

#### 5. `references/owasp-checklist.md`
Comprehensive OWASP authentication security checklist covering password security, session management, token security, and compliance.

### Assets

#### 1. `assets/auth-config-template.ts`
Complete Better Auth configuration template with all options documented.

#### 2. `assets/env-template.txt`
Environment variables template with all necessary secrets and configuration options.

#### 3. `assets/middleware-template.ts`
Next.js middleware template for route protection with security headers.

---

## Skill Structure

```
auth-agent/
├── SKILL.md (main documentation)
├── scripts/
│   ├── generate-secrets.py
│   ├── validate-auth-config.py
│   └── test-token-flow.py
├── references/
│   ├── oauth-patterns.md
│   ├── email-verification.md
│   ├── 2fa-implementation.md
│   ├── rbac-patterns.md
│   └── owasp-checklist.md
└── assets/
    ├── auth-config-template.ts
    ├── env-template.txt
    └── middleware-template.ts
```

---

## Usage Examples

### When This Skill Triggers

- "Set up authentication for my Next.js app"
- "Implement JWT refresh tokens"
- "Add OAuth login with Google"
- "Protect my API routes"
- "Enable two-factor authentication"
- "Implement role-based access control"
- "Set up email verification"
- "Create a secure signup flow"

### Key Features

✅ Complete Better Auth integration
✅ JWT access & refresh token management
✅ OAuth social providers
✅ Email verification
✅ Two-factor authentication
✅ Role-based access control
✅ OWASP security best practices
✅ Rate limiting & brute force protection
✅ Secure session management
✅ Environment secrets management

---

## Installation

Import the `auth-agent.skill` file into Claude to enable authentication expertise.

---

## License

See individual license files in the skill package.
