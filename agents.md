# Harden this repository for exponential engineering

You are a coding agent working in the repository where this guide was opened. Your task is to turn recurring mistakes into deterministic checks, then keep those checks running. Work on the current repository, not on the Exponential Engineering website.

**Definition of done:** all applicable checks pass, their configuration is committed, and at least one negative fixture demonstrates each newly introduced rule actually catches a violation. Do not disable checks, add blanket exclusions, or delete useful requirements to manufacture a green result.

## 1. Understand the repository

Inspect the languages, package manager, test commands, CI, existing linters, project layout, and current failures. Reuse what is already present. Record the baseline before changing anything. Make minimal changes; do not introduce another build system or framework.

## 2. Fuck Your Markdown: replace wishes with enforcement

Install or run [Fuck Your Markdown](https://github.com/benomahony/fuck-your-markdown) (Python 3.13+):

```sh
uvx --from fuck-your-markdown fym --hr
```

Read **every** finding. For each actionable requirement in flagged Markdown, implement an appropriate deterministic test, linter rule, architecture check, type check, script, or CI gate. First prove the new check fails on a representative violation and passes on compliant code. Only then remove redundant instructions or relocate useful explanations to `docs/`. Preserve human-facing documentation and any genuinely necessary agent bootstrap instructions. Rerun `fym --hr` until clean. The tool reports findings but does not fix files for you.

Note: `fym` intentionally flags `AGENTS.md` and similar instruction files. Do not evade it with an allowlist. Replace their enforceable contents with actual checks and keep only the smallest unavoidable bootstrap guidance.

## 3. Zanity: enforce code quality

Install [Zanity](https://github.com/benomahony/zanity) using the release instructions for your OS. On macOS/Linux:

```sh
curl -fsSL https://raw.githubusercontent.com/benomahony/zanity/main/install.sh | sh
zanity init
zanity check . --fix
zanity check . --fail-on warning --strict
```

Review the generated `zanity.toml` and adapt exclusions only for genuine generated, vendored, or fixture content. Fix remaining findings by changing code, not lowering severity. Keep `zanity check . --fail-on warning --strict` in the repository's existing CI workflow. If the language or repository is unsupported, document that limitation rather than pretending it passed.

## 4. Overwatch: make failures visible while coding

Install [Overwatch](https://github.com/benomahony/overwatch) using its current README and the integration for the coding agent or editor in use. Inspect its documented installation instructions rather than guessing a command.

Configure Overwatch for this repository's **real** test/build command. Prefer automatic language detection. Add a root `.overwatch.json` only when the defaults are insufficient. Keep the project enabled and make sure the baseline command runs the existing suite. Overwatch also runs Zanity alongside the tests when Zanity is on `PATH`.

Verify the integration reports a deliberately failing test, then reports green after restoring it. Do not claim a working integration merely because installation succeeded.

## 5. Close the loop

Run the repository's full tests, its existing lint/build checks, `zanity check . --fail-on warning --strict`, and `uvx --from fuck-your-markdown fym --hr`. Fix all actionable findings. Confirm CI executes the relevant deterministic gates and that Overwatch surfaces regressions during agent edits.

Report: checks added, original violations removed, negative fixtures tested, final command results, and any genuinely unresolved blockers. Never report success for a command you did not run.

**The rule:** every mistake should become the last mistake of its kind. Not another paragraph telling an agent to be careful.

[Exponential Engineering](https://exponentialengineering.dev/) · [Fuck Your Markdown](https://github.com/benomahony/fuck-your-markdown) · [Zanity](https://github.com/benomahony/zanity) · [Overwatch](https://github.com/benomahony/overwatch)
