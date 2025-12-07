import { useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Home,
  TrendingUp,
  Brain,
  PieChart,
  ShieldAlert,
  Newspaper,
  Bell,
  MessageSquare,
  Settings,
  LogOut,
  Menu,
  Sparkles,
} from 'lucide-react';
import { NavLink } from '@/components/NavLink';
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
  useSidebar,
} from '@/components/ui/sidebar';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/ThemeToggle';
import { supabase } from '@/integrations/supabase/client';
import { useAuthStore } from '@/stores/authStore';
import { toast } from 'sonner';

const navItems = [
  { title: 'Dashboard', url: '/dashboard', icon: Home },
  { title: 'Market Data', url: '/market', icon: TrendingUp },
  { title: 'Predictions', url: '/predictions', icon: Brain },
  { title: 'Portfolio', url: '/portfolio', icon: PieChart },
  { title: 'Risk Analysis', url: '/risk', icon: ShieldAlert },
  { title: 'News', url: '/news', icon: Newspaper },
  { title: 'Alerts', url: '/alerts', icon: Bell },
  { title: 'AI Chat', url: '/chat', icon: MessageSquare },
  { title: 'Settings', url: '/settings', icon: Settings },
];

function DashboardSidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const currentPath = location.pathname;

  const isActive = (path: string) => currentPath === path;

  const handleLogout = async () => {
    const { error } = await supabase.auth.signOut();
    if (error) {
      toast.error('Failed to logout');
    } else {
      toast.success('Logged out successfully');
      navigate('/');
    }
  };

  return (
    <Sidebar>
      <SidebarContent className="glass-strong border-r border-border/50">
        {/* Logo */}
        <div className="p-4 flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-secondary glow-primary flex items-center justify-center">
            <Sparkles className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="text-lg font-bold gradient-text">TradeAI</span>
        </div>

        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.url}
                      end
                      className="hover:bg-muted/50 transition-smooth"
                      activeClassName="bg-primary/10 text-primary font-medium border-l-2 border-primary"
                    >
                      <item.icon className="h-4 w-4" />
                      <span>{item.title}</span>
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <div className="mt-auto p-4">
          <Button
            onClick={handleLogout}
            variant="ghost"
            className="w-full justify-start hover:bg-destructive/10 hover:text-destructive transition-smooth"
          >
            <LogOut className="h-4 w-4" />
            <span className="ml-2">Logout</span>
          </Button>
        </div>
      </SidebarContent>
    </Sidebar>
  );
}

export default function DashboardLayout() {
  const navigate = useNavigate();
  const { session, setSession } = useAuthStore();

  useEffect(() => {
    // Check initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (!session) {
        navigate('/login');
      }
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event, session) => {
      setSession(session);
      if (!session) {
        navigate('/login');
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate, setSession]);

  if (!session) {
    return null;
  }

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full">
        <DashboardSidebar />

        <div className="flex-1 flex flex-col">
          {/* Header */}
          <header className="h-16 glass-strong border-b border-border/50 flex items-center justify-between px-4 sticky top-0 z-40">
            <SidebarTrigger>
              <Button variant="ghost" size="icon" className="hover:bg-muted transition-smooth">
                <Menu className="h-5 w-5" />
              </Button>
            </SidebarTrigger>
            <ThemeToggle />
          </header>

          {/* Main content */}
          <main className="flex-1 overflow-auto">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
            >
              <Outlet />
            </motion.div>
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
