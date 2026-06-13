---
title: "Movie Recommender System (Netflix Ratings)"
excerpt: "K-means clustering to explore organic groupings in movie rating profiles — unsupervised learning as data exploration."
date: 2021-07-01
header:
  teaser: /assets/images/teasers/kmeans.svg
  overlay_color: "#6C739C"
---

From my time in the UVA School of Data Science. A team and I used a variety of techniques to predict movie scores on the Netflix Prize dataset (~100M ratings). This is some of the work from that project, where I used k-means clustering in PySpark to explore whether movies form organic clusters based on the rating profiles of the 1,000 most active reviewers — a way to use unsupervised learning for data exploration before building the prediction models.

Key findings: the cleanest structure is a two-way split, but a four-cluster model produced interpretable segments whose average ratings span 2.75 to 3.46 — the clusters track audience reception even though the algorithm never saw a quality label.

[View the results presentation](/projects/kmeans_movie_recommender.html){: .btn .btn--primary}
[View the notebook](https://github.com/veridisquojoe/veridisquojoe.github.io/blob/main/projects/kmeans_movie_recommender.ipynb){: .btn .btn--inverse}
