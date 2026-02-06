/**
 * Signup Page
 *
 * Public route for user registration.
 * Server component that imports the client-side SignupForm.
 *
 * Features:
 * - Redirect to /tasks if already authenticated (handled by middleware)
 * - Link to login page for existing users
 * - Centered, responsive layout
 *
 * Reference: specs/002-frontend-auth/spec.md (User Story 1, Scenario 3)
 */

import Link from "next/link";
import { SignupForm } from "@/components/auth/signup-form";

export default function SignupPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">Todo App</h1>
          <p className="text-slate-600">Create an account to get started</p>
        </div>

        <SignupForm />

        <p className="text-center text-sm text-slate-600">
          Already have an account?{" "}
          <Link
            href="/login"
            className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
          >
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
