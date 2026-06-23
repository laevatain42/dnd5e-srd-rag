# dnd5e-srd-rag

## 中文

### 项目目标

`dnd5e-srd-rag` 是一个基于 D&D Beyond 发布的 SRD v5.2.1 PDF 构建的本地 RAG MVP。

当前目标是建立一条最小可用链路：

```text
PDF -> 抽取文本和页码 -> 标注章节 -> chunk -> embedding -> Chroma 检索 -> 带来源的问答上下文
```

### 当前能力

- 从本地 SRD PDF 抽取每页文本。
- 保留 SRD 版本、页码、section、subsection 等 metadata。
- 使用手动维护的目录页码 map 标注章节。
- 生成适合检索的 chunks。
- 使用 `Qwen/Qwen3-Embedding-0.6B` 生成本地 embeddings。
- 使用 ChromaDB 建立本地向量索引。
- 使用 `search.py` 做语义检索调试。
- 使用 `ask.py` 输出引用式问答上下文和 sources。

### 数据源与授权

- Source page: https://www.dndbeyond.com/srd
- Source PDF: https://media.dndbeyond.com/compendium-images/srd/5.2.1/SRD_CC_v5.2.1.pdf
- SRD version: 5.2.1
- Published date: 2025-05-01
- SRD content license: CC-BY-4.0

本仓库的 MIT License 仅覆盖本项目原创代码和文档，不重新授权 SRD 内容、PDF、抽取文本、chunks、embeddings 或向量库。

更多归属和授权说明见 [NOTICE.md](NOTICE.md)。

### 不提交的数据

以下内容是本地数据或生成产物，不应提交到 Git：

- `data/raw/*.pdf`
- `data/extracted/*`
- `data/chunks/*`
- `data/vectorstores/*`
- `data/indexes/*`
- `.env`
- `.venv/`
- `*.egg-info/`

目录中的 `.gitkeep` 仅用于保留空目录结构。

### 环境准备

建议使用 Python 3.11 或更新版本。

在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
```

如果 PowerShell 阻止激活脚本，可以在当前进程临时允许：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### 准备 PDF

把 SRD PDF 放到：

```text
data/raw/SRD_CC_v5.2.1.pdf
```

PDF 文件被 `.gitignore` 忽略，不会提交到仓库。

### 执行流程

按顺序运行：

```powershell
.\.venv\Scripts\python.exe scripts\ingest_pdf.py
.\.venv\Scripts\python.exe scripts\annotate_sections.py
.\.venv\Scripts\python.exe scripts\chunk_pages.py
.\.venv\Scripts\python.exe scripts\inspect_chunks.py
.\.venv\Scripts\python.exe scripts\index_chunks.py --reset
```

这些命令分别负责：

1. `ingest_pdf.py`：从 PDF 抽取每页文本和页码。
2. `annotate_sections.py`：根据 `section_map.py` 标注 section、subsection 和 `include_in_rag`。
3. `chunk_pages.py`：把页面文本切成检索 chunks。
4. `inspect_chunks.py`：检查 chunks 的长度、章节分布、页眉残留和异常开头。
5. `index_chunks.py --reset`：重新建立 Chroma 向量索引。

### 检索与问答

语义检索调试：

```powershell
.\.venv\Scripts\python.exe scripts\search.py "How does Cleric spellcasting work?" --top-k 3
```

按 section 过滤：

```powershell
.\.venv\Scripts\python.exe scripts\search.py "What does Fire Bolt do?" --section Spells --top-k 3
```

引用式问答上下文：

```powershell
.\.venv\Scripts\python.exe scripts\ask.py "How does Cleric spellcasting work?" --top-k 3
```

### 项目结构

```text
dnd5e-srd-rag/
  data/
    raw/              # 本地 PDF，不提交
    extracted/        # pages JSONL / annotated pages JSONL，不提交
    chunks/           # chunks JSONL，不提交
    vectorstores/     # Chroma 向量库，不提交
    indexes/          # 其他本地索引产物，不提交
  scripts/
    ingest_pdf.py
    annotate_sections.py
    chunk_pages.py
    inspect_pages.py
    inspect_chunks.py
    index_chunks.py
    search.py
    ask.py
  src/dnd5e_srd_rag/
    config.py
    pdf_extract.py
    jsonl.py
    section_map.py
    sections.py
    chunking.py
    embeddings.py
    vector_store.py
    retrieval.py
  tests/
