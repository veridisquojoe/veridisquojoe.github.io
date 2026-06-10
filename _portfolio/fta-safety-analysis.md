---
title: "FTA Safety Analysis & Visualization"
excerpt: "Interactive geospatial analysis of NYC transit safety incidents — heat maps, time-slider visualization, and data-driven insights for policy makers."
date: 2025-10-01
header:
  teaser: /assets/images/teasers/fta_safety.svg
  overlay_color: "#424658"
---

I've developed a suite of tools for analyzing and visualizing Federal Transit Administration (FTA) safety data. This work demonstrates geospatial analysis, interactive visualization, and data-driven insights for public transit safety to aid policy makers.

For example, I developed an analysis to help answer business questions about trends in New York City. While I can't share the real example, here is an overview of what I did in a new file: data cleaning and preprocessing of FTA safety datasets, statistical analysis of incident patterns and trends, and identification of high-risk areas and incident types.

[View the FTA safety analysis code](https://github.com/veridisquojoe/veridisquojoe.github.io/blob/main/projects/fta_safety_analysis.py){: .btn .btn--primary}

## General Map with Heat Map Option

A general map with a heat map option where you can toggle on and off the types of deadly events occurring from 2014–present.

<iframe class="map-embed" src="/projects/fta_nyc_fatal_incidents_map.html" title="NYC Fatal Incidents Map" loading="lazy"></iframe>

## Interactive Time-Slider Visualization

The next iteration is a more interactive time-slider visualization of transit safety incidents in New York City, with temporal analysis via time-slider (note the increase in severe events beginning in 2020 and escalating in following years) and geospatial mapping of incidents across NYC's transit modes.

<iframe class="map-embed" src="/projects/fta_nyc_time_slider_map.html" title="NYC Time Slider Map" loading="lazy"></iframe>

## Code

I used data collected through the NTD that my team helped validate and publish to [DOT's open data portal](https://data.transportation.gov/Public-Transit/Major-Safety-Events/9ivb-8ae9). I asked Claude for some help finding the deadliest events in New York City. The resulting code:

- [NYC base map generation](https://github.com/veridisquojoe/veridisquojoe.github.io/blob/main/projects/fta_nyc_basemap.py) — creating the foundational map
- [Time-slider map script](https://github.com/veridisquojoe/veridisquojoe.github.io/blob/main/projects/fta_nyc_time_slider_map.py) — the temporal visualization
- [Deadly events mapping](https://github.com/veridisquojoe/veridisquojoe.github.io/blob/main/projects/fta_deadly_events_map.py) — focused analysis of fatal incidents
