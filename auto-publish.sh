#!/bin/bash
# FinTech AI 每周文章自动发布
# n8n Execute Command 每周期调用此脚本

set -e
YEAR=$(date +%Y)
WEEK=$(date +%V)
DATE=$(date +%Y-%m-%d)
POST_DIR="/home/thor/finAI-website/docs/posts"
REPO_DIR="/home/thor/finAI-website"

# 生成文章内容
ARTICLE=$(hermes -p yuanjian chat -q "
写一篇金融科技AI行业追踪文章（中文，800-1200字，Markdown格式）。

主题池轮换使用（每次选一个）：
1. 银行AI风控模型落地实践
2. 大模型在金融合规审查中的应用
3. AI驱动的智能投顾发展趋势
4. 保险科技：AI理赔自动化
5. 监管科技(RegTech)：AI助力合规管理
6. AI反欺诈：图神经网络在金融交易监测中的应用
7. 金融NLP：从文档处理到智能客服
8. 量化投资中的机器学习方法

要求：
- 带YAML frontmatter（title, date, tags）
- 有具体案例或数据支撑
- 面向金融从业者，专业但不晦涩
- 不谈个股推荐或投资建议
- 标题格式如 'FinTech AI Weekly - W$WEEK'
- 标签用英文如 [fintech, ai, banking]
" 2>/dev/null)

# 写入文件
echo "$ARTICLE" > "$POST_DIR/fintech-ai-w$WEEK.md"

# 更新文章列表索引
echo "# 文章列表" > "$POST_DIR/index.md"
echo "" >> "$POST_DIR/index.md"
for f in $(ls -t "$POST_DIR"/*.md); do
  name=$(basename "$f" .md)
  [ "$name" = "index" ] && continue
  title=$(head -10 "$f" | grep "^title:" | sed 's/title: *//' | sed "s/^'//;s/'$//;s/^\"//;s/\"$//")
  [ -z "$title" ] && title="$name"
  echo "- [$title](./$name)" >> "$POST_DIR/index.md"
done

# 推送
cd "$REPO_DIR"
git add -A
git commit -m "auto: fintech ai weekly w$WEEK [$DATE]"
git push
echo "OK: fintech-ai-w$WEEK.md published"
