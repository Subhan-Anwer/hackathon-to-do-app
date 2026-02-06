/**
 * Header Component
 *
 * Application header with user information and logout functionality.
 * Client component that uses the useAuth hook for session state.
 *
 * Features:
 * - Display user email
 * - Logout button with loading state
 * - Responsive layout
 * - Clear session and redirect on logout
 *
 * Reference: specs/002-frontend-auth/spec.md (FR-016, SC-010)
 */

"use client";

import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";

export function Header() {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <header className="bg-white border-b border-slate-200 shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo/Title */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <svg
                className="w-5 h-5 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
            </div>
            <h1 className="text-xl font-bold text-slate-900">My Tasks</h1>
          </div>

          {/* User info and logout */}
          <div className="flex items-center gap-4">
            {user && (
              <>
                <div className="hidden sm:flex flex-col items-end">
                  <span className="text-sm font-medium text-slate-700">
                    {user.email}
                  </span>
                  <span className="text-xs text-slate-500">
                    ID: {user.userId.substring(0, 8)}...
                  </span>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLogout}
                  className="text-slate-700 hover:text-slate-900 hover:bg-slate-100"
                >
                  <svg
                    className="w-4 h-4 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                    />
                  </svg>
                  Logout
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
