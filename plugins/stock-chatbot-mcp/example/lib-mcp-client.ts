// lib/mcp-client.ts
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js'

let mcpClient: Client | null = null
let isConnecting = false

/**
 * Get or create MCP client singleton
 */
export async function getMCPClient(): Promise<Client> {
  if (mcpClient) {
    return mcpClient
  }

  // Prevent multiple simultaneous connection attempts
  if (isConnecting) {
    // Wait for the connection to complete
    while (isConnecting) {
      await new Promise(resolve => setTimeout(resolve, 100))
    }
    if (mcpClient) {
      return mcpClient
    }
  }

  isConnecting = true

  try {
    const serverUrl = process.env.MCP_SERVER_URL || 'http://localhost:8003/sse/'

    console.log('Connecting to MCP server:', serverUrl)

    // Create SSE transport
    const transport = new SSEClientTransport(new URL(serverUrl))

    // Create client
    const client = new Client(
      {
        name: 'stock-chatbot',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
          prompts: {},
          resources: {},
        },
      }
    )

    // Connect to server
    await client.connect(transport)

    console.log('Successfully connected to MCP server')

    // List available tools
    const toolsResult = await client.listTools()
    console.log(`Discovered ${toolsResult.tools.length} MCP tools:`,
      toolsResult.tools.map(t => t.name).join(', ')
    )

    mcpClient = client
    return client
  } catch (error) {
    console.error('Failed to connect to MCP server:', error)
    throw new Error(
      `MCP connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    )
  } finally {
    isConnecting = false
  }
}

/**
 * Call an MCP tool
 */
export async function callMCPTool(
  toolName: string,
  args: Record<string, unknown>
): Promise<unknown> {
  const client = await getMCPClient()

  try {
    console.log(`Calling MCP tool: ${toolName}`, args)

    const result = await client.callTool({
      name: toolName,
      arguments: args,
    })

    console.log(`Tool ${toolName} completed successfully`)

    return result
  } catch (error) {
    console.error(`MCP tool ${toolName} failed:`, error)
    throw error
  }
}

/**
 * List available MCP tools
 */
export async function listMCPTools() {
  const client = await getMCPClient()
  return await client.listTools()
}

/**
 * Disconnect MCP client
 */
export async function disconnectMCP() {
  if (mcpClient) {
    try {
      await mcpClient.close()
      mcpClient = null
      console.log('MCP client disconnected')
    } catch (error) {
      console.error('Error disconnecting MCP client:', error)
    }
  }
}

// Graceful shutdown
if (typeof process !== 'undefined') {
  process.on('SIGTERM', disconnectMCP)
  process.on('SIGINT', disconnectMCP)
}
