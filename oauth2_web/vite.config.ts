// Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
// licensed under the Mulan PSL v2.
// You can use this software according to the terms and conditions of the Mulan PSL v2.
// You may obtain a copy of Mulan PSL v2 at:
//      http://license.coscl.org.cn/MulanPSL2
// THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
// PURPOSE.
// See the Mulan PSL v2 for more details.
import { URL, fileURLToPath } from 'node:url'
import { ConfigEnv, defineConfig } from 'vite'
import Vue from '@vitejs/plugin-vue'

export default ({ mode }: ConfigEnv) => {
  const isBuild = mode === 'production'

  return defineConfig({
    base: isBuild ? '/authhub/' : './',
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    plugins: [
      // https://github.com/vuejs/eslint-plugin-vue
      Vue(),
    ],
    // https://vitejs.dev/config/build-options.html#build-options
    build: {
      rollupOptions: {
        output: {
          assetFileNames: '[ext]/[name]-[hash].[ext]',
          entryFileNames: 'js/[name]-[hash].js',
          chunkFileNames: 'js/[name]-[hash].js',
          manualChunks(id) {
            try {
              if (typeof id === 'string' && id.includes('node_modules')) {
                const parts = id.split('node_modules/');
                if (parts.length > 1) {
                  const name = parts[1].split('/');
                  if (name.length > 0) {
                    if (name[0] === '.pnpm' && name.length > 1) {
                      return name[1];
                    }
                    return name[0];
                  }
                }
              }
              return 'unknown';
            } catch (error) {
              console.error('An error occurred while processing the id:', error);
            }
          },
        },
      },
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: true,
          drop_debugger: true,
        },
      },

    },
    server: {
      host: '0.0.0.0',
      hmr: true,
      port: 8000,
      proxy: {
        '/oauth2': {
          target: 'http://127.0.0.1:11111',
          secure: false,
          changeOrigin: true,
          ws: false,
        },
      },
    },
  })

}
