/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000",
    NEXT_PUBLIC_DEFAULT_TZ: process.env.NEXT_PUBLIC_DEFAULT_TZ || "Asia/Kolkata",
  },
};

module.exports = nextConfig;

