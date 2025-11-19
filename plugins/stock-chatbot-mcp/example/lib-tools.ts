// lib/tools.ts
import { z } from 'zod'
import { tool } from 'ai'
import { getMCPClient, callMCPTool } from './mcp-client'

/**
 * Get stock analysis tools compatible with Vercel AI SDK
 */
export async function getStockAnalysisTools() {
  // Initialize MCP client
  await getMCPClient()

  return {
    analyzeStock: tool({
      description: 'Analyze a stock with technical indicators and price data. Returns current price, volume, and calculated technical indicators like RSI, MACD, Bollinger Bands, etc.',
      parameters: z.object({
        symbol: z.string().describe('Stock ticker symbol (e.g., AAPL, TSLA)'),
        indicators: z.array(z.enum([
          'RSI', 'MACD', 'BB', 'SMA', 'EMA', 'STOCH', 'ADX',
          'ATR', 'OBV', 'CCI', 'ROC', 'WILLR', 'MFI'
        ])).optional().describe('Technical indicators to calculate'),
        period: z.enum(['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y'])
          .optional()
          .default('1y')
          .describe('Time period for analysis'),
      }),
      execute: async ({ symbol, indicators, period }) => {
        try {
          // Call MaverickMCP analyze_stock tool
          const result = await callMCPTool('analyze_stock', {
            symbol: symbol.toUpperCase(),
            indicators: indicators || ['RSI', 'MACD', 'BB'],
            period,
          })
          return result
        } catch (error) {
          return {
            error: `Failed to analyze ${symbol}: ${error instanceof Error ? error.message : 'Unknown error'}`
          }
        }
      },
    }),

    backtestStrategy: tool({
      description: 'Backtest a trading strategy on historical stock data. Returns performance metrics including returns, Sharpe ratio, max drawdown, and win rate.',
      parameters: z.object({
        symbol: z.string().describe('Stock ticker symbol'),
        strategy: z.enum([
          'momentum', 'mean_reversion', 'breakout', 'rsi_oversold',
          'macd_crossover', 'bollinger_bounce', 'moving_average_crossover'
        ]).describe('Trading strategy to backtest'),
        startDate: z.string().optional().describe('Start date (YYYY-MM-DD)'),
        endDate: z.string().optional().describe('End date (YYYY-MM-DD)'),
        initialCapital: z.number().optional().default(10000).describe('Initial capital in USD'),
      }),
      execute: async ({ symbol, strategy, startDate, endDate, initialCapital }) => {
        try {
          const result = await callMCPTool('backtest_strategy', {
            symbol: symbol.toUpperCase(),
            strategy,
            start_date: startDate,
            end_date: endDate,
            initial_capital: initialCapital,
          })
          return result
        } catch (error) {
          return {
            error: `Failed to backtest ${strategy} on ${symbol}: ${error instanceof Error ? error.message : 'Unknown error'}`
          }
        }
      },
    }),

    optimizePortfolio: tool({
      description: 'Create an optimized portfolio using Modern Portfolio Theory. Returns optimal weights, expected returns, volatility, and Sharpe ratio.',
      parameters: z.object({
        symbols: z.array(z.string()).describe('List of stock ticker symbols'),
        objective: z.enum(['max_sharpe', 'min_volatility', 'max_return'])
          .optional()
          .default('max_sharpe')
          .describe('Optimization objective'),
        riskFreeRate: z.number().optional().default(0.02).describe('Risk-free rate (e.g., 0.02 for 2%)'),
      }),
      execute: async ({ symbols, objective, riskFreeRate }) => {
        try {
          const result = await callMCPTool('optimize_portfolio', {
            symbols: symbols.map(s => s.toUpperCase()),
            objective,
            risk_free_rate: riskFreeRate,
          })
          return result
        } catch (error) {
          return {
            error: `Failed to optimize portfolio: ${error instanceof Error ? error.message : 'Unknown error'}`
          }
        }
      },
    }),

    screenStocks: tool({
      description: 'Screen stocks based on technical and fundamental criteria. Returns a list of stocks matching the specified filters.',
      parameters: z.object({
        minPrice: z.number().optional().describe('Minimum stock price'),
        maxPrice: z.number().optional().describe('Maximum stock price'),
        minVolume: z.number().optional().describe('Minimum daily volume'),
        minMarketCap: z.number().optional().describe('Minimum market cap'),
        maxPE: z.number().optional().describe('Maximum P/E ratio'),
        sector: z.string().optional().describe('Sector filter (e.g., Technology, Healthcare)'),
        rsiBelow: z.number().optional().describe('RSI below threshold (oversold)'),
        rsiAbove: z.number().optional().describe('RSI above threshold (overbought)'),
      }),
      execute: async (filters) => {
        try {
          const result = await callMCPTool('screen_stocks', {
            min_price: filters.minPrice,
            max_price: filters.maxPrice,
            min_volume: filters.minVolume,
            min_market_cap: filters.minMarketCap,
            max_pe: filters.maxPE,
            sector: filters.sector,
            rsi_below: filters.rsiBelow,
            rsi_above: filters.rsiAbove,
          })
          return result
        } catch (error) {
          return {
            error: `Failed to screen stocks: ${error instanceof Error ? error.message : 'Unknown error'}`
          }
        }
      },
    }),

    compareStocks: tool({
      description: 'Compare performance and correlation of multiple stocks. Returns comparative metrics and correlation matrix.',
      parameters: z.object({
        symbols: z.array(z.string()).min(2).describe('List of stock ticker symbols to compare'),
        period: z.enum(['1mo', '3mo', '6mo', '1y', '2y', '5y'])
          .optional()
          .default('1y')
          .describe('Time period for comparison'),
        metrics: z.array(z.enum(['returns', 'volatility', 'sharpe', 'correlation']))
          .optional()
          .describe('Metrics to compare'),
      }),
      execute: async ({ symbols, period, metrics }) => {
        try {
          const result = await callMCPTool('compare_stocks', {
            symbols: symbols.map(s => s.toUpperCase()),
            period,
            metrics: metrics || ['returns', 'volatility', 'correlation'],
          })
          return result
        } catch (error) {
          return {
            error: `Failed to compare stocks: ${error instanceof Error ? error.message : 'Unknown error'}`
          }
        }
      },
    }),

    getMarketData: tool({
      description: 'Get real-time or historical market data for a stock including price, volume, market cap, and key statistics.',
      parameters: z.object({
        symbol: z.string().describe('Stock ticker symbol'),
        dataType: z.enum(['quote', 'historical', 'fundamentals', 'all'])
          .optional()
          .default('quote')
          .describe('Type of data to retrieve'),
      }),
      execute: async ({ symbol, dataType }) => {
        try {
          const result = await callMCPTool('get_market_data', {
            symbol: symbol.toUpperCase(),
            data_type: dataType,
          })
          return result
        } catch (error) {
          return {
            error: `Failed to get market data for ${symbol}: ${error instanceof Error ? error.message : 'Unknown error'}`
          }
        }
      },
    }),
  }
}
