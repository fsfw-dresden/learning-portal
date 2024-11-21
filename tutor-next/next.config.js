/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  distDir: 'export',
  images: {
    unoptimized: true
  },
  assetPrefix: '.',
  basePath: ''
}

module.exports = nextConfig
