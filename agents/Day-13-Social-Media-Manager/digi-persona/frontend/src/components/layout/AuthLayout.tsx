import { ReactNode } from "react";
import { ThemeToggle } from "@/components/theme/theme-toggle";

interface AuthLayoutProps {
  children: ReactNode;
  title: string;
  description: string;
}

export function AuthLayout({ children, title, description }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>
      <div className="flex-1 flex flex-col sm:flex-row">
        {/* Left side - Brand/Logo */}
        <div className="hidden sm:flex sm:w-1/2 bg-primary/10 items-center justify-center">
          <div className="max-w-md p-8 text-center">
            <h1 className="text-4xl font-bold mb-4">Digi-Persona</h1>
            <p className="text-xl text-muted-foreground">
              Manage multiple virtual personas, generate content, and engage with your audience across platforms.
            </p>
            <div className="mt-8 grid grid-cols-3 gap-4">
              <div className="flex flex-col items-center p-4 rounded-lg bg-background/80">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary mb-2">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                  <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
                <span className="text-sm font-medium">Multiple Personas</span>
              </div>
              <div className="flex flex-col items-center p-4 rounded-lg bg-background/80">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary mb-2">
                  <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
                <span className="text-sm font-medium">AI Content</span>
              </div>
              <div className="flex flex-col items-center p-4 rounded-lg bg-background/80">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary mb-2">
                  <path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z" />
                </svg>
                <span className="text-sm font-medium">Social Media</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right side - Auth Form */}
        <div className="flex-1 flex items-center justify-center p-4 sm:p-8">
          <div className="w-full max-w-md space-y-6">
            <div className="text-center sm:text-left">
              <h2 className="text-3xl font-bold tracking-tight">{title}</h2>
              <p className="text-sm text-muted-foreground mt-2">{description}</p>
            </div>
            {children}
          </div>
        </div>
      </div>

      <footer className="py-6 border-t">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          &copy; {new Date().getFullYear()} Digi-Persona. All rights reserved.
        </div>
      </footer>
    </div>
  );
}
