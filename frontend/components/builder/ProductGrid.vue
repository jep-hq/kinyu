<template>
  <section class="product-grid py-12 px-4">
    <div class="container mx-auto">
        <h2 v-if="title" class="text-3xl font-bold mb-8 text-center">{{ title }}</h2>
        <div v-if="products && products.length" class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-8">
            <div v-for="product in products" :key="product.id" class="product-card group relative">
                <div class="aspect-w-1 aspect-h-1 w-full overflow-hidden rounded-md bg-gray-200 lg:aspect-none group-hover:opacity-75 lg:h-80">
                   <!-- Placeholder if no image -->
                   <img src="https://placehold.co/400" alt="" class="h-full w-full object-cover object-center lg:h-full lg:w-full" />
                </div>
                <div class="mt-4 flex justify-between">
                    <div>
                        <h3 class="text-sm text-gray-700">
                            <NuxtLink :to="`/products/${product.handle}`">
                                <span aria-hidden="true" class="absolute inset-0"></span>
                                {{ product.title }}
                            </NuxtLink>
                        </h3>
                        <p class="mt-1 text-sm text-gray-500">{{ product.color }}</p>
                    </div>
                    <p class="text-sm font-medium text-gray-900">${{ product.price }}</p>
                </div>
            </div>
        </div>
        <div v-else class="text-center text-gray-500">
            No products found.
        </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
  collectionHandle?: string
  limit?: number
  // In a real app, products might be passed in props directly or fetched based on collectionHandle
  products?: any[]
}>()
</script>
