import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { reportApi } from '../api/reportApi';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import { FileText, Plus, Trash2, Download, AlertTriangle, FileUp, Loader2, CheckCircle, FileSearch, Sparkles } from 'lucide-react';
import { format, parseISO } from 'date-fns';

const MedicalReports = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  
  const [viewingReport, setViewingReport] = useState(null);
  const [summary, setSummary] = useState(null);
  const [summarizing, setSummarizing] = useState(false);
  const [consentGiven, setConsentGiven] = useState(false);

  useEffect(() => {
    if (user) {
      loadReports();
    }
  }, [user]);

  const loadReports = async () => {
    setLoading(true);
    try {
      const data = await reportApi.getReports();
      setReports(data);
    } catch (err) {
      setError('Failed to load medical reports.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    if (file.size > 10 * 1024 * 1024) {
      setError('File is too large. Maximum size is 10MB.');
      return;
    }
    
    const validMimes = ['application/pdf', 'image/jpeg', 'image/png', 'image/webp'];
    if (!validMimes.includes(file.type)) {
      setError('Invalid format. Please upload PDF, JPEG, PNG, or WebP.');
      return;
    }
    
    setSelectedFile(file);
    setError('');
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true);
    setError('');
    
    try {
      const data = await reportApi.uploadReport(selectedFile);
      setReports([data, ...reports]);
      setSelectedFile(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to permanently delete this report?")) return;
    try {
      await reportApi.deleteReport(id);
      setReports(reports.filter(r => r.id !== id));
      if (viewingReport?.id === id) setViewingReport(null);
    } catch (err) {
      setError('Failed to delete report.');
    }
  };

  const handleDownload = (id) => {
    // Basic download trigger using our authenticated endpoint via standard fetch (or open in new tab if we attach auth token, but we are using HTTP Only cookies typically or bearer token).
    // Given the architecture, an easiest approach is just to fetch blob and download it.
    const token = localStorage.getItem('token');
    fetch(`/api/reports/${id}/content`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => res.blob())
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report-${id}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    })
    .catch(() => setError('Failed to download file.'));
  };

  const handleSummarize = async (id) => {
    if (!consentGiven) return;
    setSummarizing(true);
    setError('');
    try {
      const data = await reportApi.summarizeReport(id);
      setSummary(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to summarize report.');
    } finally {
      setSummarizing(false);
    }
  };

  if (!user) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-10 text-center">
        <AlertTriangle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Login Required</h2>
        <p className="text-slate-600 mb-6">Medical reports contain highly sensitive data and require an authenticated account for secure storage.</p>
        <button onClick={() => navigate('/login')} className="bg-teal-600 text-white px-6 py-2 rounded-lg font-bold">Log In</button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-teal-800 flex justify-center items-center gap-2">
          <FileText className="w-8 h-8 text-teal-600" /> Medical Reports
        </h1>
        <p className="text-slate-600 mt-2 max-w-2xl mx-auto">
          Upload and review your lab results, imaging reports, and medical documents.
        </p>
      </div>

      <ErrorMessage message={error} />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Left Column: Upload & List */}
        <div className="md:col-span-1 space-y-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h3 className="font-bold text-slate-800 mb-4">Upload New Report</h3>
            <div className="space-y-4">
              <input type="file" id="report-upload" accept="application/pdf, image/jpeg, image/png, image/webp" className="hidden" onChange={handleFileSelect} disabled={uploading} />
              <label htmlFor="report-upload" className="flex flex-col items-center justify-center w-full h-32 border-2 border-slate-300 border-dashed rounded-lg cursor-pointer bg-slate-50 hover:bg-slate-100">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <FileUp className="w-8 h-8 text-slate-500 mb-2" />
                  <p className="text-sm text-slate-600"><span className="font-semibold">Click to browse</span></p>
                  <p className="text-xs text-slate-500">PDF, JPG, PNG (Max 10MB)</p>
                </div>
              </label>
              
              {selectedFile && (
                <div className="bg-teal-50 p-3 rounded border border-teal-200">
                  <p className="text-sm text-teal-800 font-medium truncate">{selectedFile.name}</p>
                  <button 
                    onClick={handleUpload}
                    disabled={uploading}
                    className="w-full mt-2 bg-teal-600 text-white py-2 rounded font-semibold flex items-center justify-center gap-2 hover:bg-teal-700"
                  >
                    {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Securely Upload'}
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h3 className="font-bold text-slate-800 mb-4">Your Reports</h3>
            {loading ? <LoadingSpinner /> : reports.length === 0 ? (
              <p className="text-sm text-slate-500 text-center py-4">No reports uploaded yet.</p>
            ) : (
              <div className="space-y-3">
                {reports.map(report => (
                  <div key={report.id} onClick={() => {setViewingReport(report); setSummary(null); setConsentGiven(false); setError('');}} className={`p-3 rounded-lg border cursor-pointer transition-colors ${viewingReport?.id === report.id ? 'border-teal-500 bg-teal-50' : 'border-slate-200 hover:bg-slate-50'}`}>
                    <div className="font-medium text-slate-800 text-sm truncate">{report.filename}</div>
                    <div className="flex justify-between items-center mt-2 text-xs text-slate-500">
                      <span>{format(parseISO(report.created_at), 'MMM d, yyyy')}</span>
                      {report.status === 'extracted' ? (
                        <span className="text-teal-600 flex items-center gap-1"><CheckCircle className="w-3 h-3"/> Ready</span>
                      ) : report.status === 'failed' ? (
                        <span className="text-red-500 flex items-center gap-1"><AlertTriangle className="w-3 h-3"/> Failed</span>
                      ) : (
                        <span className="text-slate-400">Processing</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Viewer */}
        <div className="md:col-span-2">
          {viewingReport ? (
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-full">
              <div className="flex justify-between items-start border-b border-slate-200 pb-4 mb-4">
                <div>
                  <h2 className="text-xl font-bold text-slate-800">{viewingReport.filename}</h2>
                  <p className="text-sm text-slate-500">Uploaded on {format(parseISO(viewingReport.created_at), 'PPP p')} • {(viewingReport.size_bytes / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => handleDownload(viewingReport.id)} className="p-2 text-slate-600 hover:bg-slate-100 rounded" title="Download Original">
                    <Download className="w-5 h-5" />
                  </button>
                  <button onClick={() => handleDelete(viewingReport.id)} className="p-2 text-red-600 hover:bg-red-50 rounded" title="Delete">
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {viewingReport.content_type === 'application/pdf' ? (
                <div className="mb-6">
                  <h3 className="font-bold text-slate-700 flex items-center gap-2 mb-2"><FileSearch className="w-5 h-5"/> Extracted Text</h3>
                  {viewingReport.status === 'failed' ? (
                    <div className="bg-red-50 text-red-700 p-4 rounded border border-red-200 text-sm">
                      We were unable to extract text from this document. It may be encrypted, malformed, or a scanned image lacking digital text.
                    </div>
                  ) : (
                    <div className="bg-slate-50 border border-slate-200 p-4 rounded-lg max-h-96 overflow-y-auto text-sm font-mono text-slate-800 whitespace-pre-wrap">
                      {viewingReport.extracted_text || 'No text content available.'}
                    </div>
                  )}
                </div>
              ) : (
                <div className="mb-6">
                  <h3 className="font-bold text-slate-700 flex items-center gap-2 mb-2"><FileSearch className="w-5 h-5"/> Image File</h3>
                  <div className="bg-slate-50 text-slate-700 p-4 rounded border border-slate-200 text-sm">
                    This is an image file. We do not extract raw text from images natively. You can request an AI summary to extract the visible medical data securely.
                  </div>
                </div>
              )}

              {/* AI Summarization Section */}
              <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-5">
                <h3 className="font-bold text-indigo-900 flex items-center gap-2 mb-3">
                  <Sparkles className="w-5 h-5"/> AI Report Summarization
                </h3>
                
                {summary ? (
                  <div className="space-y-4">
                    <div className="bg-white p-4 rounded border border-indigo-100 text-slate-800 text-sm whitespace-pre-wrap leading-relaxed shadow-sm">
                      {summary.summary}
                    </div>
                    <div className="text-xs text-indigo-700 font-medium">
                      <strong>Disclaimer:</strong> {summary.disclaimer}
                    </div>
                  </div>
                ) : (
                  <div>
                    <p className="text-sm text-indigo-800 mb-4">
                      Our secure AI can read this report and provide a simplified summary. It will strictly preserve your values and units, and will not provide a medical diagnosis.
                    </p>
                    <label className="flex items-start gap-3 cursor-pointer mb-4">
                      <input type="checkbox" checked={consentGiven} onChange={(e) => setConsentGiven(e.target.checked)} className="mt-1 w-4 h-4 text-indigo-600 rounded border-indigo-300 focus:ring-indigo-500" />
                      <div className="text-sm text-indigo-900 font-medium">
                        I explicitly consent to sending the contents of this medical report to the configured AI provider for summarization. I understand it may contain errors.
                      </div>
                    </label>
                    <button 
                      onClick={() => handleSummarize(viewingReport.id)} 
                      disabled={!consentGiven || summarizing || viewingReport.status === 'failed'}
                      className="bg-indigo-600 text-white py-2 px-6 rounded-lg font-semibold hover:bg-indigo-700 disabled:bg-indigo-300 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      {summarizing ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Generate AI Summary'}
                    </button>
                    {viewingReport.status === 'failed' && <p className="text-xs text-red-600 mt-2">Cannot summarize a failed document.</p>}
                  </div>
                )}
              </div>

            </div>
          ) : (
            <div className="bg-slate-50 border border-slate-200 rounded-xl h-full flex items-center justify-center text-slate-400 p-10 text-center">
              <div>
                <FileText className="w-16 h-16 mx-auto mb-4 text-slate-300" />
                <p>Select a report from the list to view its details, extracted text, and AI summary.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MedicalReports;
