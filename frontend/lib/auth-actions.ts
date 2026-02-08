"use server";

import { auth } from "@/lib/auth";
import { headers } from "next/headers";

/**
 * Sign up a new user with Better Auth (database-backed)
 *
 * @param name - User's full name
 * @param email - User's email address
 * @param password - User's password (will be hashed with bcrypt)
 * @returns Success status with userId or error message
 */
export async function signup(
  name: string,
  email: string,
  password: string
): Promise<{ success: boolean; userId?: string; error?: string }> {
  try {
    const result = await auth.api.signUpEmail({
      body: { name, email, password },
      headers: await headers(),
    });

    if (!result?.user) {
      return { success: false, error: "Signup failed" };
    }

    return {
      success: true,
      userId: result.user.id,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Signup failed",
    };
  }
}

/**
 * Sign in an existing user with Better Auth
 *
 * @param email - User's email address
 * @param password - User's password
 * @returns Success status with userId or error message
 */
export async function signin(
  email: string,
  password: string
): Promise<{ success: boolean; userId?: string; error?: string }> {
  try {
    const result = await auth.api.signInEmail({
      body: { email, password },
      headers: await headers(),
    });

    if (!result?.user) {
      return { success: false, error: "Invalid credentials" };
    }

    return {
      success: true,
      userId: result.user.id,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Login failed",
    };
  }
}

/**
 * Sign out current user
 */
export async function signout(): Promise<void> {
  await auth.api.signOut({
    headers: await headers(),
  });
}

/**
 * Get current session
 *
 * @returns User session with userId and email, or null if not authenticated
 */
export async function getSession(): Promise<{
  userId: string;
  email: string;
} | null> {
  try {
    const requestHeaders = await headers();

    const session = await auth.api.getSession({
      headers: requestHeaders,
    });

    if (!session?.user) {
      return null;
    }

    return {
      userId: session.user.id,
      email: session.user.email,
    };
  } catch (error) {
    return null;
  }
}
