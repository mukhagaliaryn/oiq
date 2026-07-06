document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-question-block]").forEach(function (block) {
        const container = block.querySelector("[data-options-container]");
        const addButton = block.querySelector("[data-add-option-button]");
        const emptyTemplate = block.querySelector("[data-option-empty-form]");
        const totalForms = block.querySelector("input[name$='-options-TOTAL_FORMS']");

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

            const deleteField = row.querySelector('input[name$="-DELETE"]');
            if (deleteField) {
                deleteField.checked = true;
            }
            row.classList.add("hidden");
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
