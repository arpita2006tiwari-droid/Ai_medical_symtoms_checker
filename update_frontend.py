import re

with open("frontend/src/pages/SymptomChecker.jsx", "r") as f:
    content = f.read()

# Replace state initialization
state_init = """  const [step, setStep] = useState('input'); // input -> review -> followup -> analyze
  const [text, setText] = useState('');
  const [extractedSymptoms, setExtractedSymptoms] = useState([]);
  const [detailedSymptoms, setDetailedSymptoms] = useState([]);"""

content = re.sub(
    r"const \[step, setStep\] = useState\('input'\);.*?const \[extractedSymptoms, setExtractedSymptoms\] = useState\(\[\]\);",
    state_init,
    content,
    flags=re.DOTALL
)

# Replace handleExtract
handle_extract_new = """  const handleExtract = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    setLoading(true);
    setError('');
    
    try {
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
      setError(err.response?.data?.detail || 'Failed to extract symptoms.');
    } finally {
      setLoading(false);
    }
  };

  const handleProceedFromReview = async () => {
    setLoading(true);
    setError('');
    try {
      // Only proceed with the symptoms that haven't been removed
      // (They are already in extractedSymptoms state)
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
      setError(err.response?.data?.detail || 'Failed to start follow-up.');
    } finally {
      if (step !== 'followup') setLoading(false);
    }
  };

  const removeSymptom = (canonical) => {
    setExtractedSymptoms(prev => prev.filter(s => s !== canonical));
    setDetailedSymptoms(prev => prev.filter(s => s.canonical !== canonical));
  };
"""

content = re.sub(
    r"const handleExtract = async \(e\) => \{.*?finally \{\s*if \(step !== 'followup'\) setLoading\(false\);\s*\}\s*\};",
    handle_extract_new,
    content,
    flags=re.DOTALL
)

# Update step indicators
steps_ui = """      {/* Progress Steps */}
      <div className="mb-10">
        <div className="flex flex-wrap items-center justify-center space-x-2 md:space-x-4">
          <div className={`flex items-center gap-2 ${step === 'input' ? 'text-teal-600 font-bold' : 'text-slate-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'input' ? 'bg-teal-100' : 'bg-slate-100'}`}>1</div>
            <span className="hidden sm:inline">Input</span>
          </div>
          <div className="w-8 md:w-12 h-px bg-slate-300"></div>
          <div className={`flex items-center gap-2 ${step === 'review' ? 'text-teal-600 font-bold' : 'text-slate-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'review' ? 'bg-teal-100' : 'bg-slate-100'}`}>2</div>
            <span className="hidden sm:inline">Review</span>
          </div>
          <div className="w-8 md:w-12 h-px bg-slate-300"></div>
          <div className={`flex items-center gap-2 ${step === 'followup' ? 'text-teal-600 font-bold' : 'text-slate-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'followup' ? 'bg-teal-100' : 'bg-slate-100'}`}>3</div>
            <span className="hidden sm:inline">Follow-up</span>
          </div>
          <div className="w-8 md:w-12 h-px bg-slate-300"></div>
          <div className={`flex items-center gap-2 ${step === 'analyze' ? 'text-teal-600 font-bold' : 'text-slate-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'analyze' ? 'bg-teal-100' : 'bg-slate-100'}`}>4</div>
            <span className="hidden sm:inline">Results</span>
          </div>
        </div>
      </div>"""

content = re.sub(
    r"\{\/\* Progress Steps \*\/\}.*?<\/div>\s*<\/div>",
    steps_ui,
    content,
    flags=re.DOTALL
)

# Add review step UI
review_ui = """      {step === 'review' && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 md:p-8">
          <div className="mb-6 text-center">
            <h2 className="text-2xl font-bold text-slate-800">Review Recognized Symptoms</h2>
            <p className="text-slate-500 mt-2">Here is what we understood from your input. Please review before proceeding.</p>
          </div>
          
          <div className="space-y-3 mb-8">
            {detailedSymptoms.map((sym, idx) => (
              <div key={idx} className="flex flex-col sm:flex-row justify-between items-start sm:items-center p-4 border rounded-lg bg-slate-50 border-slate-200">
                <div>
                  <div className="font-bold text-slate-800 capitalize">{sym.canonical}</div>
                  <div className="text-sm text-slate-500">From text: "{sym.original_phrase}"</div>
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
                <button onClick={() => removeSymptom(sym.canonical)} className="mt-2 sm:mt-0 text-red-500 hover:text-red-700 text-sm font-medium">
                  Remove
                </button>
              </div>
            ))}
          </div>

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

      {step === 'followup'"""

content = content.replace("{step === 'followup'", review_ui)

# Add AlertTriangle and CheckCircle to lucide-react imports if missing
if "AlertTriangle" not in content:
    content = content.replace("Loader2 } from 'lucide-react'", "Loader2, AlertTriangle, CheckCircle } from 'lucide-react'")

with open("frontend/src/pages/SymptomChecker.jsx", "w") as f:
    f.write(content)
