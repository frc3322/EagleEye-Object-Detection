export function setupCameraFeedHandlers() {
    const addFeedBackgroundDiv = document.getElementById("addFeedBackgroundDiv");
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
                for (const key of Object.keys(data)) {
                    const option = document.createElement("option");
                    option.value = data[key];
                    option.textContent = key;
                    cameraSelect.appendChild(option);
                }
            })
            .catch((error) => {
                console.error("Error fetching cameras:", error);
            });

        addFeedBackgroundDiv.classList.remove("hidden");
        addFeedBackgroundDiv.style.display = "flex";
        document.body.classList.add("overflow-hidden");
    });

    cancelFeedBtn.addEventListener("click", () => {
        addFeedBackgroundDiv.classList.add("hidden");
        addFeedBackgroundDiv.style.display = "none";
        document.body.classList.remove("overflow-hidden");
    });

    function updateGridLayout() {
        const cameraList = document.getElementById("cameraList");
        const cameraCount = cameraList.children.length;
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
        const cameraBox = document.createElement("div");
        cameraBox.className = "camera-box";
        cameraBox.textContent = `${selectedCameraName}`;
        const cameraView = document.createElement("img");
        cameraView.className = "camera-view";
        cameraView.src = `/feed/${selectedCameraName.replace(/ /g, "_")}`;
        cameraBox.appendChild(cameraView);
        const removeButton = document.createElement("button");
        removeButton.className = "camera-remove-btn";
        removeButton.textContent = "×";
        removeButton.addEventListener("click", function () {
            cameraBox.remove();
            const cameraList = document.getElementById("cameraList");
            if (cameraList.children.length === 0) {
                document.getElementById("noCamerasMessage").style.display =
                    "block";
            } else {
                updateGridLayout();
            }
        });
        cameraBox.appendChild(removeButton);
        const cameraList = document.getElementById("cameraList");
        cameraList.appendChild(cameraBox);
        updateGridLayout();
        document.getElementById("noCamerasMessage").style.display = "none";
        addFeedBackgroundDiv.classList.add("hidden");
        addFeedBackgroundDiv.style.display = "none";
        document.body.classList.remove("overflow-hidden");
    });

    window.addEventListener("click", (event) => {
        if (event.target === addFeedBackgroundDiv) {
            addFeedBackgroundDiv.classList.add("hidden");
            addFeedBackgroundDiv.style.display = "none";
            document.body.classList.remove("overflow-hidden");
        }
    });
}
