import { OrbitControls } from "OrbitControls";
import { GLTFLoader } from "GLTFLoader";
import {
    PCFSoftShadowMap,
    WebGLRenderer,
    AmbientLight,
    DirectionalLight,
    PerspectiveCamera,
    Scene,
    Color,
    Clock,
    Mesh,
    MeshStandardMaterial,
    SphereGeometry,
    Vector3,
} from "three";

let renderer, scene, camera, directionalLight;
let shadowsEnabled = true;
let gamePiecesVisible = true;
let statsDisplay;
let frameCount = 0;
let lastTime = performance.now();

let trackedSphere = null;

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

export function init3DView(modelUrl) {
    const container = document.getElementById("view-3d");
    statsDisplay = document.getElementById("statsDisplay");
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

    scene = new Scene();
    scene.background = new Color(0x222222);

    const scale = 40;

    camera = new PerspectiveCamera(
        75,
        container.clientWidth / container.clientHeight,
        100,
        40000,
    );
    camera.position.set(100 * scale, 100 * scale, 100 * scale);

    renderer = new WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = PCFSoftShadowMap;
    renderer.domElement.style.width = "100%";
    renderer.domElement.style.height = "100%";
    renderer.domElement.style.display = "block";
    container.appendChild(renderer.domElement);

    scene.add(new AmbientLight(0xffffff, 0.2));

    directionalLight = new DirectionalLight(0xffffff, 2);
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

    let clock = new Clock();
    let delta = 0;
    let interval = 1 / 60;

    function animate() {
        requestAnimationFrame(animate);
        delta += clock.getDelta();

        if (delta > interval) {
            renderer.render(scene, camera);
            updateStats();

            delta = delta % interval;
        }
    }

    window.addEventListener("resize", () => {
        const width = container.clientWidth;
        const height = container.clientHeight;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
    });

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

    // Add tracked sphere
    if (!trackedSphere) {
        const sphereGeometry = new SphereGeometry(30, 32, 32);
        const sphereMaterial = new MeshStandardMaterial({ color: 0xff0000 });
        trackedSphere = new Mesh(sphereGeometry, sphereMaterial);
        trackedSphere.castShadow = true;
        trackedSphere.receiveShadow = true;
        trackedSphere.position.set(0, 0, 0);
        scene.add(trackedSphere);
    }
}

export function updateTrackedSpherePosition(x, y, z) {
    if (trackedSphere) {
        trackedSphere.position.set(x, y, z);
    }
}
