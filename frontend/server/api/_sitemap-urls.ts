// frontend/server/api/_sitemap-urls.ts
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()

  // Fetch all slugs from Backend
  // Note: Backend needs an endpoint that lists all public slugs
  // Let's assume GET /api/v1/cms/routes returns ["/blog/post-1", "/shop/product-1"]

  try {
    const routes = await $fetch<string[]>(`${config.public.apiBase}/cms/routes`)

    return routes.map(route => {
        return {
            loc: route,
            lastmod: new Date().toISOString(),
            changefreq: 'daily',
            priority: 0.8
        }
    })
  } catch (e) {
    console.error("Failed to fetch sitemap routes from backend", e)
    return []
  }
})
