<template>
  <section class="hero-slider bg-gray-100 py-20">
    <div class="container mx-auto text-center">
      <h1 class="text-4xl font-bold mb-4">{{ title }}</h1>
      <p class="text-xl text-gray-600 mb-8">{{ subtitle }}</p>
      <button v-if="ctaText" class="bg-black text-white px-6 py-3 rounded-full hover:bg-gray-800 transition">
        {{ ctaText }}
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
  ctaText?: string
  ctaLink?: string
  images?: any[]
}>()
</script>
