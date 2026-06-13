<template>
  <div id="app">
    <MainView />
  </div>
</template>

<script>
import MainView from './views/MainView.vue'

export default {
  name: 'App',
  components: {
    MainView
  }
}
</script>

<style>
#app {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>
