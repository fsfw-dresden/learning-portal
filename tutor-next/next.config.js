/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  distDir: 'export',
  images: {
    unoptimized: true
  },
  basePath: ''
}

module.exports = nextConfig
