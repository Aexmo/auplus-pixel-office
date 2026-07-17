#!/usr/bin/env python3
"""
Notion Agent Hub → Star Office UI 桥接脚本 v2
双源：花名册(全部Agent) + 任务池(活跃任务) → 像素办公室agents-state.json
"""
import json, os, sys, re
from datetime import datetime
from pathlib import Path

STAR_OFFICE_DIR = Path.home() / "starspace"
AGENTS_FILE = STAR_OFFICE_DIR / "agents-state.json"
STATE_FILE = STAR_OFFICE_DIR / "state.json"

NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
NOTION_VERSION = "2025-09-03"
TASK_POOL_DS = "35af1b70-ce7a-8189-9bda-000bf43b64f6"
MAIN_PAGE_ID = "35af1b70-ce7a-8138-995b-d1a842357b76"
BASE_URL = "https://api.notion.com/v1"

STATE_MAP = {
    "执行中": ("writing", "writing"),
    "待领取": ("idle", "breakroom"),
    "已完成": ("idle", "breakroom"),
    "失败": ("error", "error"),
}

def notion_request(endpoint, method="POST", body=None):
    import urllib.request
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {NOTION_API_KEY}")
    req.add_header("Notion-Version", NOTION_VERSION)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  ⚠️ API 错误: {e}", file=sys.stderr)
        return None

def fetch_roster():
    """从花名册拉全部Agent（主页面bullet list）"""
    if not NOTION_API_KEY:
        return []
    
    blocks = notion_request(f"/blocks/{MAIN_PAGE_ID}/children?page_size=50", method="GET")
    if not blocks:
        return []

    agents = []
    for b in blocks.get("results", []):
        if b.get("type") != "bulleted_list_item":
            continue
        text = "".join(
            rt.get("plain_text", "")
            for rt in b.get("bulleted_list_item", {}).get("rich_text", [])
        )
        # 解析花名册行: 🟢/🟡 <Agent名>（<平台>）— <职责> ｜ 最后活跃 <日期>
        status_emoji = ""
        if text.startswith("🟢"):
            status_emoji = "online"
        elif text.startswith("🟡"):
            status_emoji = "idle"
        elif text.startswith("🔴"):
            status_emoji = "offline"
        else:
            continue

        # Agent名: emoji之后、"（"之前
        rest = text[1:]  # 去掉emoji
        name_match = re.match(r"^\s*([^（]+)", rest)
        if not name_match:
            continue
        name = name_match.group(1).strip()

        # 跳过非Agent条目
        if any(kw in name.upper() for kw in ["AARON", "AUPLUS", "NOTION", "总控"]):
            continue

        # 提取平台
        platform = ""
        platform_match = re.search(r"（([^）]+)）", rest)
        if platform_match:
            platform = platform_match.group(1)

        # 去重：跳过花名册中的旧/重复条目
        if name.upper() == "HERMES" and platform.upper() == "HOME":
            continue

        # 提取职责
        role = ""
        role_match = re.search(r"—\s*(.+?)(?:｜|$)", rest)
        if role_match:
            role = role_match.group(1).strip()

        # 提取最后活跃
        last_active = ""
        active_match = re.search(r"最后活跃\s*(\S+)", rest)
        if active_match:
            last_active = active_match.group(1)

        agents.append({
            "name": name,
            "platform": platform,
            "role": role,
            "status_emoji": status_emoji,
            "last_active": last_active,
        })

    return agents

def fetch_task_pool_agents():
    """从任务池查各Agent执行中的任务"""
    if not NOTION_API_KEY:
        return {}

    result = notion_request(
        f"/data_sources/{TASK_POOL_DS}/query",
        body={"page_size": 50}
    )
    if not result or "results" not in result:
        return {}

    agents = {}
    for page in result.get("results", []):
        props = page.get("properties", {})

        # 指派Agent
        assignee = ""
        ap = props.get("指派Agent") or {}
        if ap.get("select"):
            assignee = ap["select"].get("name", "")

        # 状态
        status = ""
        sp = props.get("状态") or {}
        if sp.get("select"):
            status = sp["select"].get("name", "")

        # 任务名
        task = ""
        tp = props.get("任务名") or {}
        if tp.get("title"):
            task = "".join(t.get("plain_text", "") for t in tp["title"])

        if not assignee or assignee in ("待分配",):
            continue

        if assignee not in agents:
            agents[assignee] = {"active_tasks": [], "all_statuses": set()}
        if task:
            agents[assignee]["active_tasks"].append(f"[{status}] {task}")
        if status:
            agents[assignee]["all_statuses"].add(status)

    return agents

