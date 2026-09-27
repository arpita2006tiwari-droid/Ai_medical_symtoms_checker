import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAnalysis } from '../context/AnalysisContext';
import { useAuth } from '../context/AuthContext';
import { historyApi } from '../api/historyApi';
import Disclaimer from '../components/Disclaimer';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { ShieldAlert, Stethoscope, Phone, AlertTriangle, CheckCircle, Activity, MessageSquare } from 'lucide-react';

const UrgencyBadge = ({ urgency }) => {
  const urgencyMap = {
    'urgent_attention': { label: 'URGENT ATTENTION', color: 'bg-red-100 text-red-800 border-red-300', icon: <ShieldAlert className="w-5 h-5"/> },
    'medical_attention': { label: 'MEDICAL ATTENTION', color: 'bg-yellow-100 text-yellow-800 border-yellow-300', icon: <AlertTriangle className="w-5 h-5"/> },
    'routine': { label: 'ROUTINE', color: 'bg-green-100 text-green-800 border-green-300', icon: <CheckCircle className="w-5 h-5"/> }
  };
  const ui = urgencyMap[urgency] || urgencyMap['routine'];
  
  return (
    <div className={`flex items-center gap-2 px-4 py-2 rounded-full border ${ui.color} font-bold text-lg`}>
      {ui.icon} {ui.label}
    </div>
  );
};

