---
name: frontend-nextjs
description: Design and build frontend user interfaces with Next.js. Create pages, layouts, and reusable components with responsive design, consistent styling, and production-ready code. Use when building Next.js applications, implementing UI components, creating page layouts, applying styling systems (Tailwind, CSS modules), structuring component hierarchies, or optimizing frontend performance. Covers component design, state management, accessibility, and maintainable architecture patterns.
---

# Frontend Next.js Development

Build production-ready Next.js user interfaces with clean architecture, responsive design, and maintainable code.

## Core Principles

**Component-First Thinking**: Break UI into small, reusable pieces. Each component should have a single responsibility.

**Responsive by Default**: Design mobile-first, scale up to desktop. Use responsive utilities consistently.

**Accessibility First**: Semantic HTML, ARIA labels, keyboard navigation, and proper contrast ratios are non-negotiable.

**Performance Matters**: Lazy load components, optimize images, minimize bundle size, use server components when possible.

**Predictable State**: Keep state close to where it's used. Lift state only when necessary for sharing.

## Project Structure

```
app/
├── (routes)/
│   ├── page.tsx              # Home page
│   ├── layout.tsx            # Root layout
│   └── [feature]/
│       ├── page.tsx          # Feature page
│       └── layout.tsx        # Feature layout
├── components/
│   ├── ui/                   # Base UI components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── input.tsx
│   ├── layout/               # Layout components
│   │   ├── header.tsx
│   │   ├── footer.tsx
│   │   └── sidebar.tsx
│   └── features/             # Feature-specific components
│       └── [feature]/
└── lib/
    ├── utils.ts              # Utility functions
    └── hooks/                # Custom React hooks
```

## Building Components

### Component Template

```tsx
// components/ui/button.tsx
import { ButtonHTMLAttributes, forwardRef } from 'react'
import { cn } from '@/lib/utils'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline'
  size?: 'sm' | 'md' | 'lg'
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          // Base styles
          'inline-flex items-center justify-center rounded-md font-medium transition-colors',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
          'disabled:pointer-events-none disabled:opacity-50',
          // Variants
          {
            'bg-blue-600 text-white hover:bg-blue-700 focus-visible:ring-blue-600': variant === 'primary',
            'bg-gray-200 text-gray-900 hover:bg-gray-300 focus-visible:ring-gray-500': variant === 'secondary',
            'border border-gray-300 bg-transparent hover:bg-gray-100 focus-visible:ring-gray-500': variant === 'outline',
          },
          // Sizes
          {
            'h-8 px-3 text-sm': size === 'sm',
            'h-10 px-4 text-base': size === 'md',
            'h-12 px-6 text-lg': size === 'lg',
          },
          className
        )}
        {...props}
      >
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'
export { Button }
```

### Component Design Rules

**Composition over Configuration**: Prefer composing simple components over complex prop APIs.

**Prop Forwarding**: Spread native HTML props using `...props` to maintain full flexibility.

**Class Name Merging**: Use `cn()` utility to merge Tailwind classes properly, handling conflicts.

**TypeScript First**: Define clear interfaces, extend native HTML types, use discriminated unions for variants.

**Ref Forwarding**: Use `forwardRef` for components that need DOM access.

## Layouts

### Root Layout

```tsx
// app/layout.tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'App Name',
  description: 'App description',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.className}>
      <body className="min-h-screen bg-gray-50 antialiased">
        {children}
      </body>
    </html>
  )
}
```

### Feature Layout

```tsx
// app/dashboard/layout.tsx
import { Header } from '@/components/layout/header'
import { Sidebar } from '@/components/layout/sidebar'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
```

## Styling Approach

### Tailwind Utilities (Recommended)

Use Tailwind for rapid, consistent styling with utility classes:

```tsx
<div className="flex items-center gap-4 rounded-lg bg-white p-6 shadow-sm">
  <img className="h-12 w-12 rounded-full" src={avatar} alt={name} />
  <div className="flex-1">
    <h3 className="text-lg font-semibold text-gray-900">{name}</h3>
    <p className="text-sm text-gray-600">{role}</p>
  </div>
</div>
```

