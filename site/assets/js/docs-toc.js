// "On this page" sub-list under the current page's entry in the docs sidebar.
// Progressive enhancement: without JS the sidebar is the plain page tree.
// Reads the ids kramdown already puts on h2/h3 (no ids are invented here) and
// highlights the section in view with an IntersectionObserver.
(function () {
  "use strict";

  var current = document.querySelector('.docs-nav-group a[aria-current="page"]');
  var article = document.querySelector(".docs-article");
  if (!current || !article) return;

  var headings = Array.prototype.slice.call(
    article.querySelectorAll("h2[id], h3[id]")
  );
  var h2Count = headings.filter(function (h) { return h.tagName === "H2"; }).length;
  if (h2Count < 2) return;

  var nav = document.createElement("nav");
  nav.className = "docs-nav-sub";
  nav.setAttribute("aria-label", "On this page");
  var title = document.createElement("p");
  title.setAttribute("aria-hidden", "true");
  title.textContent = "On this page";
  var list = document.createElement("ul");

  var links = {};
  headings.forEach(function (heading) {
    var item = document.createElement("li");
    item.dataset.depth = heading.tagName.charAt(1);
    var link = document.createElement("a");
    link.href = "#" + heading.id;
    link.textContent = heading.textContent;
    item.appendChild(link);
    list.appendChild(item);
    links[heading.id] = link;
  });
  nav.appendChild(title);
  nav.appendChild(list);
  current.parentNode.appendChild(nav);

  if (!("IntersectionObserver" in window)) return;

  var active = null;
  function setActive(id) {
    if (active === links[id]) return;
    if (active) active.classList.remove("is-active");
    active = links[id];
    active.classList.add("is-active");
    // `nearest` keeps the page still; it only scrolls the sidebar box.
    if (active.scrollIntoView) active.scrollIntoView({ block: "nearest" });
  }

  // A heading counts as "in view" while it sits in the top band of the
  // viewport; the last heading to enter that band is the current section.
  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) setActive(entry.target.id);
      });
    },
    { rootMargin: "-80px 0px -70% 0px" }
  );
  headings.forEach(function (heading) { observer.observe(heading); });
})();
