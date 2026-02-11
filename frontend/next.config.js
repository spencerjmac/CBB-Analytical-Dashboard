/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // API proxy for development
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/:path*',
      },
    ];
  },
  
  // Image optimization
  images: {
    domains: ['localhost'],
  },
};

module.exports = nextConfig;
