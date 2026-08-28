// theme.js — shared design system for the Sarvam workshop decks
// Palette: "Sovereign Midnight" — deep navy dominant, saffron accent, teal support.

const C = {
  INK:    "12172E",  // dominant deep midnight navy
  INK2:   "1E2547",  // raised card on dark
  INK3:   "2A3255",  // border / divider on dark
  SAF:    "FF8A3D",  // sharp saffron accent
  SAF2:   "FFB37A",  // soft saffron
  TEAL:   "2AA198",  // secondary accent
  GREEN:  "3FA34D",
  RED:    "E5484D",
  WHITE:  "FFFFFF",
  PAPER:  "F4F5F8",  // light slide background
  CARD:   "FFFFFF",
  MUTED:  "9AA0BA",  // muted text on dark
  MUTEDL: "5A6076",  // muted text on light
  CODEBG: "0B0F1F",
  CODEFG: "D8DEF5",
};

const F = { H: "Cambria", B: "Calibri", M: "Courier New" };

/* ---------- presenter identity (rendered on the FIRST title slide) ---------- */
// Edit once here; every deck's opening slide picks it up on the next rebuild.
const AUTHOR = {
  name:  "Dr. Bhaveshkumar C. Dharmani · PhD (ICT), DA-IICT Gandhinagar · Founder, AIVidhya4Sarvam",
  links: "https://www.aividhya.in/ · https://www.aividhya4sarvam.in/ · bhavesh@aividhya.in · https://www.linkedin.com/in/bhaveshdharmani/",
};
const W = 13.333, H = 7.5, M = 0.62;      // slide w/h, side margin
const CW = W - M * 2;                      // content width = 12.093

/* ---------- primitives ---------- */

function bg(slide, color) { slide.background = { color }; }

function txt(slide, text, o) {
  slide.addText(text, Object.assign({ fontFace: F.B, margin: 0 }, o));
}

// Page furniture on light content slides
function foot(slide, left, right) {
  txt(slide, left || "AIVidhya4Sarvam · Building with Sarvam", {
    x: M, y: H - 0.46, w: 7, h: 0.28, fontSize: 9, color: C.MUTEDL, align: "left",
  });
  if (right) txt(slide, right, {
    x: W - M - 4, y: H - 0.46, w: 4, h: 0.28, fontSize: 9, color: C.MUTEDL, align: "right",
  });
}

/* ---------- brand logo (top-right, auto-added by every slide shell) ---------- */

// Path is resolved by pptxgenjs at build time — relative to the CWD you invoke
// node from (i.e. Slides/build/). Override with the LOGO_PATH env var if needed.
const LOGO_PATH = process.env.LOGO_PATH || "./assets/logo.png";

// Two sizes: BIG for title/section slides where space is free,
// SMALL for content slides so it doesn't collide with the deck title (which
// starts at y=0.55 with kicker at y=0.42). Numbers preserve the same 1.585:1
// aspect ratio the user chose in his 01_Opening reference.
// Both boxes are kept fully INSIDE the 13.333 x 7.5 in slide with a real margin.
// (The earlier LOGO_BIG sat at x=11.330 w=2.468 → right edge 13.798, i.e. 0.465"
//  past the right edge, so PowerPoint clipped the logo on every title/section
//  slide. Aspect ratio 1.583:1 is preserved in both boxes.)
const LOGO_MARGIN = 0.34;                                        // clear space at the right edge
const LOGO_BIG   = { x: 10.933, y: 0.300, w: 2.060, h: 1.301 };  // right edge 12.993 → 0.34" clear
const LOGO_SMALL = { x: 12.033, y: 0.230, w: 0.960, h: 0.606 };  // right edge 12.993 → 0.34" clear

// Load the logo once as base64 so pptxgenjs can dedupe the embed across slides.
// (Passing `path:` per-slide causes pptxgenjs to embed a fresh copy each time,
// which inflates a 9-slide deck from ~600KB to ~5MB.)
const fs = require("fs");
let _LOGO_DATA = null;
function _logoData() {
  if (_LOGO_DATA !== null) return _LOGO_DATA;
  try {
    const b64 = fs.readFileSync(LOGO_PATH).toString("base64");
    _LOGO_DATA = "data:image/png;base64," + b64;
  } catch (e) {
    console.warn(`theme.js: could not load logo at ${LOGO_PATH} — slides will render without the brand mark. (${e.message})`);
    _LOGO_DATA = false;
  }
  return _LOGO_DATA;
}

