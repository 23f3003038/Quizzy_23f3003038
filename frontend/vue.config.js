// vue.config.js
module.exports = {
  devServer: {
    proxy: {
      // Proxy any request starting with /api to your Flask server
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        pathRewrite: { '^/api': '' }
      }
    }
  }
};
