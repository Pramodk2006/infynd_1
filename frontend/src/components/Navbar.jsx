import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Database, PlusCircle, Layers } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path ? 'bg-blue-700' : '';
  };

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2 hover:opacity-80">
            <Database size={28} />
            <span className="text-xl font-bold">B2B Data Fusion</span>
          </Link>

          <div className="flex space-x-1">
            <Link
              to="/"
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition ${isActive('/')} hover:bg-blue-700`}
            >
              <Layers size={18} />
              <span>Dashboard</span>
            </Link>

            <Link
              to="/extract/new"
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition ${isActive('/extract/new')} hover:bg-blue-700`}
            >
              <PlusCircle size={18} />
              <span>New Extraction</span>
            </Link>

            <Link
              to="/extract/batch"
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition ${isActive('/extract/batch')} hover:bg-blue-700`}
            >
              <Layers size={18} />
              <span>Batch Extract</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
