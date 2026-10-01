<template>
  <div class="p-8">
    <h1 class="text-3xl font-bold mb-6">Backoffice Dashboard</h1>

    <div v-if="!user">
      <p class="mb-4">You are not logged in.</p>
      <button
        @click="login"
        class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        Sign In with Zitadel
      </button>
    </div>

    <div v-else>
      <div class="bg-gray-100 p-4 rounded mb-6">
        <h2 class="text-xl font-semibold">User Context</h2>
        <p><strong>Name:</strong> {{ user.profile.name }}</p>
        <p><strong>Email:</strong> {{ user.profile.email }}</p>
        <p v-if="currentTenantId" class="text-green-600 font-bold mt-2">
          Current Organization Context: {{ currentTenantId }}
        </p>
        <p v-else class="text-yellow-600 font-bold mt-2">
          No Organization Context Selected (Global User)
        </p>
      </div>

      <div class="mb-6">
        <div class="flex items-center justify-between mb-2">
           <h2 class="text-2xl font-semibold">Available Organizations (Tenants)</h2>
           <button @click="fetchGrants" class="text-sm text-blue-600 underline">Refresh List</button>
        </div>

        <div v-if="userGrants.length === 0" class="text-gray-500 italic">
          No grants found or not fetched yet.
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="grant in userGrants"
            :key="grant.id"
            class="border p-4 rounded hover:shadow-lg transition cursor-pointer"
            :class="{'border-blue-500 bg-blue-50': currentTenantId === grant.orgId}"
            @click="switchTenant(grant.orgId)"
          >
            <h3 class="font-bold text-lg">{{ grant.orgName }}</h3>
            <p class="text-sm text-gray-600">Org ID: {{ grant.orgId }}</p>
            <div class="mt-2 text-xs bg-gray-200 inline-block px-2 py-1 rounded">
              Roles: {{ grant.roles?.join(', ') || 'None' }}
            </div>
          </div>
        </div>
      </div>

      <div class="mt-8 border-t pt-8">
        <h3 class="text-lg font-bold mb-2">Access Token inspection</h3>
        <pre class="bg-gray-900 text-green-400 p-4 rounded overflow-auto text-xs max-h-60">
{{ JSON.stringify(user.profile, null, 2) }}
        </pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { user, login, fetchGrants, userGrants, switchTenant, currentTenantId } = useZitadelAuth();

// Fetch grants automatically if logged in
watchEffect(() => {
  if (user.value) {
    fetchGrants();
  }
});
</script>
