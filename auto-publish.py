#!/usr/bin/env python3
"""FinTech AI Weekly - auto generate & publish"""

import subprocess, re, os, glob
from datetime import datetime

REPO_DIR = "/home/thor/finAI-website"
POST_DIR = os.path.join(REPO_DIR, "docs/posts")
GIT_TOKEN = open("/home/thor/.hermes/.env").read()
match = re.search(r"GITHUB_TOKEN=(.+)", GIT_TOKEN)
TOKEN = match.group(1).strip() if match else ""

WEEK = datetime.now().strftime("%V")
DATE = datetime.now().strftime("%Y-%m-%d")
TOPICS = [
    "银行AI风控模型落地实践",
    "大模型在金融合规审查中的应用",
    "AI驱动的智能投顾发展趋势",
    "保险科技：AI理赔自动化",
    "监管科技(RegTech)：AI助力合规管理",
    "AI反欺诈：图神经网络在金融交易监测中的应用",
    "金融NLP：从文档处理到智能客服",
    "量化投资中的机器学习方法",
]
TOPIC = TOPICS[(int(WEEK)) % len(TOPICS)]

print(f"[{DATE}] W{WEEK} topic: {TOPIC}")

# 调用 Hermes CLI
result = subprocess.run(
    ["hermes", "-p", "yuanjian", "chat", "-q", f"""
写一篇关于【{TOPIC}】的金融科技AI行业追踪文章（中文，800-1200字，Markdown格式）。

要求：
- 带YAML frontmatter（title, date, tags）
- title格式：FinTech AI Weekly - W{WEEK} - {TOPIC}
- 有具体案例或数据支撑
- 面向金融从业者，专业但不晦涩
- 不谈个股推荐或投资建议
- 标签用英文，如 [fintech, ai, banking]
- Markdown正文用中文
"""],
    capture_output=True, text=True, timeout=300, cwd=REPO_DIR
)

output = result.stdout
# 提取方框内正文
lines = output.split("\n")
article_lines = []
in_box = False
for line in lines:
    if "╭─" in line or "╰─" in line:
        continue
    if in_box:
        article_lines.append(line)
    if "────────────────────────────────────────" in line:
        continue

# Fallback: 提取 Query 之后、第一次出现中文开始
if not article_lines:
    start = False
    for line in lines:
        if "Query:" in line:
            start = True
            continue
        if start and line.strip() and not line.startswith("Init"):
            article_lines.append(line)

body = "\n".join(article_lines).strip()

# 如果 body 没内容，尝试另一种方式
if not body or len(body) < 50:
    text = output.strip()
    # 取 Initializing agent... 之后的内容
    idx = text.find("Initializing agent")
    if idx > 0:
        text = text[idx + 20:]
    # 去掉 box 装饰
    text = re.sub(r"[╭─╰─╮│╯╮╭]", "", text).strip()
    body = text

# 写入文件
slug = f"fintech-ai-w{WEEK}"
filepath = os.path.join(POST_DIR, f"{slug}.md")
with open(filepath, "w") as f:
    f.write(body)
print(f"Written: {filepath} ({len(body)} chars)")

# 验证 frontmatter
first_line = body.strip().split("\n")[0] if body.strip() else ""
if first_line != "---":
    print(f"WARN: article may not have frontmatter, first line: {first_line[:30]}")

# 更新索引
index_lines = ["# 文章列表", ""]
for f in sorted(glob.glob(os.path.join(POST_DIR, "*.md")), reverse=True):
    name = os.path.basename(f).replace(".md", "")
    if name == "index":
        continue
    with open(f) as fp:
        title = None
        for line in fp:
            m = re.match(r'^title:\s*["\']?(.+?)["\']?\s*$', line)
            if m:
                title = m.group(1)
                break
    link_text = title or name
    index_lines.append(f"- [{link_text}](./{name})")
with open(os.path.join(POST_DIR, "index.md"), "w") as f:
    f.write("\n".join(index_lines))

# git push with retry
os.chdir(REPO_DIR)
subprocess.run(["git", "add", "-A"], capture_output=True)
subprocess.run(["git", "commit", "-m", f"auto: fintech ai weekly w{WEEK} [{DATE}]"], capture_output=True)

for attempt in range(3):
    r = subprocess.run(
        ["git", "push", f"https://Thor-Zhao:{TOKEN}@github.com/Thor-Zhao/finAI.git", "main"],
        capture_output=True, text=True, timeout=60
    )
    if r.returncode == 0:
        print(f"Pushed successfully (attempt {attempt+1})")
        break
    print(f"Push failed (attempt {attempt+1}): {r.stderr[:80]}")
else:
    print("Push failed after 3 attempts - commit is local, retry later with 'git push'")

print(f"DONE: W{WEEK} - {TOPIC}")
