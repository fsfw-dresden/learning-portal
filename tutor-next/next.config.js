/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'output',
  distDir: 'export',
  images: {
    unoptimized: true
  },
  basePath: ''
}

module.exports = nextConfig
