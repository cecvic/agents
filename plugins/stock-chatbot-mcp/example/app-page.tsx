// app/page.tsx
import { Chat } from './components/chat'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <Chat />
    </main>
  )
}
