import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useAnalysis } from '../context/AnalysisContext';
import { menstruationApi } from '../api/menstruationApi';
import { analysisApi } from '../api/analysisApi';
import { followupApi } from '../api/followupApi';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import { Calendar, Droplets, Bell, Settings, Plus, Trash2, Activity, ArrowRight, ClipboardList, Loader2, AlertTriangle, CheckCircle } from 'lucide-react';
import { addDays, differenceInDays, format, parseISO, isValid } from 'date-fns';

const MenstruationTracking = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { setAnalysisResult } = useAnalysis();

  const [cycles, setCycles] = useState([]);
  const [prefs, setPrefs] = useState({ reminders_enabled: false, reminder_days_before: 2 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [view, setView] = useState('dashboard'); // dashboard, log, settings, review, followup, analyze
  
  // Log Form State
  const [formData, setFormData] = useState({
    start_date: format(new Date(), 'yyyy-MM-dd'),
    end_date: '',
    cycle_length: '',
    flow_level: 'medium',
    cramps_severity: 0,
    associated_symptoms: '',
    notes: ''
  });

  // NLP Analysis State
  const [extractedSymptoms, setExtractedSymptoms] = useState([]);
  const [detailedSymptoms, setDetailedSymptoms] = useState([]);
  const [savedCycleId, setSavedCycleId] = useState(null);
  const [followupState, setFollowupState] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);

  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [cRes, pRes] = await Promise.all([
        menstruationApi.getCycles(),
        menstruationApi.getPreferences()
      ]);
      setCycles(cRes);
      setPrefs(pRes);
    } catch (err) {
      setError('Failed to load tracking data.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const calculateEstimate = () => {
    if (cycles.length < 2) return null;
    // Calculate average cycle length from last 3 cycles if available
    const sorted = [...cycles].sort((a, b) => new Date(b.start_date) - new Date(a.start_date));
    let totalLength = 0;
    let count = 0;
    
    for (let i = 0; i < sorted.length - 1 && i < 3; i++) {
      const current = parseISO(sorted[i].start_date);
      const previous = parseISO(sorted[i+1].start_date);
      if (isValid(current) && isValid(previous)) {
        const diff = differenceInDays(current, previous);
        if (diff > 15 && diff < 100) { // basic sanity check
          totalLength += diff;
          count++;
        }
      }
    }
    
    if (count === 0) return null;
    const avgCycle = Math.round(totalLength / count);
    const lastStart = parseISO(sorted[0].start_date);
    const nextEst = addDays(lastStart, avgCycle);
    return { date: format(nextEst, 'PPP'), avgCycle };
  };

  const estimate = calculateEstimate();

  const handleSavePreferences = async () => {
    try {
      await menstruationApi.updatePreferences(prefs);
      setView('dashboard');
    } catch (err) {
      setError('Failed to save preferences.');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this cycle record?")) return;
    try {
      await menstruationApi.deleteCycle(id);
      setCycles(cycles.filter(c => c.id !== id));
    } catch (err) {
      setError('Failed to delete cycle.');
    }
  };

  const handleLogSubmit = async (e, analyze = false) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      let cycleId = null;
      if (user) {
        const payload = {
          ...formData,
          end_date: formData.end_date || null,
          cycle_length: formData.cycle_length ? parseInt(formData.cycle_length) : null,
          associated_symptoms: formData.associated_symptoms.split(',').map(s => s.trim()).filter(Boolean),
          cramps_severity: parseInt(formData.cramps_severity),
          age: null,
          patient_type: 'general' // Assuming adults
        };
        const saved = await menstruationApi.createCycle(payload);
        cycleId = saved.id;
        setSavedCycleId(saved.id);
        setCycles([saved, ...cycles]);
      }

      if (analyze) {
        const text = `I am on my period with ${formData.flow_level} flow and ${formData.cramps_severity}/10 menstrual cramps. Associated symptoms: ${formData.associated_symptoms}. ${formData.notes}`;
        const data = await analysisApi.extractSymptoms(text);
        
        const recognized = data.recognized_symptoms || [];
        if (recognized.length === 0) {
           setExtractedSymptoms(['menstrual cramps']);
           setDetailedSymptoms([{ canonical: 'menstrual cramps', is_model_supported: true }]);
        } else {
           setExtractedSymptoms(recognized);
           setDetailedSymptoms(data.detailed_symptoms || []);
        }
        setView('review');
      } else {
        setView('dashboard');
        // Reset form
        setFormData({
          start_date: format(new Date(), 'yyyy-MM-dd'), end_date: '', cycle_length: '', flow_level: 'medium', cramps_severity: 0, associated_symptoms: '', notes: ''
        });
      }
    } catch (err) {
      const msg = err.response?.data?.detail?.[0]?.msg || 'Failed to save cycle.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleProceedFromReview = async () => {
    setLoading(true);
    setError('');
    try {
      if (extractedSymptoms.length === 0) {
        setError('You must have at least one symptom to continue.');
        setLoading(false); return;
      }
      
      const followupData = await followupApi.startFollowup(extractedSymptoms);
      if (followupData.complete === false && followupData.question) {
        setFollowupState(followupData.state);
        setCurrentQuestion(followupData.question);
        setView('followup');
      } else {
        handleFinalAnalysis(extractedSymptoms);
      }
    } catch (err) {
      setError('Failed to start follow-up.');
    } finally {
      if (view !== 'followup') setLoading(false);
    }
  };

  const handleAnswer = async (answerValue) => {
    setLoading(true);
    setError('');
    try {
      const data = await followupApi.answerFollowup(followupState, currentQuestion.id, answerValue);
      if (data.complete === false && data.question) {
        setFollowupState(data.state);
        setCurrentQuestion(data.question);
        setView('followup');
      } else {
        const finalSymptoms = data.state?.recognized_symptoms || extractedSymptoms;
        handleFinalAnalysis(finalSymptoms);
      }
    } catch (err) {
      setError('Failed to submit answer.');
    } finally {
      setLoading(false);
    }
  };

  const handleFinalAnalysis = async (symptoms) => {
    setLoading(true);
    setView('analyze');
    try {
      const data = await analysisApi.predict(symptoms, { patient_type: 'general' });
      
      if (savedCycleId && user) {
        try {
          await menstruationApi.updateCycle(savedCycleId, { analysis_id: data.id });
        } catch (e) {
          console.error('Could not link analysis', e);
        }
      }
      setTimeout(() => {
        setAnalysisResult(data);
        navigate(`/analysis-result`);
      }, 1000);
    } catch (err) {
      setError('Failed to generate analysis.');
      setView('dashboard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-teal-800 flex justify-center items-center gap-2">
          <Droplets className="w-8 h-8 text-pink-500" /> Menstruation Tracking
        </h1>
        <p className="text-slate-600 mt-2 max-w-2xl mx-auto">
          Track your menstrual cycle and related symptoms.<br/>
          <strong>Disclaimer:</strong> This is an educational tool. Cycle predictions are estimates and do not guarantee ovulation, fertility, or rule out medical conditions. Do not use this tool for contraception.
        </p>
      </div>

      <ErrorMessage message={error} />

      {view === 'dashboard' && (
        <div className="space-y-6">
          <div className="flex gap-4 mb-6">
             <button onClick={() => setView('log')} className="flex-1 bg-teal-600 text-white p-4 rounded-xl shadow hover:bg-teal-700 flex items-center justify-center gap-2 font-bold">
               <Plus /> Log Period
             </button>
             {user && (
               <button onClick={() => setView('settings')} className="bg-white border-2 border-slate-200 text-slate-700 p-4 rounded-xl shadow-sm hover:bg-slate-50 flex items-center justify-center gap-2 font-bold">
                 <Settings /> Preferences
               </button>
             )}
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
             <h2 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2"><Calendar className="text-teal-600"/> Cycle Estimates</h2>
             {estimate ? (
               <div className="bg-pink-50 border border-pink-100 rounded-lg p-6 text-center">
                 <div className="text-sm text-pink-800 font-semibold uppercase tracking-wide">Estimated Next Period</div>
                 <div className="text-3xl font-bold text-pink-600 my-2">{estimate.date}</div>
                 <div className="text-sm text-slate-600">Based on an average cycle length of {estimate.avgCycle} days</div>
               </div>
             ) : (
               <div className="text-center p-6 text-slate-500 bg-slate-50 rounded-lg border border-slate-200">
                 Not enough history to estimate your next period. Log at least 2 cycles.
               </div>
             )}
          </div>

          {!user && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800 flex items-start gap-2">
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              <div>You are using Guest Mode. You can log a period and analyze symptoms, but your history will not be saved permanently.</div>
            </div>
          )}

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h2 className="text-xl font-bold text-slate-800 mb-4">Cycle History</h2>
            {loading ? <LoadingSpinner /> : cycles.length === 0 ? (
              <p className="text-slate-500">No recorded cycles found.</p>
            ) : (
              <div className="space-y-4">
                {cycles.map(cycle => (
                  <div key={cycle.id} className="border border-slate-200 rounded-lg p-4 flex flex-col md:flex-row justify-between md:items-center gap-4 hover:bg-slate-50">
                    <div>
                      <div className="font-bold text-slate-800">{format(parseISO(cycle.start_date), 'PPP')} {cycle.end_date && `- ${format(parseISO(cycle.end_date), 'PPP')}`}</div>
                      <div className="text-sm text-slate-500 flex gap-4 mt-1">
                        <span className="capitalize">Flow: {cycle.flow_level}</span>
                        <span>Cramps: {cycle.cramps_severity}/10</span>
                      </div>
                      {cycle.associated_symptoms?.length > 0 && (
                        <div className="text-xs text-slate-400 mt-1">Symptoms: {cycle.associated_symptoms.join(', ')}</div>
                      )}
                    </div>
                    <div className="flex gap-2">
                       {cycle.analysis_id && (
                         <button onClick={() => navigate(`/analysis/${cycle.analysis_id}`)} className="text-teal-600 hover:text-teal-800 text-sm font-medium flex items-center gap-1"><Activity className="w-4 h-4"/> Results</button>
                       )}
                       <button onClick={() => handleDelete(cycle.id)} className="text-red-500 hover:text-red-700 p-2"><Trash2 className="w-4 h-4"/></button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {view === 'settings' && user && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2"><Bell className="text-teal-600"/> Reminder Preferences</h2>
          <div className="space-y-4 max-w-md">
             <label className="flex items-center gap-3 cursor-pointer">
               <input type="checkbox" checked={prefs.reminders_enabled} onChange={e => setPrefs({...prefs, reminders_enabled: e.target.checked})} className="w-5 h-5 text-teal-600 rounded focus:ring-teal-500" />
               <span className="font-medium text-slate-700">Enable estimated period reminders</span>
             </label>
             
             {prefs.reminders_enabled && (
               <div>
                 <label className="block text-sm font-medium text-slate-700 mb-2">Remind me</label>
                 <div className="flex items-center gap-2">
                   <input type="number" min="1" max="7" value={prefs.reminder_days_before} onChange={e => setPrefs({...prefs, reminder_days_before: parseInt(e.target.value)})} className="w-20 p-2 border border-slate-300 rounded" />
                   <span className="text-slate-600">days before estimated start date</span>
                 </div>
               </div>
             )}
             
             <div className="text-xs text-slate-500 mt-4">
               Note: Push/Email notifications are currently simulated. Preferences are securely stored in the backend.
             </div>

             <div className="flex gap-4 pt-6">
               <button onClick={() => setView('dashboard')} className="flex-1 py-2 px-4 rounded-lg bg-slate-100 text-slate-700 font-semibold hover:bg-slate-200">Cancel</button>
               <button onClick={handleSavePreferences} className="flex-1 py-2 px-4 rounded-lg bg-teal-600 text-white font-semibold hover:bg-teal-700">Save</button>
             </div>
          </div>
        </div>
      )}

      {view === 'log' && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-xl font-bold text-slate-800 mb-6">Log Period</h2>
          <form className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Start Date *</label>
                <input type="date" name="start_date" value={formData.start_date} onChange={handleInputChange} required className="w-full p-3 border border-slate-300 rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">End Date (Optional)</label>
                <input type="date" name="end_date" value={formData.end_date} onChange={handleInputChange} className="w-full p-3 border border-slate-300 rounded-lg" />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Flow Level *</label>
                <select name="flow_level" value={formData.flow_level} onChange={handleInputChange} required className="w-full p-3 border border-slate-300 rounded-lg bg-white">
                  <option value="light">Light</option>
                  <option value="medium">Medium</option>
                  <option value="heavy">Heavy</option>
                  <option value="unknown">Unknown</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Known Cycle Length (Optional)</label>
                <input type="number" name="cycle_length" value={formData.cycle_length} onChange={handleInputChange} placeholder="e.g. 28" min="15" max="100" className="w-full p-3 border border-slate-300 rounded-lg" />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Cramps Severity (0-10)</label>
              <input type="range" name="cramps_severity" min="0" max="10" value={formData.cramps_severity} onChange={handleInputChange} className="w-full accent-pink-500" />
              <div className="text-center mt-2 font-bold text-pink-600">{formData.cramps_severity} / 10</div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Associated Symptoms</label>
              <input type="text" name="associated_symptoms" value={formData.associated_symptoms} onChange={handleInputChange} placeholder="e.g. Headache, bloating, fatigue, back pain" className="w-full p-3 border border-slate-300 rounded-lg" />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Optional Notes</label>
              <textarea name="notes" value={formData.notes} onChange={handleInputChange} className="w-full p-3 border border-slate-300 rounded-lg h-24 resize-none"></textarea>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 pt-4 border-t border-slate-200">
               <button type="button" onClick={() => setView('dashboard')} className="py-3 px-4 rounded-lg bg-slate-100 text-slate-700 font-semibold hover:bg-slate-200">Cancel</button>
               <div className="flex-1 flex gap-2">
                 <button type="button" onClick={(e) => handleLogSubmit(e, false)} disabled={loading} className="flex-1 py-3 px-4 rounded-lg border-2 border-teal-600 text-teal-700 font-semibold hover:bg-teal-50">Save Only</button>
                 <button type="button" onClick={(e) => handleLogSubmit(e, true)} disabled={loading} className="flex-1 py-3 px-4 rounded-lg bg-teal-600 text-white font-semibold hover:bg-teal-700 flex items-center justify-center gap-1">Save & Analyze <Activity className="w-4 h-4"/></button>
               </div>
            </div>
          </form>
        </div>
      )}

      {/* Review, Followup, and Analyze steps reused from Pain Assessment */}
      {view === 'review' && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 md:p-8">
          <div className="mb-6 text-center">
            <h2 className="text-2xl font-bold text-slate-800">Review Recognized Symptoms</h2>
          </div>
          <div className="space-y-3 mb-8">
            {detailedSymptoms.map((sym, idx) => (
              <div key={idx} className="flex justify-between items-center p-4 border rounded-lg bg-slate-50 border-slate-200">
                <div>
                  <div className="font-bold text-slate-800 capitalize">{sym.canonical}</div>
                  {!sym.is_model_supported && <div className="text-xs text-yellow-600 mt-1 flex items-center gap-1"><AlertTriangle className="w-3 h-3"/> Not supported by prediction model</div>}
                  {sym.is_model_supported && <div className="text-xs text-teal-600 mt-1 flex items-center gap-1"><CheckCircle className="w-3 h-3"/> Supported by prediction model</div>}
                </div>
                <button type="button" onClick={() => {
                  setExtractedSymptoms(prev => prev.filter(s => s !== sym.canonical));
                  setDetailedSymptoms(prev => prev.filter(s => s.canonical !== sym.canonical));
                }} className="text-red-500 hover:text-red-700 text-sm font-medium">Remove</button>
              </div>
            ))}
          </div>
          <div className="flex gap-4">
            <button onClick={() => setView('dashboard')} className="flex-1 py-3 px-4 rounded-lg text-slate-700 bg-slate-100 hover:bg-slate-200">Cancel</button>
            <button onClick={handleProceedFromReview} disabled={loading || extractedSymptoms.length === 0} className="flex-1 py-3 px-4 rounded-lg text-white bg-teal-600 hover:bg-teal-700 flex justify-center items-center">
              {loading ? <Loader2 className="animate-spin w-5 h-5"/> : 'Continue'}
            </button>
          </div>
        </div>
      )}

      {view === 'followup' && currentQuestion && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 md:p-8 text-center max-w-2xl mx-auto">
          <ClipboardList className="w-12 h-12 text-teal-600 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-slate-800 mb-6">{currentQuestion.text}</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {currentQuestion.type === 'yes_no' ? (
              <><button onClick={() => handleAnswer('yes')} className="py-3 border-2 border-slate-200 rounded-lg hover:border-teal-500 hover:bg-teal-50">Yes</button><button onClick={() => handleAnswer('no')} className="py-3 border-2 border-slate-200 rounded-lg hover:border-teal-500 hover:bg-teal-50">No</button></>
            ) : (currentQuestion.options || []).map((opt, idx) => (
              <button key={idx} onClick={() => handleAnswer(opt)} className="py-3 border-2 border-slate-200 rounded-lg hover:border-teal-500 hover:bg-teal-50">{opt}</button>
            ))}
          </div>
        </div>
      )}

      {view === 'analyze' && (
        <div className="text-center py-12"><LoadingSpinner text="Generating analysis..." /></div>
      )}
    </div>
  );
};

export default MenstruationTracking;
