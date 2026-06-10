---
title: "NLP for Data Validation"
excerpt: "Using NLP to extract facts from free-text notes and cross-validate them against tabular records — a proof of concept on public transit data."
date: 2025-09-01
header:
  teaser: /assets/images/teasers/nlp_validation.svg
  overlay_color: "#6C739C"
---

In my job I manage a team that handles data validation. Here is an exercise I did on public data as a proof of concept for a data validation technique. The goal was to locate and extract "year" from long free-text notes, compare that year to another value in the same record, and discuss the accuracy of the results.

[View the notebook](https://github.com/veridisquojoe/veridisquojoe.github.io/blob/main/projects/nlp_public_transit_data.ipynb){: .btn .btn--primary}
[View the script](https://github.com/veridisquojoe/veridisquojoe.github.io/blob/main/projects/nlp_transit_data.py){: .btn .btn--inverse}

## Related: Treating Structured Data as Unstructured

An approach to understanding data quality by applying unsupervised learning techniques: use k-means clustering to group data with a known structure, then use neural networks to do the same thing.

[View this analysis](https://veridisquojoe.github.io/machinelearnjoe/Data%20Wrangling%20Practice.htm)
