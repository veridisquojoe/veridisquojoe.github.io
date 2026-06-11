---
title: "Transit Safety and Security Assistant (RAG Chatbot)"
excerpt: "A retrieval-augmented chatbot that answers plain-English questions about ~50k public transit safety event records, grounded with cited sources."
date: 2026-06-01
header:
  teaser: /assets/images/teasers/chatbot.svg
  overlay_color: "#424658"
---

A RAG (Retrieval-Augmented Generation) chatbot that lets anyone ask plain-English questions about the public Major Safety Events dataset — collisions, derailments, fires, personal casualties, and security events across U.S. transit agencies from 2014 to present. Questions are embedded, matched against ~50k indexed event records plus the NTD Safety & Security Policy Manual, and the top results are passed to Claude to generate a grounded answer with cited source events.

This is the architecture I recommend when advising organizations on AI adoption: connect existing data to a conversational interface without retraining a model or exposing sensitive records. The same pattern applies to HR incident logs, support tickets, regulatory filings, or any corpus of semi-structured records.

[Try the live app](https://rag-based-transit-safety-security-data-chatbot.streamlit.app/){: .btn .btn--primary}
[View the source code](https://github.com/veridisquojoe/RAG-Based-Transit-Safety-Security-Data-Chatbot){: .btn .btn--inverse}

Built with Python, Streamlit, Voyage AI embeddings, and Claude (Anthropic). Data: FTA National Transit Database via [DOT's open data portal](https://data.transportation.gov/Public-Transit/Major-Safety-Events/9ivb-8ae9). An independent project — not affiliated with FTA or U.S. DOT.
