/* Dara Dara — Firebase live character sync  (v4 — modular SDK, named 'kotor' database) */
import { initializeApp, getApps, getApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getAuth, onAuthStateChanged, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import { getFirestore, doc, onSnapshot, setDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

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

  var app  = getApps().length ? getApp() : initializeApp(firebaseConfig);
  var auth = getAuth(app);
  var db   = getFirestore(app, 'kotor');   // ← named Cloud Firestore database (NOT "(default)")

  var charId = (new URLSearchParams(location.search).get('char') || 'default')
                 .toLowerCase().replace(/[^a-z0-9_-]/g, '') || 'default';
  var ref = doc(db, 'characters', charId);
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
      setDoc(ref, { data: lastJSON, char: charId,
                    updatedAt: serverTimestamp(),
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
  ['input', 'change', 'keyup', 'click'].forEach(function (ev) {
    document.addEventListener(ev, touch, true);
  });
  setInterval(quickSync, 2000);

  function subscribe() {
    onSnapshot(ref, function (snap) {
      var C = getChar();
      if (!snap.exists()) {
        if (C) { try { lastJSON = JSON.stringify(C); } catch (e) { lastJSON = ''; } ready = true; scheduleSave(150); }
        else { ready = true; }
        pill('live · seeded'); return;
      }
      var d = snap.data() || {};
      if (d.updatedBy && auth.currentUser && d.updatedBy === auth.currentUser.uid) {
        lastJSON = d.data || lastJSON; ready = true; pill('live'); return;
      }
      try { if (d.data) applyRemote(JSON.parse(d.data)); }
      catch (e) { console.warn('[sync] parse', e); }
      ready = true; pill('live');
    }, function (err) { console.warn('[sync] snapshot', err.code || err.message); pill('error'); });
  }
  function pill(state) {
    var p = document.getElementById('fb-status');
    if (!p) {
      p = document.createElement('div'); p.id = 'fb-status';
      p.style.cssText = 'position:fixed;bottom:8px;right:10px;z-index:9998;font:11px/1.4 system-ui,sans-serif;padding:4px 9px;border-radius:11px;cursor:pointer;user-select:none;background:rgba(26,20,16,.85)';
      document.body.appendChild(p);
    }
    var inn = !!auth.currentUser;
    p.style.color = ({ 'live':'#7ddc8a','live · seeded':'#7ddc8a','error':'#ff9c6b','sign in for live sync':'#ffce6b' }[state]) || '#bbb';
    p.textContent = (inn ? '● ' : '○ ') + state + '  ·  ' + charId;
    p.title = inn ? 'Live sync on — click to sign out' : 'Click to sign in';
    p.onclick = inn ? function () { signOut(auth); } : function () { gate(true); };
  }
  function gate(show) {
    var o = document.getElementById('fb-login');
    if (!o) {
      o = document.createElement('div'); o.id = 'fb-login';
      o.style.cssText = 'position:fixed;inset:0;background:rgba(15,11,8,.92);display:flex;align-items:center;justify-content:center;z-index:99999;font-family:system-ui,sans-serif';
      o.innerHTML =
        '<div style="background:#241c15;padding:26px;border-radius:12px;width:300px;box-shadow:0 12px 44px #000b;color:#ecdfc8;position:relative">' +
          '<div id="fb-x" style="position:absolute;top:10px;right:14px;cursor:pointer;opacity:.6;font-size:18px">×</div>' +
          '<div style="font-size:18px;margin-bottom:4px">Dara Dara</div>' +
          '<div id="fb-sub" style="font-size:12px;opacity:.7;margin-bottom:14px">Sign in for live sync</div>' +
          '<input id="fb-e" type="email" placeholder="email" autocomplete="username" style="width:100%;margin:5px 0;padding:9px;box-sizing:border-box;border-radius:6px;border:1px solid #4a3c2c;background:#1a140f;color:#ecdfc8">' +
          '<input id="fb-p" type="password" placeholder="password" autocomplete="current-password" style="width:100%;margin:5px 0;padding:9px;box-sizing:border-box;border-radius:6px;border:1px solid #4a3c2c;background:#1a140f;color:#ecdfc8">' +
          '<input id="fb-code" type="text" placeholder="invite code" style="display:none;width:100%;margin:5px 0;padding:9px;box-sizing:border-box;border-radius:6px;border:1px solid #4a3c2c;background:#1a140f;color:#ecdfc8">' +
          '<button id="fb-go" style="width:100%;margin-top:10px;padding:10px;border:0;border-radius:6px;background:#c98a3a;color:#1a140f;font-weight:600;cursor:pointer">Sign in</button>' +
          '<div id="fb-err" style="color:#ff7a9c;margin-top:10px;font-size:12px;min-height:14px"></div>' +
          '<div id="fb-toggle" style="margin-top:12px;font-size:12px;text-align:center;opacity:.85;cursor:pointer;text-decoration:underline">New here? Create an account</div>' +
        '</div>';
      document.body.appendChild(o);

      var mode = 'in';
      var eEl = o.querySelector('#fb-e'), pEl = o.querySelector('#fb-p'), codeEl = o.querySelector('#fb-code'),
          errEl = o.querySelector('#fb-err'), goEl = o.querySelector('#fb-go'),
          subEl = o.querySelector('#fb-sub'), toggleEl = o.querySelector('#fb-toggle');

      function setMode(m) {
        mode = m; errEl.textContent = '';
        if (m === 'up') {
          subEl.textContent = 'Create your account';
          goEl.textContent = 'Create account';
          toggleEl.textContent = 'Have an account? Sign in';
          codeEl.style.display = INVITE_CODE ? 'block' : 'none';
        } else {
          subEl.textContent = 'Sign in for live sync';
          goEl.textContent = 'Sign in';
          toggleEl.textContent = 'New here? Create an account';
          codeEl.style.display = 'none';
        }
      }
      toggleEl.onclick = function () { setMode(mode === 'in' ? 'up' : 'in'); };

      function go() {
        var email = eEl.value.trim(), pw = pEl.value;
        errEl.style.color = '#ff7a9c';
        if (!email || !pw) { errEl.textContent = 'enter email and password'; return; }
        if (mode === 'up') {
          if (INVITE_CODE && codeEl.value.trim() !== INVITE_CODE) { errEl.textContent = 'wrong invite code'; return; }
          if (pw.length < 6) { errEl.textContent = 'password needs 6+ characters'; return; }
          errEl.style.color = '#9c8'; errEl.textContent = 'creating account…';
          createUserWithEmailAndPassword(auth, email, pw)
            .then(function () { o.style.display = 'none'; })
            .catch(function (e) { errEl.style.color = '#ff7a9c'; errEl.textContent = (e.code || e.message).replace('auth/', ''); });
        } else {
          errEl.style.color = '#9c8'; errEl.textContent = 'signing in…';
          signInWithEmailAndPassword(auth, email, pw)
            .then(function () { o.style.display = 'none'; })
            .catch(function (e) { errEl.style.color = '#ff7a9c'; errEl.textContent = (e.code || e.message).replace('auth/', ''); });
        }
      }
      goEl.onclick = go;
      o.querySelector('#fb-x').onclick = function () { o.style.display = 'none'; };
      pEl.addEventListener('keydown', function (e) { if (e.key === 'Enter') go(); });
      codeEl.addEventListener('keydown', function (e) { if (e.key === 'Enter') go(); });
    }
    o.style.display = show ? 'flex' : 'none';
  }
  (function start() {
    if (!getChar()) return setTimeout(start, 300);
    onAuthStateChanged(auth, function (user) {
      if (user) { gate(false); ready = false; lastJSON = ''; subscribe(); }
      else { ready = false; pill('sign in for live sync'); }  // pill is clickable to open sign-in; no forced modal on load
    });
  })();
})();
