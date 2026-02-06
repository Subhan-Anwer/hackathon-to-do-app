/**
 * Login Page
 *
 * Public route for user authentication.
 * Server component that imports the client-side LoginForm.
 *
 * Features:
 * - Redirect to /tasks if already authenticated (handled by middleware)
 * - Link to signup page for new users
 * - Centered, responsive layout
 *
 * Reference: specs/002-frontend-auth/spec.md (User Story 1, Scenario 2)
 */

import Link from "next/link";
import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">Todo App</h1>
          <p className="text-slate-600">Sign in to manage your tasks</p>
        </div>

        <LoginForm />

        <p className="text-center text-sm text-slate-600">
          Don&apos;t have an account?{" "}
          <Link
            href="/signup"
            className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
          >
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
