<!-- frontend/src/components/HelloWorld.vue -->

<script setup>
import { ref, onMounted } from 'vue';
const msg = ref('Loading…');

onMounted(async () => {
  try {
    // FULL URL, no proxy needed
    const res = await fetch('http://localhost:5000/ping');
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    msg.value = data.message; // should be "pong"
  } catch (err) {
    console.error('Fetch error:', err);
    msg.value = 'Error contacting backend';
  }
});
</script>

<template>
  <h1>Backend says: {{ msg }}</h1>
</template>

<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  position: relative;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
