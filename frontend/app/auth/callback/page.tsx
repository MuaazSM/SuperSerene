"use client"

import { Suspense, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"

function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const payload = token.split(".")[1]
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/")
    const json = atob(normalized)
    return JSON.parse(json)
  } catch (error) {
    return null
  }
}

function AuthCallbackHandler() {
  const searchParams = useSearchParams()
  const router = useRouter()

  useEffect(() => {
    const token = searchParams.get("token")
    if (!token) {
      router.replace("/login?error=oauth_missing_token")
      return
    }

    const payload = decodeJwtPayload(token)
    if (!payload) {
      router.replace("/login?error=oauth_invalid_token")
      return
    }

    const userId = (payload["user_id"] as string) || (payload["sub"] as string) || ""
    const email = (payload["email"] as string) || ""
    const name = (payload["name"] as string) || ""

    if (typeof window !== "undefined") {
      localStorage.setItem("auth_token", token)
      if (userId) localStorage.setItem("user_id", userId)
      if (email) localStorage.setItem("user_email", email)
      if (name) localStorage.setItem("user_name", name)
    }

    router.replace("/dashboard")
  }, [router, searchParams])

  return (
    <div className="flex h-screen items-center justify-center text-center">
      <p className="text-lg text-muted-foreground">Completing sign-in with Google...</p>
    </div>
  )
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={<div className="flex h-screen items-center justify-center text-center"><p className="text-lg text-muted-foreground">Completing sign-in with Google...</p></div>}>
      <AuthCallbackHandler />
    </Suspense>
  )
}