**Common Patterns**:
- Flexbox: `flex items-center justify-between gap-4`
- Grid: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6`
- Responsive: `text-sm md:text-base lg:text-lg`
- States: `hover:bg-gray-100 focus:ring-2 disabled:opacity-50`

### CSS Modules (When Needed)

For component-specific styles that need scoping or complex selectors:

```css
/* button.module.css */
.button {
  @apply inline-flex items-center justify-center rounded-md;
  transition: all 0.2s ease;
}

.button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
```

```tsx
import styles from './button.module.css'

<button className={styles.button}>Click me</button>
```

## Responsive Design

### Mobile-First Breakpoints

```tsx
// Responsive grid
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>

// Responsive text
<h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold">
  Heading
</h1>

// Responsive spacing
<div className="p-4 md:p-6 lg:p-8">
  {content}
</div>
```

### Container Patterns

```tsx
// Max-width container
<div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
  {content}
</div>

// Full-width with padding
<div className="w-full px-4 md:px-8">
  {content}
</div>
```

## State Management

### Local State (useState)

For component-specific state:

```tsx
function Counter() {
  const [count, setCount] = useState(0)
  
  return (
    <div className="flex items-center gap-4">
      <button onClick={() => setCount(count - 1)}>-</button>
      <span className="text-2xl font-bold">{count}</span>
      <button onClick={() => setCount(count + 1)}>+</button>
    </div>
  )
}
```

### Lifted State

Share state between related components by lifting to common parent:

```tsx
function FilterableList() {
  const [filter, setFilter] = useState('')
  const [items, setItems] = useState(initialItems)
  
  const filtered = items.filter(item => 
    item.name.toLowerCase().includes(filter.toLowerCase())
  )
  
  return (
    <div>
      <SearchInput value={filter} onChange={setFilter} />
      <ItemList items={filtered} />
    </div>
  )
}
```

### Server State (Next.js)

Use server components and actions for data fetching:

```tsx
// app/posts/page.tsx (Server Component)
async function PostsPage() {
  const posts = await getPosts() // Direct database/API call
  
  return (
    <div>
      {posts.map(post => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  )
}
```

## Accessibility

### Semantic HTML

```tsx
// ✅ Good - Semantic elements
<nav aria-label="Main navigation">
  <ul>
    <li><a href="/home">Home</a></li>
    <li><a href="/about">About</a></li>
  </ul>
</nav>

<article>
  <header>
    <h1>Article Title</h1>
  </header>
  <section>
    <p>Article content</p>
  </section>
</article>

// ❌ Bad - Generic divs
<div className="nav">
  <div className="link">Home</div>
  <div className="link">About</div>
</div>
```

### ARIA Labels

```tsx
// Interactive elements
<button aria-label="Close dialog">
  <X className="h-4 w-4" />
</button>

// Form inputs
<label htmlFor="email">Email</label>
<input 
  id="email"
  type="email"
  aria-describedby="email-hint"
  aria-invalid={errors.email ? 'true' : 'false'}
/>
<p id="email-hint" className="text-sm text-gray-600">
  We'll never share your email
</p>

// Loading states
<div role="status" aria-live="polite">
  {loading ? 'Loading...' : 'Data loaded'}
</div>
```

### Keyboard Navigation

```tsx
function Dialog({ isOpen, onClose }) {
  useEffect(() => {
    if (!isOpen) return
    
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose])
  
  return (
    <div
      role="dialog"
      aria-modal="true"
      tabIndex={-1}
    >
      {/* Dialog content */}
    </div>
  )
}
```

## Performance Optimization

### Code Splitting

```tsx
// Dynamic imports for heavy components
import dynamic from 'next/dynamic'

const Chart = dynamic(() => import('@/components/chart'), {
  loading: () => <div>Loading chart...</div>,
  ssr: false
})
```

### Image Optimization

```tsx
import Image from 'next/image'

// Optimized images
<Image
  src="/hero.jpg"
  alt="Hero image"
  width={1200}
  height={600}
  priority // Above fold
  placeholder="blur"
/>

// Remote images
<Image
  src={user.avatar}
  alt={user.name}
  width={48}
  height={48}
  className="rounded-full"
/>
```

### Memoization

```tsx
import { memo, useMemo, useCallback } from 'react'

// Memoize expensive computations
const ExpensiveList = memo(function ExpensiveList({ items, filter }) {
  const filtered = useMemo(
    () => items.filter(item => item.name.includes(filter)),
    [items, filter]
  )
  
  return <div>{/* Render filtered items */}</div>
})

// Memoize callbacks
function Parent() {
  const handleClick = useCallback((id: string) => {
    // Handle click
  }, [])
  
  return <Child onClick={handleClick} />
}
```

## Common Patterns

### Loading States

```tsx
function UserProfile({ userId }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetchUser(userId).then(data => {
      setUser(data)
      setLoading(false)
    })
  }, [userId])
  
  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600" />
      </div>
    )
  }
  
  return <div>{/* User content */}</div>
}
```

### Error Boundaries

```tsx
// error.tsx (Next.js 13+ App Router)
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error
  reset: () => void
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      <h2 className="text-2xl font-bold">Something went wrong!</h2>
      <button
        onClick={reset}
        className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Try again
      </button>
    </div>
  )
}
```

### Form Handling

```tsx
'use client'

