"""
AI文物活化师 - 云冈石窟第十二窟音乐窟视频生成
风格: 古代复原风 (Historical Restoration)
参考: 图片中的伎乐天手持乐器、多层佛龛、赭红底色、金色光环
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

OUTPUT_DIR = "yungang_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 云冈石窟第十二窟音乐窟 - 基于图片细节
PROMPT = """Northern Wei dynasty Yungang Grottoes Cave 12 "Music Cave" interior wall, 
multiple tiers of arched niches containing celestial musician figures (feitian), 
each figure holding ancient Chinese musical instruments - pipa lute, horizontal flute, panpipes, drums, 
the stone carvings transform from weathered grey-brown to reveal original vivid Northern Wei dynasty painted colors, 
vermillion red background with golden halos behind each figure's head, 
lapis lazuli blue and malachite green flowing robes, 
angelic feitian figures begin to sway gently as if dancing to music, 
their scarves and ribbons float in ethereal motion, 
musical instruments emit subtle golden light particles, 
slow cinematic pan across the multi-tiered wall of musicians, 
warm amber lighting illuminating the cave interior, 
historical restoration of 5th century Buddhist art splendor, 
epic documentary style, 4K resolution"""

FILENAME = "yungang_cave12_musicians_historical"

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

def main():
    print("=" * 60)
    print("AI文物活化师 - 云冈石窟第十二窟音乐窟视频生成")
    print("风格: 古代复原风")
    print("=" * 60)

    # 提交任务
    print("\n提交视频生成任务...")
    task_id = submit_video_task(PROMPT)

    if not task_id:
        print("[FAIL] 任务提交失败，请检查 API Key")
        return

    print(f"  Task ID: {task_id}")

    # 保存task信息
    task_file = os.path.join(OUTPUT_DIR, f"{FILENAME}_task.json")
    with open(task_file, "w", encoding="utf-8") as f:
        json.dump({
            "task_id": task_id,
            "name": "云冈石窟第十二窟音乐窟",
            "type": "石窟",
            "style": "古代复原风",
            "filename": FILENAME,
            "prompt": PROMPT,
            "submit_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }, f, ensure_ascii=False, indent=2)

    # 轮询等待
    print(f"\n等待视频生成（预计5-10分钟）...")
    video_url = poll_video_task(task_id, max_wait=600)

    if video_url:
        filepath = os.path.join(OUTPUT_DIR, f"{FILENAME}.mp4")
        download_file(video_url, filepath)
        print(f"\n[SUCCESS] 视频生成完成: {filepath}")

        # 更新task文件
        with open(task_file, "r", encoding="utf-8") as f:
            task_data = json.load(f)
        task_data["status"] = "SUCCEEDED"
        task_data["video_url"] = video_url
        task_data["complete_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(task_data, f, ensure_ascii=False, indent=2)
    else:
        print("\n[FAIL] 视频生成失败")

if __name__ == "__main__":
    main()
