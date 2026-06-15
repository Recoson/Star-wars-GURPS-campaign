/* Dara Dara — Firebase live character sync  (v3 — event-driven + self-service signup) */
(function () {
  var firebaseConfig = {
    apiKey: "AIzaSyA2dj_J5d4OTMDEmeSTGin1s_DCRCV3kHg",
    authDomain: "kotor-gurps.firebaseapp.com",
    projectId: "kotor-gurps",
    storageBucket: "kotor-gurps.firebasestorage.app",
    messagingSenderId: "145157387485",
    appId: "1:145157387485:web:7a838273ba52923e445734"
  };

  // ── Players type this word once when creating an account. Change it freely. '' = open signup. ──
  var INVITE_CODE = '';

  if (!window.firebase || !firebase.initializeApp) {
    console.error('[sync] Firebase compat SDK missing — the three SDK <script> tags must load BEFORE this file.');
    return;
  }
  try { firebase.initializeApp(firebaseConfig); } catch (e) {}
  var auth = firebase.auth();
  var db   = firebase.firestore();

  var charId = (new URLSearchParams(location.search).get('char') || 'default')
                 .toLowerCase().replace(/[^a-z0-9_-]/g, '') || 'default';
  var ref = db.collection('characters').doc(charId);
  var applyingRemote = false, ready = false, writeTimer = null, lastJSON = '';

  function getChar() {
    try { if (typeof C !== 'undefined' && C && typeof C === 'object') return C; } catch (e) {}
    return window.C || window.CHAR || window.character || null;
  }
  function redraw() {
    try { if (typeof recalc === 'function') recalc(); } catch (e) {}
    try {
      if (typeof showTab === 'function') {
        var a = document.querySelector('.tab.active,[data-tab].active,.nav-tab.active,.tab-btn.active,.tabs .active,nav .active');
        var id = a && (a.getAttribute('data-tab') || (a.dataset && a.dataset.tab) || a.id);
        if (id) showTab(String(id).replace(/^tab-/, ''));
      }
    } catch (e) {}
    ['renderAll','renderSheet','refresh','rebuild','render','drawAll'].forEach(function (fn) {
      try { if (typeof window[fn] === 'function') window[fn](); } catch (e) {}
    });
    try { if (typeof saveLocal === 'function') saveLocal(); } catch (e) {}
  }
  function applyRemote(obj) {
    var C = getChar(); if (!C) return;
    applyingRemote = true;
    try {
      Object.keys(C).forEach(function (k) { delete C[k]; });
      Object.assign(C, obj);
      redraw();
      try { lastJSON = JSON.stringify(C); } catch (e) {}
    } finally { applyingRemote = false; }
  }
  function scheduleSave(delay) {
    if (applyingRemote || !ready) return;
    clearTimeout(writeTimer);
    writeTimer = setTimeout(function () {
      ref.set({ data: lastJSON, char: charId,
                updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
                updatedBy: auth.currentUser ? auth.currentUser.uid : null }, { merge: true })
        .catch(function (e) { console.warn('[sync] write', e.code || e.message); });
    }, delay || 150);
  }
  function quickSync() {
    if (applyingRemote || !ready) return;
    var C = getChar(); if (!C) return;
    var cur; try { cur = JSON.stringify(C); } catch (e) { return; }
    if (cur !== lastJSON) { lastJSON = cur; scheduleSave(120); }
  }
  function touch() { setTimeout(quickSync, 0); }
  ['input', 'change', 'keyup', 'click'].fo