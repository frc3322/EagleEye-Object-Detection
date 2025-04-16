import { init3DView } from "../init3DView.js";
import { loadSettings } from "../settings/loadSettings.js";

export function setupSidebar() {
    const sidebarItems = document.querySelectorAll(".sidebar li");
    const views = document.querySelectorAll(".view");

    sidebarItems.forEach((item) => {
        item.addEventListener("click", () => {
            sidebarItems.forEach((i) => i.classList.remove("active"));
            item.classList.add("active");
            views.forEach((v) => v.classList.remove("active"));
            const targetView = document.getElementById(
                item.getAttribute("data-view"),
            );
            if (targetView) {
                targetView.classList.add("active");
                if (targetView.id === "view-3d") {
                    init3DView(
                        "./assets/fields/2025/field_files/FE-2025-NGP-Simple.glb",
                    );
                    console.log("3D view loaded");
                }
                if (targetView.id === "view-settings") {
                    loadSettings();
                    console.log("Settings view loaded");
                }
            }
        });
    });
}
