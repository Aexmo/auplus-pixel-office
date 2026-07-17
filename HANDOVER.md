# 像素办公室项目 · 交接文档

> 接任者：YIMU 大内总管（Claude Code）  
> 交付人：Hermes  
> 日期：2026-07-17

---

## 一、项目概述

像素风 AI Agent 办公室看板，实时显示 Notion 协同中心各 Agent 的工作状态。

- **源码**：`~/starspace/`（本机）→ 待推 GitHub
- **运行地址**：`http://192.168.0.109:19000`（局域网）/ `http://127.0.0.1:19000`
- **技术栈**：Flask 后端 + Phaser 3.80 前端（Canvas 渲染）
- **接入方式**：Agent 更新 Notion 花名册 → `bridge_notion.py`(每1分钟cron) → `agents-state.json` → 办公室渲染

---

## 二、文件结构

```
~/starspace/
├── backend/
│   └── app.py              # Flask 后端 (2103行，端口19000)
├── frontend/
│   ├── index.html          # 主页面 + 内联CSS/JS (4889行)
│   ├── game.js             # Phaser 游戏主逻辑 (1022行)
│   └── layout.js           # 布局/坐标/家具配置 (133行)
├── bridge_notion.py        # Notion→办公室桥接脚本 v2
├── set_state.py            # 主Agent状态推送
├── set_state_py3.sh        # 快捷shell封装
├── state.json              # 主Agent当前状态
├── agents-state.json       # 全部Agent状态（桥接写入）
├── AGENT_ONBOARDING.md     # Agent接入指南
├── join-keys.json          # Join key配置（未启用）
└── bridge_notion_run.sh    # Cron调用的桥接脚本
```

---

## 三、已做的改动（相对上游 Star-Office-UI）

| 文件 | 改动 | 原因 |
|------|------|------|
| `frontend/index.html` | 1280→1600, 720→900 容器CSS | 办公室视觉放大25% |
| `frontend/game.js` | AREA_POSITIONS 8→12 slots/区 | 容纳更多Agent |
| `bridge_notion.py` | **新增**花名册 `state:detail` 解析 | Agent实时状态 |
| `bridge_notion.py` | **新增**任务池+花名册双源合并 | 全面Agent覆盖 |
| `set_state_py3.sh` | **新增** | Hermes快捷状态推送 |
| `AGENT_ONBOARDING.md` | **新增** | 其他Agent接入指南 |

---

## 四、运行方式

### 启动
```bash
cd ~/starspace/backend
~/.hermes/hermes-agent/venv/bin/python3 app.py &
```

### Cron 桥接
```
job: notion-star-office-bridge (a7a9d0fa119f)
schedule: every 1m
script: bridge_notion_run.sh → source credentials → bridge_notion.py
deliver: local (不通知)
```

### Hermes 手动切状态
```bash
bash ~/starspace/set_state_py3.sh writing "正在做XXX"
```

---

## 五、Notion API 凭证

```
NOTION_API_KEY: ntn_6488… (完整见 ~/.hermes/credentials/notion_agent_hub)
NOTION_VERSION: 2025-09-03
任务池 DS:    35af1b70-ce7a-8189-9bda-000bf43b64f6
花名册页面:    35af1b70-ce7a-8138-995b-d1a842357b76
```

---

## 六、桥接读取逻辑（bridge_notion.py）

```
优先级:
1. 任务池「执行中」任务 → state=writing（最高）
2. 花名册 state:detail  → 用花名册实时状态
3. 花名册 emoji 只有🟢/🟡  → state=idle（兜底）

state值: idle / writing / researching / executing / syncing / error
```

---

## 七、待办 / 改进方向

1. **办公室扩容**：目前 1600×900 CSS 等比放大，内部仍是 1280×720。可考虑真正扩大内部分辨率+重绘背景
2. **Agent气泡**：当前气泡显示随机预置文案，不是 state.json 的 detail。可改为显示实际 detail
3. **主角色名字标签**：Star 没有名字标签，只有访客有
4. **Notion→桥延迟**：cron 最小粒度 1 分钟，想更快需换方案
5. **错误处理**：Notion API 挂了时 agents-state.json 不变，办公室静止
6. **文倩/陈白露实时状态**：目前只有 emoji 粗状态，需她们也按 `state:detail` 格式更新花名册

---

## 八、工作方式建议

1. 你 clone/pull 这个 repo 到你的 Vultr 服务器
2. 改完代码 → 推 GitHub
3. Hermes 这边 `git pull && 重启后端` 就生效
4. 需要我帮忙做的事：在 Hermes Chat 里告诉我，我来操作本机

---

## 九、GitHub 仓库

（由 Hermes 创建并推送后填入）
