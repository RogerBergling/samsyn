(() => {
  'use strict';

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const TERMINAL = new Set(['verified', 'mismatch', 'expired', 'cancelled']);
  const state = {
    session: null,
    compare: { code: false, person: false },
    hidePn: false,
    pollTimer: null,
    countdownTimer: null,
    lastHash: '',
    busy: false,
  };

  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (ch) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[ch]));

  const I18N = (() => {
    try {
      return JSON.parse(document.getElementById('i18n')?.textContent || '{}');
    } catch (e) {
      return { lang: 'en', strings: {}, labels: {} };
    }
  })();

  function t(key, vars) {
    let text = (I18N.strings && I18N.strings[key]) || key;
    if (vars) {
      text = text.replace(/\{(\w+)\}/g, (match, name) => (
        Object.prototype.hasOwnProperty.call(vars, name) ? String(vars[name]) : match
      ));
    }
    return text;
  }

  function tLabel(group, code) {
    return (I18N.labels && I18N.labels[group] && I18N.labels[group][code]) || code;
  }

  function isDev() {
    return document.body.dataset.isDev === '1';
  }

  function assuranceLabel(code) {
    const base = tLabel('assurance', code);
    return isDev() ? `${base} ${I18N.lang === 'sv' ? '(test)' : '(mock)'}` : base;
  }

  function errorText(error) {
    const code = error?.code || error?.data?.error?.code;
    if (code) {
      const key = `error.${code}`;
      const text = t(key);
      if (text !== key) return text;
    }
    return error?.message || t('error.generic');
  }

  function csrf() {
    return $('meta[name="csrf-token"]')?.getAttribute('content') || '';
  }

  async function api(path, options = {}) {
    const method = options.method || (options.body ? 'POST' : 'GET');
    const headers = new Headers(options.headers || {});
    headers.set('Accept', 'application/json');
    if (options.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
    if (method !== 'GET' && method !== 'HEAD') headers.set('X-CSRF-Token', csrf());
    const response = await fetch(path, {
      ...options,
      method,
      headers,
      credentials: 'same-origin',
      cache: 'no-store',
    });
    let data = null;
    try { data = await response.json(); } catch (e) { /* no JSON */ }
    if (!response.ok) {
      const error = new Error(data?.error?.message || `Request failed (${response.status})`);
      error.status = response.status;
      error.code = data?.error?.code;
      error.data = data;
      if (response.status === 401) {
        const isDev = document.body.dataset.isDev === '1';
        window.location.href = isDev ? '/login' : '/';
      }
      throw error;
    }
    return data;
  }

  let toastTimer = null;
  function toast(message, kind = '') {
    const el = $('#toast');
    if (!el) return;
    el.textContent = message;
    el.className = `toast ${kind}`.trim();
    el.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { el.hidden = true; }, 4200);
  }

  function openModal(inner) {
    const root = $('#modal-root');
    if (!root) return;
    root.innerHTML = `<div class="modal-backdrop" data-action="close-modal"><div class="modal" role="dialog" aria-modal="true">${inner}</div></div>`;
    const first = root.querySelector('button, a, input');
    if (first) first.focus();
  }

  function closeModal() {
    const root = $('#modal-root');
    if (root) root.innerHTML = '';
  }

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeModal();
  });

  async function copyText(text) {
    if (!text) return false;
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (e) {
      const area = document.createElement('textarea');
      area.value = text;
      area.setAttribute('readonly', '');
      area.style.position = 'fixed';
      area.style.opacity = '0';
      document.body.appendChild(area);
      area.select();
      let ok = false;
      try { ok = document.execCommand('copy'); } catch (e2) { ok = false; }
      document.body.removeChild(area);
      return ok;
    }
  }

  function fmtDate(value) {
    if (!value) return '—';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleString(I18N.lang === 'sv' ? 'sv-SE' : 'en-GB', { dateStyle: 'medium', timeStyle: 'short' });
  }

  function secondsUntil(value) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return 0;
    return Math.max(0, Math.round((date.getTime() - Date.now()) / 1000));
  }

  function fmtRemaining(seconds) {
    const safe = Math.max(0, Number(seconds) || 0);
    const minutes = Math.floor(safe / 60);
    const rest = safe % 60;
    return `${String(minutes).padStart(2, '0')}:${String(rest).padStart(2, '0')}`;
  }

  function assuranceClass(assurance) {
    return assurance === 'eid_auth' || assurance === 'eid_sign' ? 'ok' : 'warn';
  }

  function stateClass(value) {
    if (value === 'verified') return 'ok';
    if (value === 'mismatch' || value === 'expired' || value === 'cancelled') return 'danger';
    if (value === 'confirming') return 'accent';
    return 'warn';
  }

  function progress(view) {
    const s = view.state;
    const step1 = s === 'waiting' ? 'active' : 'done';
    const step2 = s === 'verified' ? 'done' : (s === 'ready' || s === 'confirming' ? 'active' : (s === 'waiting' ? '' : 'done'));
    const step3 = s === 'verified' ? 'done' : '';
    return `
      <div class="progress" aria-label="Verification progress">
        <span class="step ${step1}"><span class="step-dot">1</span>${t("Share")}</span>
        <span class="step ${step2}"><span class="step-dot">2</span>${t("Compare")}</span>
        <span class="step ${step3}"><span class="step-dot">3</span>${t("Done")}</span>
      </div>`;
  }

  function identityCard(person) {
    if (!person) return '';
    const showFull = Boolean(person.pn) && !state.hidePn;
    let pnRow;
    if (showFull) {
      pnRow = `
        <div class="pn-row sensitive">
          <span class="label">${t("Personal number")}</span>
          <strong>${esc(person.pn)}</strong>
          <span class="pill danger">${t("Sensitive")}</span>
          <button class="btn btn-sm" type="button" data-action="toggle-pn">${t("Hide")}</button>
        </div>`;
    } else {
      const reveal = person.is_me && person.can_reveal && !person.revealed
        ? `<button class="btn btn-sm" type="button" data-action="reveal-pn">${t("Share mine")}</button>`
        : '';
      const notShared = !person.is_me && !person.pn ? `<span class="pill">${t("Not shared")}</span>` : '';
      const show = person.pn ? `<button class="btn btn-sm" type="button" data-action="toggle-pn">${t("Show")}</button>` : '';
      pnRow = `
        <div class="pn-row">
          <span class="label">${t("Personal number")}</span>
          <strong>${esc(person.pn_masked)}</strong>
          ${show}${reveal}${notShared}
        </div>`;
    }
    return `
      <article class="identity-card ${person.is_me ? 'me' : ''}">
        <div class="identity-head">
          <span class="avatar">${esc(person.initials)}</span>
          <div>
            <h3>${esc(person.name)} ${person.is_me ? '<span class="pill accent">' + t("You") + '</span>' : ''}</h3>
            <span class="muted">${esc(tLabel("role", person.role))}${person.org ? ` · ${esc(person.org)}` : ''}</span>
          </div>
        </div>
        <div class="identity-meta">
          <span class="pill ${assuranceClass(person.assurance)}">${esc(assuranceLabel(person.assurance))}</span>
          ${person.revealed ? '<span class="pill ok">' + t("Shared full number") + '</span>' : ''}
        </div>
        ${pnRow}
      </article>`;
  }

  function codePanel(view) {
    const words = (view.words || []).map((word) => `<span>${esc(word)}</span>`).join('');
    return `
      <div class="code-panel">
        <p class="eyebrow">${t("Verification code")}</p>
        <div class="code-digits">${esc(view.code)}</div>
        <div class="code-words">${words}</div>
        <div class="countdown">
          <svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i-clock"></use></svg>
          <span>${t("Expires in")} <strong id="countdown">${fmtRemaining(secondsUntil(view.expires_at))}</strong></span>
        </div>
      </div>`;
  }

  function counterpartLabel(view) {
    const map = { bob: 'Bob', alice: 'Alice', customer: t('Customer'), agent: 'Agent Anna' };
    return map[view.dev_counterpart] || view.dev_counterpart || t('other person');
  }

  function waiting(view) {
    const joinBlock = view.join_url
      ? `<div class="link-row">
           <input class="input" id="join-link" readonly value="${esc(view.join_url)}" aria-label="Invitation link">
           <button class="btn" type="button" data-action="copy-link"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i-copy"></use></svg>${t("Copy")}</button>
         </div>
         <p class="safety-note">${t("Share this link in the call chat. It works once and expires.")}</p>`
      : `<p class="safety-note">${t("The link is no longer available. Start a new verification.")}</p>`;
    const devButton = view.join_url && view.dev_counterpart
      ? `<button class="btn" type="button" data-action="open-counterpart">${t("Open as {name}", { name: counterpartLabel(view) })}</button>`
      : '';
    return `
      <div class="status-card warn">
        <span class="status-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i-clock"></use></svg></span>
        <div><h2>${t("Waiting for the other person.")}</h2><p>${t("Share the link below. The verification starts when they join.")}</p></div>
      </div>
      <div class="panel session-single">
        <div class="panel-head">
          <div><p class="eyebrow">${t("Your code")}</p><h2>${t("Send this link.")}</h2></div>
          <span class="pill warn">${t("Waiting")}</span>
        </div>
        ${codePanel(view)}
        ${joinBlock}
        <div class="session-help">
          <strong>${t("What happens next")}</strong>
          <ol>
            <li>${t("They open the link and join.")}</li>
            <li>${t("You both see the same name and code.")}</li>
            <li>${t("Read the code aloud. Both of you confirm.")}</li>
          </ol>
          <p>${t("Share the link, not the code. Anyone on the call can hear the code; it is not a password and expires.")}</p>
          <a href="/how-it-works">${t("How it works")}</a>
        </div>
        <div class="confirm-actions">
          ${devButton}
          <button class="btn btn-danger" type="button" data-action="cancel">${t("Cancel")}</button>
        </div>
        <p class="safety-note">${t("You are signed in as {name}.", { name: view.me.name })}</p>
      </div>`;
  }

  function compare(view) {
    const otherName = view.other ? view.other.name : 'the other person';
    let confirmBlock;
    if (view.my_confirmed) {
      confirmBlock = `
        <div class="status-row">
          <span class="status-chip ok"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i-check"></use></svg>${t("You confirmed")}</span>
          <span class="status-chip ${view.other_confirmed ? 'ok' : 'pending'}">${view.other_confirmed ? t("And {name} confirmed", { name: otherName }) : t("Waiting for {name}", { name: otherName })}</span>
        </div>
        <p class="safety-note">${t("Keep this page open until the result appears.")}</p>`;
    } else {
      confirmBlock = `
        <div class="status-row">
          <span class="status-chip ${view.other_confirmed ? 'ok' : 'pending'}">${view.other_confirmed ? t("{name} confirmed", { name: otherName }) : t("{name} has not confirmed yet", { name: otherName })}</span>
        </div>
        <label class="check-row"><input type="checkbox" id="confirm-code" ${state.compare.code ? 'checked' : ''}> ${t("I see the same code: {code}", { code: view.code })}</label>
        <label class="check-row"><input type="checkbox" id="confirm-person" ${state.compare.person ? 'checked' : ''}> ${t("I confirm this is the person I am talking to.")}</label>
        <div class="confirm-actions">
          <button class="btn btn-primary btn-lg" type="button" id="confirm-button" data-action="confirm" ${state.compare.code && state.compare.person ? '' : 'disabled'}>${t("Confirm")} <svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i-check"></use></svg></button>
          <button class="btn btn-danger" type="button" data-action="mismatch">${t("Something is wrong")}</button>
        </div>`;
    }
    return `
      <div class="session-grid">
        <div class="panel">
          <div class="panel-head">
            <div><p class="eyebrow">${t("Participants")}</p><h2>${t("Who is in this session?")}</h2></div>
            <span class="pill ${stateClass(view.state)}">${esc(tLabel("state", view.state))}</span>
          </div>
          <div class="identity-grid">
            ${identityCard(view.me)}
            ${identityCard(view.other)}
          </div>
        </div>
        <div class="panel">
          <p class="eyebrow">${t("Compare")}</p>
          <h2>${t("Read the code aloud.")}</h2>
          ${codePanel(view)}
          <div class="session-help">
            <strong>${t("What to do")}</strong>
            <ol>
              <li>${t("Read the code aloud.")}</li>
              <li>${t("Check that the name is the person you expected.")}</li>
              <li>${t("Both press Confirm.")}</li>
            </ol>
            <p>${t("Anyone on the call can hear the code. It is not a password and expires. Do not text or email it.")}</p>
            <a href="/how-it-works">${t("How it works")}</a>
          </div>
          <p class="safety-note">${t("Only confirm if the name and code match.")}</p>
          <div class="confirm-panel">${confirmBlock}</div>
          <div class="confirm-actions">
            <button class="btn btn-ghost btn-sm" type="button" data-action="cancel">${t("Cancel")}</button>
          </div>
        </div>
      </div>`;
  }

  function verified(view) {
    const receipt = view.receipt;
    const receiptButtons = receipt
      ? `<div class="receipt-cta">
           <a class="btn btn-primary" href="/receipts/${esc(receipt.id)}">${t("Open receipt")} <svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i-arrow"></use></svg></a>
           <button class="btn" type="button" data-action="print"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i-print"></use></svg>${t("Save PDF")}</button>
           <button class="btn btn-ghost" type="button" data-action="new-session">${t("Start another")}</button>
         </div>`
      : `<div class="receipt-cta"><button class="btn btn-primary" type="button" data-action="new-session">${t("Start a new verification")}</button></div>`;
    return `
      <div class="panel verified-card">
        <div class="verified-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i-check"></use></svg></div>
        <h1>${t("Verified.")}</h1>
        <p class="muted">${t("Both people confirmed the same session. A receipt is available.")}</p>
        ${receiptButtons}
      </div>
      <div class="panel">
        <p class="eyebrow">${t("Participants")}</p>
        <div class="identity-grid">${identityCard(view.me)}${identityCard(view.other)}</div>
      </div>`;
  }

  function closed(view) {
    const info = {
      mismatch: {
        cls: 'danger',
        title: t("Do not continue the call."),
        text: t("The code or the person did not match. No receipt was created."),
      },
      expired: {
        cls: 'warn',
        title: t("This verification expired."),
        text: t("The time ran out before both people confirmed."),
      },
      cancelled: {
        cls: 'warn',
        title: t("This verification was cancelled."),
        text: t("No receipt was created."),
      },
    }[view.state] || { cls: 'warn', title: t("This verification is closed."), text: t("Start a new verification.") };
    return `
      <div class="status-card ${info.cls}">
        <span class="status-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i-${view.state === 'mismatch' ? 'warning' : 'clock'}"></use></svg></span>
        <div><h2>${info.title}</h2><p>${info.text}</p></div>
      </div>
      <div class="confirm-actions">
        <button class="btn btn-primary" type="button" data-action="new-session">${t("Start a new verification")}</button>
        <a class="btn btn-ghost" href="/security">${t("Safety")}</a>
      </div>`;
  }

  function titleFor(view) {
    if (view.state === 'waiting') return t("Share this verification.");
    if (view.state === 'ready' || view.state === 'confirming') return t("Compare and confirm.");
    if (view.state === 'verified') return t("Verified.");
    if (view.state === 'mismatch') return t("Do not continue.");
    if (view.state === 'expired') return t("Expired.");
    if (view.state === 'cancelled') return t("Cancelled.");
    return tLabel("state", view.state);
  }

  function renderSession(view) {
    const root = $('#session-root');
    if (!root || !view) return;
    if (!state.session || state.session.id !== view.id) {
      state.compare = { code: false, person: false };
    }
    state.session = view;
    state.lastHash = JSON.stringify(view);
    const body = view.state === 'waiting'
      ? waiting(view)
      : (view.state === 'ready' || view.state === 'confirming')
        ? compare(view)
        : view.state === 'verified'
          ? verified(view)
          : closed(view);
    root.innerHTML = `
      <div class="session-head">
        <div>
          <p class="eyebrow">${t("Verification")} · ${esc(view.public_ref)}</p>
          <h1>${esc(titleFor(view))}</h1>
          <div class="session-meta">
            <span class="pill ${stateClass(view.state)}">${esc(tLabel("state", view.state))}</span>
            <span class="pill">${esc(tLabel("kind", view.kind))}</span>
            ${view.context ? `<span class="pill">${esc(view.context)}</span>` : ''}
          </div>
        </div>
      </div>
      ${progress(view)}
      ${body}`;
    root.setAttribute('aria-busy', 'false');
    if (TERMINAL.has(view.state)) stopPoll(); else startPoll(view.id);
    startCountdown();
    updateConfirmButton();
  }

  function updateConfirmButton() {
    const button = $('#confirm-button');
    if (!button) return;
    button.disabled = !(state.compare.code && state.compare.person);
  }

  function startCountdown() {
    clearInterval(state.countdownTimer);
    const tick = () => {
      const el = $('#countdown');
      if (!el || !state.session) return;
      const remaining = secondsUntil(state.session.expires_at);
      el.textContent = fmtRemaining(remaining);
      if (remaining <= 0) {
        clearInterval(state.countdownTimer);
        refreshSession();
      }
    };
    tick();
    state.countdownTimer = setInterval(tick, 1000);
  }

  function startPoll(id) {
    if (state.pollTimer) clearInterval(state.pollTimer);
    state.pollTimer = setInterval(() => {
      if (!document.hidden) refreshSession();
    }, 1400);
  }

  function stopPoll() {
    if (state.pollTimer) clearInterval(state.pollTimer);
    state.pollTimer = null;
    clearInterval(state.countdownTimer);
    state.countdownTimer = null;
  }

  async function refreshSession() {
    if (!state.session || state.busy) return;
    state.busy = true;
    try {
      const data = await api(`/api/sessions/${state.session.id}`);
      const next = data.session;
      const hash = JSON.stringify(next);
      if (hash !== state.lastHash) {
        renderSession(next);
      }
    } catch (error) {
      if (error.status !== 401) toast(errorText(error), 'danger');
    } finally {
      state.busy = false;
    }
  }

  function setLoading(button, loading, text) {
    if (!button) return;
    if (loading) {
      button.dataset.original = button.innerHTML;
      button.disabled = true;
      button.textContent = text || t('Working…');
    } else {
      button.disabled = false;
      if (button.dataset.original) button.innerHTML = button.dataset.original;
    }
  }

  async function confirmSession(decision) {
    if (!state.session) return;
    try {
      const data = await api(`/api/sessions/${state.session.id}/confirm`, {
        method: 'POST',
        body: JSON.stringify({ decision, roster_version: state.session.roster_version }),
      });
      renderSession(data.session);
      toast(decision === 'match' ? t("Confirmation recorded.") : t("The session was marked as a mismatch."), decision === 'match' ? 'ok' : 'danger');
    } catch (error) {
      toast(errorText(error), 'danger');
    }
  }

  async function revealPn() {
    if (!state.session) return;
    try {
      const data = await api(`/api/sessions/${state.session.id}/reveal`, { method: 'POST', body: '{}' });
      renderSession(data.session);
      toast(t("Your full personal number is now shared with the other participant."), 'warn');
    } catch (error) {
      toast(errorText(error), 'danger');
    }
  }

  async function cancelSession() {
    if (!state.session) return;
    try {
      const data = await api(`/api/sessions/${state.session.id}/cancel`, { method: 'POST', body: '{}' });
      closeModal();
      renderSession(data.session);
      toast(t("Session cancelled."), 'warn');
    } catch (error) {
      toast(errorText(error), 'danger');
    }
  }

  function mismatchModal() {
    openModal(`
      <h2>${t("What is wrong?")}</h2>
      <p class="muted">${t("Reporting a mismatch closes the session immediately. No receipt will be created. If you are unsure, keep the session open and compare again.")}</p>
      <div class="modal-actions">
        <button class="btn btn-danger" type="button" data-action="mismatch-reason">${t("The code does not match")}</button>
        <button class="btn btn-danger" type="button" data-action="mismatch-reason">${t("The person is not who I expected")}</button>
        <button class="btn" type="button" data-action="close-modal">${t("Keep the session open")}</button>
      </div>`);
  }

  function cancelModal() {
    openModal(`
      <h2>${t("Cancel this session?")}</h2>
      <p class="muted">${t("The other participant will see that the session was cancelled. No receipt will be created.")}</p>
      <div class="modal-actions">
        <button class="btn btn-danger" type="button" data-action="cancel-confirm">${t("Cancel session")}</button>
        <button class="btn" type="button" data-action="close-modal">${t("Keep it open")}</button>
      </div>`);
  }

  function handleAction(event) {
    const el = event.target.closest('[data-action]');
    if (!el) return;
    const action = el.dataset.action;

    if (action === 'close-modal') {
      if (el.classList.contains('modal-backdrop') && event.target !== el) return;
      closeModal();
      return;
    }
    if (action === 'copy-link') {
      const link = state.session?.join_url;
      copyText(link).then((ok) => toast(ok ? t("Invite link copied.") : t("Could not copy the link."), ok ? 'ok' : 'danger'));
      return;
    }
    if (action === 'copy') {
      copyText(el.dataset.copy || '').then((ok) => toast(ok ? t("Copied.") : t("Could not copy."), ok ? 'ok' : 'danger'));
      return;
    }
    if (action === 'toggle-pn') {
      state.hidePn = !state.hidePn;
      if (state.session) renderSession(state.session);
      return;
    }
    if (action === 'reveal-pn') {
      revealPn();
      return;
    }
    if (action === 'confirm') {
      confirmSession('match');
      return;
    }
    if (action === 'mismatch') {
      mismatchModal();
      return;
    }
    if (action === 'mismatch-reason') {
      closeModal();
      confirmSession('no_match');
      return;
    }
    if (action === 'cancel') {
      cancelModal();
      return;
    }
    if (action === 'cancel-confirm') {
      cancelSession();
      return;
    }
    if (action === 'open-counterpart') {
      if (!state.session?.join_url || !state.session?.dev_counterpart) return;
      const url = new URL(state.session.join_url, window.location.origin);
      const next = `${url.pathname}${url.search}`;
      window.open(`/dev/login?user=${encodeURIComponent(state.session.dev_counterpart)}&next=${encodeURIComponent(next)}`, '_blank', 'noopener');
      return;
    }
    if (action === 'new-session') {
      window.location.href = '/';
      return;
    }
    if (action === 'print') {
      window.print();
      return;
    }
  }

  function handleChange(event) {
    if (event.target.id === 'confirm-code') {
      state.compare.code = event.target.checked;
      updateConfirmButton();
    }
    if (event.target.id === 'confirm-person') {
      state.compare.person = event.target.checked;
      updateConfirmButton();
    }
  }

  function initHome() {
    const form = $('#create-form');
    if (form) {
      form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const button = $('#create-button');
        const payload = {
          kind: $('#kind')?.value || 'one_to_one',
          context: $('#context')?.value || '',
          pn_mode: $('#pn-mode')?.value || 'full',
          duration_minutes: Number($('#duration')?.value || 5),
        };
        setLoading(button, true, t('Creating…'));
        try {
          const data = await api('/api/sessions', { method: 'POST', body: JSON.stringify(payload) });
          window.location.href = `/session/${data.id}`;
        } catch (error) {
          toast(errorText(error), 'danger');
          setLoading(button, false);
        }
      });
    }

    const joinForm = $('#join-form');
    if (joinForm) {
      joinForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const raw = $('#join-input')?.value.trim() || '';
        let token = raw;
        if (raw.includes('/join/')) token = raw.split('/join/')[1];
        token = token.split('?')[0].split('#')[0].replace(/[^A-Za-z0-9_-]/g, '');
        if (!token) {
          toast(t("Paste an invite link or token."), 'warn');
          return;
        }
        window.location.href = `/join/${encodeURIComponent(token)}`;
      });
    }
  }

  function initJoin() {
    const button = $('#join-button');
    if (!button) return;
    button.addEventListener('click', async () => {
      const sessionId = button.dataset.sessionId;
      const token = button.dataset.token;
      button.disabled = true;
      const original = button.innerHTML;
      button.textContent = t("Joining…");
      try {
        await api(`/api/sessions/${sessionId}/join`, { method: 'POST', body: JSON.stringify({ token }) });
        window.location.href = `/session/${sessionId}`;
      } catch (error) {
        toast(errorText(error), 'danger');
        button.disabled = false;
        button.innerHTML = original;
      }
    });
  }

  function initSession() {
    const root = $('#session-root');
    if (!root) return;
    const id = root.dataset.sessionId;
    api(`/api/sessions/${id}`)
      .then((data) => renderSession(data.session))
      .catch((error) => {
        root.innerHTML = `<div class="status-card danger"><span class="status-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><use href="#i-warning"></use></svg></span><div><h2>${t("Could not load this session.")}</h2><p>${esc(errorText(error))}</p></div></div>`;
        toast(errorText(error), 'danger');
      });

    document.addEventListener('visibilitychange', () => {
      if (document.hidden && state.session) {
        const hasPn = (state.session.participants || []).some((person) => person.pn);
        if (hasPn) {
          state.hidePn = true;
          renderSession(state.session);
        }
      }
    });
  }

  function initReceipt() {
    const button = $('#print-receipt');
    if (button) button.addEventListener('click', () => window.print());
  }

  document.addEventListener('click', handleAction);
  document.addEventListener('change', handleChange);
  document.addEventListener('DOMContentLoaded', () => {
    initHome();
    initJoin();
    initSession();
    initReceipt();
  });
})();
