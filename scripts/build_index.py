#!/usr/bin/env python3
"""从 bundle 的 source.json 建页码→block 索引。

用法: python3 build_index.py <bundle目录> [输出.json]
"""
import json, sys
from pathlib import Path


def build(bundle: Path):
    src = json.load(open(bundle / "source.json"))
    # 页码键是 'page'，不是 'pageNo'
    return {
        int(pg["page"]): [[b["id"], b.get("text", "")] for b in pg["blocks"]]
        for pg in src["pages"]
    }


def main():
    bundle = Path(sys.argv[1])
    idx = build(bundle)
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else bundle.parent / "blocks.json"
    json.dump({str(k): v for k, v in idx.items()}, open(out, "w"), ensure_ascii=False)

    pages = sorted(idx)
    print(f"{len(pages)} 页，页码 {pages[0]}–{pages[-1]}  →  {out}")
    for p in pages[:3]:
        first = idx[p][0] if idx[p] else ("-", "")
        print(f"  p{p}: {len(idx[p]):>3} blocks | {first[0]} = {first[1][:40]!r}")


if __name__ == "__main__":
    main()
