import { useState } from "react";
import { Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { useAuthStore } from "@/store/authStore";

interface ForgotPasswordFormData {
  email: string;
}

export function ForgotPassword() {
  const { resetPassword, error, isLoading, clearError } = useAuthStore();
  const [isSubmitted, setIsSubmitted] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<ForgotPasswordFormData>({
    defaultValues: {
      email: ""
    }
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    try {
      await resetPassword(data.email);
      setIsSubmitted(true);
      toast.success("Password reset instructions sent to your email");
    } catch (error) {
      // Error is handled by the store
    }
  };

  // Clear any previous errors when component mounts
  useState(() => {
    clearError();
  }, []);

  if (isSubmitted) {
    return (
      <AuthLayout
        title="Check your email"
        description="We've sent you a password reset link"
      >
        <div className="space-y-6">
          <div className="flex justify-center">
            <div className="rounded-full bg-primary/10 p-6">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                <rect width="20" height="16" x="2" y="4" rx="2" />
                <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
              </svg>
            </div>
          </div>
          <div className="text-center">
            <p className="text-sm text-muted-foreground">
              We've sent a password reset link to your email address. Please check your inbox and follow the instructions to reset your password.
            </p>
          </div>
          <div className="flex flex-col gap-2">
            <Button asChild>
              <Link to="/auth/login">Back to login</Link>
            </Button>
            <Button variant="outline" onClick={() => setIsSubmitted(false)}>
              Try another email
            </Button>
          </div>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Forgot password"
      description="Enter your email to reset your password"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="name@example.com"
            {...register("email", {
              required: "Email is required",
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: "Invalid email address"
              }
            })}
            disabled={isLoading}
          />
          {errors.email && (
            <p className="text-sm text-destructive">{errors.email.message}</p>
          )}
        </div>

        {error && (
          <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
            {error}
          </div>
        )}

        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? "Sending..." : "Send reset link"}
        </Button>

        <div className="text-center text-sm">
          Remember your password?{" "}
          <Link to="/auth/login" className="text-primary hover:underline">
            Back to login
          </Link>
        </div>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-background px-2 text-muted-foreground">
              Demo Accounts
            </span>
          </div>
        </div>

        <div className="rounded-md border p-3">
          <div className="text-sm">
            <p><strong>Email:</strong> john@example.com</p>
            <p><strong>Password:</strong> password123</p>
          </div>
        </div>
      </form>
    </AuthLayout>
  );
}
