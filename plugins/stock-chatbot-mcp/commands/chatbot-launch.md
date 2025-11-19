---
name: chatbot-launch
description: Launch a production-ready stock analysis chatbot with Vercel AI SDK and MCP integration
---

Create and launch a sophisticated stock analysis chatbot application with the following components:

## Project Initialization
1. Create a Next.js 14+ project with TypeScript and App Router
2. Set up TailwindCSS and shadcn/ui for styling
3. Configure environment variables for API keys and MCP endpoints

## Dependencies Installation
Install required dependencies:
- `ai` - Vercel AI SDK for streaming and tool calling
- `@ai-sdk/anthropic` - Anthropic provider for Claude models
- `@modelcontextprotocol/sdk` - MCP SDK for tool integration
- `zod` - Schema validation
- `zustand` (optional) - State management
- Other UI libraries as needed

## Core Implementation

### 1. API Route for Chat
Create `/app/api/chat/route.ts` with:
- Streaming text generation using Vercel AI SDK
- Integration with MCP tools for stock analysis
- Tool definitions for financial operations
- Error handling and rate limiting
- Conversation context management

### 2. Chat UI Component
Create `/app/components/chat.tsx` with:
- Message list with streaming support
- Input field with validation
- Tool call visualization
- Chart rendering for financial data
- Loading states and error handling
- Export functionality

### 3. MCP Client Setup
Create `/lib/mcp-client.ts` with:
- MCP client initialization
- SSE transport configuration
- Tool discovery and registration
- Error handling and reconnection logic
- Caching layer for performance

### 4. Stock Analysis Tools
Implement tool wrappers for:
- `analyzeStock` - Get technical indicators and price data
- `backtestStrategy` - Run backtesting on historical data
- `optimizePortfolio` - Create optimized portfolios
- `screenStocks` - Filter stocks by criteria
- `getMarketData` - Fetch real-time market information
- `compareStocks` - Compare multiple stocks

### 5. Data Visualization
Create chart components for:
- Price charts (candlestick, line, area)
- Technical indicator overlays
- Portfolio allocation pie charts
- Performance comparison charts
- Volume and market depth visualizations

## Configuration Files

### Environment Variables (.env.local)
```env
# AI Provider
ANTHROPIC_API_KEY=your_anthropic_key

# MCP Server
MCP_SERVER_URL=http://localhost:8003/sse/
TIINGO_API_KEY=your_tiingo_key

# Optional
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://localhost:5432/stockbot
```

### Next.js Configuration (next.config.js)
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverActions: true,
  },
}

module.exports = nextConfig
```

### TailwindCSS Configuration
Set up Tailwind with shadcn/ui presets

## Features to Implement

### Core Chatbot Features
- ✅ Real-time streaming responses
- ✅ Multi-turn conversations with context
- ✅ Tool calling for stock analysis
- ✅ Data visualization in chat
- ✅ Error recovery and retry logic
- ✅ Conversation history
- ✅ Export results (CSV, JSON, PDF)
- ✅ Mobile-responsive design

### Stock Analysis Features
- ✅ Real-time stock price lookup
- ✅ Technical indicator calculation (RSI, MACD, etc.)
- ✅ Portfolio optimization
- ✅ Strategy backtesting
- ✅ Stock screening
- ✅ Market sentiment analysis
- ✅ Correlation analysis
- ✅ Risk assessment

### Advanced Features (Optional)
- User authentication with NextAuth.js
- Persistent conversation history
- Shareable analysis links
- Custom alert creation
- Portfolio tracking
- Watchlist management
- Real-time price alerts
- Multi-user support

## Project Structure
```
stock-chatbot/
├── app/
│   ├── api/
│   │   └── chat/
│   │       └── route.ts          # Streaming chat API
│   ├── components/
│   │   ├── chat.tsx              # Main chat interface
│   │   ├── message.tsx           # Message component
│   │   ├── chart.tsx             # Chart visualizations
│   │   ├── tool-result.tsx       # Tool call results
│   │   └── input.tsx             # Chat input
│   ├── lib/
│   │   ├── mcp-client.ts         # MCP client setup
│   │   ├── tools.ts              # Tool definitions
│   │   ├── utils.ts              # Utility functions
│   │   └── validators.ts         # Zod schemas
│   ├── page.tsx                  # Home page
│   └── layout.tsx                # Root layout
├── public/
│   └── assets/
├── .env.local                    # Environment variables
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## Setup Instructions

