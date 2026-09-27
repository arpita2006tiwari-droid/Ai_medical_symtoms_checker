import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useAnalysis } from '../context/AnalysisContext';
import { moodApi } from '../api/moodApi';
import { menstruationApi } from '../api/menstruationApi';
import { analysisApi } from '../api/analysisApi';
import { followupApi } from '../api/followupApi';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import { Heart, Smile, Meh, Frown, Activity, Plus, Trash2, Calendar, ClipboardList, Loader2, AlertTriangle, CheckCircle, PhoneCall } from 'lucide-react';
import { format, parseISO } from 'date-fns';

const EMOTIONS_LIST = ['Anxious', 'Sad', 'Stressed', 'Irritable', 'Calm', 'Happy', 'Overwhelmed', 'Angry', 'Hopeful'];

const MoodTracking = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { setAnalysisResult } = useAnalysis();

  const [checkins, setCheckins] = useState([]);
  const [cycles, setCycles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [view, setView] = useState('dashboard');
  
  const [formData, setFormData] = useState({
    mood: 'neutral',
    intensity: 5,
    emotions: [],
    energy_level: 'medium',
    sleep_quality: 'fair',
    notes: '',
    cycle_id: ''
  });

  const [crisisAlert, setCrisisAlert] = useState(false);

  // NLP Analysis State
  const [extractedSymptoms, setExtractedSymptoms] = useState([]);
  const [detailedSymptoms, setDetailedSymptoms] = useState([]);
  const [savedCheckinId, setSavedCheckinId] = useState(null);
  const [followupState, setFollowupState] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);

  useEffect(() => {
    if (user) loadData();
  }, [user]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [mRes, cRes] = await Promise.all([
        moodApi.getCheckins(),
        menstruationApi.getCycles().catch(() => []) // Optional
      ]);
      setCheckins(mRes);
      setCycles(cRes);
    } catch (err) {
      setError('Failed to load data.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const toggleEmotion = (emotion) => {
    setFormData(prev => {
      if (prev.emotions.includes(emotion)) return { ...prev, emotions: prev.emotions.filter(e => e !== emotion) };
      return { ...prev, emotions: [...prev.emotions, emotion] };
    });
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this entry?")) return;
    try {
      await moodApi.deleteCheckin(id);
      setCheckins(checkins.filter(c => c.id !== id));
    } catch (err) {
      setError('Failed to delete.');
    }
  };

  const checkCrisis = () => {
    const text = (formData.notes + " " + formData.emotions.join(" ")).toLowerCase();
    const triggerWords = ['suicide', 'kill myself', 'die', 'end it all', 'self harm', 'hurt myself', 'want to die'];
    return triggerWords.some(word => text.includes(word));
  };

  const handleLogSubmit = async (e, analyze = false) => {
    e.preventDefault();
    setError('');

    if (checkCrisis()) {
      setCrisisAlert(true);
      return;
    }

    setLoading(true);
    try {
      let checkinId = null;
      if (user) {
        const payload = {
          ...formData,
          intensity: parseInt(formData.intensity),
          cycle_id: formData.cycle_id || null
        };
        const saved = await moodApi.createCheckin(payload);
        checkinId = saved.id;
        setSavedCheckinId(saved.id);
        setCheckins([saved, ...checkins]);
      }

      if (analyze) {
        const text = `I am feeling ${formData.mood} (intensity ${formData.intensity}/10). Emotions: ${formData.emotions.join(', ')}. Energy is ${formData.energy_level}, sleep was ${formData.sleep_quality}. ${formData.notes}`;
        const data = await analysisApi.extractSymptoms(text);
        
        const recognized = data.recognized_symptoms || [];
        if (recognized.length === 0) {
           // Fallback to basic emotions if NLP misses
           const basic = formData.emotions.length > 0 ? formData.emotions : [formData.mood + ' mood'];
           setExtractedSymptoms(basic);
           setDetailedSymptoms(basic.map(b => ({ canonical: b.toLowerCase(), is_model_supported: true })));
        } else {
           setExtractedSymptoms(recognized);
           setDetailedSymptoms(data.detailed_symptoms || []);
        }
        setView('review');
      } else {
        setView('dashboard');
        resetForm();
      }
    } catch (err) {
      const msg = err.response?.data?.detail?.[0]?.msg || 'Failed to save.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({ mood: 'neutral', intensity: 5, emotions: [], energy_level: 'medium', sleep_quality: 'fair', notes: '', cycle_id: '' });
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
      if (savedCheckinId && user) {
        try { await moodApi.updateCheckin(savedCheckinId, { analysis_id: data.id }); } catch (e) {}
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

  const getMoodIcon = (mood) => {
    switch (mood) {
      case 'very good': case 'good': return <Smile className="text-green-500" />;
      case 'neutral': return <Meh className="text-yellow-500" />;
      case 'low': case 'very low': return <Frown className="text-red-500" />;
      default: return <Smile />;
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-teal-800 flex justify-center items-center gap-2">
          <Heart className="w-8 h-8 text-indigo-500" /> Mood & Emotional Wellbeing
        </h1>
        <p className="text-slate-600 mt-2 max-w-2xl mx-auto">
          Track your mood and feelings over time.<br/>
          <strong>Disclaimer:</strong> This tool is for personal reflection and is not a clinical mental health assessment or diagnostic tool.
        </p>
      </div>

      <ErrorMessage message={error} />

      {crisisAlert && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6 text-center border-t-4 border-red-600">
            <PhoneCall className="w-16 h-16 text-red-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-slate-900 mb-2">You are not alone. Help is available.</h2>
            <p className="text-slate-600 mb-6">
              It sounds like you are going through a difficult time. Please reach out to someone who can help immediately.
            </p>
            <div className="bg-red-50 border border-red-100 rounded-lg p-4 mb-6 text-left">
              <ul className="space-y-3">
                <li className="flex items-center gap-2"><strong className="text-red-700">India Emergency:</strong> 112</li>
                <li className="flex items-center gap-2"><strong className="text-red-700">Tele-MANAS (Mental Health):</strong> 14416</li>
              </ul>
            </div>
            <button onClick={() => { setCrisisAlert(false); setView('dashboard'); resetForm(); }} className="w-full bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold py-3 rounded-lg">
              Close and Return
            </button>
          </div>
        </div>
      )}

      {view === 'dashboard' && (
        <div className="space-y-6">
          <div className="flex mb-6">
             <button onClick={() => setView('log')} className="flex-1 bg-teal-600 text-white p-4 rounded-xl shadow hover:bg-teal-700 flex items-center justify-center gap-2 font-bold">
               <Plus /> Log Mood
             </button>
          </div>

          {!user && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800 flex items-start gap-2">
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              <div>You are using Guest Mode. You can log your mood and analyze symptoms temporarily, but they will not be saved.</div>
            </div>
          )}

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h2 className="text-xl font-bold text-slate-800 mb-4">Mood History</h2>
            {loading ? <LoadingSpinner /> : checkins.length === 0 ? (
              <p className="text-slate-500">No mood entries found.</p>
            ) : (
              <div className="space-y-4">
                {checkins.map(entry => (
                  <div key={entry.id} className="border border-slate-200 rounded-lg p-4 flex flex-col md:flex-row justify-between md:items-center gap-4 hover:bg-slate-50">
                    <div className="flex gap-4 items-center">
                      <div className="bg-slate-100 p-3 rounded-full">
                        {getMoodIcon(entry.mood)}
                      </div>
                      <div>
                        <div className="font-bold text-slate-800 capitalize">{entry.mood} <span className="text-slate-400 font-normal text-sm ml-2">{format(parseISO(entry.created_at), 'PPP p')}</span></div>
                        <div className="text-sm text-slate-500 flex gap-4 mt-1">
                          <span>Intensity: {entry.intensity}/10</span>
                          {entry.emotions?.length > 0 && <span>Emotions: {entry.emotions.join(', ')}</span>}
                        </div>
                        {entry.cycle_id && (
                          <div className="text-xs text-pink-600 mt-1 flex items-center gap-1"><Calendar className="w-3 h-3"/> Logged during a cycle</div>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2 shrink-0">
                       {entry.analysis_id && (
                         <button onClick={() => navigate(`/analysis/${entry.analysis_id}`)} className="text-teal-600 hover:text-teal-800 text-sm font-medium flex items-center gap-1"><Activity className="w-4 h-4"/> Results</button>
                       )}
                       <button onClick={() => handleDelete(entry.id)} className="text-red-500 hover:text-red-700 p-2"><Trash2 className="w-4 h-4"/></button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {view === 'log' && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-xl font-bold text-slate-800 mb-6">How are you feeling?</h2>
          <form className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Overall Mood *</label>
              <div className="flex flex-wrap gap-3">
                {['very low', 'low', 'neutral', 'good', 'very good'].map(m => (
                  <button type="button" key={m} onClick={() => setFormData({...formData, mood: m})}
                    className={`capitalize px-4 py-2 rounded-lg border-2 font-medium ${formData.mood === m ? 'border-teal-600 bg-teal-50 text-teal-700' : 'border-slate-200 text-slate-600 hover:border-teal-300'}`}>
                    {m}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Intensity (1-10)</label>
              <input type="range" name="intensity" min="1" max="10" value={formData.intensity} onChange={handleInputChange} className="w-full accent-indigo-500" />
              <div className="text-center mt-2 font-bold text-indigo-600">{formData.intensity}</div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Emotions</label>
              <div className="flex flex-wrap gap-2">
                {EMOTIONS_LIST.map(e => (
                  <button type="button" key={e} onClick={() => toggleEmotion(e)}
                    className={`px-3 py-1.5 rounded-full border text-sm ${formData.emotions.includes(e) ? 'bg-indigo-600 border-indigo-600 text-white' : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50'}`}>
                    {e}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Energy Level</label>
                <select name="energy_level" value={formData.energy_level} onChange={handleInputChange} className="w-full p-3 border border-slate-300 rounded-lg bg-white">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Sleep Quality</label>
                <select name="sleep_quality" value={formData.sleep_quality} onChange={handleInputChange} className="w-full p-3 border border-slate-300 rounded-lg bg-white">
                  <option value="poor">Poor</option>
                  <option value="fair">Fair</option>
                  <option value="good">Good</option>
                  <option value="excellent">Excellent</option>
                </select>
              </div>
            </div>

            {cycles.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Associate with Menstrual Cycle (Optional)</label>
                <select name="cycle_id" value={formData.cycle_id} onChange={handleInputChange} className="w-full p-3 border border-slate-300 rounded-lg bg-white">
                  <option value="">-- Do not associate --</option>
                  {cycles.map(c => (
                     <option key={c.id} value={c.id}>Cycle started {format(parseISO(c.start_date), 'PPP')}</option>
                  ))}
                </select>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Journal / Notes</label>
              <textarea name="notes" value={formData.notes} onChange={handleInputChange} maxLength={1000} className="w-full p-3 border border-slate-300 rounded-lg h-24 resize-none" placeholder="What's on your mind?"></textarea>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 pt-4 border-t border-slate-200">
               <button type="button" onClick={() => {setView('dashboard'); resetForm();}} className="py-3 px-4 rounded-lg bg-slate-100 text-slate-700 font-semibold hover:bg-slate-200">Cancel</button>
               <div className="flex-1 flex gap-2">
                 <button type="button" onClick={(e) => handleLogSubmit(e, false)} disabled={loading} className="flex-1 py-3 px-4 rounded-lg border-2 border-teal-600 text-teal-700 font-semibold hover:bg-teal-50">Save Only</button>
                 <button type="button" onClick={(e) => handleLogSubmit(e, true)} disabled={loading} className="flex-1 py-3 px-4 rounded-lg bg-teal-600 text-white font-semibold hover:bg-teal-700 flex items-center justify-center gap-1 text-sm md:text-base">Analyze Symptoms <Activity className="w-4 h-4"/></button>
               </div>
            </div>
            <p className="text-xs text-slate-500 text-center">Your emotional records are kept private. If you click Analyze, only the extracted symptoms will be sent to the AI assessment model.</p>
          </form>
        </div>
      )}

      {/* Review, Followup, Analyze (Reused flow) */}
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
                  {!sym.is_model_supported && <div className="text-xs text-yellow-600 mt-1 flex items-center gap-1"><AlertTriangle className="w-3 h-3"/> Not supported by diagnostic model</div>}
                  {sym.is_model_supported && <div className="text-xs text-teal-600 mt-1 flex items-center gap-1"><CheckCircle className="w-3 h-3"/> Supported by diagnostic model</div>}
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
              {loading ? <Loader2 className="animate-spin w-5 h-5"/> : 'Continue Assessment'}
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

export default MoodTracking;
