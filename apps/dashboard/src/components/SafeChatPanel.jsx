import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { RESEARCH_URL, CONTEXT_URL } from '../config';
import JsonBlock from './JsonBlock';

export default function SafeChatPanel() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input, timestamp: Date.now() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Call research service directly - NO RAILWAY ANYWHERE
      const response = await fetch(`${RESEARCH_URL}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: input,
          max_sources: 5
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Ensure we never get [object Object] by proper handling
      const assistantMessage = {
        role: 'assistant',
        content: data,
        timestamp: Date.now(),
        raw: data
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Research error:', error);
      const errorMessage = {
        role: 'assistant',
        content: {
          status: 'error',
          error: error.message,
          query: input
        },
        timestamp: Date.now(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const renderMessage = (message) => {
    if (message.role === 'user') {
      return (
        <div className="bg-blue-600 text-white p-3 rounded-lg max-w-[80%] ml-auto">
          {message.content}
        </div>
      );
    }

    // Assistant message - render structured data safely
    const data = message.content;
    
    if (message.isError) {
      return (
        <div className="bg-red-900/50 border border-red-500 p-4 rounded-lg max-w-[90%]">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-4 h-4 text-red-400" />
            <span className="text-red-400 font-medium">Error</span>
          </div>
          <div className="text-gray-300">
            {data.error || 'Unknown error occurred'}
          </div>
          <details className="mt-2">
            <summary className="text-xs text-gray-400 cursor-pointer">Raw JSON</summary>
            <pre className="bg-black/40 p-3 rounded overflow-auto text-xs mt-1">
              {JSON.stringify(data, null, 2)}
            </pre>
          </details>
        </div>
      );
    }

    return (
      <div className="bg-gray-800 border border-gray-600 p-4 rounded-lg max-w-[90%]">
        <div className="flex items-center gap-2 mb-3">
          <CheckCircle className="w-4 h-4 text-green-400" />
          <span className="text-green-400 font-medium">SOPHIA Research</span>
        </div>
        
        {data.status && (
          <div className="mb-3">
            <span className="text-sm text-gray-400">Status: </span>
            <span className={`text-sm font-medium ${data.status === 'success' ? 'text-green-400' : 'text-yellow-400'}`}>
              {data.status}
            </span>
          </div>
        )}

        {data.summary?.text && (
          <div className="mb-3">
            <h4 className="text-sm font-medium text-gray-300 mb-1">Summary:</h4>
            <p className="text-gray-100">{data.summary.text}</p>
          </div>
        )}

        {data.results && Array.isArray(data.results) && data.results.length > 0 && (
          <div className="mb-3">
            <h4 className="text-sm font-medium text-gray-300 mb-2">
              Sources ({data.results.length}):
            </h4>
            <div className="space-y-2">
              {data.results.map((result, idx) => (
                <div key={idx} className="bg-gray-900/50 p-2 rounded border border-gray-700">
                  {result.title && (
                    <div className="text-sm font-medium text-blue-400 mb-1">
                      {result.title}
                    </div>
                  )}
                  {result.snippet && (
                    <div className="text-xs text-gray-300 mb-1">
                      {result.snippet}
                    </div>
                  )}
                  {result.url && (
                    <div className="text-xs text-gray-500">
                      {result.url}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <details>
          <summary className="text-xs text-gray-400 cursor-pointer">Raw JSON</summary>
          <pre className="bg-black/40 p-3 rounded overflow-auto text-xs mt-1">
            {JSON.stringify(data, null, 2)}
          </pre>
        </details>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold">SOPHIA Research Intelligence</h2>
        <p className="text-sm text-gray-400">
          Connected to: {RESEARCH_URL} (NO RAILWAY!)
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p>Ask SOPHIA for research and business intelligence...</p>
            <p className="text-xs mt-2">✅ Railway completely eliminated</p>
          </div>
        )}
        
        {messages.map((message, idx) => (
          <div key={idx} className="flex">
            {renderMessage(message)}
          </div>
        ))}
        
        {loading && (
          <div className="flex items-center gap-2 text-gray-400">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>SOPHIA is researching...</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask SOPHIA for business intelligence..."
            className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed px-4 py-2 rounded-lg transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
}

