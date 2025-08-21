// src/components/SafeChatPanel.jsx
import React, { useState } from 'react';
import { Button } from "@/components/ui/button.jsx";
import { Input } from "@/components/ui/input.jsx";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card.jsx";
import { Badge } from "@/components/ui/badge.jsx";
import { Alert, AlertDescription } from "@/components/ui/alert.jsx";
import { 
  Send, 
  Loader2, 
  AlertCircle, 
  CheckCircle, 
  Clock, 
  ExternalLink,
  Bot,
  User 
} from "lucide-react";
import { researchSearch } from "../lib/research.js";
import { JsonBlock } from "./JsonBlock.jsx";

export function SafeChatPanel() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: input.trim(),
      timestamp: Date.now() / 1000
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const result = await researchSearch(input.trim());
      
      const assistantMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: result,
        timestamp: Date.now() / 1000,
        isResearchResult: true
      };

      setMessages(prev => [...prev, assistantMessage]);
      setInput("");
    } catch (err) {
      console.error('Research error:', err);
      setError(err.message);
      
      const errorMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: `Sorry, I encountered an error: ${err.message}`,
        timestamp: Date.now() / 1000,
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !loading) {
      handleSend();
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleTimeString();
  };

  const renderResearchResult = (result) => {
    if (!result || typeof result !== 'object') {
      return <div className="text-red-400">Invalid result format</div>;
    }

    const hasErrors = result.errors && result.errors.length > 0;
    const hasResults = result.results && result.results.length > 0;

    return (
      <div className="space-y-3">
        {/* Status Badge */}
        <div className="flex items-center gap-2">
          <Badge 
            variant={result.status === 'success' ? 'default' : 'destructive'}
            className="capitalize"
          >
            {result.status === 'success' ? (
              <CheckCircle className="h-3 w-3 mr-1" />
            ) : (
              <AlertCircle className="h-3 w-3 mr-1" />
            )}
            {result.status}
          </Badge>
          {result.execution_time_ms && (
            <Badge variant="outline">
              <Clock className="h-3 w-3 mr-1" />
              {result.execution_time_ms}ms
            </Badge>
          )}
        </div>

        {/* Query */}
        {result.query && (
          <div className="text-sm opacity-80">
            <strong>Query:</strong> <code className="bg-black/20 px-1 py-0.5 rounded">{result.query}</code>
          </div>
        )}

        {/* Errors */}
        {hasErrors && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              <div className="space-y-1">
                {result.errors.map((error, idx) => (
                  <div key={idx} className="text-sm">
                    {error.provider && <strong>[{error.provider}]</strong>} 
                    {error.code}: {error.message || 'Unknown error'}
                  </div>
                ))}
              </div>
            </AlertDescription>
          </Alert>
        )}

        {/* Results */}
        {hasResults && (
          <div className="space-y-2">
            <h4 className="font-medium text-sm">Results ({result.results.length})</h4>
            <div className="space-y-2">
              {result.results.map((item, idx) => (
                <div key={idx} className="border border-white/10 rounded-lg p-3 space-y-2">
                  <div className="flex items-start justify-between">
                    <h5 className="font-medium text-sm leading-tight">
                      {item.title || 'Untitled'}
                    </h5>
                    {item.url && (
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:text-blue-300 ml-2 flex-shrink-0"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    )}
                  </div>
                  {item.snippet && (
                    <p className="text-sm opacity-80">
                      {item.snippet}
                    </p>
                  )}
                  {item.url && (
                    <p className="text-xs opacity-60 truncate">
                      {item.url}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Summary */}
        {result.summary && result.summary.text && (
          <div className="space-y-1">
            <h4 className="font-medium text-sm">Summary</h4>
            <p className="text-sm opacity-80">{result.summary.text}</p>
            {result.summary.confidence > 0 && (
              <p className="text-xs opacity-60">
                Confidence: {Math.round(result.summary.confidence * 100)}%
              </p>
            )}
          </div>
        )}

        {/* Raw JSON */}
        <JsonBlock data={result} />
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      {/* Header */}
      <div className="p-4 border-b border-white/10">
        <h2 className="text-xl font-semibold">SOPHIA Research Intelligence</h2>
        <p className="text-sm opacity-70">Direct connection to research services</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8 opacity-60">
            <Bot className="h-12 w-12 mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Welcome to SOPHIA Research</h3>
            <p className="text-sm">Ask me to research any topic and I'll provide structured results</p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start space-x-3 ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {message.role === "assistant" && (
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                  <Bot className="h-4 w-4 text-white" />
                </div>
              </div>
            )}

            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                message.role === "user"
                  ? "bg-blue-600 text-white ml-auto"
                  : message.isError
                    ? "bg-red-900/50 border border-red-500/50"
                    : "bg-gray-800/50 border border-white/10"
              }`}
            >
              {message.role === "user" ? (
                <div className="text-sm">{message.content}</div>
              ) : message.isResearchResult ? (
                renderResearchResult(message.content)
              ) : (
                <div className="text-sm">{message.content}</div>
              )}

              {/* Timestamp */}
              <div className="flex items-center justify-between mt-2 pt-2 border-t border-white/10">
                <div className="flex items-center space-x-2 text-xs opacity-60">
                  <Clock className="h-3 w-3" />
                  <span>{formatTimestamp(message.timestamp)}</span>
                </div>
              </div>
            </div>

            {message.role === "user" && (
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
                  <User className="h-4 w-4 text-white" />
                </div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-start space-x-3 justify-start">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                <Bot className="h-4 w-4 text-white" />
              </div>
            </div>
            <div className="bg-gray-800/50 border border-white/10 rounded-2xl px-4 py-3">
              <div className="flex items-center space-x-2 text-sm">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Researching...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-white/10">
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="flex gap-2">
          <Input
            placeholder="Ask SOPHIA to research anything..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
            className="flex-1"
          />
          <Button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-6"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

export default SafeChatPanel;

