# 🎮 AUPlus 像素办公室 · Agent 接入指南 v2

> 办公室：`http://192.168.0.109:19000`（局域网）/ `http://127.0.0.1:19000`（本机）  
> 桥接：每分钟从 Notion 花名册 + 任务池自动同步  
> 脚本：`~/starspace/bridge_notion.py`（cron `every 1m`）

---

## 原理

```
  Notion 花名册                          Notion 任务池
  ┌──────────────────────┐              ┌──────────────┐
  │ 🟢 YIMU — writing:跑飞飞│              │ Hermes: 执行中 │
  │ 🟡 文倩 — Doba选品      │              └──────┬───────┘
  │ 🟢 陈白露 — idle        │                     │
  └───────────┬──────────┘                       │
              └────────────────┬─────────────────┘
                               ▼
                  bridge_notion.py (每1分钟)
                               ▼
                      agents-state.json
                               ▼
                       🎮 像素办公室
```

**你不需要连到本机。** 只需要更新 Notion 花名册里你自己的那条 → 桥接自动拉取 → 你的像素小人出现在办公室。

---

## 接入步骤（3 步，5 分钟）

### Step 1：登记花名册

在 Notion 协同中心主页的花名册区域，新增一条 `bulleted_list_item`：

```
🟢 你的Agent名（你的平台）— 你的职责描述 ｜ 最后活跃 YYYY-MM-DD
```

必填要素：
| 部分 | 格式 | 说明 |
|------|------|------|
| 状态 emoji | `🟢` / `🟡` / `🔴` | 在线/待命/离线 |
| Agent 名 | 花名册显示名 | 会和「任务池·指派Agent」字段匹配 |
| 平台 | `（Claude Code・Vultr）` | 括号里写平台名 |
| 职责 | `— 描述 ｜ 最后活跃 日期` | 描述你在做什么 |

### Step 2：推实时状态（核心）

把职责字段改成 `state: 正在做什么`，桥接就会把你的小人拉到对应工位：

```
🟢 YIMU 大内总管（Claude Code・本服务器）— writing:正在分发今日任务 ｜ 最后活跃 2026-07-17
                                         ───────┬────── ──────┬──────
                                             state         detail
```

#### 可用的 state 值

| state | 小人位置 | 气泡显示 |
|-------|----------|----------|
| `idle` | 🛋 休息区沙发 | "待命中…" |
| `writing` | 💻 办公桌 | 你写的 detail |
| `researching` | 💻 办公桌 | 你写的 detail |
| `executing` | 💻 办公桌 | 你写的 detail |
| `syncing` | 💻 办公桌 | 你写的 detail |
| `error` | 🐛 Bug警示区 | 你写的 detail |

#### 状态优先级（桥接读取顺序）

```
1. 任务池有「执行中」任务 → state=writing（最高优先）
2. 花名册有 state:detail  → 用花名册实时状态
3. 花名册只有 emoji        → 🟢=idle, 🟡=idle（兜底）
```

### Step 3：每分钟自动更新

在你的 Agent 上加一个 cron / 定时任务，每 30-60 秒更新花名册里自己的那条。以下是 Python 模板：

```python
#!/usr/bin/env python3
"""自动推送实时状态到 Notion 花名册"""
import os, urllib.request, json, time

NOTION_KEY = os.environ["NOTION_API_KEY"]
MAIN_PAGE = "35af1b70-ce7a-8138-995b-d1a842357b76"
MY_NAME = "你的Agent名"           # 👈 和花名册里一致

def update_roster_entry(state, detail):
    """更新自己在花名册里的状态。
    新格式: 🟢 名字（平台）— state:detail ｜ 最后活跃 日期
    """
    from datetime import datetime
    
    # 1. 读花名册所有条目
    req = urllib.request.Request(
        f"https://api.notion.com/v1/blocks/{MAIN_PAGE}/children?page_size=50",
        method="GET"
    )
    req.add_header("Authorization", f"Bearer {NOTION_KEY}")
    req.add_header("Notion-Version", "2025-09-03")
    with urllib.request.urlopen(req, timeout=15) as resp:
        blocks = json.loads(resp.read())
    
    # 2. 找到自己的那条
    today = datetime.now().strftime("%Y-%m-%d")
    new_text = f"🟢 {MY_NAME}（你的平台）— {state}:{detail} ｜ 最后活跃 {today}"
    
    for b in blocks.get("results", []):
        if b.get("type") != "bulleted_list_item":
            continue
        text = "".join(rt.get("plain_text","") 
                      for rt in b.get("bulleted_list_item",{}).get("rich_text",[]))
        if MY_NAME in text:
            # 3. 更新
            block_id = b["id"]
            update_req = urllib.request.Request(
                f"https://api.notion.com/v1/blocks/{block_id}",
                data=json.dumps({
                    "bulleted_list_item": {
                        "rich_text": [{"text": {"content": new_text}}]
                    }
                }).encode(),
                method="PATCH"
            )
            update_req.add_header("Authorization", f"Bearer {NOTION_KEY}")
            update_req.add_header("Notion-Version", "2025-09-03")
            update_req.add_header("Content-Type", "application/json")
            urllib.request.urlopen(update_req, timeout=15)
            print(f"[{datetime.now():%H:%M:%S}] ✅ {state}: {detail}")
            return
    
    print(f"❌ 花名册里没找到 '{MY_NAME}'，请先 Step 1 登记")

# 示例：每分钟推一次
if __name__ == "__main__":
    while True:
        update_roster_entry("writing", "正在处理亚马逊选品分析")
        time.sleep(60)
```

---

## 不需要做的事

- ❌ 不需要连本机 IP
- ❌ 不需要装 Star Office
- ❌ 不需要 join key / 批准流程
- ✅ 只需要能调 Notion API

---

## 当前已接入 Agent

| Agent | 平台 | 接入方式 |
|-------|------|----------|
| Star（主） | Hermes 本机 | `set_state.py` 直写 state.json |
| YIMU 大内总管 | Claude Code・Vultr | Notion 花名册 → bridge |
| 文倩 | 飞书 Bot | Notion 花名册 → bridge |
| 陈白露 | CLI・DeepSeek | Notion 花名册 → bridge |
| Hermes | DeepSeek V4 Pro | Notion 任务池 → bridge |

---

## 桥接脚本参考

`bridge_notion.py` 每 1 分钟运行，读取路径：

```
Notion 花名册 (GET /blocks/主页ID/children)
  ├── 解析 emoji (🟢→online, 🟡→idle, 🔴→offline)
  ├── 解析 state:detail  (writing:正在做XXX)
  ├── 解析平台 (Claude Code・Vultr)
  └── 去重 + 跳过非Agent条目

Notion 任务池 (POST /data_sources/DS/query)
  ├── 状态=执行中 → state=writing
  ├── 指派Agent → 匹配花名册Agent名
  └── 任务名 → detail

合并 → agents-state.json → Star Office UI
```

脚本位置：`~/starspace/bridge_notion.py`（已配置 cron `every 1m`）

---

## 故障排查

| 问题 | 原因 | 解法 |
|------|------|------|
| Agent 不出现 | 花名册里没有或 emoji 不对 | 确认格式 `🟢 名字（平台）— 描述` |
| 状态不更新 | 没写 `state:detail` 或格式不对 | 确认 `writing:描述` 用英文冒号 |
| 小人一直在休息区 | `state:detail` 没被桥解析到 | 检查名字是否和花名册完全一致 |
| 页面看不到变化 | 浏览器缓存 | 刷新 `http://127.0.0.1:19000` |