function ContactForm() {
  const [formState, setFormState] = useState({ name: '', email: '', message: '' })
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    
    // Validate
    const newErrors = {}
    if (!formState.name) newErrors.name = 'Name is required'
    if (!formState.email) newErrors.email = 'Email is required'
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      setSubmitting(false)
      return
    }
    
    // Submit
    await submitForm(formState)
    setSubmitting(false)
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="name" className="block text-sm font-medium">
          Name
        </label>
        <input
          id="name"
          type="text"
          value={formState.name}
          onChange={(e) => setFormState({ ...formState, name: e.target.value })}
          className="mt-1 w-full rounded-md border px-3 py-2"
          aria-invalid={errors.name ? 'true' : 'false'}
        />
        {errors.name && (
          <p className="mt-1 text-sm text-red-600">{errors.name}</p>
        )}
      </div>
      
      <button
        type="submit"
        disabled={submitting}
        className="w-full rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {submitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  )
}
```

## File Organization

**Keep files small**: Aim for 100-200 lines per file. Split larger components.

**Colocate related code**: Keep component, styles, and tests together when possible.

**Clear naming**: Use descriptive names that indicate purpose. `UserProfileCard` over `Card`.

**Consistent exports**: Use named exports for components, default for pages.

## Quality Checklist

Before considering a component complete:

- [ ] Responsive across all breakpoints (mobile, tablet, desktop)
- [ ] Accessible (keyboard navigation, ARIA labels, semantic HTML)
- [ ] TypeScript types defined for all props
- [ ] Loading and error states handled
- [ ] Performance optimized (memo, useMemo, dynamic imports where needed)
- [ ] Consistent with design system (spacing, colors, typography)
- [ ] Clean, readable code with clear variable names
- [ ] No console errors or warnings

## Common Utilities

### Class Name Helper

```ts
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### Custom Hooks

```tsx
// lib/hooks/use-media-query.ts
import { useState, useEffect } from 'react'

export function useMediaQuery(query: string) {
  const [matches, setMatches] = useState(false)
  
  useEffect(() => {
    const media = window.matchMedia(query)
    setMatches(media.matches)
    
    const listener = (e: MediaQueryListEvent) => setMatches(e.matches)
    media.addEventListener('change', listener)
    return () => media.removeEventListener('change', listener)
  }, [query])
  
  return matches
}

// Usage
const isMobile = useMediaQuery('(max-width: 768px)')
```

## Next Steps

When building a new feature:

1. **Plan component hierarchy** - Sketch out which components you need
2. **Build UI components first** - Create base components (buttons, inputs, cards)
3. **Compose layouts** - Assemble components into layouts
4. **Add interactivity** - Wire up state and event handlers
5. **Optimize** - Add loading states, error handling, performance optimizations
6. **Test responsive** - Verify all breakpoints
7. **Verify accessibility** - Check keyboard navigation and screen reader support
