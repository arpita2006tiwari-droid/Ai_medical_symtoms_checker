import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { historyApi } from '../api/historyApi';
import LoadingSpinner from '../components/LoadingSpinner';

import { MessageSquare, ChevronRight, Trash2 } from 'lucide-react';

const ChatHistory = () => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await historyApi.getConversations(0, 100);
      setConversations(Array.isArray(data) ? data : (data.conversations || []));
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (window.confirm('Delete this conversation?')) {
      try {
        await historyApi.deleteConversation(id);
        fetchHistory();
      } catch (err) {
        console.error(err);
      }
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 min-h-[calc(100vh-10rem)]">
      <div className="flex items-center gap-3 mb-8">
        <div className="p-3 bg-teal-100 text-teal-700 rounded-lg">
          <MessageSquare className="w-6 h-6" />
        </div>
        <h1 className="text-3xl font-bold text-slate-800">Chat History</h1>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : conversations.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border border-slate-200">
          <p className="text-slate-500">No chat history found.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 divide-y divide-slate-100">
          {conversations.map((c) => (
            <div key={c.id} className="p-4 sm:p-6 hover:bg-slate-50 transition-colors flex justify-between items-center cursor-pointer group" onClick={() => navigate(`/chat-assistant`, { state: { conversationId: c.id } })}>
              <div>
                <p className="text-sm text-slate-500 mb-1">
                  {new Intl.DateTimeFormat('en-IN', {
                    timeZone: 'Asia/Kolkata',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: 'numeric',
                    minute: '2-digit',
                    hour12: true
                  }).format(new Date(c.created_at))}
                </p>
                <h3 className="text-lg font-semibold text-slate-800 line-clamp-1">
                  {c.title || 'Conversation'}
                </h3>
              </div>
              <div className="flex items-center gap-4">
                <button 
                  onClick={(e) => handleDelete(e, c.id)}
                  className="p-2 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-full transition-colors opacity-0 group-hover:opacity-100"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
                <ChevronRight className="w-6 h-6 text-slate-400" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatHistory;
