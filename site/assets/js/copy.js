// Copy-to-clipboard for command blocks — the one JS utility on this site.
// Progressive enhancement only: every command is already real, selectable
// text without this script; this just adds a faster path.
(function () {
  "use strict";

  function fallbackCopy(text) {
    var textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "absolute";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand("copy");
    } catch (err) {
      // no-op — button simply won't confirm; text remains selectable by hand
    }
    document.body.removeChild(textarea);
  }

  function copy(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    fallbackCopy(text);
    return Promise.resolve();
  }

  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-copy]");
    if (!button) return;

    var text = button.getAttribute("data-copy");
    copy(text).then(function () {
      var original = button.dataset.copyLabel || button.textContent;
      button.dataset.copyLabel = original;
      button.textContent = "Copied";
      button.classList.add("is-copied");
      window.clearTimeout(button._copyResetTimer);
      button._copyResetTimer = window.setTimeout(function () {
        button.textContent = original;
        button.classList.remove("is-copied");
      }, 1600);
    });
  });
})();
