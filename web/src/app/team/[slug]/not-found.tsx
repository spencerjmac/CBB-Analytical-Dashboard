import Link from 'next/link';

export default function TeamNotFound() {
  return (
    <div className="container mx-auto px-4 py-16 text-center">
      <div className="max-w-2xl mx-auto">
        <div className="text-6xl mb-4">🏀❓</div>
        <h1 className="text-3xl font-bold mb-4">Team Not Found</h1>
        <p className="text-text-muted mb-8">
          We couldn't find data for this team. It may not be in our database or the link may be incorrect.
        </p>
        <Link 
          href="/rankings"
          className="inline-block px-6 py-3 bg-brand-orange text-white rounded-lg hover:bg-brand-orange-hover transition-colors"
        >
          View All Teams
        </Link>
      </div>
    </div>
  );
}