def merge_agents(roster, task_data):
    """合并花名册 + 任务池 → Star Office agent列表"""
    merged = {}

    for r in roster:
        name = r["name"]
        tid = name.lower().replace(" ", "-").replace("（", "").replace("）", "")

        # 基础状态从花名册emoji映射
        if r["status_emoji"] == "online":
            state, area = "idle", "breakroom"
        elif r["status_emoji"] == "idle":
            state, area = "idle", "breakroom"
        else:
            state, area = "idle", "breakroom"

        detail = r["role"][:80] if r["role"] else "在线"

        # 实时状态：花名册格式约定
        # "writing:正在做XXX" → state=writing, detail=正在做XXX
        # "error:管线挂了"     → state=error,   detail=管线挂了
        # 无冒号前缀           → 回退到默认行为
        live_state = None
        if r.get("role"):
            m = re.match(r"^(idle|writing|researching|executing|syncing|error)\s*[:：]\s*(.+)", r["role"])
            if m:
                live_state = m.group(1)
                detail = m.group(2)[:80]

        # 有活跃任务 → 覆盖状态（任务池优先级高于花名册实时状态）
        td = task_data.get(name)
        if td and td.get("active_tasks"):
            active = [t for t in td["active_tasks"] if "[执行中]" in t]
            if active:
                state, area = "writing", "writing"
                detail = active[0].replace("[执行中] ", "")[:80]
            elif live_state:
                # 有任务但非执行中 → 用花名册实时状态
                state, area = live_state, "breakroom" if live_state == "idle" else "writing"
            elif td.get("all_statuses"):
                state, area = "idle", "breakroom"
                detail = f"最近: {td['all_statuses'].pop()}"
        elif live_state:
            # 无任务但有实时状态 → 直接用
            state = live_state
            area = "breakroom" if live_state == "idle" else ("error" if live_state == "error" else "writing")

        merged[tid] = {
            "agentId": tid,
            "name": name,
            "isMain": False,
            "state": state,
            "detail": detail,
            "area": area,
            "source": "notion",
            "joinKey": None,
            "authStatus": "approved",
            "authExpiresAt": None,
        }

    return merged

def read_main_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"state": "idle", "detail": "待命中"}

def build_agents_json(guests):
    now = datetime.now().isoformat()
    ms = read_main_state()
    ms_area = STATE_MAP.get(ms.get("state", "idle"), ("idle", "breakroom"))[1]

    agents = [{
        "agentId": "star",
        "name": "Star",
        "isMain": True,
        "state": ms.get("state", "idle"),
        "detail": ms.get("detail", "待命中"),
        "updated_at": ms.get("updated_at", now),
        "area": ms_area,
        "source": "local",
        "joinKey": None,
        "authStatus": "approved",
        "authExpiresAt": None,
        "lastPushAt": now,
    }]

    for g in guests.values():
        g["updated_at"] = now
        g["lastPushAt"] = now
        agents.append(g)

    return agents

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Notion → Star Office 桥接 v2")

    # 1. 花名册
    roster = fetch_roster()
    print(f"  📋 花名册: {len(roster)} 个 Agent")
    for r in roster:
        print(f"     {r['status_emoji']} {r['name']} ({r['platform']})")

    # 容错：花名册拉空 = Notion API 失败（正常至少有 YIMU 在线）→ 保留上次状态，不覆盖清空
    if not roster:
        print("  ⚠️ 花名册为空（疑似 Notion API 失败），保留上次 agents-state.json，不覆盖。")
        return 0

    # 2. 任务池
    task_data = fetch_task_pool_agents()
    print(f"  📋 任务池有任务的 Agent: {len(task_data)}")

    # 3. 合并
    guests = merge_agents(roster, task_data)
    agents = build_agents_json(guests)

    print(f"  🎮 像素办公室 Agent 总数: {len(agents)}")
    for a in agents:
        print(f"     [{a['state']}] {a['name']}: {a['detail'][:60]}")

    AGENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(AGENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)

    print(f"  ✅ 已写入 {AGENTS_FILE}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
