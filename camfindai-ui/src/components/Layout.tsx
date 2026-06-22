import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Camera, Users, Bell, Settings, Activity, LogOut, Video } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import clsx from 'clsx';

const NAV_ITEMS = [
  { name: 'Live View', path: '/', icon: Camera },
  { name: 'Cameras', path: '/cameras', icon: Video },
  { name: 'Identities', path: '/identities', icon: Users },
  { name: 'Timeline', path: '/timeline', icon: Activity },
  { name: 'Alerts', path: '/alerts', icon: Bell },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, setUser } = useAuth();

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    navigate('/login');
  };

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <aside className="w-64 glass-panel border-r flex flex-col hidden md:flex">
        <div className="p-6">
          <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-br from-white to-white/50 bg-clip-text text-transparent">
            CamFindAI
          </h1>
          <p className="text-xs text-muted-foreground mt-1">Multi-Camera ReID System</p>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path || 
                            (item.path !== '/' && location.pathname.startsWith(item.path));
            
            return (
              <Link
                key={item.name}
                to={item.path}
                className={clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200',
                  isActive 
                    ? 'bg-white/10 text-white shadow-[0_0_15px_rgba(255,255,255,0.1)]' 
                    : 'text-muted-foreground hover:bg-white/5 hover:text-white'
                )}
              >
                <Icon className={clsx('w-4 h-4', isActive ? 'text-white' : 'text-muted-foreground')} />
                {item.name}
              </Link>
            );
          })}
        </nav>
        
        <div className="p-4 border-t border-white/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
                <span className="text-xs font-bold uppercase">{user?.role ? user.role.substring(0, 2) : 'OP'}</span>
              </div>
              <div>
                <p className="text-sm font-medium capitalize">{user?.role || 'Operator'}</p>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)] animate-pulse" />
                  <p className="text-xs text-muted-foreground">System Online</p>
                </div>
              </div>
            </div>
            <button 
              onClick={handleLogout}
              className="p-2 text-muted-foreground hover:text-white hover:bg-white/10 rounded-lg transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto relative">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-white/5 via-background to-background pointer-events-none" />
        <div className="relative p-8 h-full">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
