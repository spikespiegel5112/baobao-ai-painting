import AutoImport from "unplugin-auto-import/vite";

export const AutoImportDeps = () => {
  return AutoImport({
    dts: "types/auto-imports.d.js",
    imports: ["vue", "vuex", "vue-router"],
  });
};
