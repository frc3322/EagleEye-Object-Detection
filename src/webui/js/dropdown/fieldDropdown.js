import { init3DView } from "../init3DView.js";

export function populateFieldDropdown() {
    const fields = {
        2025: ["FE-2025-NGP-Simple.glb", "FE-2025-NGP.glb"],
    };

    const yearSelect = document.getElementById("yearSelect");
    const fileSelect = document.getElementById("fieldFileSelect");

    Object.keys(fields).forEach((year) => {
        const option = document.createElement("option");
        option.value = year;
        option.textContent = year;
        yearSelect.appendChild(option);
    });

    yearSelect.addEventListener("change", () => {
        fileSelect.innerHTML =
            "<option disabled selected>Select Field File</option>";
        const year = yearSelect.value;
        if (fields[year]) {
            fields[year].forEach((file) => {
                const opt = document.createElement("option");
                opt.value = file;
                opt.textContent = file;
                fileSelect.appendChild(opt);
            });
        }
    });

    fileSelect.addEventListener("change", () => {
        const year = yearSelect.value;
        const file = fileSelect.value;
        init3DView(`./assets/fields/${year}/field_files/${file}`);
    });
}
