function setupFormsetControls(options) {
    const container = document.getElementById(options.containerId);
    const addButton = document.getElementById(options.addButtonId);
    const emptyTemplate = document.getElementById(options.emptyTemplateId);
    const totalForms = document.getElementById(options.totalFormsId);

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

        const row = fragment.querySelector(options.rowSelector);
        container.appendChild(fragment);
        totalForms.value = index + 1;

        if (row) {
            row.dispatchEvent(new CustomEvent("formset:added", { bubbles: true }));
        }
    });

    container.addEventListener("click", function (event) {
        const removeButton = event.target.closest(options.removeSelector);
        if (!removeButton) {
            return;
        }

        const row = removeButton.closest(options.rowSelector);
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
}

document.addEventListener("DOMContentLoaded", function () {
    setupFormsetControls({
        containerId: "options-container",
        addButtonId: "add-option-button",
        emptyTemplateId: "option-empty-form",
        totalFormsId: "id_options-TOTAL_FORMS",
        rowSelector: "[data-option-row]",
        removeSelector: "[data-remove-option]",
    });

    setupFormsetControls({
        containerId: "match-pairs-container",
        addButtonId: "add-pair-button",
        emptyTemplateId: "pair-empty-form",
        totalFormsId: "id_pairs-TOTAL_FORMS",
        rowSelector: "[data-pair-row]",
        removeSelector: "[data-remove-pair]",
    });
});

function updateQuestionPreview() {
    const textEl = document.getElementById("id_text");
    const textHtml = textEl ? (textEl.oiqEditorInstance ? textEl.oiqEditorInstance.getData() : textEl.value) : "";

    const root = document.querySelector("[data-selected-format-code]");
    const formatCode = root ? root.dataset.selectedFormatCode : "";

    const panel = document.getElementById("question-preview-content");
    if (!panel) {
        return;
    }

    let bodyHtml = "";

    if (formatCode === "matching") {
        const rows = document.querySelectorAll("#match-pairs-container [data-pair-row]");
        const pairsHtml = Array.from(rows)
            .filter(function (row) {
                const deleteField = row.querySelector('input[name$="-DELETE"]');
                return !(deleteField && deleteField.checked);
            })
            .map(function (row) {
                const editors = row.querySelectorAll("[data-oiq-editor]");
                const leftEl = editors[0];
                const rightEl = editors[1];
                const leftHtml = leftEl ? (leftEl.oiqEditorInstance ? leftEl.oiqEditorInstance.getData() : leftEl.value) : "";
                const rightHtml = rightEl ? (rightEl.oiqEditorInstance ? rightEl.oiqEditorInstance.getData() : rightEl.value) : "";

                return (
                    '<li class="flex items-center gap-3">' +
                    '<div class="min-w-0 flex-1 rounded-2xl border border-default p-4">' + leftHtml + "</div>" +
                    '<span class="flex size-8 shrink-0 items-center justify-center rounded-full border border-default bg-neutral-primary text-body-subtle">' +
                    '<i class="ph ph-dots-six-vertical size-4"></i>' +
                    "</span>" +
                    '<div class="min-w-0 flex-1 rounded-2xl border border-default p-4">' + rightHtml + "</div>" +
                    "</li>"
                );
            })
            .join("");

        bodyHtml = pairsHtml ? '<ul class="mt-6 space-y-3">' + pairsHtml + "</ul>" : "";
    } else {
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
                    (isCorrect ? "border-success-medium bg-success-soft" : "border-default") +
                    '"><i class="' +
                    (isCorrect ? "ph-fill ph-check-circle text-success" : "ph ph-circle text-body-subtle") +
                    ' mt-0.5 size-6 shrink-0"></i><div>' +
                    answerHtml +
                    "</div></li>"
                );
            })
            .join("");

        bodyHtml = optionsHtml ? '<ul class="mt-6 space-y-3">' + optionsHtml + "</ul>" : "";
    }

    panel.innerHTML = "<div>" + textHtml + "</div>" + bodyHtml;

    if (window.OIQRenderMath) {
        window.OIQRenderMath(panel);
    }
}
