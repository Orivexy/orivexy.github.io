// ORIVEXY Verify · web
(() => {
  const T = JSON.parse(document.getElementById('i18n').textContent);
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Reveal once when an element enters the viewport. Anything already above the bottom of the screen is shown
  // too, so a jump (a link, the scroll bar, a search) never leaves content hidden.
  let pending = [...document.querySelectorAll('[data-reveal]')];
  const show = (el) => el.classList.add('is-in');
  const sweep = () => {
    pending = pending.filter((el) => { if (el.getBoundingClientRect().top < innerHeight * 1.25) { show(el); return false; } return true; });
  };
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) if (e.isIntersecting) { show(e.target); io.unobserve(e.target); }
    }, { rootMargin: '0px 0px 25% 0px', threshold: 0 });
    pending.forEach((el) => io.observe(el));
    let queued = false;
    addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(() => { queued = false; sweep(); }); } }, { passive: true });
    addEventListener('load', () => setTimeout(sweep, 1200));
  } else pending.forEach(show);

  // Hero: the reel advances with the scroll while the sentence holds.
  const hero = document.querySelector('.hero');
  const track = document.querySelector('.reel__track');
  const frames = track ? [...track.children] : [];
  const count = document.querySelector('[data-reel-count]');
  const wide = matchMedia('(min-width: 1081px)');
  if (hero && track && !reduce) {
    let ticking = false;
    const update = () => {
      ticking = false;
      if (!wide.matches) {
        frames.forEach((f) => f.classList.remove('is-far'));
        const v = track.querySelector('video'); if (v && v.paused) v.play().catch(() => {});
        return;
      }
      const r = hero.getBoundingClientRect();
      const span = hero.offsetHeight - innerHeight;
      const p = span > 0 ? Math.min(1, Math.max(0, -r.top / span)) : 0;
      // The first frame (the certificate) waits above; the reel runs from the second frame to the last.
      const i = Math.min(frames.length - 1, 1 + p * (frames.length - 2) * 1.1);
      track.style.setProperty('--i', i.toFixed(3));
      const near = Math.round(i);
      frames.forEach((f, k) => f.classList.toggle('is-far', k !== near));
      if (count) count.textContent = `${near + 1} / ${frames.length}`;
      const v = frames[near] && frames[near].querySelector('video');
      document.querySelectorAll('.reel video').forEach((el) => { if (el !== v && !el.paused) el.pause(); });
      if (v && v.paused) v.play().catch(() => {});
    };
    addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    addEventListener('resize', update);
    update();
  }

  // ---------- the live check ----------
  const LEGAL = new Set(['sl', 'slu', 'sll', 'sa', 'sau', 'scp', 'cb', 'sc', 'gmbh', 'ag', 'kg', 'ltd', 'llc', 'inc', 'sas', 'sarl', 'srl', 'spa', 'bv', 'nv', 'oy', 'ab', 'as', 'plc']);
  const norm = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  const tokens = (s) => {
    const raw = norm(s).split(' ').filter(Boolean);
    const out = [];
    for (let k = 0; k < raw.length; k++) {
      if (raw[k].length === 1 && raw[k + 1] && raw[k + 1].length <= 2 && /^[a-z]$/.test(raw[k])) {
        let j = k, w = '';
        while (j < raw.length && raw[j].length <= 2 && /^[a-z]+$/.test(raw[j]) && (w + raw[j]).length <= 4) { w += raw[j]; j++; }
        if (LEGAL.has(w)) { out.push(w); k = j - 1; continue; }
      }
      out.push(raw[k]);
    }
    return out;
  };
  const split = (t) => ({ name: t.filter((w) => !LEGAL.has(w)), legal: t.filter((w) => LEGAL.has(w)) });
  const same = (a, b) => a.length === b.length && [...a].sort().join(' ') === [...b].sort().join(' ');
  function compareHolders(mine, cert) {
    if (!norm(mine)) return { r: 'other', why: T.why.empty };
    if (norm(mine) === norm(cert)) return { r: 'ok', why: T.why.identical, how: T.how.identical };
    const a = split(tokens(mine)), b = split(tokens(cert));
    if (same(a.name, b.name)) {
      if (same(a.legal, b.legal)) return { r: 'ok', why: a.name.join(' ') === b.name.join(' ') ? T.why.punct : T.why.order, how: T.how.normalised };
      if (!a.legal.length || !b.legal.length) return { r: 'review', why: T.why.legalMissing, how: T.how.similar };
      return { r: 'review', why: T.why.legal, how: T.how.similar };
    }
    // Numbers (a year in a company name) are weak evidence: compare the words first.
    const wa = a.name.filter((w) => !/^\d+$/.test(w)), wb = b.name.filter((w) => !/^\d+$/.test(w));
    if (wa.length && same(wa, wb)) return { r: 'review', why: T.why.similar, how: T.how.similar };
    const setB = new Set(wb);
    const common = wa.filter((w) => setB.has(w)).length;
    const ratio = common / Math.max(wa.length, wb.length, 1);
    if (ratio >= 0.6) return { r: 'review', why: T.why.similar, how: T.how.similar };
    return { r: 'other', why: T.why.other, how: T.how.different };
  }
  const ibanOk = (iban) => {
    const s = iban.replace(/\s+/g, '').toUpperCase();
    if (!/^[A-Z]{2}\d{2}[A-Z0-9]{10,30}$/.test(s)) return false;
    const cd = +s.slice(2, 4); if (cd < 2 || cd > 98) return false;
    const re = (s.slice(4) + s.slice(0, 4)).replace(/[A-Z]/g, (c) => c.charCodeAt(0) - 55);
    let m = 0; for (const ch of re) m = (m * 10 + +ch) % 97;
    return m === 1;
  };

  const lab = document.querySelector('[data-lab]');
  if (lab) {
    const st = { holder: lab.querySelector('#lab-holder').value, legal: null, typo: false, cert: true };
    const out = (k) => lab.querySelector(`[data-out="${k}"]`);
    const BASE_IBAN = T.lab.iban, TYPO_IBAN = T.lab.ibanTypo;
    const applyLegal = (name, legal) => {
      const t = name.replace(/[,\s]*\b(s\.?\s?l\.?\s?u?\.?|s\.?\s?a\.?\s?u?\.?|gmbh|ltd\.?|sas|srl)\s*$/i, '').trim();
      return legal ? `${t} ${legal}` : name;
    };
    function render() {
      const iban = st.typo ? TYPO_IBAN : BASE_IBAN;
      const mine = st.legal ? applyLegal(st.holder, st.legal) : st.holder;
      const valid = ibanOk(iban);
      let res, how = '';
      if (!valid) res = { r: 'invalid', why: T.why.invalid };
      else if (!st.cert) res = { r: 'missing', why: T.why.missing };
      else res = compareHolders(mine, T.lab.certHolder);
      out('iban').textContent = iban;
      out('mine').textContent = mine || '—';
      out('cert').textContent = st.cert ? T.lab.certHolder : T.lab.noCert;
      out('c-format').textContent = valid ? T.yes : T.no;
      out('c-format').className = valid ? 'yes' : 'no';
      out('c-in').textContent = !valid ? T.notChecked : (st.cert ? T.yes : T.no);
      out('c-in').className = !valid ? 'dim' : (st.cert ? 'yes' : 'no');
      how = valid && st.cert ? res.how || '' : T.notChecked;
      out('c-holder').textContent = how;
      out('c-holder').className = !valid || !st.cert ? 'dim' : (res.r === 'ok' ? 'yes' : res.r === 'other' ? 'no' : '');
      const badge = out('badge');
      badge.className = `badge badge--${res.r}`;
      badge.textContent = T.result[res.r];
      out('why').textContent = res.why;
    }
    lab.querySelector('#lab-holder').addEventListener('input', (e) => { st.holder = e.target.value; st.legal = null; lab.querySelectorAll('[data-legal]').forEach((b) => b.setAttribute('aria-pressed', 'false')); render(); });
    lab.querySelectorAll('[data-legal]').forEach((b) => b.addEventListener('click', () => {
      lab.querySelectorAll('[data-legal]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      st.legal = b.dataset.legal; render();
    }));
    lab.querySelectorAll('[data-typo]').forEach((b) => b.addEventListener('click', () => {
      lab.querySelectorAll('[data-typo]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      st.typo = b.dataset.typo === '1'; render();
    }));
    lab.querySelector('#lab-cert').addEventListener('change', (e) => { st.cert = e.target.checked; render(); });
    render();
  }

  // ---------- one row, three states: the middle one works ----------
  const live = document.querySelector('[data-review-live]');
  if (live) {
    const btn = live.querySelector('[data-resolve]');
    const note = live.querySelector('textarea');
    btn.addEventListener('click', () => {
      const text = note.value.trim();
      if (!text) { note.focus(); note.setAttribute('aria-invalid', 'true'); live.querySelector('[data-review-msg]').textContent = T.review.needNote; return; }
      const done = document.getElementById('review-done');
      live.querySelector('[data-review-actions]').hidden = true;
      live.querySelector('[data-review-msg]').textContent = '';
      const status = live.querySelector('[data-review-status]');
      status.className = 'badge badge--ok'; status.textContent = T.review.resolved;
      const p = document.createElement('p'); p.className = 'review-row__note'; p.textContent = text;
      const log = document.createElement('p'); log.className = 'review-row__log';
      const d = new Date();
      log.textContent = `${T.review.by} · ${d.toLocaleDateString(document.documentElement.lang)} ${d.toLocaleTimeString(document.documentElement.lang, { hour: '2-digit', minute: '2-digit' })}`;
      live.querySelector('.review-row').append(p, log);
      if (done) done.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
    });
  }

  // ---------- people tabs ----------
  const tabs = [...document.querySelectorAll('[role="tab"]')];
  const select = (t, focus) => {
    tabs.forEach((x) => { const on = x === t; x.setAttribute('aria-selected', String(on)); x.tabIndex = on ? 0 : -1; document.getElementById(x.getAttribute('aria-controls')).hidden = !on; });
    if (focus) t.focus();
  };
  tabs.forEach((t, k) => {
    t.addEventListener('click', () => select(t));
    t.addEventListener('keydown', (e) => {
      const d = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key];
      if (d) { e.preventDefault(); select(tabs[(k + d + tabs.length) % tabs.length], true); }
    });
  });

  // ---------- copy the install command ----------
  document.querySelectorAll('[data-copy]').forEach((b) => b.addEventListener('click', async () => {
    const text = document.getElementById(b.dataset.copy).textContent.trim();
    try { await navigator.clipboard.writeText(text); b.textContent = T.copied; } catch { b.textContent = T.copyFail; }
    setTimeout(() => { b.textContent = T.copy; }, 1800);
  }));

  // ---------- contact: open the visitor's mail with the message ----------
  const form = document.querySelector('[data-contact]');
  if (form) form.addEventListener('submit', (e) => {
    e.preventDefault();
    const msg = form.querySelector('input').value.trim();
    const body = msg ? `${msg}\n\n` : '';
    location.href = `mailto:${T.mail}?subject=${encodeURIComponent(T.mailSubject)}&body=${encodeURIComponent(body)}`;
  });

  // ---------- local time in Spain ----------
  const clock = document.querySelector('[data-clock]');
  if (clock) {
    const tick = () => { clock.textContent = new Intl.DateTimeFormat(document.documentElement.lang, { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Madrid' }).format(new Date()); };
    tick(); setInterval(tick, 30000);
  }
})();
