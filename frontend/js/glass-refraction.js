/**
 * Predict Your Placement — 3D Liquid Glass Ring Centerpiece
 * Pure optical quartz glass ring with smooth physics-based cursor glide & inertia.
 * Completely removed any thin black rings.
 */
(function() {
  "use strict";

  const stage = document.getElementById("glass-stage");
  if (!stage) return;

  if (typeof THREE === "undefined") {
    console.warn("Three.js not loaded. Skipping 3D stage.");
    return;
  }

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, stage.clientWidth / stage.clientHeight, 0.1, 100);
  camera.position.set(0, 0, 8.2);

  const renderer = new THREE.WebGLRenderer({
    alpha: true,
    antialias: true,
    powerPreference: "high-performance"
  });
  renderer.setSize(stage.clientWidth, stage.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.15;
  stage.appendChild(renderer.domElement);

  // Precision Studio Lighting for Realistic Glass Highlights
  const ambientLight = new THREE.AmbientLight(0xffffff, 1.1);
  scene.add(ambientLight);

  const keyLight = new THREE.DirectionalLight(0xffffff, 2.2);
  keyLight.position.set(7, 10, 9);
  scene.add(keyLight);

  const fillLight = new THREE.DirectionalLight(0xffffff, 1.2);
  fillLight.position.set(-8, -5, 6);
  scene.add(fillLight);

  const topRimLight = new THREE.PointLight(0xffffff, 1.6, 25);
  topRimLight.position.set(0, 7, 2);
  scene.add(topRimLight);

  const bottomRimLight = new THREE.PointLight(0xffffff, 1.4, 25);
  bottomRimLight.position.set(0, -7, -2);
  scene.add(bottomRimLight);

  // Root Ring Group
  const ringGroup = new THREE.Group();
  scene.add(ringGroup);

  // Pure Transparent Optical Liquid Glass Torus (No black rings!)
  const ringGeometry = new THREE.TorusGeometry(2.45, 0.42, 64, 160);
  const ringMaterial = new THREE.MeshPhysicalMaterial({
    color: 0xffffff,
    transmission: 0.985,
    opacity: 1,
    transparent: true,
    roughness: 0.035,
    ior: 1.54,                  // Crystal Crown Glass Refraction
    reflectivity: 0.85,
    thickness: 3.2,
    specularIntensity: 1.2,
    specularColor: 0xffffff,
    clearcoat: 1.0,
    clearcoatRoughness: 0.015,
    attenuationColor: new THREE.Color(0xfcfcfc),
    attenuationDistance: 8.0
  });

  const liquidGlassRing = new THREE.Mesh(ringGeometry, ringMaterial);
  liquidGlassRing.rotation.x = 1.12;
  liquidGlassRing.rotation.y = 0.22;
  ringGroup.add(liquidGlassRing);

  // Physics-based Mouse Tracking & Glide
  let targetPosX = 0;
  let targetPosY = 0;
  let targetRotX = 0;
  let targetRotY = 0;

  let currentPosX = 0;
  let currentPosY = 0;
  let currentRotX = 0;
  let currentRotY = 0;

  window.addEventListener("mousemove", (e) => {
    const normX = (e.clientX / window.innerWidth) * 2 - 1;
    const normY = -(e.clientY / window.innerHeight) * 2 + 1;

    // Direct cursor translation (moves prominently along the mouse)
    targetPosX = normX * 0.95;
    targetPosY = normY * 0.65;

    // Angular parallax tilt
    targetRotY = normX * 0.52;
    targetRotX = -normY * 0.38;
  }, { passive: true });

  // Background smooth glass ring DOM element follow
  const bgGlassRing = document.querySelector(".bg-glass-ring-container");
  let bgTargetX = 0;
  let bgTargetY = 0;
  let bgCurX = 0;
  let bgCurY = 0;

  if (bgGlassRing) {
    window.addEventListener("mousemove", (e) => {
      bgTargetX = (e.clientX / window.innerWidth - 0.5) * 60;
      bgTargetY = (e.clientY / window.innerHeight - 0.5) * 45;
    }, { passive: true });
  }

  // Render Loop with Fluid Inertia
  const clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);
    const t = clock.getElapsedTime();

    // Fluid interpolation for 3D glass ring
    currentPosX += (targetPosX - currentPosX) * 0.055;
    currentPosY += (targetPosY - currentPosY) * 0.055;
    currentRotX += (targetRotX - currentRotX) * 0.05;
    currentRotY += (targetRotY - currentRotY) * 0.05;

    ringGroup.position.x = currentPosX;
    ringGroup.position.y = currentPosY + Math.sin(t * 0.8) * 0.06;

    ringGroup.rotation.x = currentRotX;
    ringGroup.rotation.y = currentRotY;

    // Slow optical axial rotation so specular gleams slide over the curved glass
    liquidGlassRing.rotation.z = t * 0.045;

    renderer.render(scene, camera);

    // Parallax update for background smooth glass ring
    if (bgGlassRing) {
      bgCurX += (bgTargetX - bgCurX) * 0.05;
      bgCurY += (bgTargetY - bgCurY) * 0.05;
      bgGlassRing.style.transform = `translate(calc(-50% + ${bgCurX.toFixed(2)}px), calc(-50% + ${bgCurY.toFixed(2)}px))`;
    }
  }

  animate();

  // Resize handler
  window.addEventListener("resize", () => {
    if (!stage) return;
    camera.aspect = stage.clientWidth / stage.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(stage.clientWidth, stage.clientHeight);
  }, { passive: true });

})();
