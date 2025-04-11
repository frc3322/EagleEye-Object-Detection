import * as THREE from "three";
import { OrbitControls } from "OrbitControls";
import { GLTFLoader } from "GLTFLoader";

let renderer, scene, camera, directionalLight;
let shadowsEnabled = true;
let gamePiecesVisible = true;
let statsDisplay;
let frameCount = 0;
let lastTime = performance.now();

function populateFieldDropdown() {
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

function updateStats() {
    const currentTime = performance.now();
    frameCount++;
    if (currentTime - lastTime >= 1000) {
        const fps = frameCount;
        frameCount = 0;
        lastTime = currentTime;

        let numVerts = 0;
        scene.traverse((object) => {
            if (object.isMesh) {
                numVerts += object.geometry.attributes.position.count;
            }
        });

        statsDisplay.textContent = `Verts: ${numVerts} | FPS: ${fps}`;
    }
}

function init3DView(modelUrl) {
    const container = document.getElementById("view-3d");
    statsDisplay = document.getElementById("statsDisplay"); // Initialize stats display
    statsDisplay.style.position = "absolute";
    statsDisplay.style.bottom = "10px";
    statsDisplay.style.right = "10px";
    statsDisplay.style.color = "#f9c84a";
    statsDisplay.style.fontSize = "1rem";
    statsDisplay.style.zIndex = "10";

    // Clear previous scene if exists
    if (scene) {
        container.removeChild(renderer.domElement);
        scene.traverse((object) => {
            if (object.isMesh) {
                object.geometry.dispose();
            }
        });
        scene.clear();
    }

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x222222);

    const scale = 40;

    camera = new THREE.PerspectiveCamera(
        75,
        container.clientWidth / container.clientHeight,
        100,
        40000,
    );
    camera.position.set(100 * scale, 100 * scale, 100 * scale);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.domElement.style.width = "100%";
    renderer.domElement.style.height = "100%";
    renderer.domElement.style.display = "block";
    container.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 0.2));

    directionalLight = new THREE.DirectionalLight(0xffffff, 2);
    directionalLight.position.set(100 * scale, 200 * scale, 200 * scale);
    directionalLight.castShadow = true;
    directionalLight.shadow.bias = -0.0005;
    directionalLight.shadow.normalBias = -0.0005;
    directionalLight.shadow.mapSize.width = 1024 * 5;
    directionalLight.shadow.mapSize.height = 1024 * 5;
    directionalLight.shadow.camera.left = -300 * scale;
    directionalLight.shadow.camera.right = 300 * scale;
    directionalLight.shadow.camera.top = 150 * scale;
    directionalLight.shadow.camera.bottom = -150 * scale;
    directionalLight.shadow.camera.near = 100 * scale;
    directionalLight.shadow.camera.far = 400 * scale;
    scene.add(directionalLight);

    new OrbitControls(camera, renderer.domElement);

    const loader = new GLTFLoader();
    loader.load(
        modelUrl,
        (gltf) => {
            const model = gltf.scene;

            model.rotation.x = Math.PI / 2;

            model.traverse((child) => {
                if (child.isMesh) {
                    child.castShadow = true;
                    child.receiveShadow = true;
                    child.geometry.computeVertexNormals();
                }
            });
            scene.add(model);
            animate();
        },
        undefined,
        (error) => {
            console.error("Error loading the model:", error);
        },
    );

    const gamePiecePath =
        modelUrl.split("/").slice(0, -2).join("/") +
        "/game_pieces/" +
        modelUrl.split("/").pop().slice(0, 7) +
        "-GP.glb";

    const gamePieces = [];

    const gp_loader = new GLTFLoader();
    gp_loader.load(
        gamePiecePath,
        (gltf) => {
            const model = gltf.scene;

            model.rotation.x = Math.PI / 2;

            model.traverse((child) => {
                if (child.isMesh) {
                    child.castShadow = true;
                    child.receiveShadow = true;
                    child.geometry.computeVertexNormals();
                    gamePieces.push(child);
                }
            });
            scene.add(model);
            animate();
        },
        undefined,
        (error) => {
            console.error("Error loading the model:", error);
        },
    );

    document
        .getElementById("toggleGamePiecesBtn")
        .addEventListener("click", () => {
            gamePiecesVisible = !gamePiecesVisible;
            gamePieces.forEach((gp) => {
                gp.visible = gamePiecesVisible;
            });
        });

    new THREE.Clock();

    function animate() {
        requestAnimationFrame(animate);
        renderer.render(scene, camera);
        updateStats(); // Update stats on each frame
    }

    window.addEventListener("resize", () => {
        const width = container.clientWidth;
        const height = container.clientHeight;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
    });

    // Add toggle shadow button event
    document.getElementById("toggleShadowBtn").addEventListener("click", () => {
        shadowsEnabled = !shadowsEnabled;
        scene.traverse((object) => {
            if (object.isMesh) {
                object.castShadow = shadowsEnabled;
                object.receiveShadow = shadowsEnabled;
            }
        });
        directionalLight.castShadow = shadowsEnabled;
        renderer.shadowMap.enabled = shadowsEnabled;
    });
}

// Sidebar view switching
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
            }
        }
    });
});

// Feed button actions
document.getElementById("addFeedBtn").addEventListener("click", () => {
    alert("Add Camera Feed clicked! Implement your logic here.");
});
document.getElementById("removeFeedBtn").addEventListener("click", () => {
    alert("Remove Camera Feed clicked! Implement your logic here.");
});

// When the page loads, populate the field dropdown
window.onload = () => {
    populateFieldDropdown();
};

// Settings form logic
document.getElementById("saveSettingsBtn").addEventListener("click", () => {
    const settings = {
        log: document.getElementById("logCheckbox").checked,
        print_terminal: document.getElementById("printTerminalCheckbox")
            .checked,
        detection_logging: document.getElementById("detectionLoggingCheckbox")
            .checked,
        simulation_mode: document.getElementById("simulationModeCheckbox")
            .checked,
        server_address: document.getElementById("serverAddressInput").value,
        robot_position_key: document.getElementById("robotPositionKeyInput")
            .value,
        robot_rotation_key: document.getElementById("robotRotationKeyInput")
            .value,
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
    };

    console.log("Settings saved:", settings);
    alert("Settings have been saved!");
});
