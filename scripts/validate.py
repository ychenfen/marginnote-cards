#!/usr/bin/env python3
"""导入前的体检。任何一项红了都不要导。

用法: python3 validate.py <result.md> [bundle目录]
给了 bundle 目录才能校验 block id 是否真实存在。
"""
import json, re, sys
from collections import Counter
from pathlib import Path

RED, GRN, OFF = "\033[31m", "\033[32m", "\033[0m"


def main():
    md = Path(sys.argv[1]).read_text(encoding="utf-8")
    lines = md.split("\n")
    ok = True

    def check(cond, good, bad):
        nonlocal ok
        if cond:
            print(f"  {GRN}✓{OFF} {good}")
        else:
            ok = False
            print(f"  {RED}✗{OFF} {bad}")

    # —— LaTeX ——
    print("LaTeX")
    odd = [(i + 1, l[:60]) for i, l in enumerate(lines) if l.count("$") % 2]
    check(not odd, "$ 全部配对", f"$ 不配对: {odd[:3]}")
    check(md.count("$$") == 0, "无 $$", f"残留 {md.count('$$')} 个 $$（列表里的 $$ 会污染后文整段）")
    # 按 $ 切分：奇数段才是公式内容，避免把表格分隔符误判成公式里的 |
    # 按 $ 切分：奇数段才是公式。裸 | 只有在**表格行**里才会撑坏单元格
    bare_tbl, bare_txt = [], []
    for i, l in enumerate(lines):
        parts = l.split("$")
        if len(parts) % 2 == 0:      # $ 不配对，前面已单独报过
            continue
        hit = next((m for m in parts[1::2] if "|" in m), None)
        if hit is None:
            continue
        (bare_tbl if l.lstrip().startswith("|") else bare_txt).append((i + 1, hit[:50]))
    check(not bare_tbl, "表格行内公式无裸 |",
          f"表格里有裸 | 会撑坏单元格，改用 \\lvert \\rvert: {bare_tbl[:3]}")
    if bare_txt:
        print(f"    · {len(bare_txt)} 处公式用了裸 |（不在表格里，可渲染；"
              f"但挪进表格就会坏，建议统一 \\lvert）")
    check("\\begin{cases}" not in md, "无 cases 环境", "有 \\begin{cases}，行内模式下不稳")

    # —— 结构 ——
    print("结构")
    longest = max((len(l), i + 1) for i, l in enumerate(lines))
    check(longest[0] < 500, f"最长行 {longest[0]} 字符",
          f"第 {longest[1]} 行长达 {longest[0]} 字符 —— 多半是正则 re.S 把换行吃了")

    lv, titles = {}, []
    for m in re.finditer(r"^(#{1,4})\s+(.*)$", md, re.M):
        n = len(m.group(1))
        lv[n] = lv.get(n, 0) + 1
        titles.append(m.group(2).split("　")[0].strip())
    print(f"    层级 {dict(sorted(lv.items()))}，共 {sum(lv.values())} 节点")
    check(lv.get(1, 0) == 1, "恰好 1 个根节点", f"根节点有 {lv.get(1,0)} 个（必须恰好 1 个）")

    dup = [t for t, c in Counter(titles).items() if c > 1]
    check(not dup, "标题无重复", f"重复标题（会让 [[链接]] 指错）: {dup}")
    bad_title = [t for t in titles if "$" in t]
    check(not bad_title, "标题不含 $", f"标题里有 $: {bad_title[:3]}")

    # —— 链接 ——
    print("链接与锚点")
    links = re.findall(r"\[\[([^\]]+)\]\]", md)
    broken = sorted({l for l in links if l not in set(titles)})
    check(not broken, f"{len(links)} 条卡片链接全部有效", f"断链: {broken}")

    ids = [i.strip() for s in re.findall(r"\[block:\s*([^\]]+)\]", md) for i in s.split(",")]
    if len(sys.argv) > 2:
        src = json.load(open(Path(sys.argv[2]) / "source.json"))
        valid = {b["id"] for pg in src["pages"] for b in pg["blocks"]}
        invalid = [i for i in ids if i not in valid]
        check(not invalid, f"{len(ids)} 个锚点全部存在于 source.json", f"非法 block id: {invalid[:5]}")
    else:
        print(f"    {len(ids)} 个锚点（未给 bundle 目录，跳过存在性校验）")
    check(all(re.fullmatch(r"b_\d+_\d+", i) for i in ids), "锚点格式合法",
          "锚点必须是 b_页_序，不能简写成纯数字")

    print(f"\n{len(md.encode())} 字节 | 约 {md.count('$')//2} 处公式 "
          f"| ⚠️ {md.count('⚠️')} | 💡 {md.count('💡')}")
    print(f"\n{'可以导入' if ok else RED + '有问题，先修再导' + OFF}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
