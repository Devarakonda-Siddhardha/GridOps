/**
 * Procedural Web Audio Environmental Soundscape for Candi Prambanan
 * - Soft tropical breeze & leaves
 * - Occasional Javanese bird chirps
 * - Stone footsteps
 * - Optional subtle Javanese pentatonic (slendro/pelog) metallophone ambience
 */
export class PrambananAudio {
  constructor() {
    this.ctx = null;
    this.enabled = false;
    this.musicEnabled = false;
    this.windGain = null;
    this.birdTimer = null;
    this.musicTimer = null;
  }

  init() {
    if (this.ctx) return;
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    this.ctx = new AudioCtx();
    this.enabled = true;

    // Gentle wind noise
    const bufSize = this.ctx.sampleRate * 2;
    const buf = this.ctx.createBuffer(1, bufSize, this.ctx.sampleRate);
    const data = buf.getChannelData(0);
    for (let i = 0; i < bufSize; i++) data[i] = (Math.random() * 2 - 1) * 0.25;

    const noise = this.ctx.createBufferSource();
    noise.buffer = buf;
    noise.loop = true;

    const filter = this.ctx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.value = 380;

    this.windGain = this.ctx.createGain();
    this.windGain.gain.value = 0.04;

    noise.connect(filter);
    filter.connect(this.windGain);
    this.windGain.connect(this.ctx.destination);
    noise.start();

    // Occasional distant bird call
    this.birdTimer = setInterval(() => {
      if (!this.enabled || this.ctx.state !== "running") return;
      if (Math.random() < 0.45) this._playBird();
    }, 3400);

    // Optional subtle Indonesian metallophone ambience
    const pelogNotes = [293.66, 329.63, 392.0, 440.0, 523.25, 587.33];
    this.musicTimer = setInterval(() => {
      if (!this.enabled || !this.musicEnabled || this.ctx.state !== "running") return;
      const freq = pelogNotes[Math.floor(Math.random() * pelogNotes.length)];
      this._playMetallophone(freq);
    }, 2400);
  }

  resume() {
    if (!this.ctx) this.init();
    if (this.ctx && this.ctx.state === "suspended") this.ctx.resume();
  }

  playFootstep() {
    if (!this.ctx || !this.enabled || this.ctx.state !== "running") return;
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = "triangle";
    osc.frequency.setValueAtTime(115 + Math.random() * 25, now);
    osc.frequency.exponentialRampToValueAtTime(48, now + 0.07);
    gain.gain.setValueAtTime(0.06, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + 0.09);
  }

  _playBird() {
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    const base = 1850 + Math.random() * 700;
    osc.type = "sine";
    osc.frequency.setValueAtTime(base, now);
    osc.frequency.exponentialRampToValueAtTime(base * 1.28, now + 0.08);
    osc.frequency.exponentialRampToValueAtTime(base * 0.92, now + 0.18);
    gain.gain.setValueAtTime(0.001, now);
    gain.gain.linearRampToValueAtTime(0.022, now + 0.04);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + 0.24);
  }

  _playMetallophone(freq) {
    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(freq, now);
    gain.gain.setValueAtTime(0.001, now);
    gain.gain.linearRampToValueAtTime(0.025, now + 0.03);
    gain.gain.exponentialRampToValueAtTime(0.0008, now + 2.2);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + 2.3);
  }
}
