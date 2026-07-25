import type { Metadata } from 'next'
import './globals.css'
import Sidebar from './Sidebar'

export const metadata: Metadata = {
  title: 'Hermes Ops — Operations Dashboard',
  description: 'TKVibes Agency — Operations Dashboard for business pipeline management',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Sidebar>{children}</Sidebar>
      </body>
    </html>
  )
}
