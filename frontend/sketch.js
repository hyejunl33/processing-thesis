// MathLens — Processing (p5.js) visualization.
// Boundary: this file renders BarModelSpec and sends interaction events.
// It never parses the problem and never computes the final answer.

let problemSpec = null;
let modelSpec = null;
let sessionId = makeSessionId();

const answerEl = document.getElementById("answer");
const answerLabelEl = document.getElementById("answer-label");
const answerValueEl = document.getElementById("answer-value");
const statusEl = document.getElementById("status");
const feedbackEl = document.getElementById("feedback");
const hintBoxEl = document.getElementById("hint-box");

function makeSessionId() {
  if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
  return "s_" + Math.random().toString(36).slice(2, 12);
}

function setup() {
  const wrap = document.getElementById("canvas-wrap");
  const c = createCanvas(wrap.clientWidth || 680, 440);
  c.parent(wrap);
  textFont("sans-serif");

  document.getElementById("analyze").addEventListener("click", analyze);
  document.getElementById("hint").addEventListener("click", requestHint);
  document.getElementById("check").addEventListener("click", checkAnswer);

  answerEl.addEventListener("input", () => {
    answerValueEl.textContent = answerEl.value;
    redraw();
  });
  answerEl.addEventListener("change", () => {
    logEvent("answer_change", { value: Number(answerEl.value) });
  });

  document.getElementById("session").textContent = "session " + sessionId.slice(0, 8);
}

function windowResized() {
  const wrap = document.getElementById("canvas-wrap");
  resizeCanvas(wrap.clientWidth || 680, 440);
}

function draw() {
  background("#fbfdff");

  if (!modelSpec) {
    noStroke();
    fill("#5d6b78");
    textAlign(CENTER, CENTER);
    textSize(15);
    text("문장제를 입력하고 ‘분석’을 누르면 막대 모델이 나타납니다.", width / 2, height / 2 - 12);
    textSize(12);
    fill("#8a98a5");
    text("AI는 정답을 말하지 않고, 관계 구조만 막대 길이로 바꿉니다.", width / 2, height / 2 + 16);
    return;
  }

  const marginX = 26;
  const labelW = 102;
  const top = 58;
  const barH = 52;
  const gap = 46;
  const maxBarWidth = width - marginX * 2 - labelW - 82;
  const unit = Math.min(
    modelSpec.scale.unit_px || 40,
    maxBarWidth / Math.max(1, modelSpec.scale.max_value || 10)
  );
  const x0 = marginX + labelW;

  noStroke();
  fill("#5d6b78");
  textAlign(LEFT, CENTER);
  textSize(12);
  text(modelSpec.type === "comparison" ? "비교 막대 모델" : "막대 모델", marginX, 26);
  text("단위: " + fmt(modelSpec.scale.max_value) + "까지", marginX, 42);

  modelSpec.bars.forEach((bar, i) => {
    const y = top + i * (barH + gap);
    drawBar(bar, x0, y, unit, barH, i);
  });

  drawAnnotations(x0, unit, top, barH, gap);
  drawAnswerMarker(x0, unit, top, barH, gap);

  noStroke();
  fill("#8a98a5");
  textAlign(LEFT, BOTTOM);
  textSize(11);
  text("막대 길이를 비교하고, 아래 슬라이더로 내 답을 움직여 보세요.", marginX, height - 12);
}

function drawBar(bar, x0, y, unit, barH, index) {
  const isUnknown = bar.id === modelSpec.unknown_bar;
  const hover = mouseX > x0 && mouseX < x0 + barWidth(bar, unit) && mouseY > y && mouseY < y + barH;

  if (hover) {
    noStroke();
    fill("#eef7fd");
    rect(x0 - 8, y - 8, barWidth(bar, unit) + 16, barH + 16, 10);
  }

  let x = x0;
  const segments = bar.segments && bar.segments.length ? bar.segments : [{ value: bar.value || 0, color: "#AED6F1" }];
  segments.forEach((seg) => {
    const w = Math.max(0, seg.value * unit);
    noStroke();
    fill(seg.color);
    rect(x, y, w, barH, 5);
    if (w > 28) {
      fill("#17232e");
      textAlign(CENTER, CENTER);
      textSize(12);
      text(seg.label || fmt(seg.value), x + w / 2, y + barH / 2);
    }
    x += w;
  });

  if (isUnknown) {
    noFill();
    stroke("#2f7ebc");
    strokeWeight(1.5);
    drawingContext.setLineDash([7, 5]);
    rect(x0, y, Math.max(barWidth(bar, unit), 4), barH, 5);
    drawingContext.setLineDash([]);
    noStroke();
    fill("#2f7ebc");
    textAlign(LEFT, CENTER);
    textSize(13);
    text("?", x0 + barWidth(bar, unit) + 10, y + barH / 2);
  } else {
    noStroke();
    fill("#5d6b78");
    textAlign(LEFT, CENTER);
    textSize(12);
    text(fmt(bar.value) + "개", x0 + barWidth(bar, unit) + 10, y + barH / 2);
  }

  noStroke();
  fill("#17232e");
  textAlign(RIGHT, CENTER);
  textSize(13);
  text(bar.label, x0 - 14, y + barH / 2);
}

