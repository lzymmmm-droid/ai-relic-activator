# 手把手教你做一个AI文物活化师 | 万相2.7 + WorkBuddy全流程教程

> 从零开始，一步步带你搭建一个「文物照片→动态视频」的AI智能体Skill。不需要编程基础，跟着做就行。

---

## 写在前面

大家好，我是振一，一个专注文博AI的创业者。

上周参加WaytoAGI「万相妙思+」快闪赛，做了一个叫**AI文物活化师**的Skill——上传一张青铜器的照片，AI自动生成一段金光闪闪的活化视频。

发到群里后好多人问怎么做的，今天就把完整流程拆开讲一遍，手把手教你复现。

**最终效果：**
- 🌐 在线Demo：https://lzymmmm-droid.github.io/ai-relic-activator/demo.html
- 📦 GitHub仓库：https://github.com/lzymmmm-droid/ai-relic-activator

---

## 一、先说为什么做这个

去过博物馆的人都有这个感受——

玻璃柜里放着一件三千年前的青铜鼎，旁边的说明牌写着："商代后母戊鼎，重832.84千克，世界最大最重的青铜器。"

然后呢？

**然后就没有然后了。** 你看着一块长了绿锈的金属疙瘩，很难产生什么情感共鸣。

但如果你看到这样的画面——

> 绿锈从青铜鼎表面缓缓褪去，露出三千年前的金色光泽。金色粒子在鼎身周围旋转飞舞，博物馆的聚光灯缓缓亮起，仿佛这件器物从三千年的沉睡中醒来……

**这就是"文物活化"。** 不是让图片"动一下"，而是用AI讲一个关于文化的故事。

---

## 二、技术栈一览

别被技术名词吓到，我会一步步讲清楚。

```
┌─────────────────────────────────────────────────┐
│                 AI文物活化师                      │
├─────────────────────────────────────────────────┤
│                                                 │
│  AI模型层：通义万相 Wan 2.7（阿里云百炼）         │
│  ├── wan2.7-t2v  文生视频（核心）               │
│  ├── wan2.7-i2v  图生视频                      │
│  └── wan2.7-i2i  图生图                        │
│                                                 │
│  智能体层：WorkBuddy Skill                       │
│  ├── 文物类型自动识别                            │
│  ├── Prompt智能生成                              │
│  └── 5大风格预设切换                             │
│                                                 │
│  展示层：GitHub Pages                            │
│  └── demo.html 响应式展示页面                    │
│                                                 │
└─────────────────────────────────────────────────┘
```

**你需要准备的：**
1. ✅ 阿里云百炼账号（注册就有免费额度）
2. ✅ 一个能写代码的AI助手（我用的是WorkBuddy）
3. ✅ GitHub账号（用来部署展示页面）

**不需要的：**
- ❌ 不需要GPU
- ❌ 不需要本地安装模型
- ❌ 不需要会写Python（AI帮你写）

---

## 三、Step 1：开通万相2.7 API

这是最简单的一步，5分钟搞定。

### 3.1 注册阿里云百炼

1. 打开 https://bailian.console.aliyun.com/
2. 用支付宝/淘宝账号登录
3. 进入「模型广场」→ 搜索「万相」

### 3.2 获取API Key

1. 点击「API-KEY管理」→ 创建API Key
2. 把Key保存到安全的地方（只显示一次！）
3. 记下你的**用户ID**（后面验证要用）

### 3.3 万相2.7的三大能力

万相2.7是阿里通义实验室的视频生成模型，有三个核心能力：

| 模型 | 能力 | 我们的用法 |
|------|------|-----------|
| **wan2.7-t2v** | 文字→视频 | 输入文物的文字描述→生成活化视频 |
| **wan2.7-i2v** | 图片→视频 | 输入文物照片→生成活化视频 |
| **wan2.7-i2i** | 图片→图片 | 文物风格转换/色彩修复 |

**本次教程主要用 wan2.7-t2v**，因为文生视频最直接，不需要准备素材图片。

---

## 四、Step 2：设计5大活化风格

这是整个Skill的核心创意。不是简单调个参数，而是针对不同场景设计了5套完整的视觉风格。

### 🎬 风格1：纪录片风

**适合：** 博物馆展厅、纪录片配图、官方宣传

**视觉特征：** 专业拍摄感、博物馆灯光、慢镜头、浅景深

**Prompt模板：**
```
{文物名称}, {朝代} dynasty {文物类型},
cinematic documentary style, slow motion, museum spotlight,
shallow depth of field, warm ambient light,
professional cultural heritage photography, 4K resolution,
smooth dolly movement, dust particles in warm light
```

