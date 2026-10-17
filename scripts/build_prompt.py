#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第二世界 · 摄影二创海报提示词组装器

把母版提示词 + 三个必填槽 + 小人与旁白，拼成可直接投喂的完整 prompt。

用法:
    python build_prompt.py --subject "侧身回头的女性" --structure "她的侧脸轮廓与肩线" \\
        --paradigm slice --figures 1 --caption "hold the light still"

    python build_prompt.py --subject "..." --structure "..." --paradigm hole --lang en
    python build_prompt.py --json --paradigm peel          # 只输出结构化 spec
    python build_prompt.py --checklist                     # 出图后自检
"""

import argparse
import json
import sys

PARADIGMS = {
    "slice": {
        "zh": "主体切片式",
        "en": "subject slice",
        "zh_desc": "相片物体为沿主体轮廓切下的片状实体，直立或斜倚于纸面，切口平直、可见纸芯分层，厚度约 2–3mm，切口边缘有细微纸纤维毛边",
        "en_desc": "the photo-object is a flat piece sliced along the subject's contour, standing or leaning "
                   "on the paper, with a clean cut edge showing layered paper core, about 2-3mm thick and "
                   "slightly fibrous at the cut",
        "action_zh": "双手推着相片物体",
        "action_en": "pushing the photo-object with both hands",
    },
    "peel": {
        "zh": "表层揭取式",
        "en": "surface peel",
        "zh_desc": "相片物体为自原图表层揭起的一层薄片，一角卷起并微微悬空，背面呈纸白色，卷曲半径约为物体宽度的一半，形变克制",
        "en_desc": "the photo-object is the top layer of the image peeled up into a thin sheet, one corner "
                   "curled and lightly hovering, paper-white on the back, curl radius about half the object "
                   "width, restrained deformation",
        "action_zh": "单手掀起相片一角",
        "action_en": "lifting one corner of the print with one hand",
    },
    "hole": {
        "zh": "空间穿孔式",
        "en": "spatial cut-out",
        "zh_desc": "纸面被切出矩形孔洞，原图自孔洞中呈实体凸出约 5mm，孔缘可见纸芯厚度与轻微毛边，孔洞内即为同一张照片的实体凸出，非另一画面",
        "en_desc": "a rectangular opening is cut through the paper and the image protrudes from it as a solid "
                   "about 5mm proud, the rim showing paper core thickness and slight fraying; inside the "
                   "opening is the same photograph as a solid, not a different image",
        "action_zh": "从孔洞里探出半个身子",
        "action_en": "leaning out of the opening",
    },
}

RATIOS = {"3:4": "竖版3:4", "4:5": "竖版4:5", "1:1": "正方形1:1"}

MASTER_ZH = """请基于我上传的照片，生成一张{ratio}的「第二世界」摄影二创海报，画面上下严格各占50%，水平硬切分界，无可见分割线、无渐变过渡。

上半区（原生摄影场）需保留原始照片本体，仅做等比例居中裁切，100%保留原图的{subject}、空间关系、自然光影、色彩层次与摄影质感，禁止重绘、插画化、调色、添加或删减元素。

下半区（物态留白场）的背景为暖米白哑光艺术纸（#F4EFE4），带极细腻植物纤维纹理、克制纸面斑点与轻微印刷噪点，大面积留白为主动设计元素，相片物体占下半区面积不超过40%。从原图中提取{structure}，将其转化为一块可触碰的实体「相片物体」，采用【{paradigm}】呈现：{paradigm_desc}。

「相片物体」硬性标准：
1. 表面完整保留原图的真实摄影纹理与色彩，无描边、无滤镜、无插画化修改
2. 具备明确纸张厚度，边缘可见清晰截面质感，存在自然力学形变（一角卷起、边缘弯折、整体微弧）
3. 与纸面形成明确接触关系，底部带有柔和接触阴影，阴影与上半区光源方向一致，透明自然无硬边
4. 主体身份完整可识别，形态与原图核心主体一一对应，仅改变物理形态，不改变结构、比例与核心特征

{figures_block}

