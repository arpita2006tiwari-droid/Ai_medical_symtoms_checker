import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisApi } from '../api/analysisApi';
import { followupApi } from '../api/followupApi';
import { painAssessmentApi } from '../api/painAssessmentApi';
import { useAnalysis } from '../context/AnalysisContext';
import { useAuth } from '../context/AuthContext';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import { ArrowRight, ClipboardList, Loader2, AlertTriangle, CheckCircle } from 'lucide-react';

const getErrorMessage = (err, fallback) => {
  const detail = err?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return 'Validation Error: ' + detail.map(d => d.msg).join(', ');
  } else if (typeof detail === 'string') {
    return detail;
  }
  return fallback;
};

const PainAssessment = () => {
  const { user } = useAuth();
  const [step, setStep] = useState('demographics'); // demographics -> input -> review -> followup -> analyze
  
  const [patientType, setPatientType] = useState('general');
  const [age, setAge] = useState('');
  const [ageUnit, setAgeUnit] = useState('years');
  const [gender, setGender] = useState('');

  // Pain Form State
  const [formData, setFormData] = useState({
    body_region: '',
    pain_type: '',
    severity: 5,
    onset_duration: '',
    frequency: '',
    trend: '',
    associated_symptoms: '',
    notes: ''
  });
  
  const [extractedSymptoms, setExtractedSymptoms] = useState([]);
  const [detailedSymptoms, setDetailedSymptoms] = useState([]);
  const [savedAssessmentId, setSavedAssessmentId] = useState(null);
  
  const [followupState, setFollowupState] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { setAnalysisResult } = useAnalysis();
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleExtract = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    // Construct text from form
    const assoc = formData.associated_symptoms.trim() ? `Associated symptoms: ${formData.associated_symptoms}. ` : '';
    const notes = formData.notes.trim() ? `Notes: ${formData.notes}.` : '';
    const text = `I have ${formData.severity}/10 ${formData.pain_type} pain in my ${formData.body_region}. It started ${formData.onset_duration}. It is ${formData.frequency} and ${formData.trend}. ${assoc}${notes}`;

    try {
      // If user is authenticated, save the assessment
      if (user) {
        const assocArray = formData.associated_symptoms.split(',').map(s => s.trim()).filter(Boolean);
        const saved = await painAssessmentApi.create({
          ...formData,
          associated_symptoms: assocArray,
          age: age ? parseInt(age) : null,
          age_unit: ageUnit,
          gender: gender || null,
          patient_type: patientType
        });
        setSavedAssessmentId(saved.id);
      }

      const data = await analysisApi.extractSymptoms(text);
      const recognizedSymptoms = data.recognized_symptoms || [];
      const detailed = data.detailed_symptoms || [];

      if (recognizedSymptoms.length === 0) {
        // Fallback: use body region and pain type directly if extraction fails
        const fallbackSymptom = `${formData.body_region} pain`.toLowerCase();
        setExtractedSymptoms([fallbackSymptom]);
        setDetailedSymptoms([{
          canonical: fallbackSymptom,
          original_phrase: text,
          category: "General",
          source: "Fallback",
          is_model_supported: true
        }]);
      } else {
        setExtractedSymptoms(recognizedSymptoms);
        setDetailedSymptoms(detailed);
      }
      
      setStep('review');
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to process pain assessment.'));
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
        setLoading(false);
        return;
      }
      
      const followupData = await followupApi.startFollowup(extractedSymptoms);
      if (followupData.complete === false && followupData.question) {
        setFollowupState(followupData.state);
        setCurrentQuestion(followupData.question);
        setStep('followup');
      } else {
        handleFinalAnalysis(extractedSymptoms);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to start follow-up.'));
    } finally {
      if (step !== 'followup') setLoading(false);
    }
  };

  const removeSymptom = (canonical) => {
    setExtractedSymptoms(prev => prev.filter(s => s !== canonical));
    setDetailedSymptoms(prev => prev.filter(s => s.canonical !== canonical));
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
        const finalSymptoms = data.state?.recognized_symptoms || extractedSymptoms;
        handleFinalAnalysis(finalSymptoms);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to submit answer.'));
    } finally {
      setLoading(false);
    }
  };

  const handleFinalAnalysis = async (symptoms) => {
    setLoading(true);
    setStep('analyze');
    try {
      const demographics = {
        age: age ? parseInt(age) : null,
        age_unit: ageUnit,
        gender: gender || null,
        patient_type: patientType
      };
      
      // Perform final analysis
      const data = await analysisApi.predict(symptoms, demographics);
      
      // Update saved assessment with analysis ID if logged in
      if (savedAssessmentId && user) {
        try {
          await painAssessmentApi.update(savedAssessmentId, { analysis_id: data.id });
        } catch (e) {
          console.error('Could not link analysis to pain assessment', e);
        }
      }

      setTimeout(() => {
        setAnalysisResult(data);
        navigate(`/analysis-result`);
      }, 1000);
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to generate analysis.'));
      setStep('input');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-teal-800">Body Cramps & Pain Assessment</h1>
        <p className="text-slate-600 mt-2 max-w-2xl mx-auto">
          Detailed pain tracking helps provide more accurate severity assessments. 
          <br/><strong>Disclaimer:</strong> This is for educational purposes and is not a clinical diagnosis. Seek emergency care for severe, sudden, or crushing chest/abdominal pain.
        </p>
      </div>

      {/* Progress Steps */}
      {!user && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6 text-sm text-yellow-800 flex items-start gap-2">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <div>You are using Guest Mode. You can complete a pain assessment and analyze symptoms temporarily, but your assessment will not be saved.</div>
        </div>
      )}
      <div className="mb-10">
        <div className="flex flex-wrap items-center justify-center space-x-2 md:space-x-4">
          <div className={`flex items-center gap-2 ${step === 'demographics' ? 'text-teal-600 font-bold' : 'text-slate-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'demographics' ? 'bg-teal-100' : 'bg-slate-100'}`}>1</div>
            <span className="hidden sm:inline">Details</span>
          </div>
          <div className="w-8 md:w-12 h-px bg-slate-300"></div>
          <div className={`flex items-center gap-2 ${step === 'input' ? 'text-teal-600 font-bold' : 'text-slate-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'input' ? 'bg-teal-100' : 'bg-slate-100'}`}>2</div>
            <span className="hidden sm:inline">Assessment</span>
          </div>
          <div className="w-8 md:w-12 h-px bg-slate-300"></div>
          <div className={`flex items-center gap-2 ${step === 'review' ? 'text-teal-600 font-bold' : 'text-slate-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'review' ? 'bg-teal-100' : 'bg-slate-100'}`}>3</div>
            <span className="hidden sm:inline">Review</span>
          </div>
          <div className="w-8 md:w-12 h-px bg-slate-300"></div>
          <div className={`flex items-center gap-2 ${step === 'followup' ? 'text-teal-600 font-bold' : 'text-slate-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'followup' ? 'bg-teal-100' : 'bg-slate-100'}`}>4</div>
            <span className="hidden sm:inline">Follow-up</span>
          </div>
        </div>
      </div>

      <ErrorMessage message={error} />

      {step === 'demographics' && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 md:p-8">
          <div className="mb-6 text-center">
            <h2 className="text-2xl font-bold text-slate-800">Who is this assessment for?</h2>
          </div>
          <div className="space-y-6 max-w-lg mx-auto">
            <div className="flex gap-4 mb-6">
              <button
                onClick={() => { setPatientType('general'); setAgeUnit('years'); }}
                className={`flex-1 py-3 px-4 rounded-lg border-2 font-semibold transition-colors ${patientType === 'general' ? 'border-teal-600 bg-teal-50 text-teal-700' : 'border-slate-200 text-slate-600 hover:border-slate-300'}`}
              >
                Adult / Child (2+ yrs)
              </button>
              <button
                onClick={() => { setPatientType('newborn'); setAgeUnit('months'); }}
                className={`flex-1 py-3 px-4 rounded-lg border-2 font-semibold transition-colors ${patientType === 'newborn' ? 'border-teal-600 bg-teal-50 text-teal-700' : 'border-slate-200 text-slate-600 hover:border-slate-300'}`}
              >
                Newborn / Infant
              </button>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Age {patientType === 'newborn' ? <span className="text-red-500">* (Required)</span> : '(Optional)'}
              </label>
              <div className="flex gap-2">
                <input
                  type="number" min="0" max="120"
                  value={age} onChange={(e) => setAge(e.target.value)}
                  className="w-full p-3 border border-slate-300 rounded-lg focus:ring-teal-500 focus:border-teal-500"
                  placeholder="e.g. 30" required={patientType === 'newborn'}
                />
                <select
                  value={ageUnit} onChange={(e) => setAgeUnit(e.target.value)}
                  className="p-3 border border-slate-300 rounded-lg bg-white"
                >
                  {patientType === 'general' ? <option value="years">Years</option> : (
                    <><option value="months">Months</option><option value="weeks">Weeks</option><option value="days">Days</option></>
                  )}
                </select>
              </div>
            </div>
            
            <div className="flex gap-4 pt-4">
              {patientType === 'general' && (
                <button
                  onClick={() => { setAge(''); setStep('input'); }}
                  className="flex-1 py-3 px-4 rounded-lg text-slate-700 font-semibold bg-slate-100 hover:bg-slate-200"
                >
                  Skip
                </button>
              )}
              <button
                onClick={() => {
                  if (patientType === 'newborn' && !age) {
                    setError('Age is required for newborns and infants.');
                    return;
                  }
                  setError('');
                  setStep('input');
                }}
                className={`${patientType === 'general' ? 'flex-1' : 'w-full'} flex justify-center items-center gap-2 py-3 px-4 rounded-lg text-white font-semibold bg-teal-600 hover:bg-teal-700`}
              >
                Continue <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      )}

      {step === 'input' && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 md:p-8">
          <form onSubmit={handleExtract} className="space-y-6">
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Body Region *</label>
                <select name="body_region" value={formData.body_region} onChange={handleInputChange} required className="w-full p-3 border border-slate-300 rounded-lg bg-white">
                  <option value="">Select Region</option>
                  <option value="head">Head</option>
                  <option value="chest">Chest</option>
                  <option value="abdomen">Abdomen</option>
                  <option value="pelvis">Pelvis</option>
                  <option value="back">Back</option>
                  <option value="arms">Arms</option>
                  <option value="legs">Legs</option>
                  <option value="joints">Joints</option>
                  <option value="other">Other</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Pain Type *</label>
                <select name="pain_type" value={formData.pain_type} onChange={handleInputChange} required className="w-full p-3 border border-slate-300 rounded-lg bg-white">
                  <option value="">Select Type</option>
                  <option value="cramping">Cramping</option>
                  <option value="sharp">Sharp</option>
                  <option value="dull">Dull / Aching</option>
                  <option value="burning">Burning</option>
                  <option value="pressure">Pressure / Tightness</option>
                  <option value="throbbing">Throbbing</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Severity (0-10) *</label>
              <input type="range" name="severity" min="0" max="10" value={formData.severity} onChange={handleInputChange} className="w-full accent-teal-600" />
              <div className="text-center mt-2 font-bold text-teal-800 text-lg">
                {formData.severity} / 10
              </div>
              <div className="flex justify-between text-xs text-slate-500 px-1">
                <span>0 (None)</span>
                <span>5 (Moderate)</span>
                <span>10 (Severe/Unbearable)</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Onset & Duration *</label>
                <input type="text" name="onset_duration" value={formData.onset_duration} onChange={handleInputChange} placeholder="e.g. Started 2 hours ago" required className="w-full p-3 border border-slate-300 rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Frequency *</label>
                <select name="frequency" value={formData.frequency} onChange={handleInputChange} required className="w-full p-3 border border-slate-300 rounded-lg bg-white">
                  <option value="">Select Frequency</option>
                  <option value="constant">Constant</option>
                  <option value="intermittent">Intermittent (Comes and goes)</option>
                  <option value="occasional">Occasional</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Trend *</label>
                <select name="trend" value={formData.trend} onChange={handleInputChange} required className="w-full p-3 border border-slate-300 rounded-lg bg-white">
                  <option value="">Select Trend</option>
                  <option value="improving">Improving</option>
                  <option value="worsening">Worsening</option>
                  <option value="unchanged">Unchanged</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Associated Symptoms</label>
              <input type="text" name="associated_symptoms" value={formData.associated_symptoms} onChange={handleInputChange} placeholder="e.g. Nausea, fever, sweating (comma separated)" className="w-full p-3 border border-slate-300 rounded-lg" />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Optional Notes</label>
              <textarea name="notes" value={formData.notes} onChange={handleInputChange} placeholder="Any additional context..." className="w-full h-24 p-3 border border-slate-300 rounded-lg resize-none"></textarea>
            </div>

            <button type="submit" disabled={loading} className="w-full flex justify-center items-center gap-2 py-4 px-4 rounded-lg text-white font-semibold bg-teal-600 hover:bg-teal-700 transition-colors">
              {loading ? <><Loader2 className="w-5 h-5 animate-spin" /> Processing...</> : <><ArrowRight className="w-5 h-5" /> Analyze Assessment</>}
            </button>
          </form>
        </div>
      )}

      {/* Review, Followup, and Analyze steps are identical UX to SymptomChecker */}
      {step === 'review' && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 md:p-8">
          <div className="mb-6 text-center">
            <h2 className="text-2xl font-bold text-slate-800">Review Recognized Symptoms</h2>
          </div>
          
          <div className="space-y-3 mb-8">
            {detailedSymptoms.map((sym, idx) => (
              <div key={idx} className="flex justify-between items-center p-4 border rounded-lg bg-slate-50 border-slate-200">
                <div>
                  <div className="font-bold text-slate-800 capitalize">{sym.canonical}</div>
                  {!sym.is_model_supported && (
                    <div className="text-xs text-yellow-600 mt-1 font-semibold flex items-center gap-1">
                      <AlertTriangle className="w-3 h-3" /> Not supported by current prediction model.
                    </div>
                  )}
                  {sym.is_model_supported && (
                    <div className="text-xs text-teal-600 mt-1 font-semibold flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" /> Supported by prediction model.
                    </div>
                  )}
                </div>
                <button type="button" onClick={() => removeSymptom(sym.canonical)} className="text-red-500 hover:text-red-700 text-sm font-medium">Remove</button>
              </div>
            ))}
          </div>

          <div className="flex gap-4">
            <button onClick={() => setStep('input')} disabled={loading} className="flex-1 py-3 px-4 rounded-lg text-slate-700 font-semibold bg-slate-100 hover:bg-slate-200">Back</button>
            <button onClick={handleProceedFromReview} disabled={loading || extractedSymptoms.length === 0} className="flex-1 flex justify-center items-center gap-2 py-3 px-4 rounded-lg text-white font-semibold bg-teal-600 hover:bg-teal-700">
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Continue'}
            </button>
          </div>
        </div>
      )}

      {step === 'followup' && currentQuestion && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 md:p-8 text-center max-w-2xl mx-auto">
          <ClipboardList className="w-12 h-12 text-teal-600 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-slate-800 mb-6">{currentQuestion.text}</h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {currentQuestion.type === 'yes_no' ? (
              <>
                <button onClick={() => handleAnswer('yes')} disabled={loading} className="py-3 px-4 border-2 border-slate-200 rounded-lg font-medium text-slate-700 hover:border-teal-500 hover:bg-teal-50">Yes</button>
                <button onClick={() => handleAnswer('no')} disabled={loading} className="py-3 px-4 border-2 border-slate-200 rounded-lg font-medium text-slate-700 hover:border-teal-500 hover:bg-teal-50">No</button>
              </>
            ) : (
              (currentQuestion.options || []).map((opt, idx) => (
                <button key={idx} onClick={() => handleAnswer(opt)} disabled={loading} className="py-3 px-4 border-2 border-slate-200 rounded-lg font-medium text-slate-700 hover:border-teal-500 hover:bg-teal-50">{opt}</button>
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

export default PainAssessment;
