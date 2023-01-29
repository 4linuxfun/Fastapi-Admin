import {defineConfig} from 'vite'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import {ElementPlusResolver} from 'unplugin-vue-components/resolvers'
import {resolve} from 'path'
import vue from '@vitejs/plugin-vue'
import dynamicImport from 'vite-plugin-dynamic-import'
import Unocss from 'unocss/vite'
import {
  presetAttributify,
  presetIcons,
  presetUno,
  transformerDirectives,
  transformerVariantGroup,
} from 'unocss'

// https://vitejs.dev/config/
export default defineConfig({
  publicDir: 'public',
  base: '/',
  plugins: [
    vue(),
    dynamicImport(),
    AutoImport({resolvers: [ElementPlusResolver()]}),
    Components({
      resolvers: [
        ElementPlusResolver({
          importStyle: 'sass',
        }),
      ],
    }),
    Unocss({
      presets: [
        presetUno(),
        presetAttributify(),
        presetIcons({
          scale: 1.2,
          warn: true,
        }),
      ],
      transformers: [
        transformerDirectives(),
        transformerVariantGroup(),
      ]
    })
  ],
  server: {
    port: 8080,
    host: true,
    open: '/',
    proxy: {},
  },
  resolve: {
    extensions: ['.vue', '.mjs', '.js', '.ts', '.jsx', '.tsx', '.json'],
    alias: [
      {find: '@', replacement: resolve(__dirname, 'src')},
      {find: '~/', replacement: resolve(__dirname, 'src/')}
    ],
  },
  build: {
    outDir: 'dist',
  },
  css: {}

})