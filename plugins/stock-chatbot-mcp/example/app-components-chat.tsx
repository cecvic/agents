// app/components/chat.tsx
'use client'

import { useChat } from 'ai/react'
import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, TrendingUp } from 'lucide-react'

export function Chat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading, error } = useChat({
    api: '/api/chat',
    onError: (error) => {
      console.error('Chat error:', error)
    },
  })

  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6 pb-4 border-b">
        <div className="p-2 bg-blue-500 rounded-lg">
          <TrendingUp className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Stock Analysis Chatbot</h1>
          <p className="text-sm text-gray-600">
            Powered by MaverickMCP & Claude 3.5 Sonnet
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-6">
              Ask me anything about stocks, technical analysis, or portfolio optimization!
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
              {exampleQueries.map((query, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    handleInputChange({
                      target: { value: query },
                    } as React.ChangeEvent<HTMLInputElement>)
                  }}
                  className="p-3 text-left text-sm border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  {query}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-4 ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <div className="text-sm font-semibold mb-1">
                {message.role === 'user' ? 'You' : 'Analyst'}
              </div>
              <div className="whitespace-pre-wrap">
                {message.content}
              </div>

              {/* Tool calls visualization */}
              {message.toolInvocations && message.toolInvocations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-300 space-y-2">
                  {message.toolInvocations.map((tool, idx) => (
                    <div key={idx} className="text-xs">
                      <div className="flex items-center gap-2 font-mono">
                        <span className="text-gray-600">🔧</span>
                        <span className="font-semibold">{tool.toolName}</span>
                        {tool.state === 'call' && (
                          <Loader2 className="w-3 h-3 animate-spin" />
                        )}
                        {tool.state === 'result' && (
                          <span className="text-green-600">✓</span>
                        )}
                      </div>
                      {tool.state === 'result' && tool.result && (
                        <div className="mt-1 p-2 bg-white/50 rounded text-xs overflow-x-auto">
                          <pre>{JSON.stringify(tool.result, null, 2)}</pre>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-4">
              <Loader2 className="w-5 h-5 animate-spin text-gray-600" />
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-600 text-sm">
              <strong>Error:</strong> {error.message}
            </p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={handleInputChange}
          placeholder="Ask about stock analysis, backtesting, or portfolio optimization..."
          className="flex-1 px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              <Send className="w-5 h-5" />
              Send
            </>
          )}
        </button>
      </form>

      {/* Disclaimer */}
      <p className="text-xs text-gray-500 text-center mt-4">
        This chatbot provides informational analysis only, not financial advice.
        Consult licensed advisors for investment decisions.
      </p>
    </div>
  )
}

const exampleQueries = [
  'Analyze AAPL stock with RSI and MACD indicators',
  'Backtest a momentum strategy on TSLA for the last year',
  'Create an optimized portfolio with 5 tech stocks',
  'Find undervalued stocks in the healthcare sector',
]
