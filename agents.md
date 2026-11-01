# Harden a repository

Run the [Exponential Engineering bootstrap script](https://exponentialengineering.dev/setup.sh) from the root of the repository you are working on:

```sh
curl -fsSL https://exponentialengineering.dev/setup.sh | sh
```

The script runs [Fuck Your Markdown](https://github.com/benomahony/fuck-your-markdown), installs and initialises [Zanity](https://github.com/benomahony/zanity), and identifies the [Overwatch](https://github.com/benomahony/overwatch) installation instructions for your agent.

It is a bootstrap, not a substitute for engineering work. After running it, convert fym findings into executable checks, fix Zanity findings, install and verify Overwatch, and wire the checks into existing CI. Prove each new check catches a deliberate violation before removing the corresponding instruction. Do not suppress failures just to obtain a clean report.

The script prints any remaining work. It does not silently rewrite code or install untrusted agent hooks.
