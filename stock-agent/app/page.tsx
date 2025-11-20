'use client';

import { useChat } from '@ai-sdk/react';
import ReactMarkdown from 'react-markdown';
import { useRef, useEffect, useState } from 'react';

export default function Home() {
  const { messages, sendMessage, status } = useChat();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    sendMessage({ role: 'user', parts: [{ type: 'text', text: input }] });
    setInput('');
  };

  const isLoading = status === 'submitted' || status === 'streaming';

  // Helper function to extract text content from message parts
  const getMessageText = (message: any) => {
    if (!message.parts) return '';
    return message.parts
      .filter((part: any) => part.type === 'text')
      .map((part: any) => part.text)
      .join('');
  };

  // Helper function to get tool invocations from message parts
  const getToolInvocations = (message: any) => {
    if (!message.parts) return [];
    return message.parts.filter(
      (part: any) => part.type === 'tool-invocation' || part.type === 'tool-result'
    );
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700">
        <div className="max-w-5xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"
                />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                Stock Research AI
              </h1>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Powered by Maverick MCP Server
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-4 rounded-2xl inline-block mb-4">
                <svg
                  className="w-12 h-12 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-200 mb-2">
                Welcome to Stock Research AI
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-6 max-w-md mx-auto">
                Ask me anything about stocks! I can fetch real-time data, perform
                technical analysis, and help you make informed decisions.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
                {[
                  'What is the current price of AAPL?',
                  'Show me RSI analysis for TSLA',
                  'Find bullish stocks using Maverick setup',
                  'Analyze support and resistance for NVDA',
                ].map((suggestion, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(suggestion)}
                    className="text-left p-3 bg-white dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600 hover:border-blue-500 dark:hover:border-blue-400 hover:shadow-md transition-all duration-200 text-sm text-slate-700 dark:text-slate-300"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-4 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                      <svg
                        className="w-5 h-5 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                        />
                      </svg>
                    </div>
                  )}

                  <div
                    className={`flex-1 max-w-3xl ${
                      message.role === 'user' ? 'max-w-xl' : ''
                    }`}
                  >
                    <div
                      className={`rounded-2xl px-5 py-3 ${
                        message.role === 'user'
                          ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white'
                          : 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm border border-slate-200 dark:border-slate-600'
                      }`}
                    >
                      {message.role === 'user' ? (
                        <p className="text-white">{getMessageText(message)}</p>
                      ) : (
                        <div className="prose prose-slate dark:prose-invert max-w-none prose-pre:bg-slate-100 dark:prose-pre:bg-slate-800 prose-pre:text-slate-800 dark:prose-pre:text-slate-100">
                          <ReactMarkdown>{getMessageText(message)}</ReactMarkdown>
                        </div>
                      )}

                      {/* Tool Invocations */}
                      {getToolInvocations(message).length > 0 && (
                        <div className="mt-4 space-y-2">
                          {getToolInvocations(message).map((part: any, idx: number) => {
                            const isInvocation = part.type === 'tool-invocation';
                            const isResult = part.type === 'tool-result';

                            return (
                              <div
                                key={idx}
                                className="bg-slate-50 dark:bg-slate-800 rounded-lg p-3 border border-slate-200 dark:border-slate-600"
                              >
                                <div className="flex items-center gap-2 mb-2">
                                  {isResult || part.state === 'done' ? (
                                    <svg
                                      className="w-4 h-4 text-green-500"
                                      fill="none"
                                      stroke="currentColor"
                                      viewBox="0 0 24 24"
                                    >
                                      <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M5 13l4 4L19 7"
                                      />
                                    </svg>
                                  ) : (
                                    <svg
                                      className="w-4 h-4 text-blue-500 animate-spin"
                                      fill="none"
                                      viewBox="0 0 24 24"
                                    >
                                      <circle
                                        className="opacity-25"
                                        cx="12"
                                        cy="12"
                                        r="10"
                                        stroke="currentColor"
                                        strokeWidth="4"
                                      />
                                      <path
                                        className="opacity-75"
                                        fill="currentColor"
                                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                      />
                                    </svg>
                                  )}
                                  <span className="font-mono text-sm font-semibold text-slate-700 dark:text-slate-300">
                                    {part.toolName || 'Tool'}
                                  </span>
                                  <span className="text-xs text-slate-500 dark:text-slate-400">
                                    {isResult || part.state === 'done' ? '✓ Complete' : '⏳ Running...'}
                                  </span>
                                </div>

                                {isInvocation && part.args && (
                                  <div className="text-xs text-slate-600 dark:text-slate-400 mb-2">
                                    <span className="font-semibold">Args:</span>{' '}
                                    <code className="bg-slate-200 dark:bg-slate-700 px-1 py-0.5 rounded">
                                      {JSON.stringify(part.args)}
                                    </code>
                                  </div>
                                )}

                                {isResult && part.result && (
                                  <div className="mt-2 text-xs">
                                    <div className="font-semibold text-slate-700 dark:text-slate-300 mb-1">
                                      Result:
                                    </div>
                                    <pre className="bg-slate-100 dark:bg-slate-900 p-2 rounded text-slate-800 dark:text-slate-200 overflow-x-auto">
                                      {typeof part.result === 'string'
                                        ? part.result
                                        : JSON.stringify(part.result, null, 2)}
                                    </pre>
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  </div>

                  {message.role === 'user' && (
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-green-500 to-teal-600 flex items-center justify-center">
                      <svg
                        className="w-5 h-5 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                        />
                      </svg>
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Input Form */}
      <div className="border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
        <div className="max-w-5xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about stocks, technical analysis, or market trends..."
              disabled={isLoading}
              className="flex-1 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 px-4 py-3 text-slate-900 dark:text-slate-100 placeholder-slate-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="bg-gradient-to-br from-blue-500 to-purple-600 text-white px-6 py-3 rounded-xl font-medium hover:from-blue-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <svg
                    className="w-5 h-5 animate-spin"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Thinking...
                </>
              ) : (
                <>
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                    />
                  </svg>
                  Send
                </>
              )}
            </button>
          </form>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 text-center">
            {isLoading
              ? 'AI is analyzing your request...'
              : 'Powered by OpenAI GPT-4 and Maverick MCP Server'}
          </p>
        </div>
      </div>
    </div>
  );
}
