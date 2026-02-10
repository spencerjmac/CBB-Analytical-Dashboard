import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="container mx-auto px-4 py-16 text-center">
      <div className="max-w-2xl mx-auto">
        <div className="text-8xl font-bold text-brand-orange mb-4">404</div>
        <h1 className="text-4xl font-bold mb-4">Page Not Found</h1>
        <p className="text-text-muted mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link 
          href="/"
          className="inline-block px-6 py-3 bg-brand-orange text-white rounded-lg hover:bg-brand-orange-hover transition-colors"
        >
          Go Home
        </Link>
      </div>
    </div>
  );
}
