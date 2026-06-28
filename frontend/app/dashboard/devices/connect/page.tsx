"use client";

import { useState } from "react";
import Link from "next/link";
import { z } from "zod";
import { claimDevice } from "@/actions/devices";
import { Button } from "@/components/ui/button";
import { FormError } from "@/components/ui/form-error";
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSlot,
} from "@/components/ui/input-otp";

const codeSchema = z
  .string()
  .regex(/^\d{6}$/, "Enter the 6-digit code from your device");

export default function ConnectDevicePage() {
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | undefined>("");
  const [isLoading, setIsLoading] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    const parsed = codeSchema.safeParse(code);
    if (!parsed.success) {
      setError(parsed.error.issues[0].message);
      return;
    }

    setIsLoading(true);
    // On success the server action redirects (throws) and this never returns.
    const response = await claimDevice(code);
    if (response?.error) {
      setError(response.error);
      setIsLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-md space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
          Connect a device
        </h1>
        <p className="mt-2 text-sm text-white/80">
          Enter the 6-digit code shown on your device to claim it to your
          account.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-8">
        <div className="flex flex-col items-center gap-3">
          <InputOTP
            maxLength={6}
            value={code}
            onChange={setCode}
            disabled={isLoading}
            containerClassName="justify-center"
          >
            <InputOTPGroup>
              <InputOTPSlot index={0} />
              <InputOTPSlot index={1} />
              <InputOTPSlot index={2} />
              <InputOTPSlot index={3} />
              <InputOTPSlot index={4} />
              <InputOTPSlot index={5} />
            </InputOTPGroup>
          </InputOTP>
          <p className="text-xs text-white/40">
            The code expires 10 minutes after the device powers on.
          </p>
        </div>

        <FormError message={error} />

        <div className="flex flex-col gap-3">
          <Button
            type="submit"
            className="w-full"
            isLoading={isLoading}
            disabled={code.length !== 6}
          >
            Claim device
          </Button>
          <Button asChild variant="ghost" className="w-full">
            <Link href="/dashboard/devices">Cancel</Link>
          </Button>
        </div>
      </form>
    </div>
  );
}
