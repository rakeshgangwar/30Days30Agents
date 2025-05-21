import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { MainLayout } from "@/components/layout/MainLayout";
import { Dashboard } from "@/pages/Dashboard";

// Auth pages
import { Login } from "@/pages/auth/Login";
import { Register } from "@/pages/auth/Register";
import { ForgotPassword } from "@/pages/auth/ForgotPassword";
import { AuthGuard, GuestGuard } from "@/components/auth/AuthGuard";

// Persona pages
import { PersonaList } from "@/pages/personas/PersonaList";
import { PersonaCreate } from "@/pages/personas/PersonaCreate";
import { PersonaDetail } from "@/pages/personas/PersonaDetail";
import { PersonaEdit } from "@/pages/personas/PersonaEdit";

// Content pages
import { ContentList } from "@/pages/content/ContentList";
import { ContentCreate } from "@/pages/content/ContentCreate";
import { ContentCalendar } from "@/pages/content/ContentCalendar";
import { ContentSchedule } from "@/pages/content/ContentSchedule";
import { ContentDetail } from "@/pages/content/ContentDetail";
import { ContentEdit } from "@/pages/content/ContentEdit";

// Platform pages
import { PlatformList } from "@/pages/platforms/PlatformList";
import { PlatformConnect } from "@/pages/platforms/PlatformConnect";

// Interaction pages
import { InteractionList } from "@/pages/interactions/InteractionList";

// Analytics pages
import { AnalyticsDashboard } from "@/pages/analytics/AnalyticsDashboard";
import { AnalyticsReports } from "@/pages/analytics/AnalyticsReports";

// Settings pages
import { Settings } from "@/pages/settings/Settings";

// Create routes using the MainLayout as the root layout
const router = createBrowserRouter([
  // Auth routes (public)
  {
    path: "/auth/login",
    element: <GuestGuard><Login /></GuestGuard>,
  },
  {
    path: "/auth/register",
    element: <GuestGuard><Register /></GuestGuard>,
  },
  {
    path: "/auth/forgot-password",
    element: <GuestGuard><ForgotPassword /></GuestGuard>,
  },

  // Protected routes
  {
    path: "/",
    element: <AuthGuard><MainLayout><Dashboard /></MainLayout></AuthGuard>,
  },
  // Persona routes
  {
    path: "/personas",
    element: <AuthGuard><MainLayout><PersonaList /></MainLayout></AuthGuard>,
  },
  {
    path: "/personas/new",
    element: <AuthGuard><MainLayout><PersonaCreate /></MainLayout></AuthGuard>,
  },
  {
    path: "/personas/:id",
    element: <AuthGuard><MainLayout><PersonaDetail /></MainLayout></AuthGuard>,
  },
  {
    path: "/personas/:id/edit",
    element: <AuthGuard><MainLayout><PersonaEdit /></MainLayout></AuthGuard>,
  },
  // Content routes
  {
    path: "/content",
    element: <AuthGuard><MainLayout><ContentList /></MainLayout></AuthGuard>,
  },
  {
    path: "/content/new",
    element: <AuthGuard><MainLayout><ContentCreate /></MainLayout></AuthGuard>,
  },
  {
    path: "/content/calendar",
    element: <AuthGuard><MainLayout><ContentCalendar /></MainLayout></AuthGuard>,
  },
  {
    path: "/content/schedule",
    element: <AuthGuard><MainLayout><ContentSchedule /></MainLayout></AuthGuard>,
  },
  {
    path: "/content/:id",
    element: <AuthGuard><MainLayout><ContentDetail /></MainLayout></AuthGuard>,
  },
  {
    path: "/content/:id/edit",
    element: <AuthGuard><MainLayout><ContentEdit /></MainLayout></AuthGuard>,
  },
  {
    path: "/content/:id/schedule",
    element: <AuthGuard><MainLayout><ContentSchedule /></MainLayout></AuthGuard>, // Re-use schedule page for specific content
  },
  // Platform routes
  {
    path: "/platforms",
    element: <AuthGuard><MainLayout><PlatformList /></MainLayout></AuthGuard>,
  },
  {
    path: "/platforms/connect",
    element: <AuthGuard><MainLayout><PlatformConnect /></MainLayout></AuthGuard>,
  },
  // Interaction routes
  {
    path: "/interactions",
    element: <AuthGuard><MainLayout><InteractionList /></MainLayout></AuthGuard>,
  },
  // Analytics routes
  {
    path: "/analytics",
    element: <AuthGuard><MainLayout><AnalyticsDashboard /></MainLayout></AuthGuard>,
  },
  {
    path: "/analytics/reports",
    element: <AuthGuard><MainLayout><AnalyticsReports /></MainLayout></AuthGuard>,
  },
  // Settings routes
  {
    path: "/settings",
    element: <AuthGuard><MainLayout><Settings /></MainLayout></AuthGuard>,
  },
  // Fallback route - redirect to login
  {
    path: "*",
    element: <GuestGuard><Login /></GuestGuard>,
  },
]);

export function AppRoutes() {
  return <RouterProvider router={router} />;
}