整体风格：真实摄影 + 暖米白纸张 + 极简黑线涂鸦 + 轻微手工拼贴感 + 独立杂志感，干净克制，明亮有高级感。

严格禁止：整张图重绘插画化、下半区只有线稿无实体相片物体、发光描边特效、添加无关装饰元素、商业广告感、厚重3D渲染、陈词滥调文案。"""

FIGURES_ZH = """加入{n}个极简炭黑速写小人（炭黑#1C1C1A），无五官无细节，仅保留动态轮廓，人物动作：{action}，动作与图片中的景物产生共鸣，与相片物体形成明确力学互动，用于锚定物体尺度。在画面右下角添加一句简短英文手写旁白，内容为“{caption}”，字号极小（约为画面高度的1.5%），深炭灰色（#3A3A38），自然融入纸面，字体美观不呆板，和画面不违和。"""

FIGURES_ZH_ZERO = """本图不加入速写小人，仅依靠相片物体的形变、厚度与接触阴影锚定尺度与实体感。在画面右下角添加一句简短英文手写旁白，内容为“{caption}”，字号极小（约为画面高度的1.5%），深炭灰色（#3A3A38），自然融入纸面，字体美观不呆板，和画面不违和。"""

MASTER_EN = """Based on the uploaded photo, generate a {ratio} "second world" photo-remix poster: the frame is split into exactly two halves of 50% each by a hard horizontal cut, with no visible divider line and no gradient transition.

Upper half (native photography field): keep the original photograph itself, only proportionally center-cropped. Preserve 100% of {subject}, the spatial relationships, natural lighting, colour gradation and photographic texture. No repainting, no illustration, no colour grading, no added or removed elements.

Lower half (object-and-void field): background is warm off-white matte art paper (#F4EFE4) with very fine plant-fibre texture, restrained specks and light print noise; large areas of emptiness are an active design element, and the photo-object covers no more than 40% of this half. Extract {structure} from the original image and turn it into a touchable solid "photo-object", presented as {paradigm}: {paradigm_desc}.

Hard standards for the photo-object:
1. Its surface preserves the original photographic texture and colour completely — no outline stroke, no filter, no illustration-style modification.
2. It has a definite paper thickness, a clearly visible cut-edge texture, and natural mechanical deformation (a curled corner, a bent edge, an overall slight bow).
3. It makes definite contact with the paper, with a soft contact shadow beneath it; the shadow direction matches the light in the upper half, translucent and without hard edges.
4. The subject remains fully recognisable, one-to-one with the subject in the original — only its physical form changes, never its structure, proportions or core features.

{figures_block}

Overall style: real photography + warm off-white paper + minimal black line doodle + slight handmade collage feel + independent magazine feel; clean, restrained, bright and refined.

Strictly forbidden: repainting the whole image as illustration, a lower half with only line art and no solid photo-object, glow outline effects, irrelevant decorative elements, commercial advertising feel, heavy 3D rendering, clichéd captions."""

FIGURES_EN = """Add {n} minimal charcoal sketch figures (#1C1C1A), no facial features, no detail, only a dynamic silhouette, action: {action}; the action resonates with the scene in the photo and forms a clear mechanical interaction with the photo-object, anchoring its scale. In the lower-right corner add a short handwritten English caption reading "{caption}", very small type (about 1.5% of frame height), dark charcoal grey (#3A3A38), naturally absorbed into the paper, elegant and not stiff, never clashing with the image."""

FIGURES_EN_ZERO = """Add no sketch figures; the photo-object alone must carry its solidity and scale through deformation, thickness and contact shadow. In the lower-right corner add a short handwritten English caption reading "{caption}", very small type (about 1.5% of frame height), dark charcoal grey (#3A3A38), naturally absorbed into the paper, elegant and not stiff, never clashing with the image."""

