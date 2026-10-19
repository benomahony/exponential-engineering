# exponential-engineering

How to make every agent mistake the last of its kind: when you find a bug, add a lint rule that rules out the whole category.

Plain HTML and CSS, no build step. Open `index.html` locally. Pushes to `main` deploy to https://exponentialengineering.dev via GitHub Actions.

## Checks

We practice what we preach: everything on, zero findings.

```sh
zanity check . --fail-on warning --strict
uv run pytest
npm ci
npm run lint:html
npm run lint:css
uv run actionlint
uv run zizmor --pedantic .github
uv run typos
lychee --config lychee.toml index.html README.md
```

`pytest` runs [axe](https://github.com/dequelabs/axe-core) against the page in light and dark mode at desktop and phone widths, failing on any violation or anything axe marks for review, and turns every correction made to the site into a deterministic rule: no dashes in the copy, no naming and shaming libraries, deterministic rule not RULES.md, no JavaScript, versioned stylesheets, a 1200x630 social card, no sideways scrolling, nothing left invisible after its animation and no console errors. CI runs every check here on every push and pull request.
