/* 校務研究研習・互動實作 —— 共用程式
   1. SESSIONS：全站目錄（首頁、頁首、上一個／下一個都從這裡來）
   2. 頁首工具：QR Code（給聽眾掃）、投影模式（放大字級）、全螢幕、鍵盤快速鍵
   3. 小工具：讀 JSON、畫表格、提示框、格式化 */
(function () {
  "use strict";

  const SESSIONS = [
    {
      id: "s1", no: "課程", name: "數據驅動的學校進化", deck: "數據驅動的學校進化_研習簡報",
      lead: "觀念建立、Excel Power Query 資料整理、視覺化與判讀。",
      labs: [
        { id: "s1/powerquery", kind: "示範", title: "Power Query 兩個關鍵動作：逆透視與合併", slides: "第 23–30 張",
          desc: "一步一步看寬表變長表、兩張表怎麼用代號接起來。" },
        { id: "s1/courses", kind: "實作", title: "Q1 熱門，不等於有效", slides: "第 36 張",
          desc: "選課人數、滿意度、缺席率三個指標一起看，結論可能相反。" },
        { id: "s1/drilldown", kind: "實作", title: "Q2 85% 的陷阱：樞紐下鑽", slides: "第 37 張",
          desc: "整體上傳率看起來不錯，拆開之後才看到需要幫忙的那群人。" },
        { id: "s1/math", kind: "實作", title: "Q3 數學偏低，是老師的問題嗎", slides: "第 38 張",
          desc: "把入學分組拉進來，看班級差異的真正來源。" },
        { id: "s1/programs", kind: "示範", title: "計畫 × 指標：錢花到哪裡去了", slides: "第 70–72 張",
          desc: "六個計畫接上指標與參與名單，看投入與改變。" },
        { id: "s1/dashboard-example", kind: "示範", title: "範例：AI 自製校務研究儀表板", slides: "第 62–65 張",
          desc: "用 AI 產生的單一網頁儀表板，可下載後自己改。", external: true },
      ],
    },
    {
      id: "s2", no: "課程", name: "校務資料統整平台", deck: "校務資料統整平台_研習簡報",
      lead: "五個系統的匯出檔，清洗、對照、檢核成一張整合表，再讓它自己更新。",
      labs: [
        { id: "s2/gallery", kind: "操作", title: "髒資料圖鑑：每個檔案都有它的問題", slides: "第 31 張",
          desc: "逐一打開五個練習檔，滑過標色的格子看問題在哪。" },
        { id: "s2/cleaning", kind: "實作", title: "段考成績：清洗步驟播放器", slides: "第 38–41 張",
          desc: "照 Power Query 的步驟一步一步套用，看每一步改變了什麼。" },
        { id: "s2/tools", kind: "操作", title: "清洗小工具：民國日期、學期、學號", slides: "第 27、36、52 張",
          desc: "貼上自己的資料試試看，同時對照 M 公式。" },
        { id: "s2/join", kind: "實驗", title: "合併與檢核：誰對不起來", slides: "第 24、44–48 張",
          desc: "左方外部合併 vs. 左方反向合併，找出休學生、轉入生與錯誤帳號。" },
        { id: "s2/auto", kind: "示範", title: "自動化：12 月的檔案來了", slides: "第 58 張",
          desc: "把新檔丟進資料夾、按重新整理，整合表自動更新。" },
      ],
    },
    {
      id: "s0", no: "開場模組", name: "高中校務 50 問", deck: "開場模組_高中校務50問",
      lead: "學校每天都在面對的 50 個問題：該看什麼數據、怎麼看、怎麼找到根因。",
      labs: [
        { id: "s0/questions", kind: "操作", title: "50 問瀏覽器", slides: "開場模組 第 4–16 張",
          desc: "依面向、方法、層級篩選，點開看每一題的數據與分析步驟。" },
        { id: "s0/strata", kind: "實驗", title: "案例一：真的是「這屆比較差」嗎", slides: "開場模組 第 17 張",
          desc: "拉動生源組成與各等級表現，看整體不及格率怎麼被拆解。" },
        { id: "s0/alert", kind: "實驗", title: "案例二：預警規則先回測再上線", slides: "開場模組 第 18 張",
          desc: "調整缺曠閾值，看命中率、涵蓋率與導師名單長度的取捨。" },
        { id: "s0/card", kind: "實作", title: "問題卡與五個為什麼", slides: "開場模組 第 19、21 張",
          desc: "選一題或寫下學校真實問題，用五步拆解，可列印或下載。" },
      ],
    },
    {
      id: "s3", no: "課程", name: "數據治理與高中校務研究", deck: "數據治理與高中校務研究",
      lead: "從數據整理、預警到決策的循環；所有小操作都只用模擬資料。",
      labs: [
        { id: "s3/experiment", kind: "實驗", title: "開場實驗：把髒資料直接丟給 AI", slides: "第 3 張",
          desc: "同一個問題，髒資料和乾淨資料給出不同的名單。" },
        { id: "s3/dictionary", kind: "實作", title: "小操作一：起草資料字典", slides: "第 10 張",
          desc: "上傳或使用範例檔，自動推測欄位型別與值域，再交給 AI 與人確認。" },
        { id: "s3/quality", kind: "實作", title: "小操作二：人腦 vs. AI 找錯比賽", slides: "第 11 張",
          desc: "5 分鐘內點出資料的問題，再依六個面向對答案。" },
        { id: "s3/privacy", kind: "實作", title: "小操作三：紅綠燈與去識別化", slides: "第 12 張",
          desc: "情境卡判斷紅黃綠燈，再把假名化、概化、遮罩套到資料上。" },
        { id: "s3/regression", kind: "實驗", title: "小操作四：補救教學真的有效嗎", slides: "第 15 張",
          desc: "沒有任何介入，後 25% 的學生下次也會「進步」——均值回歸模擬。" },
        { id: "s3/workflow", kind: "實作", title: "小操作五：設計一條工作流", slides: "第 20 張",
          desc: "排出每月預警工作流，標出治理檢查點，匯出成文字。" },
      ],
    },
  ];
  const ALL = SESSIONS.flatMap((s) => s.labs.map((l) => ({ ...l, session: s })));

  /* ---------------- 小工具 ---------------- */
  const W = {
    SESSIONS, ALL,
    root: "",
    color: { navy: "#1F2A44", orange: "#D85A30", purple: "#534AB7", green: "#0F6E56", gold: "#C9A227",
      gray: "#8A94A6", line: "#D3D6DC", ink: "#1F2329", muted: "#5F5E5A", orangeL: "#F2B8A2", purpleL: "#B9B4E6", greenL: "#9CCBBE" },
    _cache: {},
    async json(name) {
      if (!W._cache[name]) {
        W._cache[name] = fetch(W.root + "data/" + name).then((r) => {
          if (!r.ok) throw new Error("無法讀取 " + name + "（請先執行 scripts/build_site_data.py）");
          return r.json();
        });
      }
      return W._cache[name];
    },
    $(sel, ctx) { return (ctx || document).querySelector(sel); },
    $$(sel, ctx) { return Array.from((ctx || document).querySelectorAll(sel)); },
    el(tag, attrs, ...kids) {
      const e = document.createElement(tag);
      for (const [k, v] of Object.entries(attrs || {})) {
        if (k.startsWith("aria-") && typeof v === "boolean") { e.setAttribute(k, String(v)); continue; }
        if (v == null || v === false) continue;
        if (k === "class") e.className = v;
        else if (k === "html") e.innerHTML = v;
        else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
        else e.setAttribute(k, v === true ? "" : v);
      }
      for (const k of kids.flat()) if (k != null && k !== false) e.append(k.nodeType ? k : document.createTextNode(String(k)));
      return e;
    },
    esc(s) { return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); },
    mean(a) { const v = a.filter((x) => typeof x === "number" && !isNaN(x)); return v.length ? v.reduce((s, x) => s + x, 0) / v.length : NaN; },
    sum(a) { return a.reduce((s, x) => s + (Number(x) || 0), 0); },
    pct(x, d = 1) { return isNaN(x) ? "—" : (x * 100).toFixed(d) + "%"; },
    fix(x, d = 1) { return isNaN(x) ? "—" : Number(x).toFixed(d); },
    bytes(n) { return n > 1048576 ? (n / 1048576).toFixed(1) + " MB" : Math.max(1, Math.round(n / 1024)) + " KB"; },
    show(v) { return v == null ? "" : String(v); },
    toast(msg) {
      let t = W.$(".toast");
      if (!t) { t = W.el("div", { class: "toast" }); document.body.append(t); }
      t.textContent = msg; t.classList.add("show");
      clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove("show"), 1800);
    },
    copy(text, msg) {
      navigator.clipboard.writeText(text).then(() => W.toast(msg || "已複製"), () => W.toast("無法複製，請手動選取"));
    },
    download(name, text, type) {
      const blob = new Blob(["﻿" + text], { type: (type || "text/plain") + ";charset=utf-8" });
      const a = W.el("a", { href: URL.createObjectURL(blob), download: name });
      document.body.append(a); a.click(); a.remove();
    },
    /* 表格：cols 為欄名陣列；rows 為陣列的陣列。
       opt.marks: [{r, c, k, n}]（r 為 rows 的索引，c=-1 表整列）；opt.rowNum: 顯示列號（起始值）
       opt.rowClass(i,row)、opt.cellClass(i,c,v)、opt.max: 最多顯示列數、opt.headMarks */
    table(container, cols, rows, opt = {}) {
      const marks = {};
      for (const m of opt.marks || []) (marks[m.r] = marks[m.r] || []).push(m);
      const max = opt.max || rows.length;
      let h = "<table class='data'><thead><tr>";
      if (opt.rowNum != null) h += "<th class='num'>#</th>";
      const numCol = cols.map((_, j) => { const v = rows.find((r) => r[j] != null && r[j] !== ""); return v ? typeof v[j] === "number" : false; });
      cols.forEach((c, j) => {
        const hm = (opt.headMarks || []).filter((m) => m.c === j);
        const cls = hm.length ? ` class='m m-${hm[0].k}${numCol[j] ? " num" : ""}' data-tip='${W.esc(hm.map((m) => m.n).join("；"))}'` : numCol[j] ? " class='num'" : "";
        h += `<th${cls}>${W.esc(c)}</th>`;
      });
      h += "</tr></thead><tbody>";
      rows.slice(0, max).forEach((row, i) => {
        const ms = marks[i] || [];
        const rowM = ms.filter((m) => m.c === -1);
        let rc = opt.rowClass ? opt.rowClass(i, row) || "" : "";
        if (rowM.length) rc += ` m m-${rowM[0].k}`;
        const rtip = rowM.length ? ` data-tip='${W.esc(rowM.map((m) => m.n).join("；"))}'` : "";
        h += `<tr class='${rc}'${rtip}>`;
        if (opt.rowNum != null) h += `<td class='rn'>${i + opt.rowNum}</td>`;
        for (let j = 0; j < cols.length; j++) {
          const v = row[j];
          const cm = ms.filter((m) => m.c === j);
          let cc = typeof v === "number" ? "num" : "";
          if (typeof v === "string" && v !== v.trim()) cc += " sp";
          if (opt.cellClass) cc += " " + (opt.cellClass(i, j, v, row) || "");
          let tip = "";
          if (cm.length) { cc += ` m m-${cm[0].k}`; tip = ` data-tip='${W.esc(cm.map((m) => m.n).join("；"))}'`; }
          let shown = W.esc(W.show(v));
          if (typeof v === "string" && v !== v.trim()) shown = shown.replace(/^ +| +$/g, (s) => "␣".repeat(s.length));
          h += `<td class='${cc.trim()}'${tip}>${shown}</td>`;
        }
        h += "</tr>";
      });
      h += "</tbody></table>";
      if (rows.length > max) h += `<div class='small faint' style='padding:6px 10px'>僅顯示前 ${max} 列，共 ${rows.length} 列</div>`;
      container.innerHTML = h;
    },
    chartDefaults() {
      if (!window.Chart) return;
      Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
      Chart.defaults.font.size = Math.round(12 * (document.documentElement.classList.contains("present") ? 1.2 : 1));
      Chart.defaults.color = "#5F5E5A";
      Chart.defaults.borderColor = "#E6E8EC";
      Chart.defaults.plugins.legend.labels.boxWidth = 12;
      Chart.defaults.maintainAspectRatio = false;
      Chart.defaults.animation.duration = 350;
    },
  };
  window.W = W;

  /* ---------------- 頁首、頁尾、工具列 ---------------- */
  function loadScript(src) {
    return new Promise((ok, no) => { const s = document.createElement("script"); s.src = src; s.onload = ok; s.onerror = no; document.head.append(s); });
  }
  let qrDone = false;
  async function openQR() {
    const ov = W.$("#qrOverlay");
    ov.classList.add("open");
    if (!qrDone) {
      try {
        await loadScript("https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js");
        new QRCode(W.$("#qr"), { text: location.href.split("#")[0], width: 512, height: 512, correctLevel: QRCode.CorrectLevel.M });
        qrDone = true;
      } catch (e) { W.$("#qr").textContent = "QR Code 載入失敗，請直接輸入網址。"; }
    }
  }
  function setPresent(on) {
    document.documentElement.classList.toggle("present", on);
    try { localStorage.setItem("ir-present", on ? "1" : "0"); } catch (e) { /* 無痕模式 */ }
    const b = W.$("#btnPresent"); if (b) b.setAttribute("aria-pressed", on ? "true" : "false");
    window.dispatchEvent(new Event("present-change"));
  }
  try { if (localStorage.getItem("ir-present") === "1") document.documentElement.classList.add("present"); } catch (e) { /* ignore */ }

  document.addEventListener("DOMContentLoaded", () => {
    const b = document.body;
    W.root = b.dataset.root || "";
    const labId = b.dataset.lab;
    const lab = ALL.find((l) => l.id === labId);
    const sess = lab ? lab.session : null;
    const main = W.$("main");

    // 頂列
    const top = W.el("header", { class: "topbar" },
      W.el("div", { class: "wrap" },
        W.el("a", { class: "brand", href: W.root + "index.html" }, "校務研究研習", W.el("span", {}, "・互動實作")),
        W.el("div", { class: "crumb" }, sess ? sess.name : (b.dataset.crumb || "")),
        W.el("div", { class: "tools" },
          W.el("a", { class: "tbtn", href: W.root + "downloads.html" + (sess ? "#" + sess.id : ""), title: "下載練習資料" }, "下載資料"),
          W.el("button", { class: "tbtn", id: "btnQR", title: "顯示本頁 QR Code（快速鍵 Q）", onclick: openQR }, "QR"),
          W.el("button", { class: "tbtn", id: "btnPresent", "aria-pressed": document.documentElement.classList.contains("present") ? "true" : "false",
            title: "投影模式：放大字級（快速鍵 P）", onclick: () => setPresent(!document.documentElement.classList.contains("present")) }, "投影模式"),
          W.el("button", { class: "tbtn", title: "全螢幕（快速鍵 F）", onclick: toggleFS }, "全螢幕"))));
    b.prepend(top);

    // 實作標題區
    if (lab) {
      const head = W.el("section", { class: "labhead" },
        W.el("div", { class: "wrap" },
          W.el("div", { class: "meta" },
            W.el("span", { class: "chip k-" + lab.kind }, lab.kind),
            W.el("span", { class: "chip slide", title: "對應簡報頁" }, "簡報：" + lab.slides),
            b.dataset.time ? W.el("span", { class: "chip gold" }, b.dataset.time) : null),
          W.el("h1", {}, lab.title),
          W.el("p", { class: "lead" }, b.dataset.lead || lab.desc)));
      top.after(head);
      // 上一個／下一個
      const list = sess.labs.filter((l) => !l.external);
      const i = list.findIndex((l) => l.id === lab.id);
      const prev = list[i - 1], next = list[i + 1];
      const nav = W.el("nav", { class: "labnav wrap" },
        prev ? W.el("a", { href: W.root + prev.id + ".html" }, W.el("small", {}, "← 上一個"), prev.title) : W.el("span"),
        next ? W.el("a", { href: W.root + next.id + ".html", style: "text-align:right" }, W.el("small", {}, "下一個 →"), next.title)
          : W.el("a", { href: W.root + "index.html#" + sess.id, style: "text-align:right" }, W.el("small", {}, "回到"), "「" + sess.name + "」全部實作"));
      main.after(nav);
      document.title = lab.title + "｜校務研究研習互動實作";
      W.prevHref = prev && W.root + prev.id + ".html";
      W.nextHref = next && W.root + next.id + ".html";
    }

    const foot = W.el("footer", { class: "site" }, W.el("div", { class: "wrap" },
      "所有資料皆為研習用模擬資料，不含任何真實學生個資。　快速鍵：",
      W.el("span", { class: "kbd" }, "Q"), " QR Code　", W.el("span", { class: "kbd" }, "P"), " 投影模式　",
      W.el("span", { class: "kbd" }, "F"), " 全螢幕　", W.el("span", { class: "kbd" }, "← →"), " 上／下一個實作"));
    (W.$(".labnav") || main).after(foot);

    // QR 浮層
    const ov = W.el("div", { class: "overlay", id: "qrOverlay", onclick: (e) => { if (e.target === ov) ov.classList.remove("open"); } },
      W.el("div", { class: "modal qrbox" },
        W.el("button", { class: "close", "aria-label": "關閉", onclick: () => ov.classList.remove("open") }, "×"),
        W.el("h2", { style: "margin-top:0" }, "掃描開啟本頁"),
        W.el("div", { id: "qr" }),
        W.el("p", { class: "url" }, decodeURI(location.href.split("#")[0]))));
    b.append(ov);

    // 提示框（data-tip）
    const tip = W.el("div", { class: "tip" });
    b.append(tip);
    document.addEventListener("mouseover", (e) => {
      const t = e.target.closest("[data-tip]");
      if (!t) { tip.style.display = "none"; return; }
      tip.textContent = t.dataset.tip; tip.style.display = "block";
    });
    document.addEventListener("mousemove", (e) => {
      if (tip.style.display === "block") {
        const x = Math.min(e.clientX + 14, innerWidth - 320);
        tip.style.left = x + "px"; tip.style.top = (e.clientY + 16) + "px";
      }
    });
    document.addEventListener("click", (e) => {      // 觸控裝置：點一下顯示
      const t = e.target.closest("[data-tip]");
      if (t && matchMedia("(hover: none)").matches) W.toast(t.dataset.tip);
    });

    // 快速鍵
    document.addEventListener("keydown", (e) => {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      if (/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) || document.activeElement.isContentEditable) return;
      const k = e.key.toLowerCase();
      if (k === "q") { const o = W.$("#qrOverlay"); o.classList.contains("open") ? o.classList.remove("open") : openQR(); }
      else if (k === "p") setPresent(!document.documentElement.classList.contains("present"));
      else if (k === "f") toggleFS();
      else if (k === "escape") W.$("#qrOverlay").classList.remove("open");
      else if (k === "arrowleft" && W.prevHref) location.href = W.prevHref;
      else if (k === "arrowright" && W.nextHref) location.href = W.nextHref;
    });
    W.chartDefaults();
  });

  function toggleFS() {
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen && document.documentElement.requestFullscreen();
  }
})();
