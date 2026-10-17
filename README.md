# 第二世界 · 摄影二创海报 Skill

一张照片被水平切成两个世界：**上面是它本来的样子，下面是被取出来、变成可以拿在手里的实物**。极简黑线小人站在暖米白纸面上与它互动，右下角一句小字旁白。

这不是拼贴滤镜，而是**物态转换**——照片的一部分必须变成有厚度、有形变、有接触阴影的实体，而表面仍是原照片的摄影质感。

> 一句话骨架：3:4 竖版 / 上下各 50% 硬切 / 上半原图不动 / 下半暖米白纸上浮起相片实体 / 0–3 个炭黑小人锚定尺度 / ≤6 词英文手写旁白。

## 安装

```bash
git clone https://github.com/shanhai256/second-world-poster-skill.git
cp -r second-world-poster-skill ~/.claude/skills/second-world-photo-poster       # Claude Code
cp -r second-world-poster-skill ~/.codebuddy/skills/second-world-photo-poster    # CodeBuddy / WorkBuddy
```

装好后提到「第二世界 / 上下二分割海报 / 相片切片 / 物态留白」会自动加载。

## 三个必填槽

缺一个就退化成普通拼贴。

| 槽位 | 填什么 | 反例 |
|---|---|---|
| `核心主体名称` | 上半区必须 100% 保留的那个东西 | 「照片内容」 |
| `核心视觉结构` | 能实体化的形态：一条栏杆、一扇窗、一道坡、一个人影 | 「氛围」「光影」 |
| `创意范式` | 主体切片式 / 表层揭取式 / 空间穿孔式，**三选一** | 三个都写 → 结果随机 |

## 用法

### 1. 让 Agent 直接调

> 「用这张照片做第二世界海报，主体是她侧脸的轮廓，用揭取式，一个小人，旁白 hold the light still」

### 2. 命令行组装

```bash
python3 scripts/build_prompt.py \
  --subject "侧身回头的女性" \
  --structure "她的侧脸轮廓与肩线" \
  --paradigm peel \
  --figures 1 \
  --caption "hold the light still"
```

```bash
# 英文版给 MJ / SD / Flux
python3 scripts/build_prompt.py --subject "a half-open green window" \
  --structure "the window frame rectangle" --paradigm hole --figures 2 \
  --lang en --caption "a room that fits in hand"

# 结构化 spec（版式 / 色值 / 阴影规则）
python3 scripts/build_prompt.py --json --paradigm peel

# 出图后自检
python3 scripts/build_prompt.py --checklist
```

`--figures 0` 会切换成「无小人」写法，靠形变与阴影单独承载实体感。

## 目录

```
second-world-poster-skill/
├── SKILL.md                     # 触发条件 / 骨架 / 三槽 / 三底线 / 自检 / 翻车
├── references/
│   ├── master-prompt.md         # 母版逐字（两段截图已拼接）+ 13 层拆解
│   ├── parameters.md            # 三范式详解、动作库、旁白写法、纸张配色、填槽示例
│   └── variations.md            # 4:5/1:1、左右分割、撕纸边、双色纸、多物体等 9 种变体
└── scripts/
    └── build_prompt.py          # 槽位组装器（中英双语、JSON spec、自检清单）
```

## 三种范式

| 范式 | 形态 | 适合 |
|---|---|---|
| **主体切片式** | 沿主体轮廓切下一片，立/卧在纸面 | 人、船、车、房子、树、山脊 |
| **表层揭取式** | 像揭起一层薄膜，一角翘起悬空 | 水面、墙面、天空、织物、路面 |
| **空间穿孔式** | 纸面挖洞，照片自洞中凸出 | 门廊、窗、隧道、镜面、井口 |

完整的「关键句 / 易错点」见 [`references/parameters.md`](references/parameters.md)。

## 翻车排查

| 症状 | 修法 |
|---|---|
| 下半区只有线稿没有实体 | 补「实体、有纸张厚度、边缘可见截面」 |
| 整张被重绘成插画 | 加「上半区禁止任何形式重绘与调色，仅等比例裁切」 |
| 中间出现分割线/渐变 | 显式写「无可见分割线、无渐变过渡、硬切」 |
| 影子方向反了 | 补「光源来自左上，阴影落向右下」 |
| 小人像卡通人物 | 写「无五官无细节，仅动态轮廓」 |
| 物体像贴纸 | 补「底部柔和接触阴影，透明自然无硬边」 |
| 像淘宝海报 | 强化「大面积留白为主动设计元素」，删装饰 |

## 出处与版权

母版提示词来自小红书作者 **花谦汨** 的公开分享（两段截图，`references/master-prompt.md` 已按原顺序拼接并**逐字保留**）。本仓库在其基础上做结构拆解、槽位化与范式归纳，**原文版权归原作者**。若作者有异议，请开 issue，我会立即下架相关文本。

## License

代码（`scripts/`）与结构文档以 MIT 发布；母版提示词原文不适用 MIT，归属原作者。
