#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过 lark-cli 分步更新飞书文档"""

import subprocess
import sys
import os
import tempfile

DOC_URL = "https://ocnkfj109ow1.feishu.cn/wiki/B3DswdhMqitIZokYGZRcsSx8nWd"

def run_update(mode, markdown, selection=None, selection_type="ellipsis", extra_args=None):
    """执行 lark-cli docs +update 命令"""
    # 写入临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(markdown)
        tmp_path = f.name
    
    try:
        cmd = ["lark-cli", "docs", "+update", "--doc", DOC_URL, "--mode", mode, "--markdown", f"@{tmp_path}"]
        if selection:
            if selection_type == "ellipsis":
                cmd += ["--selection-with-ellipsis", selection]
            elif selection_type == "title":
                cmd += ["--selection-by-title", selection]
        if extra_args:
            cmd += extra_args
        
        print(f"\n[CMD] mode={mode}, selection={selection[:30] if selection else 'none'}...")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        output = result.stdout + result.stderr
        # 过滤 CLIXML
        lines = [l for l in output.splitlines() if not l.startswith("#<") and "CLIXML" not in l and "PSCustomObject" not in l and "progress" not in l]
        clean = "\n".join(lines).strip()
        print(f"[RESULT] {clean[:500]}")
        return result.returncode == 0, clean
    finally:
        os.unlink(tmp_path)