// Define once per presentation — call this on your `p` before adding slides,
// OR let slide shells call it lazily. Uses slide masters so the logo image
// is embedded ONE time per pptx file and referenced from every slide.
function ensureMasters(pres) {
  if (pres._logoMastersReady) return;
  const data = _logoData();
  if (data === false) { pres._logoMastersReady = true; return; }
  pres.defineSlideMaster({
    title: "MASTER_LOGO_BIG",
    background: { color: C.INK },
    objects: [{ image: { data, ...LOGO_BIG } }],
  });
  pres.defineSlideMaster({
    title: "MASTER_LOGO_SMALL_DARK",
    background: { color: C.INK },
    objects: [{ image: { data, ...LOGO_SMALL } }],
  });
  pres.defineSlideMaster({
    title: "MASTER_LOGO_SMALL_LIGHT",
    background: { color: C.PAPER },
    objects: [{ image: { data, ...LOGO_SMALL } }],
  });
  pres._logoMastersReady = true;
}

// Public entrypoint — kept for backward compatibility, but with masters in place
// the slide shells no longer need to call this per-slide.
function logo(slide, size) {
  const box = (size === "big") ? LOGO_BIG : LOGO_SMALL;
  const data = _logoData();
  if (data === false) return;
  slide.addImage({ data, ...box });
}

// Convenience — create a slide bound to a logo master. Falls back to a plain
// slide with background set explicitly if the logo cannot load.
function _newSlide(pres, kind) {
  ensureMasters(pres);
  const data = _logoData();
  if (data === false) {
    const s = pres.addSlide();
    s.background = { color: kind === "light" ? C.PAPER : C.INK };
    return s;
  }
  const masterName =
    kind === "big"   ? "MASTER_LOGO_BIG" :
    kind === "light" ? "MASTER_LOGO_SMALL_LIGHT" :
                       "MASTER_LOGO_SMALL_DARK";
  return pres.addSlide({ masterName });
}

/* ---------- slide shells ---------- */

function titleSlide(pres, o) {
  // Title slides have the saffron rings in the top-right, which would cover a
  // master-supplied logo. So we skip the master image here and place the logo
  // AFTER the rings on the slide itself — one direct embed per title slide.
  ensureMasters(pres);
  const s = pres.addSlide(); bg(s, C.INK);
  // motif: saffron ring, top-right
  s.addShape(pres.ShapeType.ellipse, { x: W - 3.1, y: -1.5, w: 4.6, h: 4.6, fill: { color: C.INK2 } });
  s.addShape(pres.ShapeType.ellipse, { x: W - 2.35, y: -0.75, w: 3.1, h: 3.1, line: { color: C.SAF, width: 2 }, fill: { type: "none" } });
  if (o.eyebrow) txt(s, o.eyebrow.toUpperCase(), {
    x: M, y: 2.15, w: 9, h: 0.32, fontSize: 12, bold: true, color: C.SAF, charSpacing: 3,
  });
  txt(s, o.title, { x: M, y: 2.62, w: 9.6, h: 1.9, fontFace: F.H, fontSize: 44, bold: true, color: C.WHITE, lineSpacing: 46 });
  if (o.subtitle) txt(s, o.subtitle, { x: M, y: 4.62, w: 9.4, h: 0.9, fontSize: 17, color: C.SAF2, lineSpacing: 26 });

  // Any deck-specific meta lines move UP so the identity block owns the base.
  if (o.meta) txt(s, o.meta, { x: M, y: 5.52, w: 11.3, h: 0.62, fontSize: 12, color: C.MUTED, lineSpacing: 17 });

  // Presenter identity — first title slide of each deck only. Decks that close
  // on a second title slide (e.g. 08) must not repeat it.
  if (!pres._authorBlockDone) {
    authorBlock(pres, s);
    pres._authorBlockDone = true;
  }

  logo(s, "big");   // drawn last → sits on top of the rings, matches 01_Opening reference
  return s;
}

