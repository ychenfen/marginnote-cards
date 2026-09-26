[中文](#中文) | [English](#english)

<h1 align="center">MarginNote Cards</h1>

<p align="center">
  <strong>将 MarginNote 4 的图书拆解任务包转换为可回溯原文的关联卡片树</strong><br>
  Turn MarginNote 4 book-breakdown bundles into a linked card tree anchored to the source.
</p>

## 中文

MarginNote Cards 是一个 [Claude Code](https://claude.com/claude-code) 技能，用于将 **MarginNote 4** 的“外部 AI 智能体”图书拆解任务包转换为相互关联、可回溯原文的卡片树。

MarginNote 4 可以将一本书导出为任务包，交给外部智能体处理。智能体写入 `result.md` 后，MarginNote 会将它重新导入为思维导图，其中每张卡片都链接到其来源页面上的准确文本块。这个技能不仅定义了格式约定，更重要的是记录了官方文档中没有说明的常见问题及规避方法。

### 项目内容

```text
SKILL.md                     工作流程与实践中总结的关键问题
references/card-format.md    卡片结构、聚类方式与交叉链接
references/ocr-fallback.md   PDF 没有文本层时的处理方法
scripts/build_index.py       根据 source.json 建立页面到文本块的索引
scripts/validate.py          导入前的健康检查
```

### 为什么需要它

**`$$...$$` 会悄悄破坏其后的所有内容。** MarginNote 4 内置的 MathJax 配置为 `inlineMath: [["$","$"],["\\(","\\)"]]`。显示公式只有在独占一行且从行首开始时才能正确渲染。如果把它缩进到列表项中，或与正文写在同一行，解析器就会出错，而且该卡片中后续的每一行都会退化为原始文本。请只使用行内公式 `$...$`。

**数学表达式中未转义的 `|` 会破坏 Markdown 表格。** 请写成 `\lvert x \rvert`。包含大量公式的参考表格中经常会出现 `|f(x)| ≤ x²` 一类表达式。

**MarginNote 自带的文本提取会损坏公式。** 例如，`a=1,6=1` 中的 `6` 实际上可能是 `b`；分数可能被压成一行；还可能出现私用区字符。应优先从 PDF 文本层获取内容；如果页面是扫描件，则将页面渲染为 PNG 后直接读取图像。读取渲染后的页面通常比 OCR 更可靠：公式可以保持完整，而且不需要 API，也不会产生费用。

**不要使用 `re.S` 批量编辑 Markdown。** `re.sub(r"\$\$(.+?)\$\$", ..., flags=re.S)` 会跨段落贪婪匹配并吞掉文件中的所有换行，最终把整份文档压成一行数千字符的内容。应改为重写完整文件。`validate.py` 会专门检查最长行长度，以发现这类问题。

**导入操作会追加内容，而不是替换内容。** 笔记本中手动创建的卡片会在导入后保留，这一点已经验证。真正的风险是重复导入同一个 `result.md`，从而生成两棵相同的卡片树。请在导入对话框中选择“替换上次导入”。

### 设计理念

卡片按**方法而非题号**分组。标题采用问题形式，正文可以折叠，便于主动回忆。每章末尾都有查找表和决策流程。跨章节线索集中索引在根节点，因为这才是这套结构真正的价值；单张卡片只是支撑这些联系的证据。

### 安装

```bash
git clone https://github.com/ychenfen/marginnote-cards.git ~/.claude/skills/marginnote-cards
```

个人技能放在 `~/.claude/skills/` 中；项目技能放在 `.claude/skills/` 中。

### 许可证

MIT

---

## English

A [Claude Code](https://claude.com/claude-code) skill for turning **MarginNote 4** "external AI agent" book-breakdown bundles into a linked, source-anchored card tree.

MarginNote 4 can export a book as a task bundle for an external agent to process. The agent writes `result.md`; MarginNote imports it back as a mind-map where every card links to the exact block on the exact page it came from. This skill encodes the format contract and — more usefully — the failure modes that are not documented anywhere.

### What's in here

```text
SKILL.md                     workflow + the hard-won pitfalls
references/card-format.md    card structure, clustering, cross-links
references/ocr-fallback.md   when the PDF has no text layer
scripts/build_index.py       page → block index from source.json
scripts/validate.py          pre-import health check
```

### The pitfalls this exists for

**`$$...$$` silently corrupts everything after it.** MarginNote 4 ships MathJax configured with
`inlineMath: [["$","$"],["\\(","\\)"]]`. Display math only renders when it starts at column 0 on its own line. Indent it inside a list item, or put it on the same line as text, and the parser breaks — *and every line after it in that card degrades to raw source*. Use inline `$...$` exclusively.

**Bare `|` in math breaks markdown tables.** Write `\lvert x \rvert`. Formula-heavy reference tables are full of `|f(x)| ≤ x²`-type expressions.

**MarginNote's own text extraction mangles formulas.** `a=1,6=1` where the `6` is really a `b`; fractions collapse to one line; private-use-area glyphs. Get content from the PDF's text layer instead — or, for scanned pages, render to PNG and *read the image*. Reading a rendered page beats OCR: formulas stay intact, no API, no cost.

**Don't bulk-edit markdown with `re.S`.** `re.sub(r"\$\$(.+?)\$\$", ..., flags=re.S)` greedily spans paragraphs and eats every newline in the file, collapsing it into one multi-thousand-character line. Rewrite whole files instead. `validate.py` checks longest-line length specifically to catch this.

**Import appends, it doesn't replace.** Hand-made cards already in the notebook survive an import — verified. The real risk is importing the same `result.md` twice and getting two trees. Choose "replace last import" in the dialog.

### Design opinion

Cards are grouped **by method, not by question number**. Titles are written as questions so the body can be folded for active recall. Every chapter ends with a lookup table and a decision procedure. Cross-chapter threads are indexed at the root — that's where the actual value is; the individual cards are just the evidence.

### Install

```bash
git clone https://github.com/ychenfen/marginnote-cards.git ~/.claude/skills/marginnote-cards
```

Personal skills live in `~/.claude/skills/`; project skills in `.claude/skills/`.

### License

MIT
