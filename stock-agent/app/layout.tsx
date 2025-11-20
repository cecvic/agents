import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Stock Research AI Chat",
  description: "AI-powered stock research and analysis using Maverick MCP Server",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