// Name, credentials and contact links, pinned to the bottom of a title slide.
function authorBlock(pres, s) {
  s.addShape(pres.ShapeType.rect, {
    x: M, y: 6.30, w: 3.2, h: 0.02, fill: { color: C.SAF },
  });
  txt(s, AUTHOR.name, {
    x: M, y: 6.44, w: CW, h: 0.28, fontSize: 11.5, bold: true, color: C.WHITE,
  });
  txt(s, AUTHOR.links, {
    x: M, y: 6.76, w: CW, h: 0.26, fontSize: 9.5, color: C.SAF2,
  });
}

function sectionSlide(pres, o) {
  const s = _newSlide(pres, "big");
  s.addShape(pres.ShapeType.ellipse, { x: M, y: 2.5, w: 1.5, h: 1.5, fill: { color: C.SAF } });
  txt(s, o.num, { x: M, y: 2.86, w: 1.5, h: 0.8, fontFace: F.H, fontSize: 34, bold: true, color: C.INK, align: "center" });
  txt(s, o.title, { x: M + 2.05, y: 2.55, w: 9.4, h: 1.0, fontFace: F.H, fontSize: 34, bold: true, color: C.WHITE });
  if (o.subtitle) txt(s, o.subtitle, { x: M + 2.05, y: 3.6, w: 9.2, h: 0.9, fontSize: 15, color: C.MUTED, lineSpacing: 23 });
  return s;
}

// Light content slide. Returns slide; content should start at y >= 1.55
// Title/kicker width on content slides must stop short of the top-right logo,
// or a long title runs underneath it. HEADW is that collision-free width.
const HEADW = LOGO_SMALL.x - M - 0.12;      // 12.033 - 0.62 - 0.12 = 11.293

function slideL(pres, title, kicker) {
  const s = _newSlide(pres, "light");
  if (kicker) txt(s, kicker.toUpperCase(), { x: M, y: 0.42, w: HEADW, h: 0.26, fontSize: 10, bold: true, color: C.SAF, charSpacing: 2.5 });
  txt(s, title, { x: M, y: kicker ? 0.72 : 0.55, w: HEADW, h: 0.75, fontFace: F.H, fontSize: 30, bold: true, color: C.INK });
  return s;
}

// Dark content slide
function slideD(pres, title, kicker) {
  const s = _newSlide(pres, "dark");
  if (kicker) txt(s, kicker.toUpperCase(), { x: M, y: 0.42, w: HEADW, h: 0.26, fontSize: 10, bold: true, color: C.SAF, charSpacing: 2.5 });
  txt(s, title, { x: M, y: kicker ? 0.72 : 0.55, w: HEADW, h: 0.75, fontFace: F.H, fontSize: 30, bold: true, color: C.WHITE });
  return s;
}

/* ---------- content blocks ---------- */

// SAFE GLYPHS ONLY — colour emoji (U+1F300+) do not render in Office/LibreOffice
// reliably. Use these BMP symbols or 1-2 char text badges.
const G = {
  star: "★", dot: "●", tri: "▲", sq: "■", dia: "◆", tick: "✓", cross: "✕",
  bolt: "⚡", rupee: "₹", arrow: "→", swap: "⇄", cycle: "⟳", sec: "§",
  delta: "Δ", sigma: "Σ", omega: "Ω", lambda: "λ", pi: "π", inf: "∞",
  play: "▶", up: "▲", down: "▼", plus: "+", minus: "−", pct: "%", hash: "#",
};

// Grid of cards. items: {icon (1-2 safe chars), title, body, tint, color}
function cards(pres, s, items, o) {
  o = o || {};
  const cols = o.cols || 3, gap = o.gap || 0.28;
  const y0 = o.y || 1.62, ch = o.h || 1.95;
  const cw = (CW - gap * (cols - 1)) / cols;
  const dark = !!o.dark;
  items.forEach((it, i) => {
    const r = Math.floor(i / cols), c = i % cols;
    const x = M + c * (cw + gap), y = y0 + r * (ch + gap);
    s.addShape(pres.ShapeType.roundRect, {
      x, y, w: cw, h: ch, rectRadius: 0.06,
      fill: { color: it.tint || (dark ? C.INK2 : C.CARD) },
      line: { color: dark ? C.INK3 : "E3E6EE", width: 1 },
    });
    let ty = y + 0.2;
    if (it.icon) {
      s.addShape(pres.ShapeType.ellipse, { x: x + 0.24, y: ty, w: 0.44, h: 0.44, fill: { color: it.color || C.SAF } });
      txt(s, it.icon, { x: x + 0.24, y: ty + 0.09, w: 0.44, h: 0.3, fontSize: 12.5, bold: true, color: C.INK, align: "center" });
      ty += 0.58;
    }
    txt(s, it.title, {
      x: x + 0.24, y: ty, w: cw - 0.48, h: 0.36, fontSize: o.tSize || 13.5, bold: true,
      color: dark ? C.WHITE : C.INK,
    });
    if (it.body) txt(s, it.body, {
      x: x + 0.24, y: ty + 0.38, w: cw - 0.48, h: ch - (ty - y) - 0.52,
      fontSize: o.bSize || 10.5, color: dark ? C.MUTED : C.MUTEDL, lineSpacing: 14, valign: "top",
    });
  });
}

