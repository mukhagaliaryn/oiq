document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("options-container");
    const addButton = document.getElementById("add-option-button");
    const emptyTemplate = document.getElementById("option-empty-form");
    const totalForms = document.getElementById("id_options-TOTAL_FORMS");

    if (!container || !addButton || !emptyTemplate || !totalForms) {
        return;
    }

    addButton.addEventListener("click", function () {
        const index = parseInt(totalForms.value, 10);
        const fragment = emptyTemplate.content.cloneNode(true);

        fragment.querySelectorAll("[name], [id], label[for]").forEach(function (element) {
            ["name", "id", "for"].forEach(function (attr) {
                if (element.hasAttribute(attr)) {
                    element.setAttribute(attr, element.getAttribute(attr).replace(/__prefix__/g, index));
                }
            });
        });

        const row = fragment.querySelector("[data-option-row]");
        container.appendChild(fragment);
        totalForms.value = index + 1;

        if (row) {
            row.dispatchEvent(new CustomEvent("formset:added", { bubbles: true }));
        }

        lucide.createIcons();
    });

    container.addEventListener("click", function (event) {
        const removeButton = event.target.closest("[data-remove-option]");
        if (!removeButton) {
            return;
        }

        const row = removeButton.closest("[data-option-row]");
        if (!row) {
            return;
        }

        const idField = row.querySelector('input[name$="-id"]');
        if (idField && idField.value) {
            const deleteField = row.querySelector('input[name$="-DELETE"]');
            if (deleteField) {
                deleteField.checked = true;
            }
            row.classList.add("hidden");
        } else {
            row.remove();
        }
    });
});

function updateQuestionPreview() {
    const textEl = document.getElementById("id_text");
    const textHtml = textEl ? (textEl.oiqEditorInstance ? textEl.oiqEditorInstance.getData() : textEl.value) : "";

    const rows = document.querySelectorAll("#options-container [data-option-row]");
    const optionsHtml = Array.from(rows)
        .filter(function (row) {
            const deleteField = row.querySelector('input[name$="-DELETE"]');
            return !(deleteField && deleteField.checked);
        })
        .map(function (row) {
            const answerEl = row.querySelector("[data-oiq-editor]");
            const answerHtml = answerEl ? (answerEl.oiqEditorInstance ? answerEl.oiqEditorInstance.getData() : answerEl.value) : "";
            const isCorrectField = row.querySelector('input[name$="-is_correct"]');
            const isCorrect = !!(isCorrectField && isCorrectField.checked);

            return (
                '<li class="flex items-start gap-3 rounded-2xl border p-4 ' +
                (isCorrect ? "border-success bg-success-soft" : "border-default") +
                '"><i data-lucide="' +
                (isCorrect ? "check-circle-2" : "circle") +
                '" class="mt-0.5 size-5 shrink-0 ' +
                (isCorrect ? "text-success" : "text-body-subtle") +
                '"></i><div>' +
                answerHtml +
                "</div></li>"
            );
        })
        .join("");

    const panel = document.getElementById("question-preview-content");
    if (!panel) {
        return;
    }

    panel.innerHTML =
        '<div class="text-lg">' + textHtml + "</div>" + (optionsHtml ? '<ul class="mt-6 space-y-3">' + optionsHtml + "</ul>" : "");

    if (window.OIQRenderMath) {
        window.OIQRenderMath(panel);
    }

    lucide.createIcons();
}
