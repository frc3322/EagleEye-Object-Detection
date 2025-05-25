import { populateFieldDropdown } from "./dropdown/fieldDropdown.js";
import { setupSidebar } from "./ui/sidebar.js";
import { setupCameraFeedHandlers } from "./feeds/cameraFeedHandlers.js";
import { saveSettings } from "./settings/saveSettings.js";
import { updateTrackedSpherePosition } from "./init3DView.js";
import "../index.css";
import io from "socket.io-client";

window.onload = () => {
    populateFieldDropdown();
    setupSidebar();
    setupCameraFeedHandlers();
    saveSettings();

    const mmToM = 1000;

    // Socket.IO client for sphere position updates
    const socket = io();
    socket.on("update_sphere_position", (data) => {
        if (data && typeof data.x === "number" && typeof data.y === "number" && typeof data.z === "number") {
            const adjustedX = (data.x - 8.774125) * mmToM;
            const adjustedY = data.z * mmToM;
            const adjustedZ = (-data.y + 4.025901) * mmToM;
            updateTrackedSpherePosition(adjustedX, adjustedY, adjustedZ);
        } else {
            console.warn("Invalid sphere position data received:", data);
        }
    });
};
