# exponential-engineering

How to make every agent mistake the last of its kind: when you find a bug, add a lint rule that rules out the whole category.

Plain HTML and CSS, no build step. Open `index.html` locally. Pushes to `main` deploy to https://exponentialengineering.dev via GitHub Actions.

## Checks

We practice what we preach: every validator we could find, on its strictest setting, and zero findings or it doesn't merge. CI runs all of them on every push and pull request.

| Validator | Checks | Strictest setting | Run it |
| --- | --- | --- | --- |
| [zanity](https://github.com/benomahony/zanity) | Python and workflows | `--strict --fail-on warning` | `zanity check . --fail-on warning --strict` |
| [axe](https://github.com/dequelabs/axe-core) | accessibility, light and dark, desktop and phone | fails on violations and on anything marked for review, no exclusions | `uv run pytest` |
| pytest | every correction made to the site, as a deterministic rule | see below | `uv run pytest` |
| [Nu Html Checker](https://validator.github.io/validator/) | HTML | warnings are errors | `npm run lint:html` |
| [stylelint](https://stylelint.io) | CSS | `stylelint-config-standard` | `npm run lint:css` |
| [actionlint](https://github.com/rhysd/actionlint) | GitHub workflows | defaults | `uv run actionlint` |
| [zizmor](https://docs.zizmor.sh) | GitHub workflow security | `--pedantic` | `uv run zizmor --pedantic .github` |
| [typos](https://github.com/crate-ci/typos) | spelling | defaults | `uv run typos` |
| [lychee](https://lychee.cli.rs) | every link | retries, no ignored failures | `lychee --config lychee.toml index.html README.md` |

The pytest rules: no em or en dashes in the copy, no naming and shaming libraries, the cover says deterministic rule not RULES.md, no JavaScript, versioned stylesheets, a 1200x630 social card, highlighted text readable on its band and on the paper, no sideways scrolling at any width, nothing left invisible after its animation, working in page links and no console errors.

Install the tools with `uv sync` and `npm ci`. `npm run lint:html` needs Java.
