/**
 * Procedural Web Audio API ambience for Angkor Wat:
 * - Gentle tropical breeze (filtered pink-ish noise with slow LFO)
 * - Soft moat & reflection pool water murmur
 * - Occasional distant Cambodian dawn birdsong chirps
 */

export class AngkorAudioAmbience {
  constructor() {
    this.ctx = null;
    this.masterGain = null;
    this.enabled = false;
    this.birdTimer = null;
  }

  init() {
    if (this.ctx) return;
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;

    this.ctx = new AudioCtx();
    this.masterGain = this.ctx.createGain();
    this.masterGain.gain.value = 0.0;
    this.masterGain.connect(this.ctx.destination);

    // 1. Gentle Wind & Water Ambience (4s looping noise buffer)
    const bufferSize = this.ctx.sampleRate * 4;
    const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = noiseBuffer.getChannelData(0);
    let b0 = 0, b1 = 0, b2 = 0;
    for (let i = 0; i < bufferSize; i++) {
      const white = Math.random() * 2 - 1;
      b0 = 0.997 * b0 + white * 0.029;
      b1 = 0.985 * b1 + white * 0.032;
      b2 = 0.950 * b2 + white * 0.048;
      data[i] = (b0 + b1 + b2 + white * 0.02) * 0.25;
    }

    const windSource = this.ctx.createBufferSource();
    windSource.buffer = noiseBuffer;
    windSource.loop = true;

    const windFilter = this.ctx.createBiquadFilter();
    windFilter.type = 'lowpass';
    windFilter.frequency.value = 340;

    // Slow LFO modulating wind filter frequency
    const lfo = this.ctx.createOscillator();
    lfo.frequency.value = 0.12;
    const lfoGain = this.ctx.createGain();
    lfoGain.gain.value = 140;
    lfo.connect(lfoGain);
    lfoGain.connect(windFilter.frequency);
    lfo.start();

    const windGain = this.ctx.createGain();
    windGain.gain.value = 0.32;

    windSource.connect(windFilter);
    windFilter.connect(windGain);
    windGain.connect(this.masterGain);
    windSource.start();

    // 2. Occasional Tropical Birdsong
    this._scheduleBird();
  }

  _scheduleBird() {
    if (this.birdTimer) clearTimeout(this.birdTimer);
    const delay = 3500 + Math.random() * 6500;
    this.birdTimer = setTimeout(() => {
      if (this.enabled && this.ctx && this.ctx.state === 'running') {
        this._playBirdChirp();
      }
      this._scheduleBird();
    }, delay);
  }

  _playBirdChirp() {
    const now = this.ctx.currentTime;
    const notes = 2 + Math.floor(Math.random() * 3);
    const baseFreq = 1800 + Math.random() * 1100;

    for (let i = 0; i < notes; i++) {
      const t = now + i * (0.11 + Math.random() * 0.05);
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(baseFreq, t);
      osc.frequency.exponentialRampToValueAtTime(baseFreq * (1.15 + Math.random() * 0.25), t + 0.045);
      osc.frequency.exponentialRampToValueAtTime(baseFreq * 0.92, t + 0.09);

      gain.gain.setValueAtTime(0.0001, t);
      gain.gain.linearRampToValueAtTime(0.025, t + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.095);

      osc.connect(gain);
      gain.connect(this.masterGain);
      osc.start(t);
      osc.stop(t + 0.1);
    }
  }

  setEnabled(on) {
    this.enabled = on;
    if (on) {
      this.init();
      if (this.ctx && this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
      if (this.masterGain) {
        this.masterGain.gain.setTargetAtTime(0.65, this.ctx.currentTime, 0.4);
      }
    } else if (this.masterGain && this.ctx) {
      this.masterGain.gain.setTargetAtTime(0.0, this.ctx.currentTime, 0.25);
    }
  }

  toggle() {
    this.setEnabled(!this.enabled);
    return this.enabled;
  }
}
