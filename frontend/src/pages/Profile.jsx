import React from 'react';
import { useAuth } from '../context/AuthContext';
import { User, Mail, Calendar } from 'lucide-react';
import { format } from 'date-fns';

const Profile = () => {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="bg-gradient-to-r from-teal-500 to-emerald-600 h-32 relative">
          <div className="absolute -bottom-12 left-8 w-24 h-24 bg-white rounded-full p-2 shadow-md">
            <div className="w-full h-full bg-slate-100 rounded-full flex items-center justify-center">
              <User className="w-10 h-10 text-slate-400" />
            </div>
          </div>
        </div>
        
        <div className="pt-16 pb-8 px-8">
          <h1 className="text-2xl font-bold text-slate-900">{user.full_name || 'No Name'}</h1>
          
          <div className="mt-8 space-y-4">
            <div className="flex items-center gap-4 py-3 border-b border-slate-100">
              <Mail className="w-5 h-5 text-slate-400" />
              <div>
                <p className="text-sm text-slate-500">Email Address</p>
                <p className="font-medium text-slate-800">{user.email}</p>
              </div>
            </div>
            {user.created_at && (
              <div className="flex items-center gap-4 py-3 border-b border-slate-100">
                <Calendar className="w-5 h-5 text-slate-400" />
                <div>
                  <p className="text-sm text-slate-500">Joined</p>
                  <p className="font-medium text-slate-800">{format(new Date(user.created_at), 'PPP')}</p>
                </div>
              </div>
            )}
          </div>
          
          <div className="mt-10">
            <button 
              onClick={logout}
              className="px-6 py-2.5 bg-red-50 text-red-600 font-medium rounded-lg hover:bg-red-100 transition-colors"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
