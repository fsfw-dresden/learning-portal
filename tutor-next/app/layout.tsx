import type { Metadata } from 'next'

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
      <head>
        <link rel="stylesheet" href="/styles.css" />
      </head>
      <body>{children}</body>
    </html>
  )
}