// Big stat callouts. stats: {value, label, sub}
function stats(pres, s, list, o) {
  o = o || {};
  const y = o.y || 1.75, gap = 0.28;
  const cw = (CW - gap * (list.length - 1)) / list.length;
  const dark = !!o.dark;
  list.forEach((st, i) => {
    const x = M + i * (cw + gap);
    if (o.box !== false) s.addShape(pres.ShapeType.roundRect, {
      x, y, w: cw, h: o.h || 1.85, rectRadius: 0.06,
      fill: { color: dark ? C.INK2 : C.CARD }, line: { color: dark ? C.INK3 : "E3E6EE", width: 1 },
    });
    txt(s, st.value, {
      x: x + 0.2, y: y + 0.26, w: cw - 0.4, h: 0.8, fontFace: F.H,
      fontSize: o.vSize || 38, bold: true, color: st.color || C.SAF, align: "center",
    });
    txt(s, st.label, {
      x: x + 0.2, y: y + 1.08, w: cw - 0.4, h: 0.55, fontSize: 11,
      color: dark ? C.MUTED : C.MUTEDL, align: "center", lineSpacing: 14,
    });
  });
}

// Numbered horizontal flow. steps: strings or {t, d}
function flow(pres, s, steps, o) {
  o = o || {};
  const y = o.y || 2.4, n = steps.length, gap = 0.3;
  const cw = (CW - gap * (n - 1)) / n, dark = !!o.dark;
  steps.forEach((st, i) => {
    const x = M + i * (cw + gap);
    const t = typeof st === "string" ? st : st.t;
    const d = typeof st === "string" ? null : st.d;
    s.addShape(pres.ShapeType.roundRect, {
      x, y, w: cw, h: o.h || 1.5, rectRadius: 0.06,
      fill: { color: dark ? C.INK2 : C.CARD }, line: { color: dark ? C.INK3 : "E3E6EE", width: 1 },
    });
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.22, y: y + 0.2, w: 0.42, h: 0.42, fill: { color: C.SAF } });
    txt(s, String(i + 1), { x: x + 0.22, y: y + 0.27, w: 0.42, h: 0.3, fontSize: 12, bold: true, color: C.INK, align: "center" });
    txt(s, t, { x: x + 0.22, y: y + 0.74, w: cw - 0.44, h: 0.35, fontSize: 12, bold: true, color: dark ? C.WHITE : C.INK });
    if (d) txt(s, d, { x: x + 0.22, y: y + 1.06, w: cw - 0.44, h: 0.36, fontSize: 9.5, color: dark ? C.MUTED : C.MUTEDL, lineSpacing: 12 });
    if (i < n - 1) txt(s, "›", { x: x + cw + 0.02, y: y + 0.5, w: 0.26, h: 0.5, fontSize: 20, color: C.SAF, align: "center" });
  });
}

// Code block
function code(pres, s, o) {
  const x = o.x || M, y = o.y || 1.7, w = o.w || CW, h = o.h || 3.2;
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.05, fill: { color: C.CODEBG }, line: { color: C.INK3, width: 1 } });
  if (o.label) {
    txt(s, o.label, { x: x + 0.24, y: y + 0.16, w: w - 0.5, h: 0.26, fontSize: 9, bold: true, color: C.SAF, charSpacing: 1.5 });
  }
  txt(s, o.code, {
    x: x + 0.24, y: y + (o.label ? 0.5 : 0.22), w: w - 0.48, h: h - (o.label ? 0.72 : 0.44),
    fontFace: F.M, fontSize: o.size || 10.5, color: C.CODEFG, lineSpacing: o.ls || 15, valign: "top",
  });
}

