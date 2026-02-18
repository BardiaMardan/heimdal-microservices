"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, AuthResponse, User } from "@/lib/definitions";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function login(formData: FormData) {
  const email = formData.get("email");
  const password = formData.get("password");

  const response = await fetch(`${API_URL}/auth/login/access-token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      username: email as string,
      password: password as string,
    }),
  });

  if (!response.ok) {
    return { error: "Invalid credentials" };
  }

  const data: AuthResponse = await response.json();

  const cookieStore = await cookies();
  cookieStore.set("session", data.access_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24 * 7, // 1 week
    path: "/",
  });

  redirect("/dashboard");
}

export async function logout() {
  const cookieStore = await cookies();
  cookieStore.delete("session");
  redirect("/login");
}

export async function register(formData: FormData) {
  const email = formData.get("email");
  const password = formData.get("password");
  // const name = formData.get('name'); // user model needs updating backend side for name first

  const response = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });

  if (!response.ok) {
    const errorData: ApiError = await response.json();

    if (errorData.error) {
      return { error: errorData.error.message };
    }

    if (errorData.detail) {
      if (typeof errorData.detail === "string") {
        return { error: errorData.detail };
      }

      if (Array.isArray(errorData.detail)) {
        return { error: errorData.detail.map((e) => e.msg).join(", ") };
      }
    }

    return { error: "Registration failed" };
  }

  return login(formData);
}
