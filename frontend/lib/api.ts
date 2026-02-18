import { cookies } from "next/headers";
import { redirect } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function fetchApi<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const cookieStore = await cookies();
  const token = cookieStore.get("session")?.value;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    redirect("/login");
  }

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Something went wrong" }));
    throw new Error(error.detail || "API request failed");
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}
