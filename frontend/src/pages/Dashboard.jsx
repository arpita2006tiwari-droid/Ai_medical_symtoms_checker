import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { historyApi } from '../api/historyApi';
import { useAuth } from '../context/AuthContext';
import { Activity, PlusCircle, Clock, ChevronRight } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import { format } from 'date-fns';

const Dashboard = () => {
  const { user } = useAuth();
  const [recentAnalyses, setRecentAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await historyApi.getAnalyses(0, 5);
        setRecentAnalyses(data.analyses || []);
      } catch (error) {
        console.error("Failed to fetch history:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Welcome, {user?.full_name || 'User'}!</h1>
          <p className="text-slate-600 mt-1">What would you like to do today?</p>
        </div>
        <div className="mt-4 md:mt-0">
          <Link to="/symptom-checker" className="inline-flex items-center gap-2 bg-teal-600 text-white px-5 py-2.5 rounded-lg font-medium hover:bg-teal-700 transition-colors shadow-sm">
            <PlusCircle className="w-5 h-5" /> New Symptom Check
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="px-6 py-5 border-b border-slate-200 flex justify-between items-center bg-slate-50">
              <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <Clock className="w-5 h-5 text-teal-600" /> Recent Analyses
              </h2>
              <Link to="/history" className="text-sm font-medium text-teal-600 hover:text-teal-700">View All</Link>
            </div>
            
            <div className="divide-y divide-slate-100">
              {loading ? (
                <LoadingSpinner text="Loading history..." />
              ) : recentAnalyses.length === 0 ? (
                <div className="p-8 text-center text-slate-500">
                  <Activity className="w-10 h-10 mx-auto text-slate-300 mb-3" />
                  <p>You haven't checked any symptoms yet.</p>
                </div>
              ) : (
                recentAnalyses.map(analysis => (
                  <div key={analysis.id} onClick={() => navigate(`/analysis/${analysis.id}`)} className="p-6 hover:bg-slate-50 cursor-pointer transition-colors flex justify-between items-center">
                    <div>
                      <p className="text-sm text-slate-500 mb-1">{format(new Date(analysis.created_at), 'PPP')}</p>
                      <h4 className="font-medium text-slate-800">
                        {analysis.predictions && analysis.predictions[0]?.condition 
                          ? analysis.predictions[0].condition 
                          : 'Symptom Analysis'}
                      </h4>
                    </div>
                    <ChevronRight className="w-5 h-5 text-slate-400" />
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
