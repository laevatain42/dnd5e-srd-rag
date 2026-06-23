# TODO

## 下一步

- [ ] 基于 `POST /api/chat` 搭建第一版 Next.js 聊天 UI。

## RAG 质量

- [ ] 优化 chunk 边界，优先处理 Spells 和 Monsters。
- [ ] 增加条目级 subsection，例如 `Fire Bolt`、`Cleric`、`Grappled` 和怪物名称。
- [ ] 建立小型检索评估集，记录预期命中的页码和章节。
- [ ] 探索混合检索：BM25 关键词检索 + embedding 向量检索。

## 后续

- [ ] 增加流式响应，让体验更接近 ChatGPT。
- [ ] 增加本地开发脚本，简化常用命令。
