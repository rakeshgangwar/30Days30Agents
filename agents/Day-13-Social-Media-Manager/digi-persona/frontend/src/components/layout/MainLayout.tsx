import { ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { NavigationMenu, NavigationMenuContent, NavigationMenuItem, NavigationMenuLink, NavigationMenuList, NavigationMenuTrigger } from "@/components/ui/navigation-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { useAuthStore } from "@/store/authStore";
import { ThemeToggle } from "@/components/theme/theme-toggle";

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link to="/" className="font-bold text-xl">Digi-Persona</Link>
            <DesktopNav />
          </div>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <PersonaSelector />
            <UserMenu />
            <MobileMenuTrigger />
          </div>
        </div>
      </header>
      <main className="flex-1 container mx-auto px-4 py-6">
        {children}
      </main>
      <footer className="border-t py-6">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          &copy; {new Date().getFullYear()} Digi-Persona. All rights reserved.
        </div>
      </footer>
    </div>
  );
}

function DesktopNav() {
  return (
    <NavigationMenu className="hidden md:flex">
      <NavigationMenuList>
        <NavigationMenuItem>
          <NavigationMenuTrigger>Personas</NavigationMenuTrigger>
          <NavigationMenuContent>
            <ul className="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2 lg:w-[600px]">
              <li>
                <NavigationMenuLink asChild>
                  <Link to="/personas" className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div className="text-sm font-medium leading-none">Manage Personas</div>
                    <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                      Create, edit, and manage your virtual personas
                    </p>
                  </Link>
                </NavigationMenuLink>
              </li>
              <li>
                <NavigationMenuLink asChild>
                  <Link to="/personas/new" className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div className="text-sm font-medium leading-none">Create New Persona</div>
                    <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                      Set up a new virtual persona with custom attributes
                    </p>
                  </Link>
                </NavigationMenuLink>
              </li>
            </ul>
          </NavigationMenuContent>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <NavigationMenuTrigger>Content</NavigationMenuTrigger>
          <NavigationMenuContent>
            <ul className="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2 lg:w-[600px]">
              <li>
                <NavigationMenuLink asChild>
                  <Link to="/content" className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div className="text-sm font-medium leading-none">Content Dashboard</div>
                    <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                      Manage and monitor all your content
                    </p>
                  </Link>
                </NavigationMenuLink>
              </li>
              <li>
                <NavigationMenuLink asChild>
                  <Link to="/content/new" className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div className="text-sm font-medium leading-none">Create Content</div>
                    <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                      Generate new content with AI assistance
                    </p>
                  </Link>
                </NavigationMenuLink>
              </li>
              <li>
                <NavigationMenuLink asChild>
                  <Link to="/content/calendar" className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div className="text-sm font-medium leading-none">Content Calendar</div>
                    <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                      View your scheduled content
                    </p>
                  </Link>
                </NavigationMenuLink>
              </li>
              <li>
                <NavigationMenuLink asChild>
                  <Link to="/content/schedule" className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div className="text-sm font-medium leading-none">Schedule Content</div>
                    <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                      Schedule and generate content
                    </p>
                  </Link>
                </NavigationMenuLink>
              </li>
            </ul>
          </NavigationMenuContent>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <NavigationMenuTrigger>Platforms</NavigationMenuTrigger>
          <NavigationMenuContent>
            <ul className="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2 lg:w-[600px]">
              <li>
                <NavigationMenuLink asChild>
                  <Link to="/platforms" className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div className="text-sm font-medium leading-none">Platform Connections</div>
                    <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                      Manage your social media connections
                    </p>
                  </Link>
                </NavigationMenuLink>
              </li>
              <li>
                <NavigationMenuLink asChild>
                  <Link to="/interactions" className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div className="text-sm font-medium leading-none">Interactions</div>
                    <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                      Monitor and respond to social media interactions
                    </p>
                  </Link>
                </NavigationMenuLink>
              </li>
            </ul>
          </NavigationMenuContent>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <NavigationMenuTrigger>Analytics</NavigationMenuTrigger>
          <NavigationMenuContent>
            <ul className="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2 lg:w-[600px]">
              <li>
                <NavigationMenuLink asChild>
                  <Link to="/analytics" className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div className="text-sm font-medium leading-none">Performance Dashboard</div>
                    <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                      View performance metrics and analytics
                    </p>
                  </Link>
                </NavigationMenuLink>
              </li>
              <li>
                <NavigationMenuLink asChild>
                  <Link to="/analytics/reports" className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground">
                    <div className="text-sm font-medium leading-none">Reports</div>
                    <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                      Generate custom reports and insights
                    </p>
                  </Link>
                </NavigationMenuLink>
              </li>
            </ul>
          </NavigationMenuContent>
        </NavigationMenuItem>
      </NavigationMenuList>
    </NavigationMenu>
  );
}

