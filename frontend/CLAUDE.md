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

## Notes

- App Router structure (not Pages Router)
- No components created yet (only lib/utils.ts)
- No authentication configured
- No API integration configured
- Ready for shadcn/ui component installation
