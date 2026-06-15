/* Dara Dara — Firebase live character sync  (classic script + Firebase "compat" SDK)
 * Installed via 4 <script> lines before </body> in sheet.html (see Step 2).
 * Uses the compat/global `firebase` build as a CLASSIC script on purpose, so it shares the
 * page scope and can see the sheet's character object `C` (an ES module cannot).
 * No secrets: the Firebase web config is PUBLIC by design; access is governed by Firestore rules. */
(function () {
  var firebaseConfig = {
    apiKey: "AIzaSyA2dj_J5d4OTMDEmeSTGin1s_DCRCV3kHg",
    authDomain: "kotor-gurps.firebaseapp.com",
    projectId: "kotor-gurps",
    storageBucket: "kotor-gurps.firebasestorage.app",
    messagingSenderId: "145157387485",
    appId: "1:145157387485:web:7a838273ba52923e445734"
  };
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
    try { Object.keys(C).forEach(function (k) { delete C[k]; }); Object.assign(C, obj); redraw(); }
    finally { applyingRemote = false; }
  }
  function scheduleSave() {
    if (applyingRemote || !ready) return;
    clearTimeout(writeTimer);
    writeTimer = setTimeout(function () {
      ref.set({ data: lastJSON, char: charId,
                updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
                updatedBy: auth.currentUser ? auth.currentUser.uid : null }, { merge: true })
        .catch(function (e) { console.warn('[sync] write', e.code || e.message); });
    }, 700);
  }
  setInterval(function () {
    if (applyingRemote || !ready) return;
    var C = getChar(); if (!C) return;
    var cur; try { cur = JSON.stringify(C); } catch (e) { return; }
    if (cur && cur !== lastJSON) { lastJSON = cur; scheduleSave(); }
  }, 1200);
  function subscribe() {
    ref.onSnapshot(function (snap) {
      var C = getChar();
      if (!snap.exists) {
        if (C) { try { lastJSON = JSON.stringify(C); } catch (e) { lastJSON = ''; } scheduleSave(); }
        ready = true; pill('live · seeded'); return;
      }
      var d = snap.data() || {};
      if (d.updatedBy && auth.currentUser && d.updatedBy === auth.currentUser.uid) {
        lastJSON = d.data || lastJSON; ready = true; pill('live'); return;
      }
      try { if (d.data) { applyRemote(JSON.parse(d.data)); lastJSON = d.data; } }
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
    p.onclick = inn ? function () { auth.signOut(); } : function () { gate(true); };
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
          '<div style="font-size:12px;opacity:.7;margin-bottom:14px">Sign in for live sync</div>' +
          '<input id="fb-e" type="email" placeholder="email" autocomplete="username" style="width:100%;margin:5px 0;padding:9px;box-sizing:border-box;border-radius:6px;border:1px solid #4a3c2c;background:#1a140f;color:#ecdfc8">' +
          '<input id="fb-p" type="password" placeholder="password" autocomplete="current-password" style="width:100%;margin:5px 0;padding:9px;box-sizing:border-box;border-radius:6px;border:1px solid #4a3c2c;background:#1a140f;color:#ecdfc8">' +
          '<button id="fb-go" style="width:100%;margin-top:10px;padding:10px;border:0;border-radius:6px;background:#c98a3a;color:#1a140f;font-weight:600;cursor:pointer">Sign in</button>' +
          '<div id="fb-err" style="color:#ff7a9c;margin-top:10px;font-size:12px;min-height:14px"></div>' +
        '</div>';
      document.body.appendChild(o);
      var go = function () {
        o.querySelector('#fb-err').textContent = 'signing in…';
        auth.signInWithEmailAndPassword(o.querySelector('#fb-e').value.trim(), o.querySelector('#fb-p').value)
          .then(function () { o.style.display = 'none'; })
          .catch(function (e) { o.querySelector('#fb-err').textContent = (e.code || e.message).replace('auth/', ''); });
      };
      o.querySelector('#fb-go').onclick = go;
      o.querySelector('#fb-x').onclick = function () { o.style.display = 'none'; };
      o.querySelector('#fb-p').addEventListener('keydown', function (e) { if (e.key === 'Enter') go(); });
    }
    o.style.display = show ? 'flex' : 'none';
  }
  (function start() {
    if (!getChar()) return setTimeout(start, 300);
    auth.onAuthStateChanged(function (user) {
      if (user) { gate(false); ready = false; lastJSON = ''; subscribe(); }
      else { pill('sign in for live sync'); gate(true); }
    });
  })();
})();