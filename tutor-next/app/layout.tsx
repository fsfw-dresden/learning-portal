import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Tutorial Application',
  description: 'Learn software applications step by step',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
