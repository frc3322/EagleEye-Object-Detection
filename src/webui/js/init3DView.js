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
    PlaneGeometry,
    TextureLoader,
    Matrix4,
    NearestFilter,
    Vector3,
    Quaternion,
    BufferGeometry,
    BufferAttribute,
    LineSegments,
    LineBasicMaterial,
} from "three";
import { OrbitControls } from "OrbitControls";

let renderer, scene, camera, directionalLight;
let shadowsEnabled = true;
let gamePiecesVisible = true;
let statsDisplay;
let frameCount = 0;
let lastTime = performance.now();

let trackedCamera = null;

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
    renderer.domElement.classList.add('absolute', 'top-0', 'left-0', 'w-full', 'h-full', 'rounded-inherit', '-z-10', 'block');
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);

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

    // Add tracked camera wireframe
    if (!trackedCamera) {
        const cameraGeometry = new BufferGeometry();
        
        // Define camera wireframe vertices
        const size = 300;
        const depth = 600;
        
        // Front rectangle corners
        const frontTopLeft = [-size, size, 0];
        const frontTopRight = [size, size, 0];
        const frontBottomRight = [size, -size, 0];
        const frontBottomLeft = [-size, -size, 0];
        
        // Back point (camera origin)
        const backPoint = [0, 0, -depth];
        
        // Create vertices array for line segments
        const vertices = new Float32Array([
            // Front rectangle (4 lines)
            ...frontTopLeft, ...frontTopRight,
            ...frontTopRight, ...frontBottomRight,
            ...frontBottomRight, ...frontBottomLeft,
            ...frontBottomLeft, ...frontTopLeft,
            
            // Lines from corners to back point (4 lines)
            ...frontTopLeft, ...backPoint,
            ...frontTopRight, ...backPoint,
            ...frontBottomRight, ...backPoint,
            ...frontBottomLeft, ...backPoint,
        ]);
        
        cameraGeometry.setAttribute('position', new BufferAttribute(vertices, 3));
        
        const cameraMaterial = new LineBasicMaterial({ color: 0xff0000, linewidth: 2 });
        trackedCamera = new LineSegments(cameraGeometry, cameraMaterial);
        trackedCamera.position.set(0, 0, 0);
        scene.add(trackedCamera);
    }

    // Add AprilTag PNGs as planes at fiducial transforms
    fetch("/frc2025r2.json")
        .then((response) => response.json())
        .then((json) => {
            const textureLoader = new TextureLoader();
            json.fiducials.forEach((fiducial) => {
                const tagId = fiducial.id;
                const pngName = `tag36_11_${String(tagId).padStart(5, "0")}.png`;
                const pngPath = `/src/webui/assets/apriltags/${pngName}`;
                textureLoader.load(pngPath, (texture) => {
                    // Configure texture for crisp pixel art
                    texture.magFilter = NearestFilter;
                    texture.minFilter = NearestFilter;
                    texture.generateMipmaps = false;
                    
                    const planeGeometry = new PlaneGeometry(fiducial.size, fiducial.size);
                    const planeMaterial = new MeshStandardMaterial({ 
                        map: texture,
                    });
                    const plane = new Mesh(planeGeometry, planeMaterial);
                    // Apply 4x4 transform from JSON
                    const t = fiducial.transform;
                    // Three.js uses column-major, so set matrix directly
                    const matrix = new Matrix4();
                    matrix.set(
                        t[0], t[1], t[2], t[3] * 1000,
                        t[4], t[5], t[6], t[7] * 1000,
                        t[8], t[9], t[10], t[11] * 1000,
                        t[12], t[13], t[14], t[15]
                    );

                    const rotationYMatrix = new Matrix4();
                    rotationYMatrix.makeRotationY(Math.PI / 2);
                    const rotationXMatrix = new Matrix4();
                    rotationXMatrix.makeRotationX(-Math.PI / 2);
                    matrix.premultiply(rotationXMatrix);
                    matrix.multiply(rotationYMatrix);

                    plane.applyMatrix4(matrix);

                    // Move plane 1 unit along its world normal
                    const normal = new Vector3();
                    matrix.extractBasis(new Vector3(), new Vector3(), normal);
                    normal.normalize();
                    plane.position.add(normal);
                    
                    plane.castShadow = true;
                    plane.receiveShadow = true;
                    scene.add(plane);
                });
            });
        });
}

export function updateTrackedCameraTransform(transformMatrix) {
    if (trackedCamera) {
        const matrix = new Matrix4();
        matrix.set(
            transformMatrix[0][0], transformMatrix[0][1], transformMatrix[0][2], transformMatrix[0][3],
            transformMatrix[1][0], transformMatrix[1][1], transformMatrix[1][2], transformMatrix[1][3],
            transformMatrix[2][0], transformMatrix[2][1], transformMatrix[2][2], transformMatrix[2][3],
            transformMatrix[3][0], transformMatrix[3][1], transformMatrix[3][2], transformMatrix[3][3]
        );
        
        trackedCamera.matrixAutoUpdate = false;
        trackedCamera.matrix.copy(matrix);
        trackedCamera.matrixWorldNeedsUpdate = true;
        
        // Force immediate re-render when transformation updates
        if (renderer && scene && camera) {
            renderer.render(scene, camera);
        }
    } else {
        console.warn("Tracked camera not initialized yet");
    }
}
