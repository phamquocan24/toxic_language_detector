import { defineConfig } from "vite";
import laravel from "laravel-vite-plugin";
import vue from "@vitejs/plugin-vue2";
import { glob } from "glob";
import copy from "rollup-plugin-copy";
import path from "path";
import autoprefixer from "autoprefixer";

const VERSION = "1.0.1";

export default defineConfig(async ({ command, mode }) => {
    return {
        base: "",
        plugins: [
            laravel({
                input: [
                    "modules/Admin/Resources/assets/sass/dashboard.scss",
                    "modules/Admin/Resources/assets/js/dashboard.js",
                    "modules/Product/Resources/assets/admin/sass/options.scss",
                    "modules/User/Resources/assets/sass/pages/auth/main.scss",
                    "modules/User/Resources/assets/js/pages/auth/main.js",


                    // identify assets through pattern matching
                    ...(await glob(
                        [
                            "**/app.scss",
                            "**/app.js",
                            "**/main.scss",
                            "**/main.js",
                            "**/create.js",
                            "**/edit.js",
                        ],
                        { ignore: "node_modules/**" }
                    )),
                ],
                refresh: true,
            }),
            vue({
                template: {
                    transformAssetUrls: {
                        base: null,
                        includeAbsolute: false,
                    },
                },
            }),
            copy({
                targets: [
                    {
                        src: [
                            "public/favicon.ico",
                            "node_modules/jquery/dist/jquery.min.js",
                            "node_modules/tinymce",
                            "node_modules/selectize/dist/js/standalone/selectize.min.js",
                            "node_modules/jstree/dist/jstree.min.js",
                            "modules/Admin/Resources/assets/images/*",
                            "modules/Admin/Resources/assets/vendors/js/bootstrap.min.js",
                        ],
                        dest: "public/build/assets",
                    },
                    {
                        src: "modules/Admin/Resources/assets/fonts",
                        dest: "public/build",
                    }
                ],
                copyOnce: true,
                hook: command === "build" ? "writeBundle" : "buildStart",
            }),
        ],
        css: {
            postcss: {
                plugins: [
                    autoprefixer(),
                ],
            },
        },
        resolve: {
            alias: {
                vue: path.resolve(
                    __dirname,
                    "./node_modules/vue/dist/vue.esm.js"
                ),
                "@modules": path.resolve(__dirname, "./modules"),
                "@admin": path.resolve(
                    __dirname,
                    "./modules/Admin/Resources/assets"
                ),
            },
        },
        build: {
            sourcemap: mode === "development",
            rollupOptions: {
                output: {
                    manualChunks(id) {
                        if (id.includes("node_modules")) {
                            return id
                                .toString()
                                .split("node_modules/")[1]
                                .split("/")[0]
                                .toString();
                        }
                    },
                    entryFileNames: `assets/[name]-[hash]-v${VERSION}.js`,
                    chunkFileNames: `assets/[name]-[hash]-v${VERSION}.js`,
                    assetFileNames: function () {
                        return `assets/[name]-[hash]-v${VERSION}.[ext]`;
                    },
                },
            },
        },
    }
})
