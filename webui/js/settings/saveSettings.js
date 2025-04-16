export function saveSettings() {
    document.getElementById("saveSettingsBtn").addEventListener("click", () => {
        const settings = {
            Constants: {
                log: document.getElementById("logCheckbox").checked,
                print_terminal: document.getElementById("printTerminalCheckbox")
                    .checked,
                detection_logging: document.getElementById(
                    "detectionLoggingCheckbox",
                ).checked,
                simulation_mode: document.getElementById(
                    "simulationModeCheckbox",
                ).checked,
            },
            NetworkTableConstants: {
                server_address:
                    document.getElementById("serverAddressInput").value,
                robot_position_key: document.getElementById(
                    "robotPositionKeyInput",
                ).value,
                robot_rotation_key: document.getElementById(
                    "robotRotationKeyInput",
                ).value,
            },
            ObjectDetectionConstants: {
                input_size: parseInt(
                    document.getElementById("inputSizeInput").value,
                    10,
                ),
                confidence_threshold: parseFloat(
                    document.getElementById("confidenceThresholdInput").value,
                ),
                combined_threshold: parseFloat(
                    document.getElementById("combinedThresholdInput").value,
                ),
                max_distance: parseFloat(
                    document.getElementById("maxDistanceInput").value,
                ),
            },
        };

        console.log("Settings saved:", settings);

        fetch("/save-settings", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(settings),
        })
            .then((response) => {
                if (response.ok) {
                    alert("Settings have been saved!");
                } else {
                    alert("Failed to save settings on the server.");
                }
            })
            .catch((error) => {
                console.error("Error sending settings to the server:", error);
                alert("An error occurred while saving settings.");
            });
    });
}
