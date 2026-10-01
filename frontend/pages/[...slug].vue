<template>
  <div>
    <div v-if="page">
      <!-- SEO Metadata is handled in script setup -->

      <!-- Dynamic Page Builder -->
      <!-- We access page.data.blocks assuming the JSON structure from CMS puts strict content in 'data' -->
      <PageBuilder :blocks="page.data.blocks || []" />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="container mx-auto px-4 py-20 text-center">
        <div v-if="error.statusCode === 404">
            <h1 class="text-4xl font-bold mb-4">404 - Page Not Found</h1>
            <p class="text-gray-600 mb-8">We couldn't find the page you're looking for.</p>
        </div>
        <div v-else>
            <h1 class="text-4xl font-bold mb-4">Error</h1>
            <p class="text-gray-600 mb-8">An unexpected error occurred while loading the page.</p>
        </div>
        <NuxtLink to="/" class="inline-block bg-black text-white px-6 py-3 rounded-md hover:bg-gray-800 transition">
            Return Home
        </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Ref } from 'vue'

// --- Types & Interfaces ---

/**
 * structure of a Block within the JSONB 'data' field
 */
interface ContentBlock {
    type: string; // e.g., 'hero-slider', 'rich-text'
    id?: string;
    props: Record<string, any>; // Arbitrary props passed to the component
}

/**
 * The 'data' column content for a Page model
 */
interface PageData {
    blocks: ContentBlock[];
    [key: string]: any;
}

/**
 * The API Resource shape for ContentEntry
 */
interface ContentEntry {
    id: string;
    title: string;
    slug: string;
    seo_title?: string;
    seo_description?: string;
    seo_keywords?: string[];
    og_image_id?: string;
    data: PageData;
}

// --- Routing & Data Fetching ---

const route = useRoute()

// Handle catch-all route: /foo/bar -> "foo/bar"
const slugArray = route.params.slug as string[]
// If root is visited via this catch-all (unlikely if index.vue exists, but nice fallback), use 'home'
const slug = slugArray ? slugArray.join('/') : 'home'

// Fetch content from API
// We assume backend exposes: GET /api/v1/cms/entries/slug/{slug}
const { data: page, error } = await useFetchAPI<ContentEntry>(`/cms/entries/slug/${slug}`, {
    key: `content-${slug}`, // Cache key for hydration
    lazy: false // SEO requires blocking fetch usually, or useServerSeoMeta
})

// Handle 404 or other errors to throw correct SSR error
if (error.value) {
    throw createError({
        statusCode: error.value.statusCode || 404,
        statusMessage: error.value.statusMessage || 'Page Not Found',
        fatal: true // Forces the error page to render instead of this component
    })
}

// --- SEO & Meta Tags ---

useHead({
    title: computed(() => page.value?.seo_title || page.value?.title),
    meta: [
        {
            name: 'description',
            content: computed(() => page.value?.seo_description || '')
        },
        {
            name: 'keywords',
            content: computed(() => page.value?.seo_keywords?.join(', ') || '')
        },
        // Open Graph
        { property: 'og:title', content: computed(() => page.value?.seo_title || page.value?.title) },
        { property: 'og:description', content: computed(() => page.value?.seo_description) },
        // We would resolve og_image_id to a URL here if we had the media map
    ]
})
</script>
