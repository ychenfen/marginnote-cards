---
name: marginnote-cards
description: 把 MarginNote 4「外部 AI Agent 拆书」导出的 bundle 变成可回源、可主动回忆的卡片树 result.md。TRIGGER：用户给出 BreakdownBundles 里的任务包、提到「拆书」「待导入」「result.md」「回源卡片树」「anchorMode/block/source.json」；要把教材/习题册/错题做成 MarginNote 脑图卡片；或撞上这些坑——MarginNote 里 `$$...$$` 缩进在列表中导致后文整段变成红色原始文本、表格里裸 `|` 撑坏单元格、扫描版 PDF 没有文本层、MarginNote 抽取的文本把数学公式打烂、正则 re.S 跨段贪婪匹配把 markdown 换行吃掉。即使没明说 MarginNote，只要是「把一本书/一份习题拆成带回源锚点的卡片树」就用它。SKIP（不要触发）：普通 Markdown 笔记整理、Anki/Obsidian 卡片（回源机制完全不同）、不需要 block 锚点的纯摘要。
---

# MarginNote 拆书卡片树

把 MN4 导出的 bundle 变成 `result.md`，导回后成为可点击回源的脑图卡片树。

## 一、先摸清 bundle

包在 `~/Library/Containers/QReader.MarginStudy.easy/Data/Documents/BreakdownBundles/breakdown_<ID>_<时间戳>/`，
里面有 `manifest.json`（topicid / bookTitle / pageRange / anchorMode）、`source.json`（逐页 blocks）、
`OUTPUT-CONTRACT.md`（**每次都读，这是硬约束**）、`TASK.md`、待写的 `result.md`。

⚠️ **同一本书常有多个重复包**（用户点了几次导出）。只填一个，其余告诉用户删掉，否则会导入出重复卡片树。
⚠️ 选**题目所在的那个包**做锚点宿主，不要选答案包 —— 回源要跳到题干，符合「先回忆再看解法」。

建页码→block 索引（**页码键是 `pg['page']`，不是 `pageNo`**）：

```python
d=json.load(open('source.json'))
idx={int(pg['page']):[[b['id'],b.get('text','')] for b in pg['blocks']] for pg in d['pages']}
```

## 二、内容从哪来（决定成败的一步）

MarginNote 自己抽的文本**对公式基本不可用**（`a=1,6=1` 里的 6 其实是 b、分式塌成一行、`` 私有区乱码）。按这个顺序找数据源：

1. **PDF 自带文本层** —— `fitz` 直接抽，比 MN 抽的准得多。先验：
   `doc[n].get_text()` 有内容就能用（公式会线性化但可读）
2. **扫描版没有文本层** —— 别急着上 OCR。**把页渲染成 PNG 直接读图**：
   `doc[n].get_pixmap(dpi=130).save(...)`，然后用 Read 工具看图。公式完整清晰，比任何 OCR 都准
3. 真要批量 OCR 才考虑 Mistral `mistral-ocr-latest`（见 `references/ocr-fallback.md`）

💡 定位章节边界：先渲染**页眉裁切拼接的联系表**（每页顶部 7% 竖向拼成一张），一次读图就能定位所有章的页码，
比逐页试读省几十倍。缩略图网格（每页缩到 230px 排成 6 列）可用来找「综合题」这类大标题分界。

⚠️ **不确定的内容必须回原书**，绝不凭记忆写数学步骤。

## 三、卡片格式

见 `references/card-format.md`。核心：

- `#` 根 / `##` 章 / `###` 簇 / `####` 单卡
- **卡片标题写成提问式**（"偏导数存在，能推出连续吗？"），配折叠正文就能主动回忆
- 正文用 `-` 列表，`⚠️` 标陷阱、`💡` 标心法，末行 `[block: b_页_序]` 回源
- **按方法聚类，不按题号排** —— 这是整份材料的价值所在
- 每章尾部给【必背数字】表 + 【解题路线】卡
- `[[标题]]` 做卡片互链，只能链到本文件出现过的标题

## 四、LaTeX（MarginNote 的雷区，务必照做）

MN4 自带 MathJax，`Contents/Resources/richnote-template.html` 里配的是
`inlineMath: [["$","$"],["\\(","\\)"]]`。

🔴 **只用行内 `$...$`，绝对不要用 `$$...$$`。**
`$$` 只在顶格独立成行时才渲染；一旦缩进在列表项里或跟文字同行，解析就断，
**从断点往后整段退化成红色原始文本**。需要独立成行的公式，就单独占一个 `-` 列表项。

🔴 **数学里的绝对值一律写 `\lvert x \rvert`，不写裸 `|`。**
裸 `|` 在 markdown 表格里会被当成单元格分隔符，把表格撑烂。必背数字表里 `|f(x)| ≤ x²`、`|y''|` 这类特别多。

🔴 **不用 `\begin{cases}` 等多行环境**，行内模式下不稳。分段函数改并列写法：
`$f(x)=-1$（$0<\lvert x\rvert<1$）；$f(x)=x^2$（$\lvert x\rvert>1$）`

🔴 **卡片标题里不要放 `$`** —— 标题要当 `[[链接]]` 的锚，混排容易对不上。

其余：`\dfrac` 比 `\frac` 在卡片里更清楚；`\lim\limits_{x\to0}` 保证下标在正下方。

## 五、脚本

- `scripts/build_index.py` —— 从 source.json 建 block 索引 + 每题锚点表
- `scripts/validate.py` —— **写完必跑**：`$` 配对 / 残留 `$$` / 最长行 / 层级分布 / 非法 block id / 断链 / 重复标题 / 标题含 `$`

## 六、血泪教训

⚠️ **别用 `re.sub(..., flags=re.S)` 批量改 markdown。**
`\$\$(.+?)\$\$` 加了 `re.S` 会跨段贪婪匹配，把整个文件的换行吃掉压成一条几千字符的巨行，而且不可逆。
要改就**整文件重写**，或逐行处理（`for line in text.split('\n')`）。validate.py 里的「最长行」检查就是为了兜住这个。

⚠️ **导入时选「替换上次（删除旧卡片树后重新导入）」**。
MarginNote 的导入是**追加**不是覆盖 —— 已验证：学习集里原有的手做卡片会完整保留，
但同一份 result.md 导两次会出现两棵树。旧笔记安全，重复才是真风险。

⚠️ **章节页码不能靠页脚推**。分节标题（「二、填空题」）常出现在**页面中部**，
用页码区间切分会漏题。要用标题文本本身切分。

⚠️ 用户给的题号清单**先做越界校验**再动手。（实测帮用户抓到一个笔误：某节只有 14 题却写了 19。）
