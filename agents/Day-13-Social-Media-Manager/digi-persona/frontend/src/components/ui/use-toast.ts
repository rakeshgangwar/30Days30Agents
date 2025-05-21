// Real toast implementation using sonner
import { toast as sonnerToast } from "sonner";

type ToastProps = {
  title?: string;
  description?: string;
  variant?: "default" | "destructive";
};

export function useToast() {
  const toast = (props: ToastProps) => {
    const { title, description, variant } = props;

    // Map our variant to sonner's type
    const type = variant === "destructive" ? "error" : "default";

    // Use sonner's toast function
    return sonnerToast[type](title, {
      description,
      id: Date.now().toString(),
    });
  };

  return {
    toast,
    // These are kept for API compatibility but not used with sonner
    toasts: [],
    dismiss: (id: number) => sonnerToast.dismiss(id.toString()),
  };
}
