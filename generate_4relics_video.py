"""
AI文物活化师 - 4类文物批量视频生成
书画 / 石雕玉雕 / 丝织品 / 简牍古籍
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import os
import time
import json

API_KEY = os.environ.get('DASHSCOPE_API_KEY')
if not API_KEY:
    print("❌ 请设置环境变量 DASHSCOPE_API_KEY")
    sys.exit(1)
BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

OUTPUT_DIR = "relic_4types_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# 4类文物的视频Prompt设计
# ============================================================

RELICS = [
    {
        "id": "painting",
        "name": "千里江山图",
        "type": "书画",
        "style": "古代复原风",
        "prompt": """Song dynasty Chinese handscroll painting 'A Thousand Li of Rivers and Mountains' comes to life, 
vibrant mineral pigments of malachite green and azurite blue shimmering on the silk surface, 
mountains and rivers in the scroll begin to breathe with morning mist rising between peaks, 
scholar figures appear walking along mountain paths in the painting, 
pine trees sway gently in the breeze, waterfalls begin to cascade, 
ancient Chinese ink painting aesthetic with rich color transformation, 
slow cinematic pan across the scroll, warm amber ambient lighting, 
period-accurate Northern Song dynasty landscape, 4K resolution""",
        "filename": "painting_qianli_jiangshan"
    },
    {
        "id": "jade",
        "name": "玉璧（战国）",
        "type": "石雕/玉雕",
        "style": "奇幻穿越风",
        "prompt": """Warring States period Chinese jade bi disc, nephrite jade with celadon green color and russet skin, 
dragon grain pattern on the surface, 
magical awakening sequence - the jade begins to glow with inner light, 
cloud-scroll patterns emerge from the surface in ethereal golden light, 
particles of jade-green and gold swirl around the ancient ritual object, 
time travel transformation effect, the jade transcends 2300 years, 
mystical atmosphere, supernatural light emanating from within, 
cinematic dramatic lighting, dark museum background with soft spotlight, 
4K resolution, smooth orbit camera movement""",
        "filename": "jade_bi_disc"
    },
    {
        "id": "silk",
        "name": "素纱禅衣（马王堆）",
        "type": "丝织品",
        "style": "粒子光效风",
        "prompt": """Han dynasty plain silk robe from Mawangdui, ultra-fine silk gauze weighing only 49 grams, 
the translucent fabric begins to shimmer and float in golden light, 
thousands of silk threads illuminate individually like luminous fibers, 
golden and silver particles dance around the ancient garment, 
the fabric unfolds gracefully in slow motion revealing its extraordinary thinness, 
light passes through the gossamer silk creating rainbow prismatic effects, 
ethereal glow transformation sequence, 
warm museum spotlight, 2000-year-old Han dynasty craftsmanship reawakening, 
particle light trail effects, cinematic 4K resolution""",
        "filename": "silk_mawangdui_robe"
    },
    {
        "id": "bamboo",
        "name": "睡虎地秦简",
        "type": "简牍",
        "style": "博物馆展示风",
        "prompt": """Qin dynasty bamboo slips from Shuihudi archaeological site, 
