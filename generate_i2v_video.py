#!/usr/bin/env python3
"""
AI文物活化师 - I2V图生视频生成
基于真实文物照片生成活化视频，确保文物本体高保真
"""

import os
import sys
import io
import time
import json
import base64
import requests
from datetime import datetime

# 修复编码
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
OUTPUT_DIR = "i2v_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def image_to_base64(image_path):
    """将本地图片转为Base64编码"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    # 检测图片格式
    ext = os.path.splitext(image_path)[1].lower()
    mime_type = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp'
    }.get(ext, 'image/jpeg')
    
    base64_data = base64.b64encode(image_data).decode('utf-8')
    return f"data:{mime_type};base64,{base64_data}"


def submit_i2v_task(img_url, prompt):
    """提交I2V图生视频任务"""
    url = f"{BASE_URL}/services/aigc/video-generation/video-synthesis"
    payload = {
        "model": "wanx2.1-i2v-turbo",
        "input": {
            "img_url": img_url,
            "prompt": prompt
        },
        "parameters": {
            "resolution": "720P",
            "duration": 5,
            "prompt_extend": False  # 关闭智能改写，保持prompt精准控制
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


def download_video(video_url, filepath):
    """下载视频"""
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    return False


def generate_i2v_video(image_path, name, prompt, filename):
    """生成I2V视频"""
    print(f"\n{'='*60}")
    print(f"🎬 I2V图生视频: {name}")
    print(f"{'='*60}")
    
    # 图片转Base64
    print(f"📷 加载图片: {image_path}")
    img_url = image_to_base64(image_path)
    print(f"✅ Base64编码完成 ({len(img_url)//1024}KB)")
    
    # 提交任务
    print(f"📤 提交I2V任务...")
    task_id = submit_i2v_task(img_url, prompt)
    if not task_id:
        print(f"❌ 提交失败")
        return False
    
    print(f"✅ Task ID: {task_id}")
    
    # 轮询等待
    max_wait = 600
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
                filepath = os.path.join(OUTPUT_DIR, f"{filename}.mp4")
                print(f"📥 下载视频...")
                if download_video(video_url, filepath):
                    print(f"✅ 已保存: {filepath}")
                    # 保存task_id
                    with open(os.path.join(OUTPUT_DIR, f"{filename}_task.txt"), 'w') as f:
                        f.write(task_id)
                    return True
            else:
                print(f"⚠️ 无视频URL")
            break
        elif status in ["FAILED", "CANCELLED"]:
            print(f"❌ 任务失败: {status}")
            break
    
    return False


def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python generate_i2v_video.py <图片路径>")
        print("示例: python generate_i2v_video.py ./niaozun.jpg")
        return
    
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"❌ 图片不存在: {image_path}")
        return
    
    # 晋侯鸟尊 I2V 配置 - V1原版prompt + I2V高保真
    # 用I2V模式保证文物本体还原，prompt完全还原V1的旋转+粒子+内部微光
    prompt = "Golden luminous particles slowly rise from the bronze surface, swirling around the phoenix vessel. Museum spotlight rotates gently, casting dramatic shadows. Warm golden glow emanates from within, the bronze surface subtly shifts in the light. Fantasy cinematic atmosphere, 4K quality."

    success = generate_i2v_video(
        image_path=image_path,
        name="晋侯鸟尊 (I2V V1原版)",
        prompt=prompt,
        filename="niaozun_i2v_v1_goldglow"
    )
    
    print(f"\n{'='*60}")
    print("📊 生成结果")
    print(f"{'='*60}")
    print(f"{'✅ 成功' if success else '❌ 失败'} | 晋侯鸟尊 I2V图生视频")


if __name__ == "__main__":
    main()
