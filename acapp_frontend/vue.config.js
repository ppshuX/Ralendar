const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  outputDir: '../acapp/dist',
  publicPath: '/',
  devServer: {
    port: 8081,
    proxy: {
      '/api': {
        target: 'https://app7626.acapp.acwing.com.cn',
        changeOrigin: true
      }
    }
  },
  lintOnSave: false
})
