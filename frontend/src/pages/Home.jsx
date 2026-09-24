import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldPlus, Brain, Activity, ArrowRight } from 'lucide-react';
import Disclaimer from '../components/Disclaimer';

const Home = () => {
  return (
    <div className="flex flex-col min-h-[calc(100vh-4rem)] bg-slate-50">
      <main className="flex-grow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-24 text-center">
          <h1 className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight mb-6">
            AI Medical Symptom <span className="text-teal-600">Checker</span>
          </h1>
          <p className="max-w-2xl mx-auto text-xl text-slate-600 mb-10">
            Describe your symptoms naturally and our AI will extract relevant medical terms, ask dynamic follow-up questions and provide potential conditions and specialist recommendations.
          </p>
          <div className="flex justify-center gap-4">
            <Link to="/register" className="inline-flex items-center gap-2 bg-teal-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-teal-700 transition-colors shadow-sm">
              Get Started <ArrowRight className="w-5 h-5" />
            </Link>
            <Link to="/login" className="inline-flex items-center gap-2 bg-white text-slate-700 border border-slate-300 px-6 py-3 rounded-lg font-semibold hover:bg-slate-50 transition-colors shadow-sm">
              Log In
            </Link>
          </div>
        </div>

        <div className="bg-white py-16 border-t border-slate-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="p-6 bg-slate-50 rounded-xl border border-slate-100">
                <Brain className="w-10 h-10 text-teal-600 mb-4" />
                <h3 className="text-lg font-bold text-slate-800 mb-2">Natural Language</h3>
                <p className="text-slate-600">Simply describe how you feel in your own words. Our NLP engine will translate it into medical terminology.</p>
              </div>
              <div className="p-6 bg-slate-50 rounded-xl border border-slate-100">
                <Activity className="w-10 h-10 text-teal-600 mb-4" />
                <h3 className="text-lg font-bold text-slate-800 mb-2">Smart Analysis</h3>
                <p className="text-slate-600">Utilizing trained machine learning models to assess potential conditions based on your symptom profile.</p>
              </div>
              <div className="p-6 bg-slate-50 rounded-xl border border-slate-100">
                <ShieldPlus className="w-10 h-10 text-teal-600 mb-4" />
                <h3 className="text-lg font-bold text-slate-800 mb-2">Secure & Private</h3>
                <p className="text-slate-600">Your health data and conversation history is securely stored and entirely private to your account.</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <div className="max-w-3xl mx-auto w-full px-4 mb-8">
        <Disclaimer />
      </div>
    </div>
  );
};

export default Home;
