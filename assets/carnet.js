// Petit Carnet — 唯一的 JS。
// 1. 在每個 [data-speak] 元素後面加「聽」按鈕，用瀏覽器內建的法文語音念出來。
// 2. 首頁的分類篩選。
(function () {
  "use strict";

  // ---------- 1. 發音 ----------
  var canSpeak = "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;

  if (canSpeak) {
    var frVoice = null;
    var pickVoice = function () {
      var voices = window.speechSynthesis.getVoices();
      frVoice =
        voices.find(function (v) { return v.lang === "fr-FR"; }) ||
        voices.find(function (v) { return /^fr/i.test(v.lang || ""); }) ||
        null;
    };
    pickVoice();
    window.speechSynthesis.onvoiceschanged = pickVoice;

    document.querySelectorAll("[data-speak]").forEach(function (el) {
      var text = el.textContent.trim();
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "speak";
      btn.textContent = "聽";
      btn.setAttribute("aria-label", "播放法文發音：" + text);
      btn.setAttribute("aria-pressed", "false");

      btn.addEventListener("click", function () {
        window.speechSynthesis.cancel();
        var u = new SpeechSynthesisUtterance(text);
        u.lang = "fr-FR";
        u.rate = 0.85;
        if (frVoice) u.voice = frVoice;
        u.onstart = function () { btn.setAttribute("aria-pressed", "true"); };
        u.onend = u.onerror = function () { btn.setAttribute("aria-pressed", "false"); };
        window.speechSynthesis.speak(u);
      });

      el.appendChild(document.createTextNode(" "));
      el.appendChild(btn);
    });
  }

  // ---------- 2. 首頁分類篩選 ----------
  var filters = document.querySelectorAll("[data-filter]");
  var cards = document.querySelectorAll(".cards .card");
  var empty = document.querySelector(".empty");

  filters.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var f = btn.getAttribute("data-filter");
      var shown = 0;
      filters.forEach(function (b) { b.setAttribute("aria-pressed", String(b === btn)); });
      cards.forEach(function (card) {
        var hide = f !== "all" && card.getAttribute("data-category") !== f;
        card.parentElement.hidden = hide;
        if (!hide) shown += 1;
      });
      if (empty) empty.hidden = shown > 0;
    });
  });
})();
