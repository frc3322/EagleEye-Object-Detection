export function setupCameraFeedHandlers() {
    // Remove the event listener for the global remove button

    const addFeedModal = document.getElementById("addFeedModal");
    const cameraSelect = document.getElementById("cameraSelect");
    const saveFeedBtn = document.getElementById("saveFeedBtn");
    const cancelFeedBtn = document.getElementById("cancelFeedBtn");

    document.getElementById("addFeedBtn").addEventListener("click", () => {
        fetch("/get-available-cameras", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => response.json())
            .then((data) => {
                cameraSelect.innerHTML =
                    "<option disabled selected>Select a camera</option>";
                data.forEach((camera) => {
                    const option = document.createElement("option");
                    option.value = camera.index;
                    option.textContent = camera.name;
                    cameraSelect.appendChild(option);
                });
            })
            .catch((error) => {
                console.error("Error fetching cameras:", error);
            });

        addFeedModal.style.display = "flex";
    });

    cancelFeedBtn.addEventListener("click", () => {
        addFeedModal.style.display = "none";
    });

    // Function to update grid layout based on number of cameras
    function updateGridLayout() {
        const cameraList = document.getElementById("cameraList");
        const cameraCount = cameraList.children.length;

        // Ensure 2 cameras always result in 2 columns and 1 row
        let columns;
        if (cameraCount === 2) {
            columns = 2;
        } else if (cameraCount <= 2) {
            columns = 1;
        } else if (cameraCount <= 4) {
            columns = 2;
        } else if (cameraCount <= 9) {
            columns = 3;
        } else {
            columns = 4;
        }

        // Update grid styles
        cameraList.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;
    }

    saveFeedBtn.addEventListener("click", () => {
        const selectedCamera = cameraSelect.value;
        if (!selectedCamera) {
            alert("Please select a camera.");
            return;
        }

        const selectedCameraName =
            cameraSelect.options[cameraSelect.selectedIndex].textContent;

        // Create a camera box with selected camera name
        const cameraBox = document.createElement("div");
        cameraBox.className = "camera-box";
        cameraBox.textContent = selectedCameraName;

        // Add X button for individual camera removal
        const removeButton = document.createElement("button");
        removeButton.className = "camera-remove-btn";
        removeButton.textContent = "×";
        removeButton.addEventListener("click", function () {
            cameraBox.remove();

            // Show "No Cameras Available" message if no cameras are left
            const cameraList = document.getElementById("cameraList");
            if (cameraList.children.length === 0) {
                document.getElementById("noCamerasMessage").style.display =
                    "block";
            } else {
                // Update grid layout after removing a camera
                updateGridLayout();
            }
        });

        cameraBox.appendChild(removeButton);

        // Add the camera box to the camera list
        const cameraList = document.getElementById("cameraList");
        cameraList.appendChild(cameraBox);

        // Update the grid layout
        updateGridLayout();

        // Hide the "No Cameras Available" message
        document.getElementById("noCamerasMessage").style.display = "none";

        console.log("Selected Camera:", selectedCamera);

        addFeedModal.style.display = "none";
    });

    window.addEventListener("click", (event) => {
        if (event.target === addFeedModal) {
            addFeedModal.style.display = "none";
        }
    });
}
