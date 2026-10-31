(function () {
"use strict";

var stage = document.getElementById("stage");
var scorechip = document.getElementById("scorechip");
var progressTrack = document.getElementById("progressTrack");
var progressFill = document.getElementById("progressFill");

var state = null; // set once an exam is picked
var timerHandle = null;

function esc(s) {
  return String(s).replace(/[&<>"']/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
  });
}
function arraysEqual(a, b) {
  if (a.length !== b.length) return false;
  for (var i = 0; i < a.length; i++) if (a[i] !== b[i]) return false;
  return true;
}
function correctIndices(opts) {
  return opts.map(function (o, i) { return o.c ? i : null; }).filter(function (v) { return v !== null; });
}

// ---------- picker screen ----------

function renderPicker(manifest) {
  scorechip.hidden = true;
  progressTrack.hidden = true;
  var html = '<div class="card">';
  html += '<div class="meta-row"><span class="domain-tag">Pick a set</span></div>';
  html += '<div class="question" style="font-size:16px">Mock exams (65 Qs, scraped &amp; verified single-answer questions, official explanation per question)</div>';
  html += '<div class="pickgrid">';
  manifest.exams.forEach(function (e) {
    html += '<div class="pickrow" data-file="' + esc(e.file) + '" data-timed="1">' +
      '<div><div class="name">' + esc(e.label) + '</div><div class="sub">' + e.count + ' questions &middot; ~' + Math.round(e.count / 65 * 130) + ' min</div></div>' +
      '<div class="sub">Start &rarr;</div></div>';
  });
  html += '</div>';
  html += '<div class="meta-row" style="margin-top:4px"><span class="domain-tag">Drill</span></div>';
  html += '<div class="question" style="font-size:16px">Curated drill (33 Qs, hand-written, full per-option explanations)</div>';
  html += '<div class="pickgrid">';
  html += '<div class="pickrow" data-file="curated.json" data-timed="0">' +
    '<div><div class="name">Curated drill set</div><div class="sub">33 questions &middot; untimed, every option explained</div></div>' +
    '<div class="sub">Start &rarr;</div></div>';
  html += '</div></div>';
  stage.innerHTML = html;

  stage.querySelectorAll(".pickrow").forEach(function (row) {
    row.addEventListener("click", function () {
      var file = row.getAttribute("data-file");
      var timed = row.getAttribute("data-timed") === "1";
      loadExam(file, timed);
    });
  });
}

function loadExam(file, timed) {
  fetch("data/" + file)
    .then(function (r) { return r.json(); })
    .then(function (questions) {
      startExam(questions, timed);
    })
    .catch(function (err) {
      stage.innerHTML = '<div class="card"><div class="verdict fail">Could not load ' + esc(file) + ' — ' + esc(err.message) +
        '. If you opened index.html directly from disk, serve the folder instead: <code>python3 -m http.server</code> then open http://localhost:8000.</div></div>';
    });
}

// ---------- exam runner ----------

function startExam(questions, timed) {
  state = {
    questions: questions,
    idx: 0,
    answered: false,
    selected: {},
    correctCount: 0,
    answeredCount: 0,
    timed: timed,
    secondsLeft: timed ? Math.round(questions.length / 65 * 130 * 60) : null,
  };
  scorechip.hidden = false;
  progressTrack.hidden = false;
  if (timerHandle) clearInterval(timerHandle);
  if (timed) {
    timerHandle = setInterval(function () {
      state.secondsLeft -= 1;
      if (state.secondsLeft <= 0) {
        clearInterval(timerHandle);
        state.secondsLeft = 0;
        state.idx = state.questions.length; // time's up -> jump to summary
        render();
        return;
      }
      updateTimerDisplay();
    }, 1000);
  }
  render();
}

function updateTimerDisplay() {
  var el = document.getElementById("timerDisplay");
  if (!el || state.secondsLeft == null) return;
  var m = Math.floor(state.secondsLeft / 60);
  var s = state.secondsLeft % 60;
  el.textContent = "Time left: " + m + ":" + (s < 10 ? "0" : "") + s;
  el.classList.toggle("low", state.secondsLeft < 300);
}

function updateTop() {
  var total = state.questions.length;
  progressFill.style.width = (Math.min(state.idx, total) / total * 100) + "%";
  scorechip.textContent = state.correctCount + " / " + state.answeredCount + " correct";
}

function render() {
  updateTop();
  if (state.idx >= state.questions.length) { renderSummary(); return; }

  var q = state.questions[state.idx];
  var ansKey = String(state.idx);
  var picked = state.selected[ansKey] || [];
  var locked = !!state.answered;

  var html = '<div class="card">';
  html += '<div class="meta-row">';
  html += q.d ? '<span class="domain-tag">' + esc(q.d) + '</span>' : '<span class="domain-tag">Question</span>';
  html += '<span class="qnum">Question ' + (state.idx + 1) + ' of ' + state.questions.length + '</span>';
  html += '</div>';
  if (state.timed) html += '<div class="timer" id="timerDisplay"></div>';
  html += '<div class="question">' + esc(q.q) + '</div>';
  if (q.multi || q.n_correct > 1) html += '<div class="hint">Select all answers that apply.</div>';

  html += '<div class="options" id="optList">';
  q.o.forEach(function (opt, oi) {
    var isPicked = picked.indexOf(oi) !== -1;
    var isMulti = q.multi || q.n_correct > 1;
    var cls = "opt" + (locked ? " locked" : "");
    if (locked) {
      if (opt.c) cls += " correct";
      else if (isPicked && !opt.c) cls += " incorrect";
    }
    html += '<label class="' + cls + '" data-oi="' + oi + '">';
    html += '<input type="' + (isMulti ? "checkbox" : "radio") + '" name="opt" ' + (isPicked ? "checked" : "") + ' ' + (locked ? "disabled" : "") + '>';
    html += '<span class="otext">' + esc(opt.t);
    if (locked && opt.w) html += '<div class="why">' + esc(opt.w) + '</div>';
    html += '</span></label>';
  });
  html += '</div>';

  if (locked) {
    var correctSet = correctIndices(q.o);
    var isRight = arraysEqual(picked.slice().sort(), correctSet.slice().sort());
    html += '<div class="verdict ' + (isRight ? "pass" : "fail") + '">' + (isRight ? "Correct" : "Not quite — review the explanation") + '</div>';
    if (q.explain) html += '<div class="explain-block">' + esc(q.explain) + '</div>';
  }

  html += '<div class="actions">';
  if (!locked) {
    html += '<button class="primary" id="submitBtn" disabled>Check answer</button>';
  } else {
    html += '<button class="primary" id="nextBtn">' + (state.idx === state.questions.length - 1 ? "See results" : "Next question") + '</button>';
  }
  html += '</div></div>';

  stage.innerHTML = html;
  if (state.timed) updateTimerDisplay();
  wireOptions(q, ansKey, locked);
}

function wireOptions(q, ansKey, locked) {
  if (locked) {
    document.getElementById("nextBtn").addEventListener("click", function () {
      state.idx += 1;
      state.answered = false;
      render();
    });
    return;
  }
  var isMulti = q.multi || q.n_correct > 1;
  var opts = stage.querySelectorAll(".opt");
  var submitBtn = document.getElementById("submitBtn");
  opts.forEach(function (el) {
    el.addEventListener("click", function (ev) {
      ev.preventDefault();
      var oi = parseInt(el.getAttribute("data-oi"), 10);
      var cur = state.selected[ansKey] || [];
      if (isMulti) {
        var pos = cur.indexOf(oi);
        if (pos === -1) cur.push(oi); else cur.splice(pos, 1);
      } else {
        cur = [oi];
      }
      state.selected[ansKey] = cur;
      opts.forEach(function (el2) {
        var oi2 = parseInt(el2.getAttribute("data-oi"), 10);
        el2.querySelector("input").checked = cur.indexOf(oi2) !== -1;
      });
      submitBtn.disabled = cur.length === 0;
    });
  });
  submitBtn.addEventListener("click", function () {
    state.answered = true;
    state.answeredCount += 1;
    var picked = state.selected[ansKey] || [];
    var correctSet = correctIndices(q.o);
    var isRight = arraysEqual(picked.slice().sort(), correctSet.slice().sort());
    if (isRight) state.correctCount += 1;
    render();
  });
}

function renderSummary() {
  if (timerHandle) clearInterval(timerHandle);
  var total = state.questions.length;
  var pct = total ? Math.round(state.correctCount / total * 100) : 0;
  var byDomain = {};
  var hasDomains = state.questions.some(function (q) { return q.d; });

  if (hasDomains) {
    state.questions.forEach(function (q, qi) {
      var d = q.d || "General";
      byDomain[d] = byDomain[d] || { correct: 0, total: 0 };
      byDomain[d].total += 1;
      var picked = state.selected[String(qi)] || [];
      var correctSet = correctIndices(q.o);
      if (arraysEqual(picked.slice().sort(), correctSet.slice().sort())) byDomain[d].correct += 1;
    });
  }

  var html = '<div class="card summary">';
  html += '<div class="domain-tag">' + (state.answeredCount < total ? "Time's up" : "Exam complete") + '</div>';
  html += '<div class="big">' + pct + '%</div>';
  html += '<div style="color:var(--muted);font-size:14px">' + state.correctCount + ' of ' + total + ' questions correct' +
    (state.answeredCount < total ? ' (' + (total - state.answeredCount) + ' unanswered)' : '') + '</div>';
  html += '<div style="font-size:13px;color:var(--muted)">AWS SAA-C03 passing score is 720/1000 (roughly 72%).</div>';

  if (hasDomains) {
    html += '<div class="domainbars">';
    Object.keys(byDomain).forEach(function (d) {
      var b = byDomain[d];
      var p = b.total ? Math.round(b.correct / b.total * 100) : 0;
      html += '<div class="dbar-row"><div class="dbar-label">' + esc(d) + '</div><div class="dbar-track"><div class="dbar-fill" style="width:' + p + '%"></div></div><div class="dbar-val">' + b.correct + '/' + b.total + '</div></div>';
    });
    html += '</div>';
  }
  html += '<button class="primary" id="restartBtn" style="margin-top:8px">Back to set picker</button>';
  html += '</div>';
  stage.innerHTML = html;
  document.getElementById("restartBtn").addEventListener("click", function () {
    state = null;
    scorechip.hidden = true;
    progressTrack.hidden = true;
    init();
  });
}

function init() {
  fetch("data/manifest.json")
    .then(function (r) { return r.json(); })
    .then(function (manifest) { renderPicker(manifest); })
    .catch(function (err) {
      stage.innerHTML = '<div class="card"><div class="verdict fail">Could not load data/manifest.json — ' + esc(err.message) +
        '. Serve this folder over HTTP (e.g. <code>python3 -m http.server</code>) rather than opening index.html directly.</div></div>';
    });
}

init();
})();