function MobileMenuTrigger() {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline" size="icon" className="md:hidden">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-menu">
            <line x1="4" x2="20" y1="12" y2="12" />
            <line x1="4" x2="20" y1="6" y2="6" />
            <line x1="4" x2="20" y1="18" y2="18" />
          </svg>
          <span className="sr-only">Toggle menu</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="right">
        <nav className="flex flex-col gap-4 mt-8">
          <Link to="/personas" className="text-lg font-medium">Personas</Link>
          <Link to="/content" className="text-lg font-medium">Content</Link>
          <Link to="/content/calendar" className="text-lg font-medium">Content Calendar</Link>
          <Link to="/content/schedule" className="text-lg font-medium">Schedule Content</Link>
          <Link to="/platforms" className="text-lg font-medium">Platforms</Link>
          <Link to="/platforms/connect" className="text-lg font-medium">Connect Platform</Link>
          <Link to="/interactions" className="text-lg font-medium">Interactions</Link>
          <Link to="/analytics" className="text-lg font-medium">Analytics</Link>
          <Link to="/analytics/reports" className="text-lg font-medium">Analytics Reports</Link>
          <Link to="/settings" className="text-lg font-medium">Settings</Link>
        </nav>
      </SheetContent>
    </Sheet>
  );
}

function PersonaSelector() {
  // This would be populated from your state management
  const personas = [
    { id: 1, name: "Tech Expert", avatar: "/avatars/tech.png" },
    { id: 2, name: "Finance Guru", avatar: "/avatars/finance.png" },
    { id: 3, name: "Health Coach", avatar: "/avatars/health.png" },
  ];

  const activePersona = personas[0];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="flex items-center gap-2">
          <Avatar className="h-6 w-6">
            <AvatarImage src={activePersona.avatar} alt={activePersona.name} />
            <AvatarFallback>{activePersona.name.substring(0, 2)}</AvatarFallback>
          </Avatar>
          <span className="hidden sm:inline">{activePersona.name}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>Switch Persona</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {personas.map((persona) => (
          <DropdownMenuItem key={persona.id} className="cursor-pointer">
            <Avatar className="h-6 w-6 mr-2">
              <AvatarImage src={persona.avatar} alt={persona.name} />
              <AvatarFallback>{persona.name.substring(0, 2)}</AvatarFallback>
            </Avatar>
            {persona.name}
          </DropdownMenuItem>
        ))}
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link to="/personas/new" className="cursor-pointer">Create New Persona</Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function UserMenu() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate("/auth/login");
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="rounded-full">
          <Avatar>
            <AvatarImage src={user?.avatar || "/avatars/user.png"} alt={user?.name || "User"} />
            <AvatarFallback>{user?.name?.substring(0, 1) || "U"}</AvatarFallback>
          </Avatar>
          <span className="sr-only">User menu</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>{user?.name || "My Account"}</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link to="/settings" className="cursor-pointer">Settings</Link>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <Link to="/help" className="cursor-pointer">Help</Link>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleLogout} className="cursor-pointer text-destructive focus:text-destructive">
          Logout
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
