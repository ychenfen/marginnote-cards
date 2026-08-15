# OCR 兜底（只在渲染读图不可行时用）

优先级：PDF 文本层 > 渲染成图直接读 > OCR。
**读图几乎总是更好** —— 公式完整、无需 API、无额外成本。只有需要机器批量处理全书文本时才 OCR。

## Mistral OCR

模型 `mistral-ocr-latest`，对数学排版明显好于通用 OCR。

```python
up  = client.files.upload(file={"file_name": name, "content": f}, purpose="ocr")
url = client.files.get_signed_url(file_id=up.id, expiry=120).url
r   = client.ocr.process(model="mistral-ocr-latest",
                         document={"type": "document_url", "document_url": url})
client.files.delete(file_id=up.id)
```

要点：
- 按 8 页一块切分，逐块缓存到磁盘，**跳过已存在的块**（断点续跑）
- 每页前插 `<!-- page: N -->` 标记，后面对齐页码要用
- 失败重试 3 次，退避 8s / 16s / 24s
- 过滤水印噪声行（"关注公众号"、`www.`、`http`、"版权所有"）

## 密钥

🔴 **绝不把密钥写进代码、配置或输出。**
放 `~/.config/<service>/secret.env` 并 `chmod 600`，用 `set -a; . 文件; set +a` 注入环境变量。
仓库/示例里一律用占位符 `REDACTED_REPLACE_LOCALLY`。

⚠️ 跑之前先确认里面不是占位符：

```bash
python3 -c "
import os
v = os.environ.get('MISTRAL_API_KEY','')
print('len', len(v), '占位符' if 'REDACTED' in v else 'ok')"
```

## 依赖

`mistralai` 和 `PyMuPDF(fitz)` 可能只装在某一个 Python 里。先探：

```bash
for P in python3.13 python3.12 python3.11 /opt/homebrew/bin/python3 /usr/bin/python3; do
  command -v $P >/dev/null || continue
  echo "$P -> $($P -c 'import mistralai,fitz;print("ok")' 2>&1|tail -1)"
done
```
