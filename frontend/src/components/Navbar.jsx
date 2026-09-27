import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useAnalysis } from '../context/AnalysisContext';
import { Activity, User as UserIcon, LogOut, FileClock, MessageSquare } from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useAuth();
  const { clearAnalysis } = useAnalysis();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    clearAnalysis();
    navigate('/');
  };

  return (
    <nav className="bg-white shadow-sm border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to={user ? "/dashboard" : "/"} className="flex items-center gap-2">
              <Activity className="h-8 w-8 text-teal-600" />
              <span className="font-bold text-xl text-slate-800 tracking-tight">AI MedCheck</span>
            </Link>
          </div>
          <div className="flex items-center gap-4">
            {user ? (
              <>
                <Link to="/symptom-checker" className="text-sm font-medium text-slate-600 hover:text-teal-600">Check Symptoms</Link>
                <Link to="/pain-assessment" className="text-sm font-medium text-slate-600 hover:text-teal-600">Pain Assessment</Link>
                <Link to="/menstruation" className="text-sm font-medium text-slate-600 hover:text-teal-600">Menstruation</Link>
                <Link to="/mood" className="text-sm font-medium text-slate-600 hover:text-teal-600">Mood</Link>
                <Link to="/reports" className="text-sm font-medium text-slate-600 hover:text-teal-600">Reports</Link>
                <Link to="/consultation" className="text-sm font-medium text-slate-600 hover:text-teal-600">Telemedicine</Link>
                <Link to="/history" className="text-sm font-medium text-slate-600 hover:text-teal-600 flex items-center gap-1"><FileClock className="w-4 h-4"/> History</Link>
                <Link to="/chat-history" className="text-sm font-medium text-slate-600 hover:text-teal-600 flex items-center gap-1"><MessageSquare className="w-4 h-4"/> Chats</Link>
                <div className="border-l border-slate-300 h-6 mx-2"></div>
                <Link to="/profile" className="flex items-center gap-2 text-sm font-medium text-slate-700 hover:text-teal-600">
                  <UserIcon className="w-5 h-5" />
                  <span className="hidden sm:inline">{user.full_name || user.email}</span>
                </Link>
                <button onClick={handleLogout} className="p-2 text-slate-500 hover:text-red-600 rounded-full hover:bg-slate-100 transition-colors">
                  <LogOut className="w-5 h-5" />
                </button>
              </>
            ) : (
              <>
                <Link to="/symptom-checker" className="text-sm font-medium text-slate-600 hover:text-teal-600 mr-2">Check Symptoms</Link>
                <Link to="/pain-assessment" className="text-sm font-medium text-slate-600 hover:text-teal-600 mr-2">Pain</Link>
                <Link to="/menstruation" className="text-sm font-medium text-slate-600 hover:text-teal-600 mr-2">Menstruation</Link>
                <Link to="/mood" className="text-sm font-medium text-slate-600 hover:text-teal-600 mr-2">Mood</Link>
                <Link to="/reports" className="text-sm font-medium text-slate-600 hover:text-teal-600 mr-2">Reports</Link>
                <Link to="/consultation" className="text-sm font-medium text-slate-600 hover:text-teal-600 mr-2">Telemedicine</Link>
                <Link to="/login" className="text-sm font-medium text-slate-600 hover:text-teal-600">Log in</Link>
                <Link to="/register" className="inline-flex items-center justify-center rounded-md text-sm font-medium bg-teal-600 text-white hover:bg-teal-700 h-9 px-4 py-2 transition-colors">
                  Sign up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
