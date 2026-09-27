import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { AnalysisProvider } from './context/AnalysisContext';

import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';

import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import SymptomChecker from './pages/SymptomChecker';
import PainAssessment from './pages/PainAssessment';
import MenstruationTracking from './pages/MenstruationTracking';
import MoodTracking from './pages/MoodTracking';
import DoctorConsultation from './pages/DoctorConsultation';
import MedicalReports from './pages/MedicalReports';
import AnalysisResult from './pages/AnalysisResult';
import ChatAssistant from './pages/ChatAssistant';
import History from './pages/History';
import ChatHistory from './pages/ChatHistory';
import Profile from './pages/Profile';

function App() {
  return (
    <Router>
      <AuthProvider>
        <AnalysisProvider>
          <div className="flex flex-col min-h-screen bg-slate-50">
            <Navbar />
            <div className="flex-grow">
              <Routes>
                {/* Public Routes */}
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                
                <Route path="/symptom-checker" element={<SymptomChecker />} />
                <Route path="/pain-assessment" element={<PainAssessment />} />
                <Route path="/menstruation" element={<MenstruationTracking />} />
                <Route path="/mood" element={<MoodTracking />} />
                <Route path="/consultation" element={<DoctorConsultation />} />
                <Route path="/reports" element={<MedicalReports />} />
                <Route path="/analysis-result" element={<AnalysisResult />} />
                <Route path="/analysis/:id" element={<AnalysisResult />} />
                <Route path="/chat-assistant" element={<ChatAssistant />} />

                {/* Protected Routes */}
                <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
                <Route path="/chat-history" element={<ProtectedRoute><ChatHistory /></ProtectedRoute>} />
                <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
              </Routes>
            </div>
            <Footer />
          </div>
        </AnalysisProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
