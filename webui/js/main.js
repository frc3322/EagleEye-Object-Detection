import { populateFieldDropdown } from "./dropdown/fieldDropdown.js";
import { setupSidebar } from "./ui/sidebar.js";
import { setupCameraFeedHandlers } from "./feeds/cameraFeedHandlers.js";
import { saveSettings } from "./settings/saveSettings.js";

import "../index.css";

window.onload = () => {
    populateFieldDropdown();
    setupSidebar();
    setupCameraFeedHandlers();
    saveSettings();
};