function drawAnnotations(x0, unit, top, barH, gap) {
  modelSpec.annotations.forEach((ann) => {
    if (ann.type !== "difference" || !ann.from_bar || !ann.to_bar) return;
    const from = modelSpec.bars.find((b) => b.id === ann.from_bar);
    const to = modelSpec.bars.find((b) => b.id === ann.to_bar);
    if (!from || !to) return;
    const iFrom = modelSpec.bars.indexOf(from);
    const iTo = modelSpec.bars.indexOf(to);
    const y = top + Math.max(iFrom, iTo) * (barH + gap) + barH + 18;
    const x1 = x0 + barWidth(from, unit);
    const x2 = x0 + barWidth(to, unit);
    drawArrow(x1, x2, y, ann.label || "차이");
  });
}

function drawAnswerMarker(x0, unit, top, barH, gap) {
  const bar = modelSpec.bars.find((b) => b.id === modelSpec.unknown_bar);
  if (!bar) return;
  const answer = Number(answerEl.value);
  if (!Number.isFinite(answer) || answer <= 0) return;
  const i = modelSpec.bars.indexOf(bar);
  const y = top + i * (barH + gap);
  const x = x0 + answer * unit;
  stroke("#c0392b");
  strokeWeight(1.5);
  drawingContext.setLineDash([4, 4]);
  line(x, y - 8, x, y + barH + 8);
  drawingContext.setLineDash([]);
  noStroke();
  fill("#c0392b");
  textAlign(CENTER, BOTTOM);
  textSize(11);
  text("내 답 " + answer, x, y - 10);
}

function drawArrow(x1, x2, y, label) {
  const left = Math.min(x1, x2);
  const right = Math.max(x1, x2);
  stroke("#b65c2c");
  strokeWeight(1.5);
  line(left, y, right, y);

  const head = 5;
  fill("#b65c2c");
  noStroke();
  triangle(left, y, left + head, y - head, left + head, y + head);
  triangle(right, y, right - head, y - head, right - head, y + head);

  fill("#b65c2c");
  textAlign(CENTER, BOTTOM);
  textSize(11);
  text(label, (left + right) / 2, y - 6);
}

function barWidth(bar, unit) {
  const total = (bar.segments || []).reduce((sum, seg) => sum + seg.value, 0);
  return Math.max(0, (bar.value != null ? bar.value : total) * unit);
}

function fmt(value) {
  if (value == null || Number.isNaN(value)) return "?";
  return Number.isInteger(value) ? String(value) : String(Math.round(value * 100) / 100);
}

function setStatus(text) {
  statusEl.textContent = text;
}

function setBusy(busy) {
  ["analyze", "hint", "check"].forEach((id) => {
    document.getElementById(id).disabled = busy;
  });
}

async function analyze() {
  const text = document.getElementById("problem").value.trim();
  if (!text) {
    setStatus("문장제를 입력해 주세요.");
    return;
  }

  setBusy(true);
  setStatus("분석 중…");
  feedbackEl.textContent = "";
  hintBoxEl.hidden = true;

  try {
    const parseRes = await fetch("/api/problems/parse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!parseRes.ok) throw new Error(await parseRes.text());
    problemSpec = await parseRes.json();

    const modelRes = await fetch("/api/models/build", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(problemSpec),
    });
    if (!modelRes.ok) throw new Error(await modelRes.text());
    modelSpec = await modelRes.json();

    const unknownBar = modelSpec.bars.find((b) => b.id === modelSpec.unknown_bar);
    answerLabelEl.textContent = (unknownBar ? unknownBar.label : "답") + " 수";
    answerEl.max = String(Math.max(20, Math.ceil((modelSpec.scale.max_value || 10) * 1.5)));
    answerEl.value = "0";
    answerValueEl.textContent = "0";

    setStatus("분석 완료");
    logEvent("analyze", {
      problem_type: problemSpec.problem_type,
      warnings: problemSpec.warnings || [],
    });
  } catch (err) {
    console.error(err);
    setStatus("오류: " + err.message);
  } finally {
    setBusy(false);
    redraw();
  }
}

async function requestHint() {
  if (!problemSpec || !modelSpec) {
    setStatus("먼저 문장제를 분석해 주세요.");
    return;
  }

  try {
    const res = await fetch("/api/hints", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        problem: problemSpec,
        model: modelSpec,
        student_state: { answer: Number(answerEl.value) },
        history: [],
      }),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    hintBoxEl.hidden = false;
    hintBoxEl.textContent = data.text;
    logEvent("hint", { source: data.source, level: data.level, focus: data.focus });
  } catch (err) {
    console.error(err);
    setStatus("힌트 오류: " + err.message);
  }
}

async function checkAnswer() {
  if (!problemSpec || !modelSpec) {
    setStatus("먼저 문장제를 분석해 주세요.");
    return;
  }

  try {
    const answer = Number(answerEl.value);
    const res = await fetch("/api/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ problem: problemSpec, answer }),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    feedbackEl.textContent = data.message;
    feedbackEl.style.color = data.correct ? "#1e8449" : "#b65c2c";
    logEvent("check", { answer, correct: data.correct });
  } catch (err) {
    console.error(err);
    setStatus("확인 오류: " + err.message);
  }
}

function logEvent(type, payload) {
  if (!problemSpec) return;
  fetch("/api/events", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      problem_id: problemSpec.id,
      ts: Date.now() / 1000,
      type,
      target: modelSpec ? modelSpec.unknown_bar : null,
      payload: payload || {},
    }),
  }).catch(() => {});
}
