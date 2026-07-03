import { InputHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(
          "h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-900",
          "placeholder:text-slate-400 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200",
          "disabled:bg-slate-50 disabled:text-slate-400",
          className
        )}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

export const Textarea = forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => {
  return (
    <textarea
      ref={ref}
      className={cn(
        "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900",
        "placeholder:text-slate-400 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200",
        className
      )}
      {...props}
    />
  );
});
Textarea.displayName = "Textarea";
