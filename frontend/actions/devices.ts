"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";
import { StandardResponse, Device } from "@/lib/definitions";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function claimDevice(claimCode: string) {
  const cookieStore = await cookies();
  const token = cookieStore.get("session")?.value;

  if (!token) {
    redirect("/login");
  }

  const response = await fetch(`${API_URL}/devices/claim`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ claim_code: claimCode }),
  });

  const result: StandardResponse<Device> = await response
    .json()
    .catch(() => ({
      status: false,
      code: response.status,
      message: "Something went wrong",
      data: null,
    }));

  if (!result.status) {
    return { error: result.message };
  }

  revalidatePath("/dashboard/devices");
  redirect("/dashboard/devices");
}
