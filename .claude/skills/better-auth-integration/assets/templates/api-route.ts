// app/api/auth/[...all]/route.ts - Better Auth API handler
import { auth } from "@/lib/auth"

export const { GET, POST } = auth.handler
