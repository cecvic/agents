# Stock Research AI Chat

A powerful stock research web application where users can chat with an AI agent that can fetch real-time stock data and perform technical analysis using the Maverick MCP Server.

## Features

- 🤖 **AI-Powered Chat Interface**: Conversational interface powered by OpenAI GPT-4
- 📊 **Real-Time Stock Data**: Fetch current stock prices, historical data, and market information
- 📈 **Technical Analysis**: RSI, MACD, support/resistance levels, and chart analysis
- 🎯 **Stock Screening**: Find bullish stocks and trending breakout opportunities
- 💼 **Portfolio Management**: Track and manage your stock positions
- 🔧 **Tool Invocation Visibility**: See exactly what tools the AI is using in real-time
- 🎨 **Beautiful UI**: Modern, responsive design with Tailwind CSS and dark mode support
- 📝 **Markdown Support**: Rich formatting for analysis and data tables

## Tech Stack

- **Framework**: Next.js 14+ (App Router) with TypeScript
- **Styling**: Tailwind CSS
- **AI Framework**: Vercel AI SDK Core (`ai` package)
- **Backend**: `streamText` with MCP client integration
- **Frontend**: `useChat` from `@ai-sdk/react` for streaming UI
- **MCP Server**: Maverick (Python-based) running locally via SSE

## Prerequisites

1. **Node.js**: Version 18.17 or higher
2. **OpenAI API Key**: Required for the AI reasoning model
3. **Maverick MCP Server**: Must be running locally on port 8003
   - The Maverick server handles the Tiingo API key internally

## Installation

### 1. Clone and Install Dependencies

```bash
# Navigate to the stock-agent directory
cd stock-agent

# Install dependencies
npm install
```

### 2. Configure Environment Variables

Create a `.env.local` file in the root directory:

```bash
cp .env.example .env.local
```

Edit `.env.local` and add your OpenAI API key:

```env
# OpenAI API Key for AI reasoning model
OPENAI_API_KEY=your_openai_api_key_here

# Maverick MCP Server URL (default: http://localhost:8003/sse)
MAVERICK_MCP_URL=http://localhost:8003/sse
```

### 3. Start the Maverick MCP Server

Ensure your Maverick MCP server is running on `http://localhost:8003/sse`. The application will gracefully handle the case where the server is offline, but stock-related tools won't be available.

### 4. Run the Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Available Stock Tools

The Maverick MCP Server provides the following financial tools:

### Stock Data
- `fetch_stock_data`: Get historical stock data
- `get_news_sentiment`: Analyze news sentiment for stocks

### Technical Analysis
- `get_rsi_analysis`: Calculate Relative Strength Index
- `get_macd_analysis`: Moving Average Convergence Divergence analysis
- `get_support_resistance`: Identify key support and resistance levels
- `get_stock_chart_analysis`: Comprehensive chart analysis

### Stock Screening
- `get_maverick_stocks`: Find stocks with bullish Maverick setup
- `get_trending_breakout_stocks`: Identify trending breakout opportunities

### Portfolio Management
- `portfolio_add_position`: Add stock positions to your portfolio
- `portfolio_get_my_portfolio`: View your current portfolio

## Example Queries

Try asking the AI questions like:

- "What is the current price of AAPL?"
- "Show me RSI analysis for TSLA"
- "Find bullish stocks using Maverick setup"
- "Analyze support and resistance for NVDA"
- "What's the MACD indicator showing for SPY?"
- "Get me trending breakout stocks"
- "Add 100 shares of AAPL to my portfolio at $150"

## Architecture

### API Route (`app/api/chat/route.ts`)

The chat API route handles:
- Connection to Maverick MCP Server via SSE
- Dynamic tool fetching from the MCP server
- Streaming responses with multi-step reasoning (up to 10 steps)
- Graceful error handling when MCP server is offline

### Chat UI (`app/page.tsx`)

The frontend provides:
- Real-time streaming chat interface
- Tool invocation indicators showing:
  - Tool name
  - Arguments passed
  - Execution state (running/complete)
  - Results returned
- Markdown rendering for rich content
- Auto-scrolling message history
- Responsive design with dark mode support

## Development

### Build for Production

```bash
npm run build
npm start
```

### Linting

```bash
npm run lint
```

### Type Checking

TypeScript is configured for strict type checking. The IDE will show type errors automatically.

## Troubleshooting

### MCP Server Connection Issues

If you see warnings about MCP connection failures:

1. Verify Maverick server is running: `curl http://localhost:8003/sse`
2. Check the `MAVERICK_MCP_URL` in `.env.local`
3. Review server logs for any errors

The chat will still work for general questions even without MCP connection, but stock-related tools won't be available.

### API Key Issues

If you get OpenAI API errors:

1. Verify `OPENAI_API_KEY` is set in `.env.local`
2. Ensure the API key is valid and has credits
3. Check your OpenAI account dashboard for usage limits

### Build Errors

If you encounter build errors:

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

## Project Structure

```
stock-agent/
├── app/
│   ├── api/
│   │   └── chat/
│   │       └── route.ts          # Chat API with MCP integration
│   ├── layout.tsx                # Root layout
│   └── page.tsx                  # Main chat interface
├── public/                       # Static assets
├── .env.local                    # Environment variables (create this)
├── .env.example                  # Environment template
├── package.json                  # Dependencies
├── tsconfig.json                 # TypeScript config
├── tailwind.config.ts            # Tailwind CSS config
└── README.md                     # This file
```

## Key Features Explained

### Multi-Step Reasoning

The AI can perform complex multi-step operations:

1. **Fetch Data**: Get current stock price from Maverick
2. **Analyze**: Calculate RSI, MACD, or other indicators
3. **Advise**: Provide investment insights based on the analysis

This is enabled by `maxSteps: 10` in the `streamText` configuration.

### Tool Invocation Visibility

Users can see exactly what the AI is doing:
- When a tool is called, a card appears showing the tool name
- Arguments are displayed in a code format
- Results are shown once the tool completes
- Visual indicators (spinner/checkmark) show execution state

### Graceful Degradation

The application is designed to work even when the MCP server is offline:
- Connection errors are caught and logged
- The chat continues to work for general questions
- Users are informed about limited functionality

## License

MIT License - see LICENSE file for details

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs for both Next.js and Maverick
3. Verify all environment variables are set correctly

## Contributing

Contributions are welcome! Please ensure:
- TypeScript types are properly defined
- Code follows the existing style
- Error handling is comprehensive
- UI remains responsive and accessible
