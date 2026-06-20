# Frontiers in Cognition — Hypothesis & Theory submission

LaTeX source for the SMN paper, converted from `../frontiers-smn-paper.md`
(the markdown remains the working scratch copy; this `.tex` is the source of truth
going forward — cross-references are automatic via `\label`/`\ref`).

## Files
- `frontiers-smn-paper.tex` — manuscript (Frontiers Harvard/author-date class)
- `references.bib` — self-contained bibliography (refine as we go)
- `FrontiersinHarvard.cls`, `Frontiers-Harvard.bst`, `logo1.eps`, `logo2.eps` — Frontiers template files (do not edit)

## Build
```
pdflatex frontiers-smn-paper
bibtex   frontiers-smn-paper
pdflatex frontiers-smn-paper
pdflatex frontiers-smn-paper
```
or `latexmk -pdf frontiers-smn-paper`.

Figures resolve from `../../figures/` via `\graphicspath`. For final submission,
copy the referenced PNGs into this directory and upload them individually.

## Submission checklist (later)
- [x] Corresponding-author email (preprint address: nagarjuna@iiserpune.ac.in)
- [x] Figures placed + referenced (ladder, menagerie, S0, Q1b, Pred-1)
- [ ] Funding statement
- [ ] Copy figure PNGs into this dir for the submission bundle
- [ ] Tidy overfull hboxes (wide ledger table, long URLs)
- [ ] Verify body word count ≤ 12,000 (main body only)
- [ ] Fill remaining bib fields (e.g. Tomasello publisher; arXiv "and others" → full author lists)
