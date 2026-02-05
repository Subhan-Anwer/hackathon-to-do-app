// lib/auth-client.ts - Client-side auth hook
import { createAuthClient } from "@better-auth/react"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
})

export const { useAuth } = authClient
