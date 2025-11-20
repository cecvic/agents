import { streamText, convertToModelMessages } from 'ai';
import { openai } from '@ai-sdk/openai';
import { experimental_createMCPClient } from '@ai-sdk/mcp';

export const maxDuration = 60; // Maximum duration for serverless function

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();

    // Get MCP server URL from environment or use default
    const mcpUrl = process.env.MAVERICK_MCP_URL || 'http://localhost:8003/sse';

    let tools = {};
    let mcpClient = null;

    // Try to connect to the Maverick MCP Server
    try {
      mcpClient = await experimental_createMCPClient({
        transport: {
          type: 'sse',
          url: mcpUrl,
        },
      });

      // Fetch tools dynamically from Maverick
      tools = await mcpClient.tools();

      console.log('Successfully connected to Maverick MCP Server');
      console.log('Available tools:', Object.keys(tools));
    } catch (mcpError) {
      // Log the error but continue - the chat will work for general questions
      console.warn('Failed to connect to Maverick MCP Server:', mcpError);
      console.warn('Chat will continue without stock market tools');
    }

    // Convert UIMessages to ModelMessages for streamText
    const modelMessages = convertToModelMessages(messages);

    console.log('Processing chat request with', modelMessages.length, 'messages');

    // Stream response with tools enabled (if available)
    const result = streamText({
      model: openai('gpt-4o'),
      messages: modelMessages,
      tools: tools,
      // The AI SDK will automatically handle multi-step tool calling
    });

    // Return UI message stream response for compatibility with useChat hook
    return result.toUIMessageStreamResponse({
      originalMessages: messages,
    });
  } catch (error) {
    console.error('Error in chat route:', error);
    return new Response(
      JSON.stringify({
        error: 'An error occurred while processing your request',
        details: error instanceof Error ? error.message : 'Unknown error',
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}
