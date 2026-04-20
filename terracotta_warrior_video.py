"""
兵马俑彩绘重现视频生成
流程：文生图(素材) => 文生视频(彩绘重现动画)
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

# ============================================================
# 兵马俑彩绘重现 - Prompt设计
# ============================================================
# 运镜：缓慢推近（从全身→面部特写），配合奇幻穿越风
# 核心：灰色陶俑 → 彩绘浮现 → 2200年前真实色彩

IMAGE_PROMPT = """A close-up portrait of a Qin Dynasty terracotta warrior, 
the warrior's face and armor gradually revealing vivid ancient paint colors - 
pink flesh tone on the face, black hair with red headband, 
purple-red tunic with blue sleeve edges, emerald green armor with vermilion red straps and white rivets, 
transformation from gray clay to fully painted state, 
magical golden dust particles floating in the air, 
ethereal iridescent light emanating from the painted surfaces, 
ancient Chinese craftsmanship, cinematic dramatic lighting, 
dark museum background with soft warm spotlight, 
hyper-realistic, 8K resolution, historically accurate Qin dynasty colors"""

VIDEO_PROMPT = """Slowly zoom in from medium shot to extreme close-up on a Qin Dynasty terracotta warrior's face. 
The gray clay surface gradually transforms as ancient vivid paint colors materialize and flow across the warrior's features - 
pink flesh tone appearing on the cheeks, black hair with a red headband, 
vermilion red lips, dark intense eyes coming alive. 
The transformation spreads from the face down to the elaborate armor - 
purple-red tunic, emerald green armor plates, bright blue sleeve edges, 
white rivets and crimson red straps revealing themselves. 
Golden shimmering particles swirl around the warrior as the 2200-year-old colors awaken. 
Ethereal iridescent glow emanating from the newly revealed painted surfaces, 
magical atmosphere of ancient colors reborn, 
cinematic dramatic lighting, dark museum background with warm spotlight, 
professional cultural heritage photography, 4K resolution"""

NEGATIVE_PROMPT = """blurry, low quality, deformed face, extra limbs, 
modern clothing, cartoon, anime, illustration, 
text, watermark, logo, signature"""

def submit_text2image(prompt, negative_prompt="", size="1024*1024", n=1):
    """提交文生图任务"""
    url = f"{BASE_URL}/services/aigc/text2image/image-synthesis"
    headers = {**HEADERS, "X-DashScope-Async": "enable"}
    
    payload = {
        "model": "wanx-v1",
        "input": {
            "prompt": prompt,
        },
        "parameters": {
            "style": "<auto>",
            "size": size,
            "n": n,
        }
    }
    if negative_prompt:
        payload["input"]["negative_prompt"] = negative_prompt
    
    resp = requests.post(url, headers=headers, json=payload)
    result = resp.json()
    
    if "output" in result and "task_id" in result["output"]:
        return result["output"]["task_id"]
    else:
        print(f"[ERROR] 文生图提交失败: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return None

def submit_text2video(prompt, resolution="720P", duration=5):
    """提交文生视频任务"""
    url = f"{BASE_URL}/services/aigc/video-generation/video-synthesis"
    headers = {**HEADERS, "X-DashScope-Async": "enable", "X-DashScope-OssResourceResolve": "enable"}
    
    payload = {
        "model": "wan2.7-t2v",
        "input": {
            "prompt": prompt,
        },
        "parameters": {
            "resolution": resolution,
            "duration": duration,
            "prompt_extend": True,
            "watermark": False,
        }
    }
    
    resp = requests.post(url, headers=headers, json=payload)
    result = resp.json()
    
    if "output" in result and "task_id" in result["output"]:
        return result["output"]["task_id"]
    else:
        print(f"[ERROR] 文生视频提交失败: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return None

def poll_task(task_id, interval=10, max_wait=300):
    """轮询任务状态"""
    url = f"{BASE_URL}/tasks/{task_id}"
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        resp = requests.get(url, headers={"Authorization": f"Bearer {API_KEY}"})
        result = resp.json()
        
        status = result.get("output", {}).get("task_status", "UNKNOWN")
        print(f"  状态: {status} (已等待 {int(time.time() - start_time)}秒)")
        
        if status == "SUCCEEDED":
            return result["output"]
        elif status in ["FAILED", "CANCELED", "UNKNOWN"]:
            print(f"[ERROR] 任务失败: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return None
        
        time.sleep(interval)
    
    print(f"[TIMEOUT] 任务超时 ({max_wait}秒)")
    return None

def download_file(url, filepath):
    """下载文件"""
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    downloaded = 0
    with open(filepath, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
    print(f"  已下载: {filepath} ({downloaded / 1024:.1f} KB)")

def main():
    print("=" * 60)
    print(">> 兵马俑彩绘重现视频生成")
    print("=" * 60)
    
    output_dir = os.path.join(os.path.dirname(__file__), "terracotta_output")
    os.makedirs(output_dir, exist_ok=True)
    
    # ============ Step 1: 文生图 ============
    print("\n[Step 1] 生成兵马俑彩绘素材图...")
    img_task_id = submit_text2image(IMAGE_PROMPT, NEGATIVE_PROMPT, size="1024*1024", n=1)
    
    if not img_task_id:
        print("[FAILED] 文生图任务创建失败，跳过。直接进入文生视频。")
        image_url = None
    else:
        print(f"  任务ID: {img_task_id}")
        print("  等待生成中（通常1-2分钟）...")
        img_result = poll_task(img_task_id, interval=10, max_wait=180)
        
        image_url = None
        if img_result and "results" in img_result:
            image_url = img_result["results"][0].get("url")
            print(f"  [OK] 图片生成成功!")
            
            # 下载图片
            img_path = os.path.join(output_dir, "terracotta_warrior_painted.png")
            download_file(image_url, img_path)
            print(f"  图片已保存: {img_path}")
        else:
            print("  [WARN] 图片生成失败，继续使用文生视频。")
    
    # ============ Step 2: 文生视频 ============
    print("\n[Step 2] 生成兵马俑彩绘重现视频...")
    video_task_id = submit_text2video(VIDEO_PROMPT, resolution="720P", duration=5)
    
    if not video_task_id:
        print("[FAILED] 文生视频任务创建失败!")
        return
    
    print(f"  任务ID: {video_task_id}")
    print("  等待生成中（通常1-3分钟）...")
    video_result = poll_task(video_task_id, interval=15, max_wait=300)
    
    if video_result and "video_url" in video_result:
        video_url = video_result["video_url"]
        print(f"  [OK] 视频生成成功!")
        
        # 下载视频
        video_path = os.path.join(output_dir, "terracotta_color_revival.mp4")
        download_file(video_url, video_path)
        print(f"  视频已保存: {video_path}")
    else:
        print("  [FAIL] 视频生成失败!")
    
    # ============ 总结 ============
    print("\n" + "=" * 60)
    print(">> 生成结果汇总")
    print("=" * 60)
    if image_url:
        print(f"  图片: OK {img_path}")
    else:
        print(f"  图片: FAIL 生成失败")
    
    if 'video_path' in dir() and os.path.exists(video_path):
        print(f"  视频: OK {video_path}")
    else:
        print(f"  视频: FAIL 生成失败")
    
    print(f"\n  输出目录: {output_dir}")
    print("完成！")

if __name__ == "__main__":
    main()
