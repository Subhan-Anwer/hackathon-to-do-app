/**
 * Authentication Hook
 *
 * Provides authentication state and methods for client components.
 * Uses server actions for auth operations to maintain httpOnly cookie security.
 *
 * Reference: specs/002-frontend-auth/spec.md (FR-016)
 */

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getSession, signout } from "@/lib/auth-actions";

interface AuthUser {
  userId: string;
  email: string;
}

export function useAuth() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Load session on mount
    getSession()
      .then((session) => {
        setUser(session);
        setLoading(false);
      })
      .catch(() => {
        setUser(null);
        setLoading(false);
      });
  }, []);

  const logout = async () => {
    await signout();
    setUser(null);
    router.push("/login");
  };

  return {
    user,
    isAuthenticated: !!user,
    loading,
    logout,
  };
}
