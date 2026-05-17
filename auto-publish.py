#!/usr/bin/env python3
"""FinTech AI Weekly - auto generate & publish"""

import subprocess, re, os, glob, sys
from datetime import datetime

REPO_DIR = "/home/thor/finAI-website"
POST_DIR = os.path.join(REPO_DIR, "docs/posts")

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

print(f"[{DATE}] W{WEEK} - {TOPIC}")

# 1. 生成文章 - 用 yuanjian profile
prompt = f"""写一篇关于【{TOPIC}】的金融科技AI行业追踪文章。

要求：
- 中文Markdown格式
- 第一行必须是 ---
- 带YAML frontmatter: title, date, tags
- title: FinTech AI Weekly W{WEEK} - {TOPIC}
- tags: [fintech, ai, banking]
- 800-1200字，有具体案例或数据
- 不谈个股推荐或投资建议
- 正文先写文章内容，不要聊天性质的文字"""

result = subprocess.run(
    ["hermes", "-p", "yuanjian", "chat", "-q", prompt],
    capture_output=True, text=True, timeout=300, cwd=REPO_DIR
)
raw = result.stdout

# 2. 解析输出 - 查找第一个 --- 开头到末尾的内容
body = ""
for line in raw.split("\n"):
    if line.strip().startswith("---"):
        # 找到 frontmatter 开始
        idx = raw.index(line)
        body = raw[idx:]
        break

if not body:
    # fallback: 取最后一个 ╰─ 框内的内容
    parts = re.split(r"[╰╯╭╮╴╵╶╷─│╎┆┊]", raw)
    for p in reversed(parts):
        p = p.strip()
        if len(p) > 100 and ("#" in p or "---" in p):
            body = p
            break

if not body or len(body) < 100:
    print(f"ERROR: failed to extract article, raw length={len(raw)}")
    print("RAW PREVIEW:", raw[:200])
    sys.exit(1)

# 3. 写入
filepath = os.path.join(POST_DIR, f"fintech-ai-w{WEEK}.md")
with open(filepath, "w") as f:
    f.write(body.strip())
print(f"Written: {filepath} ({len(body)} chars)")

# 4. 更新索引
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
    index_lines.append(f"- [{title or name}](./{name})")
with open(os.path.join(POST_DIR, "index.md"), "w") as f:
    f.write("\n".join(index_lines))
print("Index updated")

# 5. Git commit + push (with timeout, non-blocking)
os.chdir(REPO_DIR)
subprocess.run(["git", "add", "-A"], capture_output=True, timeout=30)
subprocess.run(["git", "commit", "-m", f"auto: fintech ai w{WEEK} [{DATE}]"], capture_output=True, timeout=30)

# 6. Push with longer timeout and retry
try:
    token = ""
    env = open("/home/thor/.hermes/.env").read()
    m = re.search(r"GITHUB_TOKEN=(.+)", env)
    token = m.group(1).strip() if m else ""

    for i in range(4):
        r = subprocess.run(
            ["git", "push", f"https://Thor-Zhao:{token}@github.com/Thor-Zhao/finAI.git", "main"],
            capture_output=True, text=True, timeout=(i+1)*60
        )
        if r.returncode == 0:
            print(f"Pushed OK (attempt {i+1})")
            break
        print(f"Push #{i+1}: timeout or error")
    else:
        print("Push failed after 4 attempts - commit is local, run 'cd ~/finAI-website && git push' later")
except Exception as e:
    print(f"Push error (non-fatal): {e}")
    print("Commit is local, push when network is good")

print(f"DONE: W{WEEK}")