### 🌀 风格2：奇幻穿越风（实测效果最好！）

**适合：** 社媒传播、Z世代触达、话题营销

**视觉特征：** 文物从沉睡中"醒来"、金色粒子环绕、奇幻光效

**实测Prompt（青铜器）：**
```
Ancient Chinese bronze ritual tripod ding vessel from Shang dynasty, 
green patina gradually transforming to reveal original golden luster, 
magical golden particles swirling around the vessel, 
ethereal glow emanating from within, cinematic documentary style, 
slow motion, museum spotlight, shallow depth of field, 
professional cultural heritage photography, 4K resolution, 
smooth dolly movement, dust particles in warm light
```

**实测Prompt（汝窑瓷器）：**
```
Song dynasty Ru ware celadon vase, sky-blue glaze with fine crackle pattern, 
displayed on a clean museum pedestal, soft rotating spotlight illuminating the vase, 
magical awakening animation, golden particles swirling around the vase, 
ethereal blue glow emanating from within, time travel transformation effect, 
fantasy cinematic lighting, mystical atmosphere, 4K resolution, smooth camera orbit
```

### 📜 风格3：古代复原风

**适合：** 教育科普、历史还原、文化遗产日

**视觉特征：** 还原文物的制作场景和使用场景、历史准确

**Prompt模板：**
```
{文物名称}, historical recreation, period-accurate setting,
craftsmen working, ancient workshop, warm candlelight,
cinematic wide shot, 4K resolution
```

### ✨ 风格4：粒子光效风

**适合：** 艺术展览、视觉冲击、新媒体艺术

**视觉特征：** 金色粒子飞舞、光轨环绕、发光蜕变效果

### 🏺 风格5：博物馆展示风

**适合：** 官方宣传、正式场合、数字藏品

**视觉特征：** 顶级博物馆展厅效果、旋转聚光灯、4K画质

---

## 五、Step 3：用AI帮你生成视频

这一步最简单，因为你只需要"说话"。

### 5.1 在WorkBuddy里对话

直接对AI说：

> "帮我用万相2.7生成一个商代青铜鼎的活化视频，用奇幻穿越风格"

AI会自动完成：
1. 🔍 **文物信息研究** — 自动查找青铜鼎的历史信息
2. 🎬 **Prompt智能生成** — 根据文物信息+风格生成最优Prompt
3. ✅ **确认稿预览** — 让你确认后再调用API
4. 🚀 **API调用执行** — 调用万相2.7 API生成视频

### 5.2 我的实测结果

**测试1：商代青铜鼎·奇幻穿越风**

| 项目 | 内容 |
|------|------|
| 模型 | wan2.7-t2v |
| 风格 | 奇幻穿越风 |
| 分辨率 | 720P / 16:9 |
| 时长 | 5秒 |
| 生成耗时 | 约2-3分钟 |
| 状态 | ✅ 成功 |

**测试2：北宋汝窑天青釉·奇幻穿越风**

| 项目 | 内容 |
|------|------|
| 模型 | wan2.7-t2v |
| 风格 | 奇幻穿越风 |
| 分辨率 | 720P / 16:9 |
| 时长 | 5秒 |
| 生成耗时 | 约3-5分钟 |
| 状态 | ✅ 成功 |

> 💡 小提示：万相2.7文生视频一般在2-10分钟完成，复杂场景（如瓷器釉面细节）会慢一些。

---

## 六、Step 4：制作展示页面

光有视频不够，你还需要一个好看的展示页面。

### 6.1 设计思路

我设计了一个暗金色主题的展示页，灵感来自博物馆展厅的氛围：
- **背景色**：深黑+微妙的十字纹理（像博物馆的墙壁）
- **主色调**：金色（#C9A96E）+ 朱红（#8B2500）
- **字体**：Noto Serif SC（标题）+ Noto Sans SC（正文）

### 6.2 页面结构

```
┌─────────────────────────────────┐
│         Hero 首屏               │
│   "AI文物活化师"                │
│   让沉睡的文物动起来             │
├─────────────────────────────────┤
│     万相模型实际生成演示         │
│   [青铜鼎视频] [汝窑视频]        │
├─────────────────────────────────┤
│         使用流程                 │
│   上传→选风格→生成→使用          │
├─────────────────────────────────┤
│       五大活化风格               │
│   纪录片/穿越/复原/粒子/展示     │
├─────────────────────────────────┤
│         技术架构                 │
│   wan2.7-i2v/t2v/i2i           │
├─────────────────────────────────┤
│         效率对比                 │
│   传统制作 vs AI活化师           │
├─────────────────────────────────┤
│         应用场景                 │
│   博物馆/社媒/文旅              │
└─────────────────────────────────┘
```

