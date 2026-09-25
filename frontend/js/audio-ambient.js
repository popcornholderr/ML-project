/**
 * Ambient Keynote Soundscape — Web Audio API Synthesizer
 * Produces an ultra-warm, subtle, continuous Apple-style ambient chord drone
 */
(function() {
  "use strict";

  const soundToggle = document.getElementById("soundToggle");
  const soundHint = document.getElementById("soundHint");

  if (!soundToggle) return;

  let audioCtx = null;
  let isPlaying = false;
  let masterGain = null;
  let oscillators = [];

  function initAudio() {
    if (audioCtx) return;

    const AudioContext = window.AudioContext || window.webkitAudioContext;
    audioCtx = new AudioContext();

    masterGain = audioCtx.createGain();
    masterGain.gain.setValueAtTime(0.001, audioCtx.currentTime);

    // Warm Lowpass Filter
    const filter = audioCtx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.setValueAtTime(420, audioCtx.currentTime);
    filter.Q.setValueAtTime(1.5, audioCtx.currentTime);

    // LFO for breathing filter movement
    const lfo = audioCtx.createOscillator();
    lfo.frequency.setValueAtTime(0.08, audioCtx.currentTime);
    const lfoGain = audioCtx.createGain();
    lfoGain.gain.setValueAtTime(140, audioCtx.currentTime);
    lfo.connect(lfoGain);
    lfoGain.connect(filter.frequency);
    lfo.start();

    // Harmonics: F major 9 ambient chord (F2, C3, A3, E4, G4)
    const freqs = [87.31, 130.81, 220.00, 329.63, 392.00];

    freqs.forEach((freq, idx) => {
      const osc = audioCtx.createOscillator();
      osc.type = idx % 2 === 0 ? "sine" : "triangle";
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);

      const oscGain = audioCtx.createGain();
      oscGain.gain.setValueAtTime(0.12 / freqs.length, audioCtx.currentTime);

      osc.connect(oscGain);
      oscGain.connect(filter);
      osc.start();
      oscillators.push(osc);
    });

    filter.connect(masterGain);
    masterGain.connect(audioCtx.destination);
  }

  function toggleSound() {
    initAudio();

    if (audioCtx.state === "suspended") {
      audioCtx.resume();
    }

    if (!isPlaying) {
      // Fade in gently
      masterGain.gain.linearRampToValueAtTime(0.18, audioCtx.currentTime + 1.2);
      isPlaying = true;
      soundToggle.classList.remove("needs-tap", "muted");
      soundToggle.setAttribute("aria-pressed", "true");
      if (soundHint) soundHint.classList.remove("show");
    } else {
      // Fade out
      masterGain.gain.linearRampToValueAtTime(0.001, audioCtx.currentTime + 0.6);
      isPlaying = false;
      soundToggle.classList.add("muted");
      soundToggle.setAttribute("aria-pressed", "false");
    }
  }

  soundToggle.addEventListener("click", toggleSound);

  // Show first-visit hint briefly
  setTimeout(() => {
    if (!isPlaying && soundHint) {
      soundHint.classList.add("show");
      setTimeout(() => {
        if (!isPlaying && soundHint) {
          soundHint.classList.remove("show");
        }
      }, 5000);
    }
  }, 2200);

})();
