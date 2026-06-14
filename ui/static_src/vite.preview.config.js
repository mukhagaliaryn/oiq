import { defineConfig } from "vite";
import path from "path";

// CKEditor-да сақталған Question.text мәтінінің ішіндегі math-tex
// формулаларын (KaTeX) admin тізім бетінде көрсету үшін шағын бандл.
export default defineConfig({
    build: {
        outDir: "../static/oiq-question-preview",
        emptyOutDir: false,
        lib: {
            entry: path.resolve(__dirname, "./src/js/oiq-question-preview.js"),
            name: "OIQQuestionPreview",
            formats: ["iife"],
            fileName: () => "oiq-question-preview.bundle.js",
        },
    },
});
