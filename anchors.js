/* Send old single-page hashes to the page that now holds that section.
   If the target id is already on this page, the browser scrolls as usual. */
(function () {
  "use strict";

  var shop = "shop.html";
  var free = "free.html";
  var learn = "learn.html";
  var home = "index.html";
  var map = {
    articles: learn + "#articles",
    videos: learn + "#videos",
    "florida-lighting-article": learn + "#florida-lighting-article",
    "free-quiz": free + "#free-quiz",
    "free-revit-sheet": free + "#free-revit-sheet",
    about: home + "#about",
    faq: home + "#faq",
    top: home + "#top",
    "start-free": home + "#start-free",
    newsletter: home + "#free-revit-sheet"
  };

  [
    "products", "extras", "lighting-controls", "bundles", "lean-six-sigma", "cad", "revit",
    "commercial-permitting", "preview", "autocad-starter-kit", "autocad-standards-pack",
    "ai-prompt-pack", "freelance-revit-playbook", "classroom-license", "studio-team-license",
    "office-team-license", "team-license-quote", "commercial-autocad-bundle",
    "freelance-revit-bundle", "permit-qaqc", "drafting-scenes-calendar", "revit-naming-poster",
    "cad-drafting-poster", "lighting-permit-kit", "florida-nlight-kit", "free-quiz-card"
  ].forEach(function (id) {
    map[id] = shop + "#" + id;
  });

  function go() {
    var id = (location.hash || "").replace(/^#/, "");
    if (!id || !Object.prototype.hasOwnProperty.call(map, id)) return;
    if (document.getElementById(id)) return;
    var dest = map[id];
    var file = dest.split("#")[0];
    if (location.pathname.slice(-file.length) === file) return;
    location.replace(dest);
  }

  go();
  window.addEventListener("hashchange", go);
})();
