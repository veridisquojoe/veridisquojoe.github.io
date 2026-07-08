---
title: "Portfolio AI Assistant (n8n Workflow + AI Agent)"
excerpt: "A live AI chatbot embedded in this portfolio site — built in n8n with an AI Agent node, GPT-4o Mini, and a self-hosted webhook. Zero external dependencies."
date: 2026-07-06
header:
  teaser: /assets/images/teasers/chatbot.svg
  overlay_color: "#424658"
---

The chat bubble in the bottom-right corner of this site is a live AI agent — backed by an n8n workflow running in production on a cloud n8n instance. Ask it about any project, skill, or data science topic from my background and it responds with context from a system prompt containing my full portfolio.

This project demonstrates end-to-end AI workflow deployment: designing the workflow in n8n, wiring the AI Agent node to a language model and memory buffer, embedding it on a Jekyll/GitHub Pages site with a self-contained vanilla JS widget, and publishing the active webhook trigger so it handles real traffic.

## Architecture

The workflow has three nodes connected in sequence:

1. **Chat Trigger** — n8n's `chatTrigger` node exposes a webhook endpoint and handles session routing. Any POST to the webhook URL with `{ chatInput, sessionId }` enters the workflow here.
2. **AI Agent (v3.1)** — A LangChain-backed agent node with `promptType: auto` and a full portfolio system prompt. It knows Joe's background, eight data science projects, two consulting projects, and how to route questions it can't answer.
3. **Subnodes** — OpenAI GPT-4o Mini (via resource locator, not a broken expression) and a Window Memory Buffer keyed on `sessionId` for multi-turn conversation.

The chat widget is self-contained HTML/CSS/JS injected via Jekyll's `_includes/head/custom.html` hook — no npm, no CDN dependencies, no build step required.

## What It Demonstrates

**n8n workflow design** — Building a functional AI workflow from scratch: trigger selection, agent configuration, model wiring, memory setup, credential management, and publish/activate lifecycle.

**AI Agent integration** — Practical use of n8n's LangChain agent node with a real system prompt, not a toy example. The agent handles follow-up questions via session memory.

**Webhook-based deployment** — The widget posts directly to the n8n webhook URL. This pattern generalizes to any AI workflow that needs a lightweight frontend interface.

**Jekyll/GitHub Pages embedding** — Adding interactive JS functionality to a static site without breaking the build pipeline or introducing npm dependencies.

**Production debugging** — Resolved a broken model expression (`=gpt-4o-mini` vs. resource locator format), a draft/active version divergence, and a CDN widget that silently errored — replaced with a self-contained fallback.

## Tech Stack

n8n (cloud) · OpenAI GPT-4o Mini · LangChain AI Agent (n8n node) · Window Memory Buffer · Jekyll (Minimal Mistakes theme) · vanilla JavaScript · GitHub Pages

[Try it — click the chat bubble on this site](https://veridisquojoe.github.io){: .btn .btn--primary}
