export default function Loading() {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header Skeleton */}
      <div className="mb-8">
        <div className="h-10 w-64 bg-ui-surface rounded skeleton mb-2"></div>
        <div className="h-6 w-96 bg-ui-surface rounded skeleton"></div>
      </div>
      
      {/* Table Skeleton */}
      <div className="border border-ui-border rounded-lg overflow-hidden">
        <div className="p-4 bg-ui-surface border-b border-ui-border">
          <div className="h-10 w-full bg-ui-card rounded skeleton"></div>
        </div>
        
        {/* Table rows */}
        <div className="divide-y divide-ui-border">
          {[...Array(15)].map((_, i) => (
            <div key={i} className="p-4 flex items-center gap-4">
              <div className="h-6 w-8 bg-ui-surface rounded skeleton"></div>
              <div className="h-8 w-8 bg-ui-surface rounded skeleton"></div>
              <div className="h-6 flex-1 bg-ui-surface rounded skeleton"></div>
              <div className="h-6 w-20 bg-ui-surface rounded skeleton"></div>
              <div className="h-6 w-20 bg-ui-surface rounded skeleton"></div>
              <div className="h-6 w-20 bg-ui-surface rounded skeleton"></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
