<template>
  <div class="rich-text prose lg:prose-xl mx-auto py-12 px-4" v-html="content"></div>
</template>

<script setup lang="ts">
defineProps<{
  content: string
}>()
</script>
