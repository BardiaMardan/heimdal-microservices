import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { StandardResponse } from "@/lib/definitions";

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

  const result: StandardResponse<T> = await response
    .json()
    .catch(() => ({
      status: false,
      code: response.status,
      message: "Something went wrong",
      data: null,
    }));

  if (!response.ok || !result.status) {
    throw new Error(result.message || "API request failed");
  }

  return result.data as T;
}
