// app/api/chat/route.ts
import { streamText } from 'ai'
import { anthropic } from '@ai-sdk/anthropic'
import { getStockAnalysisTools } from '@/lib/tools'

export const runtime = 'edge'
export const maxDuration = 60

export async function POST(req: Request) {
  try {
    const { messages } = await req.json()

    // Get MCP tools for stock analysis
    const tools = await getStockAnalysisTools()

    const result = await streamText({
      model: anthropic('claude-3-5-sonnet-20241022'),
      messages,
      system: `You are a professional stock market analyst with access to real-time financial data and analysis tools via MaverickMCP.

Your capabilities include:
- Real-time stock price and volume data
- Technical indicators (RSI, MACD, Bollinger Bands, Moving Averages, etc.)
- Strategy backtesting with historical data
- Portfolio optimization and risk assessment
- Stock screening and filtering
- Market correlation analysis

Guidelines:
- Always cite data sources and timestamps
- Explain technical indicators in accessible language
- Provide context for recommendations
- Highlight risks and uncertainties
- Use tools to fetch real-time data before responding
- Create visualizations when helpful
- Include relevant disclaimers about investment advice

Remember: This is informational analysis only, not financial advice. Users should consult licensed advisors for investment decisions.`,
      tools,
      maxToolRoundtrips: 5,
      temperature: 0.7,
      onFinish: ({ usage, finishReason }) => {
        console.log('Token usage:', usage)
        console.log('Finish reason:', finishReason)
      },
    })

    return result.toDataStreamResponse()
  } catch (error) {
    console.error('Chat API error:', error)

    return new Response(
      JSON.stringify({
        error: 'Failed to process request',
        details: error instanceof Error ? error.message : 'Unknown error'
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }
}
