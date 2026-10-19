# exponential-engineering

How to make every agent mistake the last of its kind: when you find a bug, add a lint rule that rules out the whole category.

Live at https://exponentialengineering.dev, built with [Zine](https://zine-ssg.io/).

## Develop

Install Zine 0.14.0, then start the development server from the repository root:

```sh
zine
```

Each page is a section in `content/index.smd`: `# [title]($section.id('slug').attrs('page'))`. The contents list and page numbers are generated from them.

## Build

```sh
zine release
```

The site is written to `public/`. Pushes to `main` build and deploy it to GitHub Pages.
