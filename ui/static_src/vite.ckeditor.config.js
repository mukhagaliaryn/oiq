import { defineConfig } from "vite";
import path from "path";

export default defineConfig({
    build: {
        outDir: "../static/oiq-ckeditor",
        emptyOutDir: false,
        lib: {
            entry: path.resolve(__dirname, "./src/js/oiq-ckeditor.js"),
            name: "OIQEditor",
            formats: ["iife"],
            fileName: () => "oiq-ckeditor.bundle.js",
        },
    },
});
