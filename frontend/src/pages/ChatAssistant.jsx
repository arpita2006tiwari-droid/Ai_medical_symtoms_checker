import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { chatApi } from '../api/chatApi';
import { historyApi } from '../api/historyApi';
import { Send, Bot, User, ArrowLeft, Loader2 } from 'lucide-react';
import Disclaimer from '../components/Disclaimer';

const ChatAssistant = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  
  const location = useLocation();
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);

  // Initial welcome message
  useEffect(() => {
    setMessages([
      { role: 'assistant', content: 'Hello! I am your AI Medical Assistant. I can help explain your analysis results, answer questions about symptoms, or provide general health information. How can I help you today?' }
    ]);
    
    // If coming from a specific existing conversation
    if (location.state?.conversationId) {
      setConversationId(location.state.conversationId);
      // Fetch conversation history
      const fetchConvo = async () => {
        try {
          const data = await historyApi.getConversationById(location.state.conversationId);
          // format messages for UI (assuming data has a messages array)
          if (data && data.messages) {
            const formatted = data.messages.map(m => ({ role: m.role, content: m.content }));
            setMessages(formatted);
          }
        } catch(e) { console.error(e); }
      };
      fetchConvo();
    }
  }, [location.state]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const data = await chatApi.sendMessage(userMessage, conversationId);
      if (!conversationId && data.conversation_id) {
        setConversationId(data.conversation_id);
      }
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 flex flex-col h-[calc(100vh-5rem)]">
      
      <div className="flex items-center gap-4 mb-4">
        <button onClick={() => navigate(-1)} className="p-2 hover:bg-slate-200 rounded-full transition-colors">
          <ArrowLeft className="w-5 h-5 text-slate-700" />
        </button>
        <h1 className="text-2xl font-bold text-slate-800">AI Health Assistant</h1>
      </div>

      <div className="flex-grow bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col overflow-hidden">
        
        <div className="flex-grow p-4 overflow-y-auto space-y-4 bg-slate-50">
          <Disclaimer className="mb-6 shadow-sm" />
          
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex max-w-[80%] gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-teal-600' : 'bg-slate-800'}`}>
                  {msg.role === 'user' ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-white" />}
                </div>
                <div className={`p-3 rounded-2xl ${msg.role === 'user' ? 'bg-teal-600 text-white rounded-tr-none' : 'bg-white border border-slate-200 text-slate-800 rounded-tl-none shadow-sm'}`}>
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center">
                   <Bot className="w-5 h-5 text-white" />
                </div>
                <div className="p-4 rounded-2xl bg-white border border-slate-200 rounded-tl-none shadow-sm flex items-center gap-2">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 bg-white border-t border-slate-200">
          <form onSubmit={handleSend} className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Ask a health question..."
              className="flex-grow px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
              disabled={loading}
            />
            <button 
              type="submit" 
              disabled={loading || !input.trim()}
              className="bg-teal-600 text-white px-5 py-3 rounded-lg hover:bg-teal-700 transition-colors disabled:bg-slate-300 disabled:text-slate-500 flex items-center justify-center"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
        
      </div>
    </div>
  );
};

export default ChatAssistant;
