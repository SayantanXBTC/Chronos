// apps/web/app/layout.tsx
import type { Metadata } from 'next'
import { Cinzel } from 'next/font/google'
import './globals.css'

const cinzel = Cinzel({
  subsets: ['latin'],
  weight: ['400', '700'],
  variable: '--font-cinzel',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'History Platform',
  description: 'Interactive temporal world map',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`h-full ${cinzel.variable}`}>
      <body className="h-full overflow-hidden bg-zinc-900">{children}</body>
    </html>
  )
}
