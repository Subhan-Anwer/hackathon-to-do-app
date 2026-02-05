// app/api/proxy/[...path]/route.ts - API Proxy for httpOnly Cookie Forwarding
import { NextRequest, NextResponse } from "next/server"
import { cookies } from "next/headers"

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000"

async function handleRequest(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
  method: string
) {
  const { path } = await params
  const cookieStore = await cookies()

  // Read httpOnly cookie (only works server-side)
  const token = cookieStore.get("better-auth.session_token")?.value

  if (!token) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 })
  }

  // Build target URL
  const targetUrl = `${BACKEND_URL}/${path.join("/")}`
  const url = new URL(targetUrl)

  // Forward query parameters
  request.nextUrl.searchParams.forEach((value, key) => {
    url.searchParams.append(key, value)
  })

  // Prepare request options
  const options: RequestInit = {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  }

  // Include body for POST/PUT/PATCH
  if (["POST", "PUT", "PATCH"].includes(method)) {
    try {
      const body = await request.json()
      options.body = JSON.stringify(body)
    } catch {
      // No body or invalid JSON
    }
  }

  // Forward request to backend
  try {
    const response = await fetch(url.toString(), options)
    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    return NextResponse.json(
      { error: "Backend request failed" },
      { status: 500 }
    )
  }
}

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return handleRequest(request, context, "GET")
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return handleRequest(request, context, "POST")
}

export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return handleRequest(request, context, "PUT")
}

export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return handleRequest(request, context, "DELETE")
}

export async function PATCH(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return handleRequest(request, context, "PATCH")
}
