// frontend/nuxt.config.ts
export default defineNuxtConfig({
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@nuxtjs/sitemap',
    '@nuxtjs/robots'
  ],

  // Enable Server Side Rendering for SEO (Facebook/Twitter bots)
  ssr: true,

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1',
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'https://kinyu.com',
    }
  },

  site: {
    url: process.env.NUXT_PUBLIC_SITE_URL || 'https://kinyu.com',
  },

  // State of the Art 2026: Hybrid Rendering
  routeRules: {
    // 1. Static Pages (Prerendered at build time)
    // NOTE: We disable prerender for build stability in Docker without mock API
    // '/': { prerender: true },
    // '/about': { prerender: true },
    // '/contact': { prerender: true },
    '/': { swr: 3600 },
    '/about': { swr: 3600 },
    '/contact': { swr: 3600 },

    // 2. CMS Pages (SWR - Stale While Revalidate)
    // cached for 1 hour, then regenerated in background on next request
    '/blog/**': { swr: 3600 },
    '/page/**': { swr: 3600 },

    // 3. E-commerce (Dynamic SSR)
    // Products need real-time stock/pricing, so we use standard SSR (no cache headers by default)
    // But we headers to allow CDN caching for short periods if needed
    '/product/**': { swr: 60 }, // Cache for 60s is usually safe for stock

    // 4. Admin/Account (Client Side Only - No SEO needed)
    '/account/**': { ssr: false },
    '/checkout/**': { ssr: false },
    '/admin/**': { ssr: false },
  },

  sitemap: {
    // Dynamically fetch URLs from our CMS for the sitemap
    sources: [
        '/api/_sitemap-urls'
    ],
    exclude: [
        '/account/**',
        '/checkout/**',
        '/admin/**'
    ]
  },

  robots: {
    allow: '/',
    disallow: ['/account', '/checkout', '/admin']
  },

  app: {
    head: {
      titleTemplate: '%s - Kinyu',
      title: 'Kinyu Store',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'charset', content: 'utf-8' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },

  devtools: { enabled: true }
})
