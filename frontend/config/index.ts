import vue from "@vitejs/plugin-vue";
import { AutoImportDeps } from "./autoImport";
import ViteComponents from "unplugin-vue-components/vite";
// 使用你所使用的UI组件库的 resolver
import { AntDesignVueResolver } from "unplugin-vue-components/resolvers";

export function createVitePlugins() {
  const vitePlugins = [
    vue(),
    ViteComponents({
      resolvers: [AntDesignVueResolver()],
      dts: "src/components.d.ts",
    }),
  ];
  // 自动按需引入依赖
  vitePlugins.push(AutoImportDeps());
  return vitePlugins;
}