### 6.3 部署到GitHub Pages

```bash
# 1. 创建仓库
git init
git add .
git commit -m "AI文物活化师参赛作品"

# 2. 推送到GitHub
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin master

# 3. 开启GitHub Pages
# Settings → Pages → Source: master / (root) → Save
```

等1-2分钟，你的页面就能公网访问了：
> 🌐 https://lzymmmm-droid.github.io/ai-relic-activator/demo.html

---

## 七、踩坑记录（血泪教训）

### 坑1：Prompt太短，效果模糊

❌ 第一次试的Prompt：
```
bronze ding, Chinese ancient vessel, video
```
结果：生成了一堆不明所以的金属块，完全不像文物。

✅ 修复后的Prompt（三层架构）：
```
第一层：具体文物描述（朝代+材质+纹饰）
第二层：风格关键词（穿越风→金色粒子+奇幻光效）
第三层：质量保障（4K+专业摄影+历史准确）
```

### 坑2：忘了指定朝代

文物的"朝代"信息对生成效果影响巨大。同样是"青铜鼎"：
- 加了"Shang dynasty" → 生成商代风格的厚重礼器 ✅
- 不加朝代 → 生成了像现代艺术品的玩意儿 ❌

### 坑3：视频比例没选对

万相2.7支持多种比例：
- 短视频用 **9:16**（720×1280）
- 公众号/网页用 **16:9**（1280×720）
- 展厅大屏用 **16:9**（1080×1920）

我第一次直接默认参数，生成了个正方形的，完全没法用。

### 坑4：GitHub Push被代理坑了

git配了Clash代理但软件没开，一直连不上GitHub。解决：
- 开Clash → push成功
- 或者 `git config --global --unset http.proxy` 去掉代理直连

---

## 八、效率对比：为什么值得做

| 对比维度 | 传统方式 | AI文物活化师 |
|---------|---------|-------------|
| 制作周期 | 1-4周 | **5-10分钟** |
| 制作成本 | ¥5,000-50,000/条 | **¥1-5/条** |
| 所需技能 | 摄影师+剪辑师+特效师 | **上传照片，选风格** |
| 产出数量 | 1-3条 | **批量生成，无限变体** |
| 风格多样性 | 受限于团队 | **5大预设+无限自定义** |
| 修改成本 | 重新拍摄/剪辑 | **调整参数，重新生成** |

**简单说：以前花5万做一条视频，现在花5块钱5分钟就能做一条。**

---

## 九、可以怎么用

### 🏛️ 博物馆
- 互动展屏：观众点击文物→播放活化视频
- 虚拟展厅：全馆文物在线展示+动态视频
- 临展宣传：新展览预告视频快速制作

### 📱 社交媒体
- 短视频矩阵：每天一件文物活化，日更IP
- 话题营销：#文物活了、#AI看国宝
- 直播互动：弹幕点文物，实时生成

### 🗺️ 文旅
- 景区导览：文物活化视频嵌入AR导览
- 文创衍生：视频→文创设计灵感
- 沉浸体验：活化视频+空间音频

---

## 十、下一步可以做什么

- [ ] 接入博物馆数字资产管理系统
- [ ] 增加3D扫描→视频生成流程
- [ ] 集成语音讲解自动生成
- [ ] 支持多国语言输出（文化出海）
- [ ] 对接抖音/小红书一键发布
- [ ] 构建文物活化视频素材库（B端SaaS）

---

## 写在最后

"让文物活起来"不是一句口号，是真正可以做到的事。

三千年前的匠人花了几年铸造一件青铜鼎，三千年后的我们只需要5分钟就能让它重新"发光"。

AI不是来替代文化的，是来帮文化讲好故事的。

如果你也想做文物活化，欢迎交流！我的GitHub仓库和Demo链接都在上面，直接fork就能开始。

**让我们一起，让每一件沉睡的文物，都被AI唤醒。** ✨

---

**作者**：振一 | 文博AI创业者
**参赛赛事**：WaytoAGI「万相妙思+」快闪赛
**在线Demo**：https://lzymmmm-droid.github.io/ai-relic-activator/demo.html
**GitHub**：https://github.com/lzymmmm-droid/ai-relic-activator
