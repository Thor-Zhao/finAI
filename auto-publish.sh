#!/bin/bash
# FinTech AI 每周文章自动发布
set -e

WEEK=$(date +%V)
DATE=$(date +%Y-%m-%d)
POST_DIR="/home/thor/finAI-website/docs/posts"
REPO_DIR="/home/thor/finAI-website"

# 选择本周主题
TOPICS=(
  "银行AI风控模型落地实践"
  "大模型在金融合规审查中的应用"
  "AI驱动的智能投顾发展趋势"
  "保险科技：AI理赔自动化"
  "监管科技(RegTech)：AI助力合规管理"
  "AI反欺诈：图神经网络在金融交易监测中的应用"
  "金融NLP：从文档处理到智能客服"
  "量化投资中的机器学习方法"
)
IDX=$(( (10#$WEEK) % ${#TOPICS[@]} ))
TOPIC="${TOPICS[$IDX]}"

# 调用 Hermes CLI 生成文章，去掉 Query 前缀行和末尾元信息
RAW=$(hermes -p yuanjian chat -q "
写一篇关于【$TOPIC】的金融科技AI行业追踪文章（中文，800-1200字，Markdown格式）。

要求：
- 带YAML frontmatter（title, date, tags）
- title格式：FinTech AI Weekly - W$WEEK - $TOPIC
- 有具体案例或数据支撑
- 面向金融从业者，专业但不晦涩
- 不谈个股推荐或投资建议
- 标签用英文如 [fintech, ai, banking, regtech]
" 2>/dev/null)

# 提取正文（跳过 Query: 开头的内容）
ARTICLE=$(echo "$RAW" | sed -n '/^---$/,$ p')

echo "$ARTICLE" > "$POST_DIR/fintech-ai-w$WEEK.md"

# 更新文章列表索引
echo "# 文章列表" > "$POST_DIR/index.md"
echo "" >> "$POST_DIR/index.md"
for f in $(ls -t "$POST_DIR"/*.md); do
  name=$(basename "$f" .md)
  [ "$name" = "index" ] && continue
  title=$(head -10 "$f" | grep "^title:" | sed 's/title: *//; s/^"//; s/"$//' | head -1)
  [ -z "$title" ] && title="$name"
  echo "- [$title](./$name)" >> "$POST_DIR/index.md"
done

# 推送
cd "$REPO_DIR"
git add -A
git commit -m "auto: fintech ai weekly w$WEEK - $TOPIC"
git push
echo "OK: fintech-ai-w$WEEK.md published [$TOPIC]"
