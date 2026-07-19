# Contributing experiments — branches & documentation versions

New experiments are developed on their own branch and published as a separate
documentation *version* on Read the Docs, so work-in-progress is browsable
alongside the stable bench without disturbing it. `main` is the canonical,
stable branch; the live site's default version (`latest`) tracks it.

## Branch naming

| Branch | Purpose |
|---|---|
| `main` | Stable, canonical bench + docs. Default RTD version (`/en/latest/`). |
| `exp/<topic>` | One experiment (or a tight cluster) in progress — e.g. `exp/r4-adaptation`, `exp/crossmodal`. |

Use a short, hyphenated `<topic>`. Because Read the Docs slugifies slashes,
`exp/r4-adaptation` publishes at `…/en/exp-r4-adaptation/`.

## How the documentation versions work

Each **activated** branch builds independently from *its own* `mkdocs.yml` and
`docs/`, and gets its own URL:

- `main` → <https://smn-lab.readthedocs.io/en/latest/>
- `exp/<topic>` → `https://smn-lab.readthedocs.io/en/exp-<topic>/`

Readers switch between active versions with the version flyout that Read the
Docs injects at the bottom of the page. An experiment branch can add its own
nav entries and pages that `main` does not have.

### Publishing a branch (one-time, in the RTD dashboard)

1. Push the branch to GitHub — RTD only sees branches that exist on the remote.
2. **readthedocs.org → project `smn-lab` → Versions → Activate** the branch.
3. It builds at `…/en/<slug>/`. Keep **Admin → Advanced Settings → Default
   version = `main`** so the site root still lands on the stable docs.

### Automating it

To avoid the dashboard step for every experiment, add an **Automation Rule**
(*Admin → Automation Rules*): *Activate version* when the branch name matches
`^exp/.*` (optionally also *Hide* it, to keep the flyout tidy). Then every
`exp/<topic>` branch you push appears as a version automatically.

!!! note "Community plan = public versions"
    On readthedocs.org every active version is public; there is no per-version
    privacy. Don't push to an `exp/` branch anything you want kept private.

## Preregistration first

An experiment branch **starts with a preregistration page**, before any result
exists — mirroring the bench's ethos (see [Pre-registration & status](test-plan.md)).
Write, in order:

1. **Hypothesis** — the claim, stated so that it can fail.
2. **Order parameter** — the single quantity that decides it.
3. **Matched foil** — the non-modulatory (or ablated) control run alongside.
4. **Pass / falsify** — the thresholds, fixed in advance.
5. **Run** — the exact command that reproduces it.

Only then build the experiment, wire the formalism into runnable code, plot the
result, and add the code-injection (see [Formalism ↔ code ↔ live bench](formalism-and-code.md)).

## Adding an experiment (checklist)

- [ ] `git checkout -b exp/<topic>` off `main`.
- [ ] `docs/experiments/<name>.md` — the preregistration page (above).
- [ ] `experiments/<name>.py` — the runnable script; expose named
      `# --8<-- [start:...]` anchors for any code shown in the docs.
- [ ] Add a nav entry under the right `§` group in `mkdocs.yml`.
- [ ] `mkdocs build --strict` passes locally (a missing snippet anchor fails
      the build).
- [ ] Push; the branch publishes as its own RTD version.
- [ ] When the result is confirmed, **merge to `main`** and deactivate the
      branch version.

The `exp/r4-adaptation` branch is a starter that follows this pattern.
