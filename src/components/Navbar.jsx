import React from 'react';
import { LogIn, UserCircle, Calendar, LayoutGrid, Sparkles } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const Navbar = ({ activeView, setActiveView }) => {
  const navItems = [
    { id: 'login', label: 'Login', icon: LogIn },
    { id: 'profile', label: 'Profile', icon: UserCircle },
    { id: 'vault', label: 'Fit Vault', icon: LayoutGrid },
    { id: 'genie', label: 'Fit Genie', icon: Sparkles },
    { id: 'planner', label: 'Planner', icon: Calendar },
  ];

  return (
    <div className="fixed top-8 left-1/2 -translate-x-1/2 z-50">
      <nav className="glass-nav rounded-full px-4 py-3 flex items-center gap-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              className={cn(
                "relative flex items-center gap-2 px-4 py-2 rounded-full transition-smooth",
                isActive ? "text-primary bg-white/5" : "text-white/60 hover:text-white"
              )}
            >
              <Icon size={18} strokeWidth={isActive ? 2 : 1.5} />
              <span className="font-manrope text-sm font-medium">{item.label}</span>
              {isActive && (
                <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 bg-primary rounded-full glow-cyan" />
              )}
            </button>
          );
        })}
      </nav>
    </div>
  );
};

export default Navbar;