// Data table. headers: [..], rows: [[..]], colW: [..] (inches)
function table(pres, s, o) {
  const head = o.headers, rows = o.rows;
  const x = o.x || M, y = o.y || 1.7, w = o.w || CW;
  const colW = o.colW || head.map(() => w / head.length);
  s.addTable([
    head.map((h) => ({ text: h, options: { bold: true, color: C.WHITE, fill: { color: C.INK }, fontSize: o.hSize || 11.5 } })),
    ...rows.map((r, ri) => r.map((c) => ({
      text: String(c),
      options: { color: C.INK, fill: { color: ri % 2 ? "ECEFF6" : C.WHITE }, fontSize: o.size || 10.5 },
    }))),
  ], {
    x, y, w, colW, border: { type: "solid", color: "DDE1EC", pt: 1 },
    fontFace: F.B, valign: "middle", rowH: o.rowH || 0.32, margin: 0.06,
  });
}

// Two-column comparison. side = {title, color, items:[..]}
function compare(pres, s, left, right, o) {
  o = o || {};
  const y = o.y || 1.7, h = o.h || 4.1, gap = 0.35;
  const cw = (CW - gap) / 2, dark = !!o.dark;
  [[left, M], [right, M + cw + gap]].forEach(([side, x]) => {
    s.addShape(pres.ShapeType.roundRect, {
      x, y, w: cw, h, rectRadius: 0.06,
      fill: { color: dark ? C.INK2 : C.CARD }, line: { color: side.color || (dark ? C.INK3 : "E3E6EE"), width: side.color ? 2 : 1 },
    });
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.3, y: y + 0.28, w: 0.44, h: 0.44, fill: { color: side.color || C.SAF } });
    txt(s, side.icon || "", { x: x + 0.3, y: y + 0.35, w: 0.44, h: 0.32, fontSize: 13, align: "center" });
    txt(s, side.title, { x: x + 0.9, y: y + 0.3, w: cw - 1.2, h: 0.42, fontSize: 15, bold: true, color: dark ? C.WHITE : C.INK });
    const items = side.items.map((t, i) => ({
      text: t, options: { bullet: true, breakLine: i < side.items.length - 1, paraSpaceAfter: 7 },
    }));
    s.addText(items, {
      x: x + 0.34, y: y + 0.95, w: cw - 0.68, h: h - 1.25, fontFace: F.B,
      fontSize: o.size || 11.5, color: dark ? C.MUTED : C.MUTEDL, lineSpacing: 16, valign: "top",
    });
  });
}

// Bulleted list
function bullets(pres, s, list, o) {
  o = o || {};
  const items = list.map((t, i) => ({
    text: t,
    options: { bullet: true, breakLine: i < list.length - 1, paraSpaceAfter: o.space || 9 },
  }));
  s.addText(items, {
    x: o.x || M, y: o.y || 1.7, w: o.w || CW, h: o.h || 4.2, fontFace: F.B,
    fontSize: o.size || 13, color: o.dark ? C.MUTED : C.MUTEDL, lineSpacing: o.ls || 19, valign: "top",
  });
}

// Takeaway callout — a card, never a stripe
function takeaway(pres, s, text, o) {
  o = o || {};
  const y = o.y || 5.85, h = o.h || 0.85;
  s.addShape(pres.ShapeType.roundRect, {
    x: M, y, w: CW, h, rectRadius: 0.06,
    fill: { color: o.dark ? C.INK2 : "FFF1E6" }, line: { color: C.SAF, width: 1.5 },
  });
  s.addShape(pres.ShapeType.ellipse, { x: M + 0.26, y: y + (h - 0.42) / 2, w: 0.42, h: 0.42, fill: { color: C.SAF } });
  txt(s, o.icon || "★", { x: M + 0.26, y: y + (h - 0.42) / 2 + 0.06, w: 0.42, h: 0.3, fontSize: 12, color: C.INK, align: "center" });
  txt(s, text, {
    x: M + 0.86, y: y + 0.14, w: CW - 1.2, h: h - 0.28, fontSize: o.size || 12.5,
    bold: true, color: o.dark ? C.WHITE : C.INK, lineSpacing: 16, valign: "middle",
  });
}

