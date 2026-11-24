import { Link, useNavigate } from 'react-router-dom';
import { BrainCircuit, LogOut, User as UserIcon } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="bg-slate-950/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center gap-2">
              <BrainCircuit className="h-8 w-8 text-primary-500" />
              <span className="font-bold text-xl text-white tracking-tight">HireMind</span>
            </Link>
          </div>
          <nav className="hidden md:flex space-x-8">
            <Link to="/" className="text-slate-300 hover:text-primary-400 font-medium transition-colors">Home</Link>
            {user && (
              <>
                <Link to="/dashboard" className="text-slate-300 hover:text-primary-400 font-medium transition-colors">Dashboard</Link>
                <Link to="/resume" className="text-slate-300 hover:text-primary-400 font-medium transition-colors">Resume</Link>
                <Link to="/interview" className="text-slate-300 hover:text-primary-400 font-medium transition-colors">Interview</Link>
                <Link to="/results" className="text-slate-300 hover:text-primary-400 font-medium transition-colors">Readiness</Link>
              </>
            )}
          </nav>
          <div className="flex items-center space-x-4">
            {user ? (
              <div className="flex items-center gap-4">
                <Link to="/profile" className="flex items-center gap-2 text-slate-300 hover:text-white transition-colors" title="My Profile">
                  <div className="bg-slate-800 p-1.5 rounded-full border border-slate-700">
                    <UserIcon className="h-4 w-4 text-primary-400" />
                  </div>
                  <span className="text-sm font-medium hidden sm:block">{user.name}</span>
                </Link>
                <button 
                  onClick={handleLogout}
                  className="text-slate-400 hover:text-red-400 p-2 transition-colors"
                  title="Logout"
                >
                  <LogOut className="h-5 w-5" />
                </button>
              </div>
            ) : (
              <>
                <Link to="/login" className="text-slate-300 hover:text-white font-medium transition-colors">
                  Log in
                </Link>
                <Link to="/register" className="bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg font-medium transition-colors shadow-sm">
                  Sign up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
