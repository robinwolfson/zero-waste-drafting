/* Shop search, topic chips, and sort. Products are in the HTML, so they stay
   visible when JavaScript does not run. This script only hides or reorders. */
(function () {
  "use strict";

  var search = document.getElementById("shop-search");
  var sort = document.getElementById("shop-sort");
  var chips = Array.prototype.slice.call(document.querySelectorAll(".chip"));
  var status = document.getElementById("shop-status");
  var empty = document.getElementById("shop-empty");
  var bucket = document.getElementById("shop-sorted");
  var sections = Array.prototype.slice.call(document.querySelectorAll("[data-shop-section]"));
  var cards = Array.prototype.slice.call(document.querySelectorAll("[data-topics]"));
  if (!search || !sort || !bucket || !cards.length) return;

  var records = cards.map(function (card) {
    var unit = card.closest(".card-with-note") || card;
    var marker = document.createComment("shop-slot");
    unit.parentNode.insertBefore(marker, unit);
    var bits = [];
    var heading = card.querySelector("h3");
    if (heading) bits.push(heading.textContent);
    Array.prototype.forEach.call(card.querySelectorAll("p, li"), function (el) {
      if (el.classList.contains("price") || el.classList.contains("free-flag")) return;
      bits.push(el.textContent);
    });
    var raw = card.getAttribute("data-price");
    var price = raw === null || raw === "" ? null : Number(raw);
    if (price !== null && isNaN(price)) price = null;
    return {
      card: card,
      unit: unit,
      marker: marker,
      topics: (card.getAttribute("data-topics") || "").split(/\s+/),
      price: price,
      text: bits.join(" ").toLowerCase().replace(/\s+/g, " ").trim()
    };
  });

  function setTopic(topic) {
    chips.forEach(function (chip) {
      var on = chip.getAttribute("data-topic") === topic;
      chip.setAttribute("aria-checked", on ? "true" : "false");
      chip.tabIndex = on ? 0 : -1;
    });
  }

  function currentTopic() {
    var on = document.querySelector(".chip[aria-checked='true']");
    return on ? on.getAttribute("data-topic") : "all";
  }

  function writeUrl(topic, query, mode) {
    var params = new URLSearchParams();
    if (topic && topic !== "all") params.set("topic", topic);
    if (query) params.set("q", query);
    if (mode && mode !== "featured") params.set("sort", mode);
    var qs = params.toString();
    var next = location.pathname + (qs ? "?" + qs : "") + location.hash;
    var now = location.pathname + location.search + location.hash;
    if (next !== now) history.replaceState(null, "", next);
  }

  function apply() {
    var topic = currentTopic();
    var query = search.value.trim().toLowerCase();
    var mode = sort.value;
    var shown = [];

    records.forEach(function (rec) {
      var topicOk = topic === "all" || rec.topics.indexOf(topic) !== -1;
      var textOk = !query || rec.text.indexOf(query) !== -1;
      var match = topicOk && textOk;
      rec.unit.hidden = !match;
      if (rec.unit !== rec.card) rec.card.hidden = !match;
      if (match) shown.push(rec);
    });

    var filtering = topic !== "all" || query !== "";
    var sorting = mode === "price-asc" || mode === "price-desc";
    ["products-title", "products-intro"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.hidden = filtering || sorting;
    });
    var catNav = document.querySelector("#products .section-nav");
    if (catNav) catNav.hidden = filtering || sorting;
    if (sorting) {
      shown.sort(function (a, b) {
        if (a.price === null && b.price === null) return 0;
        if (a.price === null) return 1;
        if (b.price === null) return -1;
        return mode === "price-asc" ? a.price - b.price : b.price - a.price;
      });
      bucket.hidden = false;
      shown.forEach(function (rec) { bucket.appendChild(rec.unit); });
      sections.forEach(function (section) { section.hidden = true; });
    } else {
      records.forEach(function (rec) {
        rec.marker.parentNode.insertBefore(rec.unit, rec.marker.nextSibling);
      });
      bucket.hidden = true;
      sections.forEach(function (section) {
        if (!section.querySelector("[data-topics]")) {
          section.hidden = filtering;
          return;
        }
        section.hidden = !section.querySelector("[data-topics]:not([hidden])");
      });
    }

    if (empty) empty.hidden = shown.length !== 0;
    if (status) {
      status.textContent = shown.length
        ? "Showing " + shown.length + (shown.length === 1 ? " product." : " products.")
        : "No products match.";
    }
    writeUrl(topic, query, mode);
  }

  search.addEventListener("input", apply);
  sort.addEventListener("change", apply);
  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      setTopic(chip.getAttribute("data-topic"));
      apply();
    });
  });

  var group = document.querySelector(".chips");
  if (group) {
    group.addEventListener("keydown", function (event) {
      var step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[event.key];
      if (!step) return;
      var index = chips.indexOf(document.activeElement);
      if (index < 0) return;
      event.preventDefault();
      var next = chips[(index + step + chips.length) % chips.length];
      next.focus();
      setTopic(next.getAttribute("data-topic"));
      apply();
    });
  }

  Array.prototype.forEach.call(document.querySelectorAll(".section-nav a"), function (link) {
    link.addEventListener("click", function () {
      search.value = "";
      sort.value = "featured";
      setTopic("all");
      apply();
    });
  });

  var params = new URLSearchParams(location.search);
  var initial = params.get("topic") || "all";
  var known = chips.some(function (chip) { return chip.getAttribute("data-topic") === initial; });
  setTopic(known ? initial : "all");
  if (params.get("q")) search.value = params.get("q");
  var initialSort = params.get("sort");
  if (initialSort && sort.querySelector('option[value="' + initialSort.replace(/"/g, "") + '"]')) {
    sort.value = initialSort;
  }
  apply();
})();
