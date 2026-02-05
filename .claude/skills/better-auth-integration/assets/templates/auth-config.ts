// lib/auth.ts - Better Auth Configuration Template
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = betterAuth({
  database: {
    provider: "postgres",
    url: process.env.DATABASE_URL!,
  },

  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },

  session: {
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24 * 7, // 7 days
    },
  },

  // JWT plugin for token generation
  plugins: [
    jwt({
      secret: process.env.BETTER_AUTH_SECRET!,
      expiresIn: "7d",
    })
  ],
})

export type Session = typeof auth.$Infer.Session