const AnalysisResult = () => {
  const { id } = useParams();
  const { currentAnalysis } = useAnalysis();
  const { user } = useAuth();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAnalysis = async () => {
      if (id) {
        try {
          const data = await historyApi.getAnalysisById(id);
          setAnalysis(data);
        } catch (err) {
          setError('Analysis not found.');
        } finally {
          setLoading(false);
        }
      } else if (currentAnalysis) {
        setAnalysis(currentAnalysis);
        setLoading(false);
      } else {
        // No ID and no context? Go to checker
        navigate('/symptom-checker');
      }
    };
    fetchAnalysis();
  }, [id, currentAnalysis, navigate]);

  if (loading) return <div className="py-20"><LoadingSpinner /></div>;
  if (error) return <div className="py-20 max-w-lg mx-auto"><ErrorMessage message={error} /></div>;
  if (!analysis) return null;

  const urgency = analysis.urgency || {};
  const predictions = analysis.predictions || [];
  const specialist = analysis.specialist_recommendation || {};

  const handleStartChat = () => {
    // Navigate to chat, maybe pass analysis context if needed via state
    navigate('/chat-assistant', { state: { analysisId: analysis.id } });
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <h1 className="text-3xl font-extrabold text-slate-900">Analysis Results</h1>
        {urgency.level && <UrgencyBadge urgency={urgency.level} />}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Main Results */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Action Required */}
          {/* Action Required */}
          {urgency.message && (
            <div className={`p-6 rounded-xl border ${urgency.level === 'urgent_attention' ? 'bg-red-50 border-red-200' : urgency.level === 'medical_attention' ? 'bg-yellow-50 border-yellow-200' : 'bg-green-50 border-green-200'}`}>
              <h3 className={`text-xl font-bold mb-2 ${urgency.level === 'urgent_attention' ? 'text-red-800' : urgency.level === 'medical_attention' ? 'text-yellow-800' : 'text-green-800'}`}>
                Urgency Assessment
              </h3>
              <p className={urgency.level === 'urgent_attention' ? 'text-red-700 font-medium' : urgency.level === 'medical_attention' ? 'text-yellow-700 font-medium' : 'text-green-700'}>
                {urgency.message}
              </p>
              {urgency.matched_rules && urgency.matched_rules.length > 0 && (
                <div className="mt-4">
                  <h4 className={`font-semibold text-sm uppercase tracking-wider mb-2 ${urgency.level === 'urgent_attention' ? 'text-red-800' : 'text-yellow-800'}`}>Matched Rules:</h4>
                  <ul className={`list-disc pl-5 text-sm ${urgency.level === 'urgent_attention' ? 'text-red-700' : 'text-yellow-700'}`}>
                    {urgency.matched_rules.map((rule, i) => <li key={i}>{rule.reason}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Predictions */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="bg-slate-50 px-6 py-4 border-b border-slate-200">
              <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <Stethoscope className="w-5 h-5 text-teal-600" /> Potential Conditions
              </h3>
            </div>
            <div className="divide-y divide-slate-100">
              {predictions.map((pred, i) => (
                <div key={i} className="p-6">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="text-xl font-bold text-slate-800">{pred.condition}</h4>
                    <span className="bg-teal-100 text-teal-800 text-xs font-bold px-2.5 py-1 rounded">
                      {Number.isFinite(Number(pred.model_probability))
                        ? `${(Number(pred.model_probability) * 100).toFixed(0)}% Match`
                        : 'N/A'}
                    </span>
                  </div>
                  {pred.description && (
                    <p className="text-slate-600 text-sm mb-4">{pred.description}</p>
                  )}
                  {pred.precautions?.length > 0 && (
                    <div className="text-sm">
                      <span className="font-semibold text-slate-700">General Precautions</span>
                      <ul className="list-disc pl-5 mt-1 text-slate-600 space-y-1">
                        {pred.precautions.map((precaution, idx) => (
                          <li key={idx}>{precaution}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
          
          <Disclaimer />
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          
          {/* Chat CTA */}
          <div className="bg-gradient-to-br from-teal-500 to-emerald-600 rounded-xl p-6 text-white shadow-md">
            <MessageSquare className="w-8 h-8 mb-4 text-teal-100" />
            <h3 className="text-xl font-bold mb-2">Have Questions?</h3>
            <p className="text-teal-50 mb-6 text-sm">Chat with our AI assistant to understand your results better or ask about your symptoms.</p>
            <button onClick={handleStartChat} className="w-full bg-white text-teal-700 font-bold py-2.5 rounded-lg hover:bg-slate-50 transition-colors">
              Start Chat
            </button>
          </div>

          {/* Guest CTA */}
          {!user && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="text-lg font-bold text-slate-800 mb-2">Save Your Results</h3>
              <p className="text-slate-600 text-sm mb-4">Create a free account to save this analysis, track your symptom history, and get personalized insights over time.</p>
              <div className="flex flex-col gap-2">
                <button onClick={() => navigate('/register')} className="w-full bg-teal-600 text-white font-bold py-2 rounded-lg hover:bg-teal-700 transition-colors">
                  Sign Up
                </button>
                <button onClick={() => navigate('/login')} className="w-full bg-slate-100 text-slate-700 font-bold py-2 rounded-lg hover:bg-slate-200 transition-colors">
                  Log In
                </button>
              </div>
            </div>
          )}

          {/* Specialist Rec */}
          {specialist.specialist && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="text-lg font-bold text-slate-800 mb-2">Recommended Specialist</h3>
              <p className="text-teal-700 font-semibold text-xl mb-4">{specialist.specialist}</p>
              <p className="text-sm text-slate-600 mb-4">{specialist.reason}</p>
              
              {specialist.providers && specialist.providers.length > 0 && (
                <div className="mt-4 pt-4 border-t border-slate-100">
                  <h4 className="font-semibold text-sm text-slate-700 mb-3">Nearby Providers</h4>
                  <ul className="space-y-3 text-sm">
                    {specialist.providers.map((p, i) => (
                      <li key={i} className="flex flex-col">
                        <span className="font-medium text-slate-800">{p.name}</span>
                        <span className="text-slate-500">{p.address}</span>
                        <a href={`tel:${p.phone}`} className="text-teal-600 flex items-center gap-1 mt-1">
                          <Phone className="w-3 h-3" /> {p.phone}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default AnalysisResult;
