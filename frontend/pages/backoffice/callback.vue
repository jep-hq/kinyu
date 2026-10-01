<template>
  <div class="flex items-center justify-center min-h-screen">
    <div class="text-center">
      <h1 class="text-xl font-bold mb-4">Authenticating...</h1>
      <p>Processing login callback.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const { handleCallback } = useZitadelAuth();
const router = useRouter();

onMounted(async () => {
  try {
    await handleCallback();
    router.push('/backoffice');
  } catch (e) {
    console.error("Callback error:", e);
  }
});
</script>
