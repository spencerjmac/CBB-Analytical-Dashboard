import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Navigation from '@/components/Navigation';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'CBB Analytics - College Basketball Analytics Dashboard',
  description: 'Advanced college basketball analytics with KenPom, Torvik, and custom metrics',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Navigation />
        <main className="min-h-screen">
          {children}
        </main>
        <footer className="bg-gray-800 text-white py-8 mt-16">
          <div className="container mx-auto px-4 text-center">
            <p className="text-sm text-gray-400">
              Data from KenPom, Bart Torvik, and CBB Analytics
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
