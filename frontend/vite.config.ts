import { defineConfig } from "vite";
import path from "path";
import vue from "@vitejs/plugin-vue";
import AutoImport from "unplugin-auto-import/vite";
import ViteComponents from "unplugin-vue-components/vite";
// 使用你所使用的UI组件库的 resolver
import {
  ElementPlusResolver,
  AntDesignVueResolver,
} from "unplugin-vue-components/resolvers";
import requireTransform from "vite-plugin-require-transform";

const pathSrc = path.resolve(__dirname, "src");

// https://vitejs.dev/config/
export default defineConfig({
  base: "./",
  resolve: {
    alias: {
      "~/": `${pathSrc}/`,
      "@/": `${pathSrc}/`,
    },
  },
  css: {
    preprocessorOptions: {
      scss: {},
    },
  },
  plugins: [
    vue(),
    AutoImport({
      imports: ["vue", "vuex", "vue-router"],
      dts: "src/auto-import.d.ts",
      resolvers: [ElementPlusResolver()],
    }),
    ViteComponents({
      resolvers: [
        ElementPlusResolver(),
        AntDesignVueResolver({
          importStyle: false, // css in js
        }),
      ],
      dts: "src/components.d.ts",
    }),
    requireTransform(),
  ],
  define: {
    "process.env": {},
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: "false",
  },
});
