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

function renderMathInside(root) {
    root.querySelectorAll(".math-tex").forEach(renderMathTex);
}

window.OIQRenderMath = renderMathInside;

document.addEventListener("DOMContentLoaded", function () {
    renderMathInside(document);
});

// htmx swap-тан кейін келген жаңа контентте (мыс. chapter/topic/question
// мәтінінде) де формулалар рендерленуі үшін.
document.body.addEventListener("htmx:afterSwap", function (event) {
    renderMathInside(event.target);
});
