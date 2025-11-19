# Stock Analysis Chatbot - Example Implementation

A production-ready stock analysis chatbot built with Next.js 14, Vercel AI SDK 4.2, and MaverickMCP integration.

## Features

- 🚀 Real-time streaming responses with Vercel AI SDK
- 📊 39+ financial analysis tools via MCP integration
- 📈 Interactive charts and data visualizations
- 💬 Multi-turn conversations with context
- 🔄 Tool calling for stock analysis, backtesting, and portfolio optimization
- 📱 Responsive design with TailwindCSS and shadcn/ui
- ⚡ Edge runtime for low latency
- 🔒 Type-safe with TypeScript and Zod

## Prerequisites

- Node.js 18+
- MaverickMCP server running at http://localhost:8003
- Anthropic API key
- Tiingo API key (for stock data)

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Set Up Environment Variables

Create a `.env.local` file:

```env
# AI Provider
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# MCP Server
MCP_SERVER_URL=http://localhost:8003/sse/
TIINGO_API_KEY=your_tiingo_api_key_here
```

### 3. Start MaverickMCP Server

In a separate terminal:

```bash
# Clone MaverickMCP if you haven't
git clone https://github.com/cecvic/maverick-mcp.git
cd maverick-mcp

# Install and start
uv sync
make dev
```

The server will be available at http://localhost:8003

### 4. Run Development Server

```bash
npm run dev
```

Open http://localhost:3000 in your browser.

## Project Structure

```
example/
├── app/
│   ├── api/
│   │   └── chat/
│   │       └── route.ts          # Streaming chat API endpoint
│   ├── components/
│   │   ├── chat.tsx              # Main chat interface
│   │   └── ui/                   # shadcn/ui components
│   ├── lib/
│   │   ├── mcp-client.ts         # MCP client configuration
│   │   └── tools.ts              # Tool definitions for AI SDK
│   ├── page.tsx                  # Home page
│   └── layout.tsx                # Root layout
├── public/
├── .env.local                    # Environment variables (create this)
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## Example Queries

Try these queries in the chatbot:

1. **Stock Analysis**
   - "Analyze AAPL stock and show me the RSI and MACD indicators"
   - "What's the current price and volume of TSLA?"

2. **Backtesting**
   - "Backtest a momentum strategy on MSFT for the last year"
   - "Run a mean reversion strategy on SPY with default parameters"

3. **Portfolio Optimization**
   - "Create an optimized portfolio with AAPL, GOOGL, MSFT, AMZN, and TSLA"
   - "Build a portfolio of 10 tech stocks focusing on risk-adjusted returns"

4. **Stock Screening**
   - "Find undervalued stocks in the healthcare sector"
   - "Screen for stocks with RSI below 30 and positive earnings"

5. **Market Analysis**
   - "Compare the performance of AAPL, MSFT, and GOOGL over the past 6 months"
   - "What's the correlation between TSLA and the broader market?"

## Key Files

### `/app/api/chat/route.ts`
Implements the streaming chat endpoint with:
- Vercel AI SDK streaming
- MCP tool integration
- Tool call handling
- Error management

### `/lib/mcp-client.ts`
MCP client setup with:
- SSE transport configuration
- Tool discovery
- Connection management
- Error handling

### `/lib/tools.ts`
Tool definitions including:
- `analyzeStock` - Technical analysis
- `backtestStrategy` - Strategy backtesting
- `optimizePortfolio` - Portfolio optimization
- `screenStocks` - Stock screening
- `compareStocks` - Stock comparison

### `/app/components/chat.tsx`
React component with:
- Streaming message display
- Tool call visualization
- Input handling
- Error states

## Architecture

### Request Flow

1. **User Input** → Chat component sends message to API route
2. **API Route** → Vercel AI SDK processes with Claude
3. **Tool Calling** → AI decides to call MCP tools
4. **MCP Client** → Executes tools via MaverickMCP server
5. **Streaming Response** → Results stream back to UI in real-time
6. **UI Update** → Messages and charts update dynamically

### MCP Integration

The chatbot connects to MaverickMCP server via SSE transport:

```typescript
const transport = new SSEClientTransport(
  new URL(process.env.MCP_SERVER_URL!)
)
const client = new Client({ name: 'stock-chatbot', version: '1.0.0' })
await client.connect(transport)
```

Tools are dynamically discovered and mapped to AI SDK format:

```typescript
const mcpTools = await client.listTools()
const aiTools = mcpTools.tools.map(tool => ({
  name: tool.name,
  description: tool.description,
  parameters: tool.inputSchema,
  execute: async (params) => client.callTool({ name: tool.name, arguments: params })
}))
```

## Deployment

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Environment Variables

Set these in Vercel dashboard:
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `MCP_SERVER_URL` - Public URL of your MCP server
- `TIINGO_API_KEY` - Your Tiingo API key

### Production Considerations

1. **MCP Server**: Deploy MaverickMCP to a public server (not localhost)
2. **Rate Limiting**: Implement rate limiting for API routes
3. **Caching**: Use Redis for MCP response caching
4. **Monitoring**: Set up Vercel Analytics and Sentry
5. **Authentication**: Add NextAuth.js for user management
6. **Database**: Use PostgreSQL for conversation history

## Troubleshooting

### MCP Connection Failed

- Verify MCP server is running: `curl http://localhost:8003/mcp/`
- Check `MCP_SERVER_URL` in `.env.local`
- Ensure trailing slash in SSE URL: `http://localhost:8003/sse/`

### Streaming Not Working

- Verify `ANTHROPIC_API_KEY` is correct
- Check browser console for errors
- Ensure AI SDK version is 4.2+

### Tools Not Being Called

- Verify MCP server has tools registered: Check startup logs
- Test tool directly: Use MCP inspector tool
- Review tool parameter schemas in console

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **AI SDK**: Vercel AI SDK 4.2
- **MCP**: @modelcontextprotocol/sdk
- **UI**: React 18, TailwindCSS, shadcn/ui
- **Validation**: Zod
- **LLM**: Anthropic Claude 3.5 Sonnet
- **Data Source**: MaverickMCP + Tiingo API
- **Deployment**: Vercel

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Resources

- [Vercel AI SDK Documentation](https://sdk.vercel.ai/docs)
- [MCP SDK Documentation](https://modelcontextprotocol.io/docs)
- [MaverickMCP GitHub](https://github.com/cecvic/maverick-mcp)
- [Next.js Documentation](https://nextjs.org/docs)
- [Anthropic API Documentation](https://docs.anthropic.com/)

## License

MIT