def main():
    # ============================================================
    # 步骤1: 在「先看效果再说」章节末尾、在线观看链接之前追加4条新视频记录
    # ============================================================
    step1_md = """
<callout emoji="scroll" background-color="light-green">

**北宋千里江山图 · 古代复原风**

- **模型**：wan2.7-t2v
- **分辨率**：720P / 16:9
- **时长**：5秒
- **文物类型**：书画
- **Task ID**：27773483-d92b-403a-8690-a84f430f860c

**效果描述：** 矿物颜料在绢面上苏醒流动，石青石绿的山水开始「呼吸」——晨雾在山峰间升腾，文人沿山路行走，瀑布开始倾泻。王希孟十八岁的才情，在AI里重走一遍。
</callout>

<callout emoji="gem" background-color="light-purple">

**战国玉璧 · 奇幻穿越风**

- **模型**：wan2.7-t2v
- **分辨率**：720P / 16:9
- **时长**：5秒
- **文物类型**：石雕/玉雕
- **Task ID**：3a6e3104-b5c8-419f-b72a-b3008f65a2fa

**效果描述：** 和田玉内部光芒透出，龙纹卷云纹饰如同活了一般浮动。玉绿与金色粒子旋绕，这枚2300年前的礼器，在光效中完成了一次时空穿越。
</callout>

<callout emoji="sparkles" background-color="light-yellow">

**马王堆素纱禅衣 · 粒子光效风**

- **模型**：wan2.7-t2v
- **分辨率**：720P / 16:9
- **时长**：5秒
- **文物类型**：丝织品
- **Task ID**：dc76bdc7-a6ff-4bce-9e2d-6ccb2b65d61f

**效果描述：** 仅重49克的汉代蚕丝开始发光——每一根丝线独立闪烁，金银粒子在飘动的轻纱间流转，光线穿过薄如蝉翼的织物折射出彩虹色。2000年前的织造技艺，以光的语言重新讲述。
</callout>

<callout emoji="page_facing_up" background-color="light-gray">

**睡虎地秦简 · 博物馆展示风**

- **模型**：wan2.7-t2v
- **分辨率**：720P / 16:9
- **时长**：5秒
- **文物类型**：简牍
- **Task ID**：6b223c4d-4fc9-489f-8363-23d63b10f6bf

**效果描述：** 整齐排列的竹简在旋转聚光灯下，墨迹随光线泛起微微金光——仿佛2200年前的法律文书刚刚写就。镜头从全貌缓缓推近至单根竹简字迹特写，极简博物馆风格。
</callout>
"""
    ok, msg = run_update("insert_before", step1_md, "**在线观看：**", "ellipsis")
    print(f"步骤1 {'✅ 成功' if ok else '❌ 失败'}: {msg[:200]}")

    # ============================================================
    # 步骤2: 在「踩过的坑」章节末尾（坑4之后）追加成本对比说明
    # ============================================================
    step2_md = """

---

## 真实成本到底怎么算？（API 价格拆解）

很多朋友问我：**「¥5000→¥5」这个成本怎么算出来的？**

这里把账算清楚：

| 调用类型 | 模型 | 规格 | 阿里云单价 | 单次成本 |
|---------|------|------|-----------|---------|
| 文生视频（纯文字输入） | wan2.7-t2v | 5秒/720P | ¥0.2/秒 | **≈¥1** |
| 图生视频（照片输入） | wan2.7-i2v | 5秒/720P | ¥0.2/秒 | **≈¥1** |
| 图生图（风格预处理） | wanx-v1 | 1024×1024 | ¥0.04/张 | **≈¥0.04** |
| **全流程合计** | — | — | — | **¥1-5/条** |

> 以上为阿里云百炼平台官方定价（2026年4月）。批量调用可享折扣。

**全年预算估算：**

- 1000条视频/年 ≈ **¥1,000-5,000**
- 传统摄制团队1条视频 ≈ ¥5,000-50,000

**节省比例：95%-99%。**
"""
    ok2, msg2 = run_update("insert_after", step2_md, "粒子效果容易过度...程度最好看。", "ellipsis")
    print(f"步骤2 {'✅ 成功' if ok2 else '❌ 失败'}: {msg2[:200]}")

    # ============================================================
    # 步骤3: 在文档末尾追加「历史准确性校验」专题章节
    # ============================================================
    step3_md = """

---

## 评审建议 · 历史准确性怎么保障？

> 这是 WaytoAGI 评委专门提出的问题，确实是个好问题，这里认真回答。

万相2.7是视频生成模型，**不是文物知识模型**。你告诉它「商代青铜鼎」，它能生成好看的青铜鼎视频，但它不保证纹饰是商代的、颜色是对的。

所以我在三层Prompt架构之上，额外加了一层**朝代/纹饰白名单校验**：

**校验流程：**

```
输入文物信息
     ↓
三层Prompt引擎 → 生成初版Prompt
     ↓
朝代/纹饰白名单校验
     ↓
发现跨朝代纹饰? → [是] → 人工复核 or 自动修正
     ↓
[否] → 提交万相生成视频
```

**典型白名单示例：**

| 朝代 | 允许纹饰 | 标准色系 |
|-----|---------|---------|
| 商 | 饕餮纹、云雷纹、蝉纹、夔纹 | 青铜绿、朱砂红 |
| 周 | 窃曲纹、重环纹、蟠螭纹 | 青铜绿、黑漆 |
| 秦 | 几何纹（简洁）| 朱砂红、石青、石绿 |
| 宋 | 折枝花卉、莲花纹 | 天青色、月白色（汝窑） |
| 唐 | 宝相花纹、联珠纹 | 唐三彩（黄绿褐）|

**博物馆级使用建议：** 开启人工复核流程，由文博专业人员对生成视频的历史准确性进行最终确认，AI负责效率，人负责准确性。
"""
    ok3, msg3 = run_update("append", step3_md)
    print(f"步骤3 {'✅ 成功' if ok3 else '❌ 失败'}: {msg3[:200]}")

    print("\n\n=== 更新完成 ===")
    print(f"步骤1（4类视频）: {'✅' if ok else '❌'}")
    print(f"步骤2（成本拆解）: {'✅' if ok2 else '❌'}")
    print(f"步骤3（历史校验）: {'✅' if ok3 else '❌'}")


if __name__ == "__main__":
    main()
