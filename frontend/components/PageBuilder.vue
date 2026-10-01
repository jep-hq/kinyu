<template>
  <div class="page-builder">
    <template v-for="(block, index) in blocks" :key="block.id || index">
        <!-- Dynamic Component Rendering -->
        <component
          :is="resolveBlockComponent(block.type)"
          v-if="resolveBlockComponent(block.type)"
          v-bind="block.props"
          class="page-block"
        />
        <div v-else class="text-red-500 p-4 border border-red-500">
          Unknown Component Type: {{ block.type }}
        </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

interface PageBlock {
    id?: string;
    type: string; // e.g. 'hero-slider', 'product-grid'
    props: Record<string, any>; // Data passed to the component
}

const props = defineProps<{
    blocks: PageBlock[]
}>()

// Map of CMS types to Vue Components
// Using defineAsyncComponent for code splitting/performance
const componentMap: Record<string, any> = {
    'hero-slider': defineAsyncComponent(() => import('~/components/builder/HeroSlider.vue')),
    'rich-text': defineAsyncComponent(() => import('~/components/builder/RichText.vue')),
    'product-grid': defineAsyncComponent(() => import('~/components/builder/ProductGrid.vue')),
    // Add more mappings here
}

const resolveBlockComponent = (type: string) => {
    return componentMap[type] || null
}
</script>
