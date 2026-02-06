# Frontend - Next.js 16 Application

## Current Structure

```
frontend/
├── app/                    # Next.js App Router (v16.1.6)
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   ├── globals.css        # Global styles with Tailwind
│   └── favicon.ico
├── lib/
│   └── utils.ts           # Utility functions (cn helper)
├── components.json        # shadcn/ui configuration
├── next.config.ts         # Next.js configuration
├── package.json           # Dependencies
└── tsconfig.json          # TypeScript configuration
```

## Installed Dependencies

**Core:**
- `next@16.1.6` - React framework with App Router
- `react@19.2.3` / `react-dom@19.2.3` - React 19
- `typescript@5` - Type safety

**UI & Styling:**
- `tailwindcss@4` - Utility-first CSS framework
- `@tailwindcss/postcss@4` - PostCSS plugin
- `class-variance-authority` - CVA for component variants
- `clsx` + `tailwind-merge` - Conditional class merging
- `tw-animate-css` - Animation utilities

**shadcn/ui Configuration:**
- Style: `new-york`
- Icon library: `lucide-react@0.563.0`
- Base color: `neutral`
- CSS variables enabled
- Path aliases configured

**Development:**
- ESLint with Next.js config
- TypeScript strict mode

## Scripts

- `npm run dev` - Development server (localhost:3000)
- `npm run build` - Production build
- `npm start` - Production server
- `npm run lint` - Run ESLint

## Context7 MCP Integration

**CRITICAL: Always use Context7 MCP proactively** for documentation, code generation, and configuration without waiting for explicit requests.

**Automatic Usage Triggers:**
- Next.js 16 App Router patterns and best practices
- React 19 Server Components and Client Components
- Tailwind CSS utility classes and configuration
- shadcn/ui component installation and usage
- Better Auth JWT integration and configuration
- TypeScript types and interfaces for libraries
- API route handlers and middleware setup

**Common Frontend Queries:**
- Next.js App Router file conventions (layout.tsx, page.tsx, route.ts)
- React Server Component vs Client Component patterns
- shadcn/ui component props and customization
- Tailwind CSS class names and responsive design
- Better Auth client setup and authentication hooks
- Next.js API proxy configuration for backend communication
- TypeScript strict mode best practices

**When to Query:**
1. **Before creating components** - Verify Next.js 16 App Router conventions
2. **During UI implementation** - Look up shadcn/ui component APIs
3. **For styling** - Check Tailwind CSS utility classes and variants
4. **For auth flows** - Reference Better Auth documentation
5. **For API calls** - Verify fetch patterns with JWT token handling

**Benefits:**
- Ensures Next.js 16 App Router best practices
- Correct shadcn/ui component usage
- Up-to-date Tailwind CSS patterns
- Proper Better Auth JWT integration
- TypeScript type safety with library types

Use Context7 silently and proactively to deliver accurate, documentation-backed implementations.

## Notes

- App Router structure (not Pages Router)
- No components created yet (only lib/utils.ts)
- No authentication configured
- No API integration configured
- Ready for shadcn/ui component installation
