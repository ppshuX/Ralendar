<template>
  <div class="content-field">
    <slot />
  </div>
</template>

<style scoped>
.content-field {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .content-field {
    padding: 12px;
  }
}
</style>