// Icon+text rows (vertical list with circular icon badges)
function rows(pres, s, list, o) {
  o = o || {};
  const y0 = o.y || 1.7, rh = o.rh || 0.92, dark = !!o.dark;
  const x0 = o.x !== undefined ? o.x : M;
  const bw = (o.w || CW) - 0.9;
  const d = o.badge || 0.56;
  list.forEach((it, i) => {
    const y = y0 + i * rh;
    s.addShape(pres.ShapeType.ellipse, { x: x0 + 0.04, y: y + 0.06, w: d, h: d, fill: { color: it.color || C.SAF } });
    txt(s, it.icon || String(i + 1), { x: x0 + 0.04, y: y + 0.06 + (d - 0.32) / 2, w: d, h: 0.32, fontSize: o.iSize || 14, bold: true, color: C.INK, align: "center" });
    txt(s, it.title, { x: x0 + 0.84, y: y + 0.04, w: bw, h: 0.34, fontSize: o.tSize || 14, bold: true, color: dark ? C.WHITE : C.INK });
    if (it.body) txt(s, it.body, { x: x0 + 0.84, y: y + 0.37, w: bw, h: rh - 0.42, fontSize: o.bSize || 11, color: dark ? C.MUTED : C.MUTEDL, lineSpacing: 14 });
  });
}

// Big analogy / story slide — the "fun" layout.
// `symbol` must be a SAFE glyph (see G) or 1-3 characters of text.
function analogy(pres, o) {
  const s = _newSlide(pres, "dark");
  txt(s, (o.kicker || "ANALOGY").toUpperCase(), { x: M, y: 0.5, w: 8, h: 0.28, fontSize: 10, bold: true, color: C.SAF, charSpacing: 2.5 });
  // Visual anchor: concentric rings with a large typographic symbol
  s.addShape(pres.ShapeType.ellipse, { x: W - 3.65, y: 1.85, w: 2.9, h: 2.9, fill: { color: C.INK2 } });
  s.addShape(pres.ShapeType.ellipse, { x: W - 3.9, y: 1.6, w: 3.4, h: 3.4, line: { color: C.SAF, width: 2 }, fill: { type: "none" } });
  txt(s, o.symbol || "★", {
    x: W - 3.65, y: 2.42, w: 2.9, h: 1.8, fontFace: F.H, fontSize: o.symSize || 72,
    bold: true, color: C.SAF, align: "center",
  });
  txt(s, o.title, { x: M, y: 0.95, w: 8.5, h: 1.05, fontFace: F.H, fontSize: 31, bold: true, color: C.WHITE, lineSpacing: 35 });
  txt(s, o.story, { x: M, y: 2.15, w: 8.4, h: 2.85, fontSize: 14, color: C.SAF2, lineSpacing: 23, valign: "top", italic: true });
  if (o.punch) {
    s.addShape(pres.ShapeType.roundRect, { x: M, y: 5.25, w: CW, h: 1.15, rectRadius: 0.06, fill: { color: C.INK2 }, line: { color: C.SAF, width: 1.5 } });
    txt(s, o.punch, { x: M + 0.3, y: 5.42, w: CW - 0.6, h: 0.82, fontSize: 13.5, bold: true, color: C.WHITE, lineSpacing: 18, valign: "middle" });
  }
  return s;
}

// Closing / quote slide
function quoteSlide(pres, o) {
  const s = _newSlide(pres, "dark");
  txt(s, "“", { x: M, y: 1.3, w: 1.5, h: 1.2, fontFace: F.H, fontSize: 90, color: C.SAF });
  txt(s, o.quote, { x: M + 0.1, y: 2.35, w: 11.4, h: 2.6, fontFace: F.H, fontSize: 28, color: C.WHITE, lineSpacing: 40, valign: "top" });
  if (o.by) txt(s, o.by, { x: M + 0.1, y: 5.2, w: 11, h: 0.4, fontSize: 13, color: C.SAF2 });
  return s;
}

module.exports = {
  C, F, G, W, H, M, CW, LOGO_PATH, LOGO_BIG, LOGO_SMALL,
  AUTHOR, bg, txt, foot, logo, authorBlock, ensureMasters, titleSlide, sectionSlide, slideL, slideD,
  cards, stats, flow, code, table, compare, bullets, takeaway, rows, analogy, quoteSlide,
};
