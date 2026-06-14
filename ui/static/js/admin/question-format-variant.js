document.addEventListener("DOMContentLoaded", function () {
    const formatField = document.getElementById("id_format");
    const variantField = document.getElementById("id_variant");

    if (!formatField || !variantField || !formatField.dataset.variantsUrl) {
        return;
    }

    function loadVariants(formatId, selectedId) {
        if (!formatId) {
            variantField.innerHTML = '<option value="">---------</option>';
            return;
        }

        fetch(formatField.dataset.variantsUrl + "?format=" + formatId)
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                const options = ['<option value="">---------</option>'];

                data.results.forEach(function (variant) {
                    const selected = String(variant.id) === String(selectedId) ? " selected" : "";
                    options.push('<option value="' + variant.id + '"' + selected + '>' + variant.name + '</option>');
                });

                variantField.innerHTML = options.join("");
            });
    }

    formatField.addEventListener("change", function () {
        loadVariants(formatField.value, "");
    });

    if (formatField.value) {
        loadVariants(formatField.value, variantField.value);
    }
});
