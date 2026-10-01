---
title: Documentation
description: Every page in the addit-harness docs, grouped by what you need.
permalink: /docs/
nav_exclude: true
---
{% assign groups = "Start,Reference,Guides,Project" | split: "," %}
{% assign docs = site.docs | where_exp: "p", "p.nav_exclude != true" | sort: "nav_order" %}
{% for group in groups %}
{% assign group_docs = docs | where: "nav_group", group %}
{% if group_docs.size > 0 %}
<h2 id="{{ group | downcase }}">{{ group }}</h2>
<ul class="docs-index-group">
  {% for doc in group_docs %}
  <li>
    <a href="{{ doc.url | relative_url }}">
      <span class="docs-index-title">{{ doc.title }}</span>
      {% if doc.description %}<span class="docs-index-desc">{{ doc.description }}</span>{% endif %}
    </a>
  </li>
  {% endfor %}
</ul>
{% endif %}
{% endfor %}
