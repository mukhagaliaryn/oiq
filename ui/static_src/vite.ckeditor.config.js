import { defineConfig } from "vite";
import path from "path";
import fs from "fs";

// CKEditor 5 icon imports (`import icon from '.../theme/icons/xxx.svg'`)
// expect the import to resolve to the *raw SVG markup string*, because
// CKEditor's IconView parses `icon` with DOMParser as XML.
//
// Vite's default asset handling instead turns `.svg` imports into a URL
// or a base64 data: URI, which DOMParser cannot parse as SVG, causing:
//   CKEditorError: Cannot read properties of null (reading 'getAttribute')
//
// This plugin intercepts those imports (for @ckeditor/* and
// @isaul32/ckeditor5-math) and returns the raw file contents as the
// default export instead, before Vite's built-in asset plugin runs.
function ckeditorSvgRaw() {
    return {
        name: "ckeditor5-svg-raw",
        enforce: "pre",
        load(id) {
            if (
                id.endsWith(".svg") &&
                /[\\/](@ckeditor|@isaul32)[\\/]/.test(id)
            ) {
                const filePath = id.split("?")[0];
                const content = fs.readFileSync(filePath, "utf-8");
                return `export default ${JSON.stringify(content)};`;
            }
        },
    };
}

export default defineConfig({
    plugins: [ckeditorSvgRaw()],
    build: {
        outDir: "../static/js/oiq-ckeditor",
        emptyOutDir: false,
        lib: {
            entry: path.resolve(__dirname, "./src/js/oiq-ckeditor.js"),
            name: "OIQEditor",
            formats: ["iife"],
            fileName: () => "oiq-ckeditor.bundle.js",
        },
    },
});