---
title: Changelog
nav_order: 11
nav_group: Project
---

Release notes come straight from
[GitHub Releases](https://github.com/{{ site.repository }}/releases) — that's
already a native, always-correct changelog, so this page renders it via
Liquid instead of duplicating it into a second, driftable file.

{% if site.data.releases and site.data.releases.size > 0 %}
<ul class="changelog-list">
  {% for release in site.data.releases %}
  <li>
    <h2>
      <a href="{{ release.html_url }}">{{ release.tag_name }}</a>
      {% if release.name and release.name != release.tag_name %} — {{ release.name }}{% endif %}
    </h2>
    <p class="docs-nav-heading">{{ release.published_at | date: "%Y-%m-%d" }}</p>
    {{ release.body | markdownify }}
  </li>
  {% endfor %}
</ul>
{% else %}
This page renders the release list at deploy time (see
`.github/workflows/deploy-docs.yml`), so a local or unreleased build shows no
entries yet. See the full history directly on
[GitHub Releases](https://github.com/{{ site.repository }}/releases) in the
meantime.
{% endif %}

## Next

- [Roadmap](../roadmap/) — what's planned next.
- [Extending](../extending/#releasing-the-claude-code-plugin) — how a release
  is cut.