```

### 当前限制

- `ask.py` 目前不调用 LLM，只输出检索到的 SRD 上下文和来源。
- `subsection` 目前基于页级目录 map；同一页多个小标题时，只能选择一个主要 subsection。
- 前 4 页不进入 RAG。
- 第一次加载 `Qwen/Qwen3-Embedding-0.6B` 时可能需要从 Hugging Face 下载模型。
- 如果 Hugging Face 匿名下载受限，可以设置 `HF_TOKEN`，但公开模型通常不强制需要。

---

## English

### Project Goal

`dnd5e-srd-rag` is a local RAG MVP built from the D&D Beyond SRD v5.2.1 PDF.

The current goal is to provide a minimal working pipeline:

```text
PDF -> text and page extraction -> section annotation -> chunking -> embeddings -> Chroma retrieval -> sourced answer context
```

### Current Features

- Extract page text from a local SRD PDF.
- Preserve SRD version, page number, section, subsection, and source metadata.
- Annotate sections from a manually maintained table-of-contents page map.
- Generate retrieval chunks.
- Generate local embeddings with `Qwen/Qwen3-Embedding-0.6B`.
- Build a local ChromaDB vector index.
- Use `search.py` for semantic retrieval debugging.
- Use `ask.py` for citation-style answer context and sources.

### Data Source and License

- Source page: https://www.dndbeyond.com/srd
- Source PDF: https://media.dndbeyond.com/compendium-images/srd/5.2.1/SRD_CC_v5.2.1.pdf
- SRD version: 5.2.1
- Published date: 2025-05-01
- SRD content license: CC-BY-4.0

The MIT License in this repository applies only to this project's original code and documentation. It does not relicense SRD content, PDFs, extracted text, chunks, embeddings, or vector indexes.

See [NOTICE.md](NOTICE.md) for attribution and licensing notes.

### Untracked Local Data

The following local data and generated artifacts should not be committed:

- `data/raw/*.pdf`
- `data/extracted/*`
- `data/chunks/*`
- `data/vectorstores/*`
- `data/indexes/*`
- `.env`
- `.venv/`
- `*.egg-info/`

The `.gitkeep` files only preserve the empty directory structure.

### Environment Setup

Python 3.11 or newer is recommended.

Run from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
```

If PowerShell blocks activation scripts, allow them for the current process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### Prepare the PDF

Place the SRD PDF at:

```text
data/raw/SRD_CC_v5.2.1.pdf
```

The PDF is ignored by `.gitignore` and should not be committed.

### Pipeline

Run the commands in this order:

```powershell
.\.venv\Scripts\python.exe scripts\ingest_pdf.py
.\.venv\Scripts\python.exe scripts\annotate_sections.py
.\.venv\Scripts\python.exe scripts\chunk_pages.py
.\.venv\Scripts\python.exe scripts\inspect_chunks.py
.\.venv\Scripts\python.exe scripts\index_chunks.py --reset
```

Command roles:

1. `ingest_pdf.py`: extract page text and page numbers from the PDF.
2. `annotate_sections.py`: annotate `section`, `subsection`, and `include_in_rag` from `section_map.py`.
3. `chunk_pages.py`: split annotated pages into retrieval chunks.
4. `inspect_chunks.py`: inspect chunk lengths, section distribution, page-header remnants, and suspicious starts.
5. `index_chunks.py --reset`: rebuild the Chroma vector index.

### Search and Ask

Semantic search debugging:

```powershell
.\.venv\Scripts\python.exe scripts\search.py "How does Cleric spellcasting work?" --top-k 3
```

Filter by section:

```powershell
.\.venv\Scripts\python.exe scripts\search.py "What does Fire Bolt do?" --section Spells --top-k 3
```

Citation-style answer context:

```powershell
.\.venv\Scripts\python.exe scripts\ask.py "How does Cleric spellcasting work?" --top-k 3
```

### Project Structure

```text
dnd5e-srd-rag/
  data/
    raw/              # Local PDF, not committed
    extracted/        # Pages JSONL / annotated pages JSONL, not committed
    chunks/           # Chunk JSONL, not committed
    vectorstores/     # Chroma vector store, not committed
    indexes/          # Other local index artifacts, not committed
  scripts/
    ingest_pdf.py
    annotate_sections.py
    chunk_pages.py
    inspect_pages.py
    inspect_chunks.py
    index_chunks.py
    search.py
    ask.py
  src/dnd5e_srd_rag/
    config.py
    pdf_extract.py
    jsonl.py
    section_map.py
    sections.py
    chunking.py
    embeddings.py
    vector_store.py
    retrieval.py
  tests/
```

### Current Limitations

- `ask.py` does not call an LLM yet; it prints retrieved SRD context and sources.
- `subsection` is currently based on a page-level table-of-contents map. If multiple headings appear on one page, only one primary subsection can be assigned.
- Pages 1-4 are excluded from RAG.
- The first load of `Qwen/Qwen3-Embedding-0.6B` may download the model from Hugging Face.
- If anonymous Hugging Face downloads are rate-limited, set `HF_TOKEN`; public models usually do not require it.
