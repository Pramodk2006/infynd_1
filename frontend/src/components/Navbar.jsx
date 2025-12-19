import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Database, PlusCircle, Layers, FileText, BarChart3 } from 'lucide-react';
import ThemeToggle from './ThemeToggle';

const Navbar = () => {
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: Layers },
    { path: '/summaries', label: 'Summaries', icon: FileText },
    { path: '/extract', label: 'New Extraction', icon: PlusCircle },
    { path: '/batch', label: 'Batch Extract', icon: Database },
  ];

  const isActive = (path) => {
    return location.pathname === path
      ? 'bg-primary-600 text-white shadow-md'
      : 'text-slate-300 hover:bg-primary-800 hover:text-white';
  };

  return (
    <nav className="bg-infynd-dark border-b border-primary-800 sticky top-0 z-50 transition-colors duration-300">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-18 py-3">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="bg-primary-500 p-2 rounded-lg shadow-lg group-hover:bg-primary-400 transition-colors duration-300">
              <BarChart3 size={24} className="text-white" />
            </div>
            <span className="text-xl font-bold text-white tracking-tight group-hover:opacity-90 transition-opacity">
              InFynd <span className="font-light text-primary-400">2.0</span>
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-2">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ease-in-out ${isActive(item.path)}`}
              >
                <item.icon size={18} />
                <span>{item.label}</span>
              </Link>
            ))}
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-4">
            <ThemeToggle />
            <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center text-white font-bold shadow-md cursor-pointer hover:bg-primary-500 transition-colors">
              U
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
