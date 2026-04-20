#!/usr/bin/env python3
"""
山西博物院文物活化视频生成
- 晋侯鸟尊：奇幻穿越风
"""

import os
import time
import json
import requests
from datetime import datetime

# 修复编码
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# API配置
API_KEY = os.environ.get('DASHSCOPE_API_KEY')
if not API_KEY:
    print("❌ 请设置环境变量 DASHSCOPE_API_KEY")
    sys.exit(1)
BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "X-DashScope-Async": "enable",
    "X-DashScope-OssResourceResolve": "enable"
}

# 输出目录
OUTPUT_DIR = "shanxi_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 文物配置：后母戊鼎 - 奇幻穿越风
RELICS = [
    {
        "name": "后母戊鼎",
        "filename": "simuwu_ding_fantasy",
        "prompt": "The legendary Houmuwu Ding, the largest and heaviest ancient bronze vessel in the world weighing 832 kg, from the late Shang dynasty circa 1200 BC. The massive rectangular cauldron sits on four sturdy legs with two prominent upright handles (er), covered in intricate taotie mask motifs and thunder patterns. Green patina on the bronze surface gradually transforms into brilliant golden luster, revealing the exquisite cast decorations. Magical golden particles swirl upward from the vessel, ethereal glow emanates from within. The ancient ritual vessel slowly rotates, three-thousand-year slumber awakening, fantasy cinematic lighting, dramatic museum spotlight, 4K resolution, highly detailed bronze texture",
        "style": "fantasy"
    }
]

def submit_task(prompt):
    """提交视频生成任务"""
    url = f"{BASE_URL}/services/aigc/video-generation/video-synthesis"
    payload = {
        "model": "wanx2.1-t2v-turbo",
        "input": {
            "prompt": prompt
        },
        "parameters": {
            "size": "1280*720"
        }
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    print(f"HTTP {response.status_code}: {response.text[:500]}")
    if response.status_code == 200:
        result = response.json()
        if "output" in result and "task_id" in result["output"]:
            return result["output"]["task_id"]
    return None

def check_task(task_id):
    """检查任务状态"""
    url = f"{BASE_URL}/tasks/{task_id}"
    
    response = requests.get(url, headers={"Authorization": f"Bearer {API_KEY}"})
    if response.status_code == 200:
        return response.json()
    return None

def download_video(url, filepath):
    """下载视频"""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    return False

def generate_relic_video(relic):
    """生成单个文物视频"""
    print(f"\n{'='*60}")
    print(f"🎬 开始生成: {relic['name']} ({relic['style']})")
    print(f"{'='*60}")
    
    # 提交任务
    print(f"📤 提交任务...")
    task_id = submit_task(relic['prompt'])
    if not task_id:
        print(f"❌ 提交失败")
        return False
    
    print(f"✅ Task ID: {task_id}")
    
    # 轮询等待
    max_wait = 600  # 10分钟
    interval = 15
    elapsed = 0
    
    while elapsed < max_wait:
        time.sleep(interval)
        elapsed += interval
        
        result = check_task(task_id)
        if not result:
            continue
        
        status = result.get("output", {}).get("task_status", "UNKNOWN")
        print(f"⏳ {elapsed}s | 状态: {status}")
        
        if status == "SUCCEEDED":
            output = result.get("output", {})
            video_url = output.get("video_url") or \
                        (output.get("results") or [{}])[0].get("video_url")
            if video_url:
                filepath = os.path.join(OUTPUT_DIR, f"{relic['filename']}.mp4")
                print(f"📥 下载视频...")
                if download_video(video_url, filepath):
                    print(f"✅ 已保存: {filepath}")
                    # 保存task_id
                    with open(os.path.join(OUTPUT_DIR, f"{relic['filename']}_task.txt"), 'w') as f:
                        f.write(task_id)
                    return True
            else:
                print(f"⚠️ 无视频URL，返回数据: {json.dumps(output, ensure_ascii=False)[:500]}")
            break
        elif status in ["FAILED", "CANCELLED"]:
            print(f"❌ 任务失败: {status}")
            break
    
    return False

def main():
    print("="*60)
    print("🏛️ 山西博物院文物活化视频生成")
    print("="*60)
    
    results = []
    for relic in RELICS:
        success = generate_relic_video(relic)
        results.append({
            "name": relic['name'],
            "style": relic['style'],
            "success": success
        })
    
    # 生成报告
    print(f"\n{'='*60}")
    print("📊 生成报告")
    print(f"{'='*60}")
    for r in results:
        status = "✅ 成功" if r['success'] else "❌ 失败"
        print(f"{status} | {r['name']} ({r['style']})")
    
    # 保存完整报告
    report = {
        "generated_at": datetime.now().isoformat(),
        "results": results
    }
    with open(os.path.join(OUTPUT_DIR, "report.json"), 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 报告已保存: {OUTPUT_DIR}/report.json")

if __name__ == "__main__":
    main()