CHECKLIST = """出图后自检（10 条）
[ ]  1 上下真的 50/50，无分割线、无渐变过渡
[ ]  2 上半区与原图一致，无重绘、无调色偏移
[ ]  3 下半区有实体（不是只有线稿、不是平贴纸）
[ ]  4 相片物体有厚度、有截面、有形变至少一处
[ ]  5 接触阴影存在，方向与上半区光源一致
[ ]  6 主体形态可识别，比例未变形
[ ]  7 小人 0–3 个，无五官，动作有真实力学接触
[ ]  8 旁白 ≤6 词、右下、字号极小、深炭灰、手写感
[ ]  9 全图干净克制，无装饰元素、无发光描边、无 3D 感
[ ] 10 缩到 30% 看：像杂志内页，不像电商广告"""


def build_zh(a):
    p = PARADIGMS[a.paradigm]
    if a.figures > 0:
        figs = FIGURES_ZH.format(n=a.figures, action=a.action or p["action_zh"], caption=a.caption)
    else:
        figs = FIGURES_ZH_ZERO.format(caption=a.caption)
    return MASTER_ZH.format(
        ratio=RATIOS[a.ratio], subject=a.subject, structure=a.structure,
        paradigm=p["zh"], paradigm_desc=p["zh_desc"], figures_block=figs)


def build_en(a):
    p = PARADIGMS[a.paradigm]
    if a.figures > 0:
        figs = FIGURES_EN.format(n=a.figures, action=a.action or p["action_en"], caption=a.caption)
    else:
        figs = FIGURES_EN_ZERO.format(caption=a.caption)
    return MASTER_EN.format(
        ratio=(a.ratio + " vertical") if a.ratio != "1:1" else "1:1 square",
        subject=a.subject, structure=a.structure, paradigm=p["en"],
        paradigm_desc=p["en_desc"], figures_block=figs)


def main():
    ap = argparse.ArgumentParser(description="第二世界 · 摄影二创海报提示词组装器")
    ap.add_argument("--subject", default="核心主体", help="核心主体名称，如「侧身回头的女性」")
    ap.add_argument("--structure", default="主体轮廓与关键线条", help="核心视觉结构，如「她的侧脸轮廓与肩线」")
    ap.add_argument("--paradigm", choices=list(PARADIGMS), default="slice",
                    help="slice=主体切片 / peel=表层揭取 / hole=空间穿孔")
    ap.add_argument("--figures", type=int, default=1, choices=[0, 1, 2, 3], help="速写小人数量 0-3")
    ap.add_argument("--action", default="", help="小人动作，留空则按范式取默认动作")
    ap.add_argument("--caption", default="", help="英文旁白，≤6 词")
    ap.add_argument("--ratio", choices=list(RATIOS), default="3:4")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh")
    ap.add_argument("--json", action="store_true", help="仅输出结构化 spec")
    ap.add_argument("--checklist", action="store_true")
    ap.add_argument("--save", default="", help="把提示词写入文件")
    a = ap.parse_args()

    if a.checklist:
        print(CHECKLIST)
        return

    if not a.caption:
        a.caption = "hold the light still"
        print("[提示] 未提供 --caption，使用默认旁白：hold the light still", file=sys.stderr)
    if len(a.caption.split()) > 6:
        print(f"[警告] 旁白 {len(a.caption.split())} 词，超过 6 词上限", file=sys.stderr)

    if a.json:
        spec = {
            "ratio": a.ratio,
            "split": "horizontal 50/50, hard cut, no divider, no gradient",
            "paradigm": a.paradigm,
            "paradigm_zh": PARADIGMS[a.paradigm]["zh"],
            "subject": a.subject,
            "structure": a.structure,
            "figures": a.figures,
            "action": a.action or PARADIGMS[a.paradigm]["action_zh"],
            "caption": a.caption,
            "paper": {"color": "#F4EFE4", "texture": "fine plant fibre", "speckle": "restrained"},
            "ink": "#1C1C1A",
            "caption_color": "#3A3A38",
            "object_area_max": "40% of lower half",
            "contact_shadow": "soft, feathered, follows upper-half light direction",
        }
        print(json.dumps(spec, ensure_ascii=False, indent=2))
        return

    text = build_zh(a) if a.lang == "zh" else build_en(a)
    print(text)
    if a.save:
        with open(a.save, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"\n[saved] {a.save}", file=sys.stderr)


if __name__ == "__main__":
    main()
