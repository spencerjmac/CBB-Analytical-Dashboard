/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export', // Static export for easy deployment
  images: {
    unoptimized: true,
  },
  basePath: process.env.NODE_ENV === 'production' ? '' : '',
}

module.exports = nextConfig
