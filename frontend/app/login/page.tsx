"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { z } from "zod";
import { login } from "@/actions/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FormError } from "@/components/ui/form-error";

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1, "Password is required"),
});

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | undefined>("");
  const [isLoading, setIsLoading] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setError("");

    const formData = new FormData(event.currentTarget);
    const data = Object.fromEntries(formData.entries());

    const result = loginSchema.safeParse(data);

    if (!result.success) {
      setError(result.error.issues[0].message);
      setIsLoading(false);
      return;
    }

    const response = await login(formData);

    if (response?.error) {
      setError(response.error);
      setIsLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-black py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-white">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-white">
            Or{" "}
            <Link
              href="/register"
              className="font-medium text-white underline"
            >
              create a new account
            </Link>
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={onSubmit}>
          <div className="space-y-4">
            <Input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              placeholder="Email address"
              label="Email"
            />
            <Input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              placeholder="Password"
              label="Password"
            />
          </div>

          <FormError message={error} />

          <Button type="submit" className="w-full" isLoading={isLoading}>
            Sign in
          </Button>
        </form>
      </div>
    </div>
  );
}
