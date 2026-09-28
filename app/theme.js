/* Persistent three-way theme; independent of song and recording storage. */
(() => {
  'use strict';
  const key = 'piano-studio-next-theme-v2';
  const valid = ['system', 'dark', 'light'];
  const media = window.matchMedia('(prefers-color-scheme: dark)');
  let choice = 'dark';
  try { const saved = localStorage.getItem(key); if (valid.includes(saved)) choice = saved; } catch (_) {}
  function apply() {
    const resolved = choice === 'system' ? (media.matches ? 'dark' : 'light') : choice;
    document.documentElement.dataset.theme = resolved;
    document.documentElement.dataset.themeChoice = choice;
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = resolved === 'dark' ? '#101521' : '#f4f6fb';
    document.querySelectorAll('[data-theme-choice]').forEach(button => {
      const selected = button.dataset.themeChoice === choice;
      button.classList.toggle('active', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    document.querySelectorAll('[data-theme-select]').forEach(select => { select.value = choice; });
    window.dispatchEvent(new CustomEvent('piano-theme-change', {detail: {choice, resolved}}));
  }
  function set(value) {
    if (!valid.includes(value)) return false;
    choice = value;
    let saved = true;
    try { localStorage.setItem(key, choice); } catch (_) { saved = false; }
    apply();
    return saved;
  }
  if (media.addEventListener) media.addEventListener('change', () => { if (choice === 'system') apply(); });
  else if (media.addListener) media.addListener(() => { if (choice === 'system') apply(); });
  window.PianoTheme = {set, apply, get: () => ({choice, resolved:document.documentElement.dataset.theme})};
  apply();
})();
