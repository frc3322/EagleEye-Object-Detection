import * as THREE from '../node_modules/three/build/three.module.js';
import { OrbitControls } from '../node_modules/three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from '../node_modules/three/examples/jsm/loaders/GLTFLoader.js';

function init3DView(modelUrl) {
  const container = document.getElementById('view-3d');
  container.innerHTML = ""; // Clear any existing content

  // Set up scene, camera, and renderer
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x222222);

  const camera = new THREE.PerspectiveCamera(
      75,
      container.clientWidth / container.clientHeight,
      0.1,
      2000
  );
  camera.position.set(100, 100, 100);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;  // Optional for softer shadows
  // Ensure the canvas always occupies the full container:
  renderer.domElement.style.width = '100%';
  renderer.domElement.style.height = '100%';
  renderer.domElement.style.display = 'block';
  container.appendChild(renderer.domElement);

  // Lighting
   const ambientLight = new THREE.AmbientLight(0xffffff, 0.2);
   scene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0xffffff, 2);
  directionalLight.position.set(100, 200, 200);
  directionalLight.castShadow = true;
  directionalLight.shadow.bias = -0.0005;
  directionalLight.shadow.mapSize.width = 1024 * 5;
  directionalLight.shadow.mapSize.height = 1024 * 5;
  directionalLight.shadow.camera.left = -300;
  directionalLight.shadow.camera.right = 300;
  directionalLight.shadow.camera.top = 150;
  directionalLight.shadow.camera.bottom = -150;
  directionalLight.shadow.camera.near = 100;
  directionalLight.shadow.camera.far = 400;
  scene.add(directionalLight);

  // OrbitControls for camera interaction
  new OrbitControls(camera, renderer.domElement);

  // Load the local model file (without loading UI)
  const loader = new GLTFLoader();
  loader.load(
      modelUrl,
      function (gltf) {
        const model = gltf.scene;
        model.rotation.x = Math.PI / 2;
        model.scale.set(0.02, 0.02, 0.02);

        // Enable shadows for each mesh in the model
        model.traverse((child) => {
          if ( child.isMesh ) {
            child.castShadow = true;
            child.receiveShadow = true;
            child.geometry.computeVertexNormals();
          }
        });

        scene.add(model);
        animate();
      },
      undefined,
      function (error) {
        console.error("Error loading the model:", error);
      }
  );

  new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
  }

  // Adjust the renderer size on window resize using current container dimensions
  window.addEventListener("resize", () => {
    const width = container.clientWidth;
    const height = container.clientHeight;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  });
}

// Sidebar view switching (unchanged)
const sidebarItems = document.querySelectorAll('.sidebar li');
const views = document.querySelectorAll('.view');
sidebarItems.forEach(item => {
  item.addEventListener('click', () => {
    sidebarItems.forEach(i => i.classList.remove('active'));
    item.classList.add('active');
    views.forEach(v => v.classList.remove('active'));
    const targetView = document.getElementById(item.getAttribute('data-view'));
    if (targetView) {
      targetView.classList.add('active');
      if (targetView.id === "view-3d") {
        init3DView("./assets/FE-2025.glb");
      }
    }
  });
});

// Feed control button actions remain unchanged
document.getElementById('addFeedBtn').addEventListener('click', () => {
  alert('Add Camera Feed clicked! Implement your logic here.');
});
document.getElementById('removeFeedBtn').addEventListener('click', () => {
  alert('Remove Camera Feed clicked! Implement your logic here.');
});
