import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisApi } from '../api/analysisApi';
import { followupApi } from '../api/followupApi';
import { imageApi } from '../api/imageApi';
import { reportApi } from '../api/reportApi';
import { authApi } from '../api/authApi';
import { useAnalysis } from '../context/AnalysisContext';
import { useAuth } from '../context/AuthContext';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import { ArrowRight, MessageSquare, ClipboardList, Send, Loader2, AlertTriangle, CheckCircle, Camera, Upload, Trash2, Image as ImageIcon } from 'lucide-react';

const getErrorMessage = (err, fallback) => {
  const detail = err?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return 'Validation Error: ' + detail.map(d => d.msg).join(', ');
  } else if (typeof detail === 'string') {
    return detail;
  }
  return fallback;
};

const SymptomChecker = () => {
  const { user, setUser } = useAuth();
  const [step, setStep] = useState('demographics'); // demographics -> input -> review -> followup -> analyze
  const [text, setText] = useState('');
  const [extractedSymptoms, setExtractedSymptoms] = useState([]);
  const [detailedSymptoms, setDetailedSymptoms] = useState([]);
  
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [uploadedImageId, setUploadedImageId] = useState(null);
  const [imageConsent, setImageConsent] = useState(false);
  const [imageObservations, setImageObservations] = useState(null);
  const [imageUploading, setImageUploading] = useState(false);
  
  const [availableReports, setAvailableReports] = useState([]);
  const [selectedReportId, setSelectedReportId] = useState('');
  const [attachedReportContext, setAttachedReportContext] = useState(null);

  const [patientType, setPatientType] = useState('general');
  const [age, setAge] = useState('');
  const [ageUnit, setAgeUnit] = useState('years');
  const [gender, setGender] = useState('');
  const [isEditingDetails, setIsEditingDetails] = useState(true);
  const [followupState, setFollowupState] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [modelMetadata, setModelMetadata] = useState(null);
  
  React.useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const data = await analysisApi.getModelMetadata();
        setModelMetadata(data);
      } catch (err) {
        console.error("Failed to fetch model metadata", err);
      }
    };
    const fetchReports = async () => {
      try {
        const data = await reportApi.getReports();
        // Only allow attaching successfully extracted reports
        setAvailableReports(data.filter(r => r.status === 'extracted'));
      } catch (err) {
        console.error("Failed to fetch reports", err);
      }
    };
    fetchMetadata();
    fetchReports();
  }, []);

  React.useEffect(() => {
    if (user && (user.age || user.gender || user.patient_type)) {
      if (user.patient_type) setPatientType(user.patient_type);
      if (user.age) setAge(user.age);
      if (user.age_unit) setAgeUnit(user.age_unit);
      if (user.gender) setGender(user.gender);
      setIsEditingDetails(false);
    } else {
      setIsEditingDetails(true);
    }
  }, [user]);
  
  const { setAnalysisResult } = useAnalysis();
  const navigate = useNavigate();

  const handleExtract = async (e) => {
    e.preventDefault();
    if (!text.trim()) {
      setError('Please enter your symptoms in the text box.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      // If consent is given and image is uploaded, get observations first
      if (uploadedImageId && imageConsent) {
        try {
          const obsData = await imageApi.analyzeImage(uploadedImageId);
          setImageObservations(obsData.observations);
        } catch (imgErr) {
          console.error("Image analysis failed:", imgErr);
          // We don't fail the whole request, just proceed without observations or show error
          // But prompt says "Errors do not erase the user's already-entered symptoms."
          setError('Image analysis failed, but symptom extraction will continue.');
        }
      }

      if (selectedReportId) {
        try {
          const report = availableReports.find(r => r.id === selectedReportId);
          if (report) {
             // We can just use the extracted text, or summarize it
             // Let's attach the extracted text or a quick blurb
             setAttachedReportContext(report.extracted_text ? "Attached Report Text:\n" + report.extracted_text.substring(0, 1000) + "..." : "Report attached but no text available.");
          }
        } catch (repErr) {
          console.error("Report attachment failed:", repErr);
        }
      }

      const data = await analysisApi.extractSymptoms(text);
      const recognizedSymptoms = data.recognized_symptoms || [];
      const detailed = data.detailed_symptoms || [];

      if (recognizedSymptoms.length === 0) {
        setError('No medical symptoms could be extracted from your text. Please be more specific.');
        setLoading(false);
        return;
      }
      setExtractedSymptoms(recognizedSymptoms);
      setDetailedSymptoms(detailed);
      
      setStep('review');
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to extract symptoms.'));
    } finally {
      setLoading(false);
    }
  };

  const handleImageSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setError('Invalid file type. Only JPEG, PNG, and WebP are supported.');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError('File is too large. Maximum size is 5MB.');
      return;
    }

    setPreviewUrl(URL.createObjectURL(file));
    setSelectedImage(file);
    setError('');
    setImageUploading(true);

    try {
      const data = await imageApi.uploadImage(file);
      setUploadedImageId(data.id);
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to upload image.'));
      handleRemoveImage();
    } finally {
      setImageUploading(false);
    }
  };

  const handleRemoveImage = async () => {
    if (uploadedImageId) {
      try { await imageApi.deleteImage(uploadedImageId); } catch(e) {}
    }
    setSelectedImage(null);
    setPreviewUrl('');
    setUploadedImageId(null);
    setImageConsent(false);
    setImageObservations(null);
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
        // Follow-ups complete, get updated symptoms from session and predict
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
      const data = await analysisApi.predict(symptoms, demographics);
      // Wait for 1 second just for UX transition
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
      
      {/* Progress Steps */}
      <div className="mb-10">
        <div className="flex flex-wrap items-center justify-center space-x-2 md:space-x-4">
          <div className={`flex items-center gap-2 ${step === 'demographics' ? 'text-teal-600 font-bold' : 'text-slate-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'demographics' ? 'bg-teal-100' : 'bg-slate-100'}`}>1</div>
            <span className="hidden sm:inline">Details</span>
          </div>
          <div className="w-8 md:w-12 h-px bg-slate-300"></div>
          <div className={`flex items-center gap-2 ${step === 'input' ? 'text-teal-600 font-bold' : 'text-slate-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'input' ? 'bg-teal-100' : 'bg-slate-100'}`}>2</div>
            <span className="hidden sm:inline">Input</span>
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
          <div className="w-8 md:w-12 h-px bg-slate-300"></div>
          <div className={`flex items-center gap-2 ${step === 'analyze' ? 'text-teal-600 font-bold' : 'text-slate-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'analyze' ? 'bg-teal-100' : 'bg-slate-100'}`}>5</div>
            <span className="hidden sm:inline">Results</span>
          </div>
        </div>
      </div>

      <ErrorMessage message={error} />

      {step === 'demographics' && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 md:p-8">
          <div className="mb-6 text-center">
            <h2 className="text-2xl font-bold text-slate-800">Who is this assessment for?</h2>
            <p className="text-slate-500 mt-2">Providing age helps us use the right safety rules and follow-up questions.</p>
          </div>
          <div className="space-y-6 max-w-lg mx-auto">
            
            {!isEditingDetails && user ? (
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-6">
                <h3 className="font-bold text-lg text-slate-800 mb-4">Your Details</h3>
                <div className="space-y-3 mb-6 text-slate-700">
                  <div className="flex justify-between border-b border-slate-200 pb-2">
                    <span className="font-semibold">Patient Type:</span>
                    <span className="capitalize">{user.patient_type === 'newborn' ? 'Newborn / Infant' : 'Adult / Child (2+ yrs)'}</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-200 pb-2">
                    <span className="font-semibold">Age:</span>
                    <span>{user.age ? `${user.age} ${user.age_unit}` : 'Not provided'}</span>
                  </div>
                  <div className="flex justify-between pb-2">
                    <span className="font-semibold">Gender:</span>
                    <span className="capitalize">{user.gender || 'Not provided'}</span>
                  </div>
                </div>
                <div className="flex gap-4">
                  <button onClick={() => setIsEditingDetails(true)} className="flex-1 py-3 px-4 rounded-lg text-slate-700 font-semibold bg-white border border-slate-300 hover:bg-slate-50 transition-colors">
                    Edit Details
                  </button>
                  <button onClick={() => { setError(''); setStep('input'); }} className="flex-1 flex justify-center items-center gap-2 py-3 px-4 rounded-lg text-white font-semibold bg-teal-600 hover:bg-teal-700 transition-colors">
                    Continue <ArrowRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ) : (
              <>
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
                  type="number"
                  min="0"
                  max="120"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  className="w-full p-3 border border-slate-300 rounded-lg focus:ring-teal-500 focus:border-teal-500"
                  placeholder="e.g. 30"
                  required={patientType === 'newborn'}
                />
                <select
                  value={ageUnit}
                  onChange={(e) => setAgeUnit(e.target.value)}
                  className="p-3 border border-slate-300 rounded-lg focus:ring-teal-500 focus:border-teal-500 bg-white"
                >
                  {patientType === 'general' ? (
                    <option value="years">Years</option>
                  ) : (
                    <>
                      <option value="months">Months</option>
                      <option value="weeks">Weeks</option>
                      <option value="days">Days</option>
                    </>
                  )}
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Gender (Optional)</label>
              <select
                value={gender}
                onChange={(e) => setGender(e.target.value)}
                className="w-full p-3 border border-slate-300 rounded-lg focus:ring-teal-500 focus:border-teal-500 bg-white"
              >
                <option value="">Select Gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
                <option value="prefer_not_to_say">Prefer not to say</option>
              </select>
            </div>
            
            {patientType === 'general' && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
                <span className="font-semibold block mb-1">Please note:</span>
                Our current AI model may not be trained specifically for demographic-specific predictions. We do not claim age or gender improves diagnostic accuracy at this stage.
              </div>
            )}
            {patientType === 'newborn' && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
                <span className="font-semibold block mb-1">Important:</span>
                The AI symptom checker model is not used for infants. Only age-appropriate safety guidelines and specialist recommendations will be provided.
              </div>
            )}

            <div className="flex gap-4 pt-4">
              {patientType === 'general' && (
                <button
                  onClick={() => { setAge(''); setGender(''); setStep('input'); }}
                  className="flex-1 py-3 px-4 rounded-lg text-slate-700 font-semibold bg-slate-100 hover:bg-slate-200 transition-colors"
                >
                  Skip
                </button>
              )}
              <button
                onClick={async () => {
                  if (patientType === 'newborn' && !age) {
                    setError('Age is required for newborns and infants.');
                    return;
                  }
                  setError('');
                  
                  if (user) {
                    try {
                      const updatedUser = await authApi.updateMe({
                        patient_type: patientType,
                        age: age ? parseInt(age) : null,
                        age_unit: ageUnit,
                        gender: gender || null
                      });
                      setUser(updatedUser);
                    } catch (err) {
                      console.error("Failed to save demographic data", err);
                    }
                  }
                  
                  setStep('input');
                }}
                className={`${patientType === 'general' ? 'flex-1' : 'w-full'} flex justify-center items-center gap-2 py-3 px-4 rounded-lg text-white font-semibold bg-teal-600 hover:bg-teal-700 transition-colors`}
              >
                {patientType === 'general' ? 'Save & Continue' : 'Continue to Symptoms'} <ArrowRight className="w-5 h-5" />
              </button>
            </div>
            </>
          )}
          </div>
        </div>
      )}

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
            
            {/* Image Upload Section */}
            {user ? (
              <div className="mb-6 p-4 border border-slate-200 rounded-lg bg-slate-50">
                <div className="flex items-center gap-2 mb-2">
                  <Camera className="w-5 h-5 text-slate-600" />
                  <h3 className="font-bold text-slate-800">Optional: Attach an Image</h3>
                </div>
                <p className="text-xs text-slate-500 mb-4">
                  You can attach an image (e.g., a rash, swelling). We support JPEG, PNG, and WebP up to 5MB. 
                  <br/><strong>Note:</strong> Do not upload images containing intimate areas or highly sensitive content.
                </p>
                
                {!selectedImage ? (
                  <div>
                    <input type="file" accept="image/jpeg, image/png, image/webp" id="image-upload" className="hidden" onChange={handleImageSelect} disabled={imageUploading || loading} />
                    <label htmlFor="image-upload" className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-slate-300 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 cursor-pointer">
                      <Upload className="w-4 h-4" /> {imageUploading ? 'Uploading...' : 'Select Image'}
                    </label>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="flex items-start gap-4">
                      <div className="relative w-24 h-24 border border-slate-300 rounded bg-white overflow-hidden flex-shrink-0">
                        {previewUrl ? <img src={previewUrl} alt="Preview" className="w-full h-full object-cover" /> : <ImageIcon className="w-8 h-8 m-auto text-slate-300 mt-8" />}
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-medium text-slate-800 break-all">{selectedImage.name}</div>
                        <div className="text-xs text-slate-500 mb-2">
                          {imageUploading ? <span className="text-amber-600">Uploading...</span> : <span className="text-teal-600 flex items-center gap-1"><CheckCircle className="w-3 h-3"/> Uploaded</span>}
                        </div>
                        <button type="button" onClick={handleRemoveImage} disabled={imageUploading || loading} className="text-xs text-red-600 font-medium hover:text-red-800 flex items-center gap-1">
                          <Trash2 className="w-3 h-3"/> Remove
                        </button>
                      </div>
                    </div>
                    
                    {uploadedImageId && (
                      <div className="bg-white p-3 border border-slate-200 rounded-lg">
                        <label className="flex items-start gap-3 cursor-pointer">
                          <input type="checkbox" checked={imageConsent} onChange={(e) => setImageConsent(e.target.checked)} className="mt-1 w-4 h-4 text-teal-600 rounded border-slate-300 focus:ring-teal-500" />
                          <div className="text-sm text-slate-700">
                            <strong>I consent</strong> to sending this image to an AI vision model for visual observations. 
                            I understand that the output will describe visual features only, will not provide a medical diagnosis, and may contain inaccuracies.
                          </div>
                        </label>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="mb-6 p-4 border border-slate-200 rounded-lg bg-slate-50 text-sm text-slate-600 flex items-start gap-2">
                <AlertTriangle className="w-5 h-5 flex-shrink-0 text-slate-400" />
                <div>
                  <strong>Optional: Attach an Image</strong><br/>
                  <span className="text-slate-500">Log in to securely upload images of symptoms (e.g. rash, swelling) for AI visual analysis.</span>
                </div>
              </div>
            )}
            
            {/* Report Attachment Section */}
            {user ? (
              availableReports.length > 0 && (
                <div className="mb-6 p-4 border border-slate-200 rounded-lg bg-slate-50">
                  <div className="flex items-center gap-2 mb-2">
                    <ClipboardList className="w-5 h-5 text-slate-600" />
                    <h3 className="font-bold text-slate-800">Optional: Attach a Medical Report</h3>
                  </div>
                  <p className="text-xs text-slate-500 mb-4">
                    You can include text from a previously uploaded medical report to provide more context. This remains separate from the symptom prediction.
                  </p>
                  <select
                    value={selectedReportId}
                    onChange={(e) => setSelectedReportId(e.target.value)}
                    className="w-full p-2 border border-slate-300 rounded-lg bg-white"
                    disabled={loading}
                  >
                    <option value="">-- No report attached --</option>
                    {availableReports.map(r => (
                      <option key={r.id} value={r.id}>{r.filename}</option>
                    ))}
                  </select>
                </div>
              )
            ) : (
              <div className="mb-6 p-4 border border-slate-200 rounded-lg bg-slate-50 text-sm text-slate-600 flex items-start gap-2">
                <AlertTriangle className="w-5 h-5 flex-shrink-0 text-slate-400" />
                <div>
                  <strong>Optional: Attach a Medical Report</strong><br/>
                  <span className="text-slate-500">Log in to securely upload and attach medical reports for additional context.</span>
                </div>
              </div>
            )}

            <button
              type="submit" disabled={loading || imageUploading}
              className="w-full flex justify-center items-center gap-2 py-3 px-4 rounded-lg text-white font-semibold bg-teal-600 hover:bg-teal-700 disabled:bg-teal-400 transition-colors"
            >
              {loading ? <><Loader2 className="w-5 h-5 animate-spin" /> Processing...</> : <><ArrowRight className="w-5 h-5" /> Analyze Symptoms</>}
            </button>
          </form>
          {modelMetadata && (
            <div className="mt-6 text-center text-sm text-slate-500">
              <p>Model Version: {modelMetadata.model_version}</p>
              <p>Supported Features: {modelMetadata.total_features} | Supported Conditions: {modelMetadata.total_conditions}</p>
            </div>
          )}
        </div>
      )}

      {step === 'review' && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 md:p-8">
          <div className="mb-6 text-center">
            <h2 className="text-2xl font-bold text-slate-800">Review Recognized Symptoms</h2>
            <p className="text-slate-500 mt-2">Here is what we understood from your input. Please review before proceeding.</p>
          </div>
          
          <div className="space-y-3 mb-6">
            {detailedSymptoms.map((sym, idx) => (
              <div key={idx} className="flex flex-col sm:flex-row justify-between items-start sm:items-center p-4 border rounded-lg bg-slate-50 border-slate-200">
                <div>
                  <div className="font-bold text-slate-800 capitalize">{sym.canonical}</div>
                  <div className="text-sm text-slate-500">From text: "{sym.original_phrase}" | Category: {sym.category || "General"} | Source: {sym.source || "Model Vocabulary"}</div>
                  {!sym.is_model_supported && (
                    <div className="text-xs text-yellow-600 mt-1 font-semibold flex items-center gap-1">
                      <AlertTriangle className="w-3 h-3" />
                      Recognized, but not supported by our current prediction model.
                    </div>
                  )}
                  {sym.is_model_supported && (
                    <div className="text-xs text-teal-600 mt-1 font-semibold flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" />
                      Supported by prediction model.
                    </div>
                  )}
                </div>
                <button type="button" onClick={() => removeSymptom(sym.canonical)} className="mt-2 sm:mt-0 text-red-500 hover:text-red-700 text-sm font-medium">
                  Remove
                </button>
              </div>
            ))}
          </div>

          {imageObservations && (
            <div className="mb-6 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
              <h3 className="font-bold text-indigo-900 mb-2 flex items-center gap-2">
                <ImageIcon className="w-5 h-5"/> Image Observations (AI Generated)
              </h3>
              <p className="text-sm text-indigo-800 whitespace-pre-wrap">{imageObservations}</p>
              <div className="mt-3 text-xs text-indigo-600 border-t border-indigo-200 pt-2 font-semibold">
                Disclaimer: These are visual observations only and do not constitute a medical diagnosis. They are kept separate from the symptom prediction model.
              </div>
            </div>
          )}

          {attachedReportContext && (
            <div className="mb-6 p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
              <h3 className="font-bold text-emerald-900 mb-2 flex items-center gap-2">
                <ClipboardList className="w-5 h-5"/> Attached Report Context
              </h3>
              <p className="text-sm text-emerald-800 whitespace-pre-wrap">{attachedReportContext}</p>
              <div className="mt-3 text-xs text-emerald-600 border-t border-emerald-200 pt-2 font-semibold">
                Disclaimer: The report context is displayed for your review and is kept separate from the deterministic symptom prediction model.
              </div>
            </div>
          )}

          {!detailedSymptoms.some(s => s.is_model_supported) && detailedSymptoms.length > 0 && (
            <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-lg text-sm">
              <strong>Note:</strong> None of the symptoms recognized are directly supported by our current model. You can still proceed to receive an analysis, but the model may have limited coverage and cannot analyze these symptoms directly.
            </div>
          )}

          <div className="flex gap-4">
            <button
              onClick={() => setStep('input')}
              disabled={loading}
              className="flex-1 py-3 px-4 rounded-lg text-slate-700 font-semibold bg-slate-100 hover:bg-slate-200 transition-colors"
            >
              Back
            </button>
            <button
              onClick={handleProceedFromReview}
              disabled={loading || extractedSymptoms.length === 0}
              className="flex-1 flex justify-center items-center gap-2 py-3 px-4 rounded-lg text-white font-semibold bg-teal-600 hover:bg-teal-700 disabled:bg-teal-400 transition-colors"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Continue to Follow-up'}
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
