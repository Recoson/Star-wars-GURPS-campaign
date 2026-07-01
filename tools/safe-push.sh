#!/bin/sh
# safe-push.sh -- the ship step, with the error-prone parts automated and the
# one unautomatable part handed back safely.
#
#   [stage + commit] -> check.py gate -> fetch -> rebase origin/main
#                    -> check.py re-gate -> push origin main   (token-masked)
#
# Guarantees:
#   * never pushes a tree that fails check.py (invariant + golden-math gate);
#   * never pushes without first rebasing onto the current origin/main;
#   * masks any token that leaks into git output (belt-and-braces -- the
#     credential.helper setup already keeps the token out of the remote);
#   * on a rebase conflict, aborts + hard-resets to a clean origin/main and
#     STOPS. Re-applying the patch fresh needs the session's own patch script,
#     which this wrapper cannot reproduce. (It treats EVERY conflict this way,
#     including the odd hand-mergeable one -- safe over clever. Re-apply, re-run.)
#
# Usage:  sh tools/safe-push.sh "commit message"    # stage -A, commit, ship
#         sh tools/safe-push.sh                      # already committed: just ship
# Run from anywhere inside the repo. POSIX / dash-safe (no bashisms, no pipefail).
set -eu

MASK='s/github_pat_[A-Za-z0-9_]*/***/g; s#x-access-token:[^@]*@#x-access-token:***@#g; s/gh[pousr]_[A-Za-z0-9]*/***/g'
cd "$(git rev-parse --show-toplevel)"

# 1. optional stage + commit
if [ "${1-}" != "" ]; then
  git add -A
  if git diff --cached --quiet; then
    echo "safe-push: nothing staged; proceeding to gate / sync / push."
  else
    git commit -m "$1"
  fi
fi

# 2. gate BEFORE touching the remote -- fail fast on your own breakage
echo "== check.py (pre-push gate) =="
if ! python3 check.py; then
  echo "safe-push: ABORT -- check.py failed. Fix invariants before pushing."
  exit 1
fi

# 3. sync onto current origin/main (rc captured via temp file; dash has no pipefail)
echo "== fetch origin/main =="
git fetch origin main 2>&1 | sed -E "$MASK" \
  || echo "  (fetch reported an issue; continuing -- a stale base is caught at push)"
echo "== rebase origin/main =="
tmp=$(mktemp)
if git rebase origin/main >"$tmp" 2>&1; then rc=0; else rc=$?; fi
sed -E "$MASK" "$tmp"; rm -f "$tmp"
if [ "$rc" -ne 0 ]; then
  echo
  echo "safe-push: rebase conflict. Recovering to a clean origin/main and STOPPING."
  echo "  Re-apply your patch fresh against origin/main (re-check state first -- a"
  echo "  parallel session may have already done your task), then re-run safe-push."
  git rebase --abort 2>/dev/null || true
  git reset --hard origin/main 2>&1 | sed -E "$MASK"
  exit 2
fi

# 4. re-gate the rebased tree (an origin change may interact), then push
echo "== check.py (post-rebase re-gate) =="
if ! python3 check.py; then
  echo "safe-push: ABORT -- check.py failed AFTER rebase (an origin change interacts"
  echo "  with yours). Resolve locally; not pushing."
  exit 1
fi
echo "== push origin main =="
tmp=$(mktemp)
if git push origin main >"$tmp" 2>&1; then rc=0; else rc=$?; fi
sed -E "$MASK" "$tmp"; rm -f "$tmp"
if [ "$rc" -ne 0 ]; then
  echo "safe-push: push failed (rc=$rc). If non-fast-forward, re-run to fetch + rebase again."
  exit "$rc"
fi
echo "safe-push: shipped. Remote HEAD ->"
git ls-remote origin main | sed -E "$MASK"
