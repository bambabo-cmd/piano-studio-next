/* Small integration layer. Does not replace the original audio/notation engine. */
(() => {
  'use strict';
  function refreshPalette() {
    // The original piano-roll renderer caches CSS colors in its own state.
    if (typeof window.readColors === 'function') window.readColors();
    if (typeof window.drawRoll === 'function') window.drawRoll();
  }
  window.addEventListener('piano-theme-change', refreshPalette);
  function boot() {
    refreshPalette();
    const target = document.getElementById('ps-tools-theme');
    if (target) {
      const link = document.createElement('a');
      link.href = './preview/';
      link.textContent = '새 화면 시안';
      link.title = '별도 화면 시안 — 실제 녹음과 AI 채보는 연결되지 않음';
      link.target = '_blank';
      link.rel = 'noopener';
      link.className = 'ps-next-preview-link';
      target.appendChild(link);
    }
    window.PianoStudioNext = Object.freeze({
      version: '2.0.0-alpha.2',
      database: 'piano-studio-next-v2',
      mode: 'original-engine-with-additive-ui',
      fullResponsiveUIIntegrated: false,
      recognitionAlgorithmChanged: false
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, {once: true});
  } else boot();
})();
