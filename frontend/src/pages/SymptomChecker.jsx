import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisApi } from '../api/analysisApi';
import { followupApi } from '../api/followupApi';
import { useAnalysis } from '../context/AnalysisContext';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import { ArrowRight, MessageSquare, ClipboardList, Send, Loader2 } from 'lucide-react';

const SymptomChecker = () => {
  const [step, setStep] = useState('input'); // input -> followup -> analyze
  const [text, setText] = useState('');
  const [extractedSymptoms, setExtractedSymptoms] = useState([]);
  const [followupState, setFollowupState] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { setAnalysisResult } = useAnalysis();
  const navigate = useNavigate();

  const handleExtract = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    setLoading(true);
    setError('');
    
    try {
      const data = await analysisApi.extractSymptoms(text);
      const recognizedSymptoms = data.recognized_symptoms || [];

      if (recognizedSymptoms.length === 0) {
        setError('No medical symptoms could be extracted from your text. Please be more specific.');
        setLoading(false);
        return;
      }
      setExtractedSymptoms(recognizedSymptoms);
      
      // Try to start followup
      const followupData = await followupApi.startFollowup(recognizedSymptoms);
      if (followupData.complete === false && followupData.question) {
        setFollowupState(followupData.state);
        setCurrentQuestion(followupData.question);
        setStep('followup');
      } else {
        // No followups needed, proceed to predict
        handleFinalAnalysis(recognizedSymptoms);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to extract symptoms.');
    } finally {
      if (step !== 'followup') setLoading(false);
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
        setStep('followup');
      } else {
        // Follow-ups complete, get updated symptoms from session and predict
        const finalSymptoms = data.state?.recognized_symptoms || extractedSymptoms;
        handleFinalAnalysis(finalSymptoms);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit answer.');
    } finally {
      setLoading(false);
    }
  };

  const handleFinalAnalysis = async (symptoms) => {
    setLoading(true);
    setStep('analyze');
    try {
      const data = await analysisApi.predict(symptoms);
      // Wait for 1 second just for UX transition
      setTimeout(() => {
        setAnalysisResult(data);
        navigate(`/analysis-result`);
      }, 1000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate analysis.');
      setStep('input');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      
      {/* Progress Steps */}
      <div className="mb-10">
        <div className="flex items-center justify-center space-x-4">
          <div className={`flex items-center gap-2 ${step === 'input' ? 'text-teal-600 font-bold' : 'text-slate-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'input' ? 'bg-teal-100' : 'bg-slate-100'}`}>1</div>
            <span className="hidden sm:inline">Describe Symptoms</span>
          </div>
          <div className="w-12 h-px bg-slate-300"></div>
          <div className={`flex items-center gap-2 ${step === 'followup' ? 'text-teal-600 font-bold' : 'text-slate-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'followup' ? 'bg-teal-100' : 'bg-slate-100'}`}>2</div>
            <span className="hidden sm:inline">Follow-up</span>
          </div>
          <div className="w-12 h-px bg-slate-300"></div>
          <div className={`flex items-center gap-2 ${step === 'analyze' ? 'text-teal-600 font-bold' : 'text-slate-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'analyze' ? 'bg-teal-100' : 'bg-slate-100'}`}>3</div>
            <span className="hidden sm:inline">Results</span>
          </div>
        </div>
      </div>

      <ErrorMessage message={error} />

      {step === 'input' && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 md:p-8">
          <div className="mb-6 text-center">
            <h2 className="text-2xl font-bold text-slate-800">What brings you here today?</h2>
            <p className="text-slate-500 mt-2">Describe your symptoms in your own words. For example, "I have had a sharp headache and slight fever since yesterday."</p>
          </div>
          <form onSubmit={handleExtract}>
            <textarea
              className="w-full h-40 p-4 border border-slate-300 rounded-lg focus:ring-teal-500 focus:border-teal-500 text-lg resize-none mb-4"
              placeholder="I feel..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              disabled={loading}
              required
            />
            <button
              type="submit" disabled={loading}
              className="w-full flex justify-center items-center gap-2 py-3 px-4 rounded-lg text-white font-semibold bg-teal-600 hover:bg-teal-700 disabled:bg-teal-400 transition-colors"
            >
              {loading ? <><Loader2 className="w-5 h-5 animate-spin" /> Processing...</> : <><ArrowRight className="w-5 h-5" /> Analyze Symptoms</>}
            </button>
          </form>
        </div>
      )}

      {step === 'followup' && currentQuestion && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 md:p-8 text-center max-w-2xl mx-auto">
          <ClipboardList className="w-12 h-12 text-teal-600 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-slate-800 mb-6">{currentQuestion.text}</h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {currentQuestion.type === 'yes_no' ? (
              <>
                <button
                  onClick={() => handleAnswer('yes')}
                  disabled={loading}
                  className="py-3 px-4 border-2 border-slate-200 rounded-lg font-medium text-slate-700 hover:border-teal-500 hover:bg-teal-50 transition-colors"
                >
                  Yes
                </button>
                <button
                  onClick={() => handleAnswer('no')}
                  disabled={loading}
                  className="py-3 px-4 border-2 border-slate-200 rounded-lg font-medium text-slate-700 hover:border-teal-500 hover:bg-teal-50 transition-colors"
                >
                  No
                </button>
              </>
            ) : (
              (currentQuestion.options || []).map((opt, idx) => (
                <button
                  key={idx}
                  onClick={() => handleAnswer(opt)}
                  disabled={loading}
                  className="py-3 px-4 border-2 border-slate-200 rounded-lg font-medium text-slate-700 hover:border-teal-500 hover:bg-teal-50 transition-colors"
                >
                  {opt}
                </button>
              ))
            )}
          </div>
        </div>
      )}

      {step === 'analyze' && (
        <div className="text-center py-12">
          <LoadingSpinner text="Generating your personalized medical analysis..." />
        </div>
      )}

    </div>
  );
};

export default SymptomChecker;
