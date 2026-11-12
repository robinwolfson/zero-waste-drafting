/* Vanilla lightbox for product card covers. No external libraries. */
(function () {
  "use strict";

  var lightbox = document.getElementById("product-lightbox");
  if (!lightbox) return;

  var image = lightbox.querySelector(".lightbox-image");
  var caption = document.getElementById("lightbox-caption");
  var closeBtn = lightbox.querySelector(".lightbox-close");
  var lastFocus = null;

  function cardTitle(trigger) {
    if (trigger.getAttribute("data-caption")) {
      return trigger.getAttribute("data-caption");
    }
    var card = trigger.closest("article.card");
    var heading = card && card.querySelector("h3");
    return heading ? heading.textContent.trim() : "";
  }

  function triggerImage(trigger) {
    return trigger.matches("img") ? trigger : trigger.querySelector("img");
  }

  function fullSrc(trigger) {
    var listed = trigger.getAttribute("data-full-src");
    if (listed) return listed;
    var img = triggerImage(trigger);
    return img ? img.getAttribute("src") : "";
  }

  function imageAlt(trigger) {
    var img = triggerImage(trigger);
    return (img && img.getAttribute("alt")) || cardTitle(trigger);
  }

  function focusables() {
    return lightbox.querySelectorAll("button, [href], input, select, textarea, [tabindex]:not([tabindex='-1'])");
  }

  function open(trigger) {
    var src = fullSrc(trigger);
    if (!src) return;
    lastFocus = trigger;
    var title = cardTitle(trigger);
    image.src = src;
    image.alt = imageAlt(trigger);
    caption.textContent = title;
    lightbox.hidden = false;
    document.body.classList.add("lightbox-open");
    closeBtn.focus();
  }

  function close() {
    if (lightbox.hidden) return;
    lightbox.hidden = true;
    document.body.classList.remove("lightbox-open");
    image.removeAttribute("src");
    image.alt = "";
    caption.textContent = "";
    if (lastFocus && typeof lastFocus.focus === "function") {
      lastFocus.focus();
    }
    lastFocus = null;
  }

  document.addEventListener("click", function (event) {
    var trigger = event.target.closest(".card-image");
    if (trigger && !lightbox.contains(trigger)) {
      event.preventDefault();
      open(trigger);
      return;
    }
    if (event.target.closest("[data-lightbox-close]")) {
      event.preventDefault();
      close();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (lightbox.hidden) {
      return;
    }
    if (event.key === "Escape") {
      event.preventDefault();
      close();
      return;
    }
    if (event.key !== "Tab") return;
    var items = Array.prototype.slice.call(focusables());
    if (!items.length) return;
    var first = items[0];
    var last = items[items.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });
})();
