"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { StandardResponse, AuthResponse } from "@/lib/definitions";

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

  const result: StandardResponse<AuthResponse> = await response.json();

  if (!result.status) {
    return { error: result.message };
  }

  const cookieStore = await cookies();
  cookieStore.set("session", result.data!.access_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24 * 7,
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

  const result: StandardResponse = await response.json();

  if (!result.status) {
    return { error: result.message };
  }

  return login(formData);
}
