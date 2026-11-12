/* Privacy-friendly pageview and click tracking via GoatCounter.
 * Cookie-less; no personal data is stored in the browser.
 * Loads only when data-goatcounter on this script tag is a real site
 * endpoint, not the YOUR-CODE placeholder.
 */
(function () {
  "use strict";

  var PLACEHOLDER = "YOUR-CODE";
  var thisScript = document.currentScript;
  var endpoint = (thisScript && thisScript.getAttribute("data-goatcounter")) || "";
  var ready = false;
  var queue = [];

  function isConfigured() {
    return endpoint && endpoint.indexOf("://" + PLACEHOLDER + ".") === -1;
  }

  function send(vars) {
    if (!isConfigured()) return;
    if (window.goatcounter && typeof window.goatcounter.count === "function") {
      window.goatcounter.count(vars);
      return;
    }
    queue.push(vars);
  }

  function flush() {
    ready = true;
    while (queue.length) {
      send(queue.shift());
    }
  }

  function waitForGoatCounter() {
    var started = Date.now();
    var timer = setInterval(function () {
      if (window.goatcounter && typeof window.goatcounter.count === "function") {
        clearInterval(timer);
        flush();
        return;
      }
      if (Date.now() - started > 8000) clearInterval(timer);
    }, 50);
  }

  function loadGoatCounter() {
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://gc.zgo.at/count.js";
    s.setAttribute("data-goatcounter", endpoint);
    s.onload = waitForGoatCounter;
    document.head.appendChild(s);
  }

  function eventNameForLink(link) {
    var href = link.getAttribute("href") || "";
    var url;
    try {
      url = new URL(href, window.location.href);
    } catch (err) {
      return null;
    }
    var host = url.hostname.replace(/^www\./, "");
    var path = url.pathname || "";
    if (host === "buymeacoffee.com" || host.endsWith(".buymeacoffee.com")) {
      return "click-bmac";
    }
    if (host === "etsy.com" || host.endsWith(".etsy.com")) {
      return "click-etsy";
    }
    if (/\.pdf$/i.test(path) || path.indexOf("Commercial-Revit-Naming-Cheat-Sheet") !== -1) {
      return "download-cheat-sheet";
    }
    return null;
  }

  document.addEventListener("click", function (event) {
    var link = event.target.closest("a[href]");
    if (!link) return;
    var name = eventNameForLink(link);
    if (!name) return;
    send({
      path: name,
      title: (link.getAttribute("aria-label") || link.textContent || name).trim().slice(0, 200),
      event: true,
    });
  });

  window.addEventListener("message", function (event) {
    if (!event || typeof event.data !== "string") return;
    if (event.data.indexOf("mlWebformSubmitSuccess") !== 0) return;
    send({
      path: "form-submit-revit-cheat-sheet",
      title: "Revit naming cheat sheet signup",
      event: true,
    });
  });

  if (isConfigured()) {
    loadGoatCounter();
  }
})();
