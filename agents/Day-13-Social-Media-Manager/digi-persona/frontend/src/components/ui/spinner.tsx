import { cn } from "@/lib/utils";

interface SpinnerProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Spinner({ className, ...props }: SpinnerProps) {
  return (
    <div
      className={cn("animate-spin rounded-full border-2 border-current border-t-transparent", className)}
      {...props}
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
}
