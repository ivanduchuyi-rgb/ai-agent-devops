import './globals.css';
import { Nav } from '@/components/Nav';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Trading Bot Dashboard',
  description: 'Trading Bot v4.0 Monitoring Dashboard',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#0b0e14] text-[#e0e0e0] min-h-screen">
        <Nav />
        <main className="container mx-auto py-6">
          {children}
        </main>
      </body>
    </html>
  );
}
