# exponential-engineering

How to make every agent mistake the last of its kind: when you find a bug, add a lint rule that rules out the whole category.

Plain HTML and CSS, no build step. Open `index.html` locally. Pushes to `main` deploy to https://exponentialengineering.dev via GitHub Actions.

## Checks

We practice what we preach: everything on, zero findings.

```sh
zanity check . --fail-on warning --strict
uv run pytest
```

`pytest` runs [axe](https://github.com/dequelabs/axe-core) against the page in light and dark mode at desktop and phone widths, and fails on any violation or anything axe marks for review. CI runs both on every push and pull request.
