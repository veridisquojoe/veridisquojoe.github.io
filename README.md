# veridisquojoe.github.io

Personal data science portfolio of Joe Eldredge, live at [veridisquojoe.github.io](https://veridisquojoe.github.io).

Built with [Jekyll](https://jekyllrb.com/) and the [Minimal Mistakes](https://github.com/mmistakes/minimal-mistakes) theme (via `remote_theme`), hosted on GitHub Pages.

## Structure

- `index.md` — homepage (splash layout with featured projects)
- `_portfolio/` — one markdown page per project
- `_pages/` — portfolio index and about page
- `projects/` — project artifacts (notebooks, scripts, HTML analysis exports, interactive maps)
- `assets/images/teasers/` — project card graphics
- `_config.yml` — site, theme, and author configuration

## Local development

```bash
gem install bundler jekyll
bundle init && bundle add github-pages webrick
bundle exec jekyll serve
```

No build step is required for deployment — GitHub Pages builds the site on push.
