import React from 'react';
import { ShieldAlert } from 'lucide-react';

const Disclaimer = ({ className = "" }) => {
  return (
    <div className={`bg-amber-50 border border-amber-200 rounded-lg p-4 flex gap-3 ${className}`}>
      <ShieldAlert className="w-6 h-6 text-amber-600 flex-shrink-0" />
      <div>
        <h4 className="text-sm font-semibold text-amber-800">Important Medical Disclaimer</h4>
        <p className="text-sm text-amber-700 mt-1">
          This tool provides preliminary informational guidance based on the symptoms entered. It does <strong>not</strong> provide a medical diagnosis, prescription, or definitive medical advice. If you have severe, worsening, or emergency symptoms, seek professional medical care immediately.
        </p>
      </div>
    </div>
  );
};

export default Disclaimer;
