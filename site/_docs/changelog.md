---
title: Changelog
description: Unreleased changes from CHANGELOG.md and every published addit-harness release.
nav_order: 12
nav_group: Project
---

The source of truth is
[`CHANGELOG.md`](https://github.com/{{ site.repository }}/blob/main/CHANGELOG.md)
at the repo root. Each release publishes its section as the
[GitHub Release](https://github.com/{{ site.repository }}/releases) notes, and
this page renders the unreleased section followed by those releases, both
pulled in at deploy time (see `.github/workflows/deploy-docs.yml`).

{% if site.data.changelog and site.data.changelog.unreleased != "" %}
<section class="changelog-unreleased">
<h2 id="unreleased">Unreleased</h2>
{{ site.data.changelog.unreleased | markdownify }}
</section>
{% endif %}

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
This page renders the release list at deploy time, so a local build shows no
entries yet. See the full history directly on
[GitHub Releases](https://github.com/{{ site.repository }}/releases) in the
meantime.
{% endif %}

## Next

- [Roadmap](../roadmap/) — what's planned next.
- [Extending](../extending/#releasing-the-claude-code-plugin) — how a release
  is cut.