ancient legal texts written in precise small seal script with black lacquer ink, 
the bamboo strips arranged in neat rows on a clean museum display surface, 
soft rotating spotlight illuminating the ancient writing, 
ink characters begin to glow with subtle golden light as if freshly written, 
the 2200-year-old legal code coming alive before our eyes, 
slow cinematic close-up push from full arrangement to extreme close-up on individual characters, 
clean museum display style with dark velvet background, 
professional cultural heritage documentation, soft diffused lighting, 4K resolution""",
        "filename": "bamboo_shuihudi_slips"
    }
]

# ============================================================
# API调用函数
# ============================================================

def submit_video_task(prompt):
    """提交文生视频任务"""
    url = f"{BASE_URL}/services/aigc/video-generation/video-synthesis"
    headers = {**HEADERS, "X-DashScope-Async": "enable", "X-DashScope-OssResourceResolve": "enable"}
    payload = {
        "model": "wan2.7-t2v",
        "input": {"prompt": prompt},
        "parameters": {
            "resolution": "720P",
            "duration": 5,
            "prompt_extend": True,
            "watermark": False
        }
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    data = resp.json()
    if "output" in data and "task_id" in data["output"]:
        return data["output"]["task_id"]
    print(f"  [ERR] 提交失败: {data}")
    return None

def poll_video_task(task_id, max_wait=600):
    """轮询视频任务状态"""
    url = f"{BASE_URL}/tasks/{task_id}"
    start = time.time()
    while time.time() - start < max_wait:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        data = resp.json()
        status = data.get("output", {}).get("task_status", "UNKNOWN")
        if status == "SUCCEEDED":
            video_url = data["output"].get("video_url") or \
                        (data["output"].get("results") or [{}])[0].get("video_url")
            return video_url
        elif status == "FAILED":
            print(f"  [FAIL] 任务失败: {data.get('output', {}).get('message', '')}")
            return None
        elapsed = int(time.time() - start)
        print(f"  [{elapsed}s] 状态: {status}，等待中...")
        time.sleep(20)
    print(f"  [TIMEOUT] 超过{max_wait}秒未完成")
    return None

def download_file(url, filepath):
    """下载文件"""
    resp = requests.get(url, stream=True, timeout=60)
    downloaded = 0
    with open(filepath, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
    print(f"  已下载: {filepath} ({downloaded / 1024 / 1024:.1f} MB)")
    return filepath

# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 60)
    print("AI文物活化师 - 4类文物视频批量生成")
    print("=" * 60)

    results = {}

    for relic in RELICS:
        print(f"\n{'='*50}")
        print(f"[{relic['type']}] {relic['name']} - {relic['style']}")
        print(f"{'='*50}")

        print("  提交视频生成任务...")
        task_id = submit_video_task(relic["prompt"])

        if not task_id:
            results[relic["id"]] = {"status": "SUBMIT_FAIL"}
            continue

        print(f"  Task ID: {task_id}")
        results[relic["id"]] = {"task_id": task_id, "name": relic["name"], "type": relic["type"]}

        # 保存task_id以便后续轮询
        task_file = os.path.join(OUTPUT_DIR, f"{relic['filename']}_task.json")
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump({
                "task_id": task_id,
                "name": relic["name"],
                "type": relic["type"],
                "style": relic["style"],
                "filename": relic["filename"],
                "prompt": relic["prompt"],
                "submit_time": time.strftime("%Y-%m-%d %H:%M:%S")
            }, f, ensure_ascii=False, indent=2)
        print(f"  Task信息已保存: {task_file}")

    # 所有任务提交完，开始轮询
    print(f"\n{'='*50}")
    print("所有任务已提交，开始轮询结果...")
    print(f"{'='*50}")

    for relic in RELICS:
        rid = relic["id"]
        if "task_id" not in results.get(rid, {}):
            continue

        task_id = results[rid]["task_id"]
        print(f"\n[轮询] {relic['name']} ({relic['type']}) - {task_id[:8]}...")

        video_url = poll_video_task(task_id, max_wait=600)

        if video_url:
            filepath = os.path.join(OUTPUT_DIR, f"{relic['filename']}.mp4")
            download_file(video_url, filepath)
            results[rid]["video_path"] = filepath
            results[rid]["video_url"] = video_url
            results[rid]["status"] = "SUCCEEDED"

            # 更新task文件
            task_file = os.path.join(OUTPUT_DIR, f"{relic['filename']}_task.json")
            if os.path.exists(task_file):
                with open(task_file, "r", encoding="utf-8") as f:
                    task_data = json.load(f)
                task_data["status"] = "SUCCEEDED"
                task_data["video_url"] = video_url
                task_data["complete_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
                with open(task_file, "w", encoding="utf-8") as f:
                    json.dump(task_data, f, ensure_ascii=False, indent=2)
        else:
            results[rid]["status"] = "FAILED"

    # 汇总报告
    print(f"\n{'='*60}")
    print(">> 生成结果汇总")
    print(f"{'='*60}")
    for relic in RELICS:
        rid = relic["id"]
        r = results.get(rid, {})
        status = r.get("status", "UNKNOWN")
        if status == "SUCCEEDED":
            print(f"  [OK]   [{relic['type']}] {relic['name']} -> {r.get('video_path', '')}")
        else:
            print(f"  [FAIL] [{relic['type']}] {relic['name']} -> {status}")

    print(f"\n  输出目录: {os.path.abspath(OUTPUT_DIR)}/")
    return results

if __name__ == "__main__":
    main()
