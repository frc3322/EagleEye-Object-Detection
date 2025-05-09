import { populateFieldDropdown } from "./dropdown/fieldDropdown.js";
import { setupSidebar } from "./ui/sidebar.js";
import { setupCameraFeedHandlers } from "./feeds/cameraFeedHandlers.js";
import { saveSettings } from "./settings/saveSettings.js";
import { updateTrackedSpherePosition } from "./init3DView.js";
import "../index.css";

window.onload = () => {
    populateFieldDropdown();
    setupSidebar();
    setupCameraFeedHandlers();
    saveSettings();

    // Socket.IO client for sphere position updates
    const socket = io();
    socket.on("update_sphere_position", (data) => {
        if (data && typeof data.x === "number" && typeof data.y === "number" && typeof data.z === "number") {
            updateTrackedSpherePosition(data.x, data.y, data.z);
        }
    });
};