### 1. Prerequisites
- Node.js 18+ installed
- MaverickMCP server running (http://localhost:8003)
- Anthropic API key
- Tiingo API key (for stock data)

### 2. Installation Steps
```bash
# Create Next.js project
npx create-next-app@latest stock-chatbot --typescript --tailwind --app

# Navigate to project
cd stock-chatbot

# Install dependencies
npm install ai @ai-sdk/anthropic @modelcontextprotocol/sdk zod

# Install UI components
npx shadcn-ui@latest init
npx shadcn-ui@latest add button input card scroll-area

# Install chart library
npm install recharts

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API keys
```

### 3. Start MaverickMCP Server
```bash
# In a separate terminal, start the MCP server
cd /path/to/maverick-mcp
make dev
```

### 4. Run Development Server
```bash
npm run dev
```

Visit http://localhost:3000 to see your chatbot

## Testing the Chatbot

### Example Queries
1. **Basic Analysis**: "Analyze AAPL stock and show me the RSI and MACD indicators"
2. **Backtesting**: "Backtest a momentum strategy on TSLA for the last year"
3. **Portfolio**: "Create an optimized portfolio with 10 tech stocks focusing on risk-adjusted returns"
4. **Screening**: "Find undervalued stocks in the healthcare sector with P/E ratio under 15"
5. **Comparison**: "Compare the performance of AAPL, MSFT, and GOOGL over the past 6 months"
6. **Market Analysis**: "What's the current market sentiment for the S&P 500?"

### Verification Steps
- ✅ Chat interface loads without errors
- ✅ Messages stream in real-time
- ✅ Stock analysis tools are called correctly
- ✅ Charts render with accurate data
- ✅ Multi-turn conversations maintain context
- ✅ Error messages are clear and helpful
- ✅ Mobile layout is responsive

## Deployment

### Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard
# - ANTHROPIC_API_KEY
# - MCP_SERVER_URL (use public URL if MCP server is hosted)
# - TIINGO_API_KEY
```

### Production Considerations
- Use production MCP server URL (not localhost)
- Enable rate limiting
- Set up monitoring and error tracking
- Configure CORS appropriately
- Use Redis for caching
- Implement user authentication
- Set up database for conversation history
- Enable HTTPS only
- Configure CDN for static assets

## Troubleshooting

### MCP Connection Issues
- Verify MCP server is running
- Check MCP_SERVER_URL in .env.local
- Ensure trailing slash in SSE URL
- Check CORS configuration
- Verify network connectivity

### Streaming Not Working
- Check AI SDK version (4.2+)
- Verify API keys are correct
- Test with simpler prompts first
- Check browser console for errors
- Verify streaming is enabled in API route

### Tools Not Being Called
- Check tool definitions in API route
- Verify MCP server has tools registered
- Test MCP tools directly
- Check tool parameter schemas
- Review conversation context

## Next Steps
1. Add user authentication
2. Implement conversation persistence
3. Create custom visualizations
4. Add more financial tools
5. Integrate additional data sources
6. Implement real-time price alerts
7. Create portfolio tracking features
8. Add multi-language support

## Resources
- [Vercel AI SDK Docs](https://sdk.vercel.ai/docs)
- [MCP SDK Documentation](https://modelcontextprotocol.io/docs)
- [MaverickMCP GitHub](https://github.com/cecvic/maverick-mcp)
- [Next.js App Router Docs](https://nextjs.org/docs/app)
- [shadcn/ui Components](https://ui.shadcn.com/)
