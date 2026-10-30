# Specs

Feature specs live here, one file per feature, named `YYYY-MM-DD-<slug>.md`. They are tracked in git (the rest of `docs/` is not).

## Writing a spec

The template is the one in the `to-spec` skill: Problem Statement, Solution, User Stories, Implementation Decisions, Testing Decisions, Out of Scope, Further Notes.

Two rules earned from a past spec:

- **A number in a spec is a guess until someone measures it.** Mark it: "约 32 KB（未实测）". The runtime estimate in the component-swap spec said 32 KB, shipped at 93 KB, and had to be corrected after review — the correction is cheap, but a reader who trusted the number wasted time on it.
- **Do not restate the implementation.** File paths and code snippets go stale within days. Record the decision and the reason; the code records itself.

## After implementation

When the work lands, update the spec where reality diverged, and write an ADR for each decision that is hard to reverse and surprising without context. The spec is the plan; the ADRs are what survives it.
