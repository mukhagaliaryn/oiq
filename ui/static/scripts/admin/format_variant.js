document.addEventListener("DOMContentLoaded", function () {
    const formatField = document.querySelector("#id_format");
    const variantField = document.querySelector("#id_variant");

    if (!formatField || !variantField) return;

    function updateVariants() {
        const formatId = formatField.value;
        const currentValue = variantField.value;

        fetch(`/core/get_variants/?format_id=${formatId}`)
            .then(response => response.json())
            .then(data => {
                variantField.innerHTML = "";

                const emptyOption = document.createElement("option");
                emptyOption.value = "";
                emptyOption.textContent = "---------";
                variantField.appendChild(emptyOption);

                data.forEach(variant => {
                    const option = document.createElement("option");
                    option.value = variant.id;
                    option.textContent = variant.name;

                    if (String(variant.id) === String(currentValue)) {
                        option.selected = true;
                    }

                    variantField.appendChild(option);
                });
            })
            .catch(err => console.error("Error loading variants:", err));
    }

    formatField.addEventListener("change", updateVariants);

    if (formatField.value && !variantField.value) {
        updateVariants();
    }
});


document.addEventListener("DOMContentLoaded", function () {
    function initInlineRow(container) {
        const formatField = container.querySelector('select[name$="-format"]');
        const variantField = container.querySelector('select[name$="-variant"]');

        if (!formatField || !variantField) return;

        function updateVariants(keepCurrent) {
            const formatId = formatField.value;
            const currentValue = keepCurrent ? variantField.value : "";

            variantField.innerHTML = "";
            const emptyOption = document.createElement("option");
            emptyOption.value = "";
            emptyOption.textContent = "---------";
            variantField.appendChild(emptyOption);

            if (!formatId) return;

            fetch(`/core/get_variants/?format_id=${formatId}`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(function (variant) {
                        const option = document.createElement("option");
                        option.value = variant.id;
                        option.textContent = variant.name;

                        if (keepCurrent && String(variant.id) === String(currentValue)) {
                            option.selected = true;
                        }

                        variantField.appendChild(option);
                    });
                })
                .catch(function (err) {
                    console.error("Inline variant load error:", err);
                });
        }

        formatField.addEventListener("change", function () {
            updateVariants(false);
        });

        if (formatField.value) {
            updateVariants(true);
        }
    }

    document.querySelectorAll(".inline-related").forEach(function (container) {
        initInlineRow(container);
    });

    document.body.addEventListener("formset:added", function (event) {
        const container = event.target.closest(".inline-related");
        if (container) {
            initInlineRow(container);
        }
    });
});
