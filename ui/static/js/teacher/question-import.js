function setupBlockFormsetControls(block, options) {
    const container = block.querySelector(options.containerSelector);
    const addButton = block.querySelector(options.addButtonSelector);
    const emptyTemplate = block.querySelector(options.emptyTemplateSelector);
    const totalForms = block.querySelector(options.totalFormsSelector);

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

        const deleteField = row.querySelector('input[name$="-DELETE"]');
        if (deleteField) {
            deleteField.checked = true;
        }
        row.classList.add("hidden");
    });
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-question-block]").forEach(function (block) {
        setupBlockFormsetControls(block, {
            containerSelector: "[data-options-container]",
            addButtonSelector: "[data-add-option-button]",
            emptyTemplateSelector: "[data-option-empty-form]",
            totalFormsSelector: "input[name$='-options-TOTAL_FORMS']",
            rowSelector: "[data-option-row]",
            removeSelector: "[data-remove-option]",
        });

        setupBlockFormsetControls(block, {
            containerSelector: "[data-pairs-container]",
            addButtonSelector: "[data-add-pair-button]",
            emptyTemplateSelector: "[data-pair-empty-form]",
            totalFormsSelector: "input[name$='-pairs-TOTAL_FORMS']",
            rowSelector: "[data-pair-row]",
            removeSelector: "[data-remove-pair]",
        });
    });

    const confirmForm = document.getElementById("import-review-form");
    if (confirmForm) {
        confirmForm.addEventListener("submit", function () {
            const submitButton = confirmForm.querySelector("button[type='submit']");
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.classList.add("opacity-70", "pointer-events-none");
            }
        });
    }
});
