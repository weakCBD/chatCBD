const { defineConfig } = require('@vue/cli-service')
const fs = require('fs')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    host: '::',
    port: 443, // 修改为您想要的端口
    server:{
      type: 'https',
      options: {
        key: fs.readFileSync('ssl/weakcbd.top.key'),
        cert: fs.readFileSync('ssl/weakcbd.top_bundle.crt'),
        //ca: fs.readFileSync('ssl/weakcbd.top_bundle.pem')
      }
    }
  },
  pages: {
    index: {
      entry: 'src/main.js',
      title: 'chatCBD',
    },
  },
})
