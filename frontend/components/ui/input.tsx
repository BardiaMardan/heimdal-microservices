import * as React from "react";

import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, label, error, ...props }, ref) => {
    return (
      <div className="w-full space-y-2">
        {label && (
          <label className="text-sm font-medium leading-none text-white">
            {label}
          </label>
        )}
        <input
          type={type}
          className={cn(
            "flex h-10 w-full border border-white/10 bg-black px-3 py-2 text-sm text-white placeholder:text-white/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/20 focus-visible:ring-offset-2 focus-visible:ring-offset-black focus-visible:border-white/20 transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-white/30 focus-visible:ring-white/30",
            className,
          )}
          ref={ref}
          {...props}
        />
        {error && (
          <p className="text-[0.8rem] font-medium text-white">{error}</p>
        )}
      </div>
    );
  },
);
Input.displayName = "Input";

export { Input };
