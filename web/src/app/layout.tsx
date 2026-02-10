import type { Metadata } from 'next';
import { Inter, IBM_Plex_Mono } from 'next/font/google';
import './globals.css';
import Navigation from '@/components/Navigation';

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const ibmPlexMono = IBM_Plex_Mono({ 
  weight: ['400', '500', '600'],
  subsets: ['latin'],
  variable: '--font-ibm-plex-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'CBB Analytics | College Basketball Advanced Metrics',
  description: 'Advanced college basketball analytics featuring efficiency metrics, four factors analysis, and predictive models. KenPom-style rankings with original methodology.',
  keywords: ['college basketball', 'analytics', 'statistics', 'KenPom', 'efficiency', 'NCAA'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${ibmPlexMono.variable}`}>
      <body className="min-h-screen flex flex-col">
        <Navigation />
        <main className="flex-1">
          {children}
        </main>
        <footer className="bg-ui-surface border-t border-ui-border py-6 mt-12">
          <div className="container mx-auto px-4 text-center text-sm text-text-muted">
            <p>
              Data sources: KenPom, Bart Torvik, CBB Analytics
            </p>
            <p className="mt-1">
              Not affiliated with KenPom.com or T-Rank. For educational and analytical purposes only.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
