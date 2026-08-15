# marginnote-cards

A [Claude Code](https://claude.com/claude-code) skill for turning **MarginNote 4** "external AI agent" book-breakdown bundles into a linked, source-anchored card tree.

MarginNote 4 can export a book as a task bundle for an external agent to process. The agent writes `result.md`; MarginNote imports it back as a mind-map where every card links to the exact block on the exact page it came from. This skill encodes the format contract and — more usefully — the failure modes that are not documented anywhere.

## What's in here

```
SKILL.md                     workflow + the hard-won pitfalls
references/card-format.md    card structure, clustering, cross-links
references/ocr-fallback.md   when the PDF has no text layer
scripts/build_index.py       page → block index from source.json
scripts/validate.py          pre-import health check
```

## The pitfalls this exists for

**`$$...$$` silently corrupts everything after it.** MarginNote 4 ships MathJax configured with
`inlineMath: [["$","$"],["\\(","\\)"]]`. Display math only renders when it starts at column 0 on its own line. Indent it inside a list item, or put it on the same line as text, and the parser breaks — *and every line after it in that card degrades to raw source*. Use inline `$...$` exclusively.

**Bare `|` in math breaks markdown tables.** Write `\lvert x \rvert`. Formula-heavy reference tables are full of `|f(x)| ≤ x²`-type expressions.

**MarginNote's own text extraction mangles formulas.** `a=1,6=1` where the `6` is really a `b`; fractions collapse to one line; private-use-area glyphs. Get content from the PDF's text layer instead — or, for scanned pages, render to PNG and *read the image*. Reading a rendered page beats OCR: formulas stay intact, no API, no cost.

**Don't bulk-edit markdown with `re.S`.** `re.sub(r"\$\$(.+?)\$\$", ..., flags=re.S)` greedily spans paragraphs and eats every newline in the file, collapsing it into one multi-thousand-character line. Rewrite whole files instead. `validate.py` checks longest-line length specifically to catch this.

**Import appends, it doesn't replace.** Hand-made cards already in the notebook survive an import — verified. The real risk is importing the same `result.md` twice and getting two trees. Choose "replace last import" in the dialog.

## Design opinion

Cards are grouped **by method, not by question number**. Titles are written as questions so the body can be folded for active recall. Every chapter ends with a lookup table and a decision procedure. Cross-chapter threads are indexed at the root — that's where the actual value is; the individual cards are just the evidence.

## Install

```bash
git clone https://github.com/ychenfen/marginnote-cards.git ~/.claude/skills/marginnote-cards
```

Personal skills live in `~/.claude/skills/`; project skills in `.claude/skills/`.

## License

MIT
