import katex from "katex";
import "katex/dist/katex.min.css";

function renderMathTex(element) {
    let tex = element.textContent.trim();
    let displayMode = false;

    if (tex.startsWith("\\[") && tex.endsWith("\\]")) {
        displayMode = true;
        tex = tex.slice(2, -2);
    } else if (tex.startsWith("\\(") && tex.endsWith("\\)")) {
        tex = tex.slice(2, -2);
    }

    try {
        katex.render(tex, element, {
            throwOnError: false,
            displayMode: displayMode,
        });
    } catch (error) {
        console.error(error);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".math-tex").forEach(renderMathTex);
});
