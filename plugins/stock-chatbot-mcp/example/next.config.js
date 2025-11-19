/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverActions: true,
  },
  webpack: (config) => {
    // Fix for MCP SDK
    config.externals = [...(config.externals || []), { canvas: 'canvas' }]
    return config
  },
}

module.exports = nextConfig
