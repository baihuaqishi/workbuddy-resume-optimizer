#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resume_to_pdf.py —— 将 Markdown 简历（或说明文档）渲染为排版干净的 PDF。

特性：
- 自动选用系统中文字体（Windows 优先用微软雅黑，含粗体），否则回退到内置 STSong-Light。
- 支持 # 标题 / ## 模块 / ### 子标题 / - 列表 / **加粗** / [链接](url) / --- 分隔线。
- 支持 Markdown 表格（| 列 | 列 |）：渲染为带边框、表头底色、斑马纹的真表格，列宽按内容自适应，中文自动换行。
- 支持任务列表 - [ ] / - [x]：渲染为 ☐ / ☑ 复选框。
- 仅依赖 reportlab（纯 Python，无需系统级排版库）。

用法：
    python resume_to_pdf.py <input.md> [output.pdf]

不指定 output.pdf 时，默认在同目录生成与输入同名的 .pdf。
依赖：pip install reportlab
"""
import sys
import os
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    HRFlowable, ListFlowable, ListItem, Table, TableStyle,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont


# 页面可用宽度（A4 宽 - 左右边距各 16mm）
AVAIL_W = A4[0] - 32 * mm


# ---------- 字体注册 ----------
def register_fonts():
    """返回 (normal, bold) 字体名。优先微软雅黑，回退 STSong-Light。"""
    candidates = [
        (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\msyhbd.ttf"),
        (r"C:\Windows\Fonts\msyh.ttf", r"C:\Windows\Fonts\msyhbd.ttf"),
        (r"C:\Windows\Fonts\STZHONGS.TTF", r"C:\Windows\Fonts\STZHONGS.TTF"),
    ]
    for reg_path, bold_path in candidates:
        if os.path.exists(reg_path):
            try:
                pdfmetrics.registerFont(TTFont("CJK", reg_path, subfontIndex=0))
                if os.path.exists(bold_path) and bold_path != reg_path:
                    pdfmetrics.registerFont(TTFont("CJK-Bold", bold_path, subfontIndex=0))
                else:
                    pdfmetrics.registerFont(TTFont("CJK-Bold", reg_path, subfontIndex=0))
                pdfmetrics.registerFontFamily("CJK", normal="CJK", bold="CJK-Bold",
                                              italic="CJK", boldItalic="CJK-Bold")
                return "CJK", "CJK-Bold"
            except Exception:
                continue
    # 回退：内置中文 CID 字体（无独立粗体）
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    pdfmetrics.registerFontFamily("CJK", normal="STSong-Light", bold="STSong-Light",
                                  italic="STSong-Light", boldItalic="STSong-Light")
    return "STSong-Light", "STSong-Light"


FONT, FONT_BOLD = register_fonts()


# ---------- 行内标记解析 ----------
def inline(text):
    """转义特殊字符并支持 **加粗** / [链接](url)。"""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # 链接 [text](url) -> 蓝色可点击
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<font color="#0645AD"><a href="{m.group(2)}">{m.group(1)}</a></font>',
        text,
    )
    # 加粗 **x**
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return text


# 估算单元格视觉宽度（CJK 占 1，其它占 0.55），用于自适应列宽
def text_width(text):
    w = 0.0
    for ch in text:
        w += 1.0 if ord(ch) > 0x2E80 else 0.55
    return w


# ---------- 样式 ----------
def build_styles():
    return {
        "name": ParagraphStyle("name", fontName=FONT_BOLD, fontSize=18, leading=22,
                                alignment=TA_CENTER, spaceAfter=2, textColor=colors.HexColor("#1a1a1a")),
        "contact": ParagraphStyle("contact", fontName=FONT, fontSize=9, leading=13,
                                  alignment=TA_CENTER, textColor=colors.HexColor("#444444"), spaceAfter=6),
        "section": ParagraphStyle("section", fontName=FONT_BOLD, fontSize=12, leading=16,
                                  textColor=colors.HexColor("#0b5cab"), spaceBefore=10, spaceAfter=3),
        "sub": ParagraphStyle("sub", fontName=FONT_BOLD, fontSize=10.5, leading=14,
                              textColor=colors.HexColor("#222222"), spaceBefore=4, spaceAfter=1),
        "body": ParagraphStyle("body", fontName=FONT, fontSize=9.5, leading=13.5,
                               spaceAfter=2, textColor=colors.HexColor("#222222")),
        "bullet": ParagraphStyle("bullet", fontName=FONT, fontSize=9.5, leading=13.5,
                                 textColor=colors.HexColor("#222222")),
        "cell": ParagraphStyle("cell", fontName=FONT, fontSize=8.5, leading=12,
                               textColor=colors.HexColor("#222222")),
        "hcell": ParagraphStyle("hcell", fontName=FONT_BOLD, fontSize=8.5, leading=12,
                                textColor=colors.white),
    }


def build_doc(filename):
    doc = BaseDocTemplate(
        filename, pagesize=A4,
        leftMargin=16 * mm, rightMargin=16 * mm,
        topMargin=14 * mm, bottomMargin=14 * mm,
        title="Resume", author="WorkBuddy Resume Optimizer",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame])])
    return doc


# ---------- 表格解析与渲染 ----------
def parse_table(lines, i):
    """从 lines[i]（表头行）开始，连续读取 | 分隔行，返回 (rows, next_i)。
    自动跳过 |---|---| 分隔符行。"""
    data = []
    while i < len(lines):
        s = lines[i].strip()
        if not s.startswith("|"):
            break
        row_text = s.strip("|")
        cells = [c.strip() for c in row_text.split("|")]
        # 分隔符行（如 |---|---| 或 |:--|:-:|）
        if data and all(re.match(r"^[\s:\-]+$", c) for c in cells):
            i += 1
            continue
        data.append(cells)
        i += 1
    return data, i


def build_table(data):
    """把解析出的表格数据渲染为真 PDF 表格（自适应列宽 + 中文换行 + 斑马纹）。"""
    if not data:
        return Spacer(1, 1)
    num_cols = max(len(r) for r in data)
    norm = [r + [""] * (num_cols - len(r)) for r in data]

    # 按各列内容视觉宽度比例分配列宽
    weights = [0.0] * num_cols
    for r in norm:
        for ci, c in enumerate(r):
            weights[ci] = max(weights[ci], text_width(c))
    total = sum(weights) or 1.0
    col_widths = [AVAIL_W * (w / total) for w in weights]

    # 单元格用 Paragraph 以支持中文自动换行与加粗
    header_cells = [Paragraph(inline(c), build_styles()["hcell"]) for c in norm[0]]
    body_rows = [[Paragraph(inline(c), build_styles()["cell"]) for c in r] for r in norm[1:]]
    table_rows = [header_cells] + body_rows

    t = Table(table_rows, colWidths=col_widths, repeatRows=1,
              spaceBefore=6, spaceAfter=8)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b5cab")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbbbbb")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f6fb")]),
    ]))
    return t


def render(md_text, out_pdf):
    styles = build_styles()
    story = []
    lines = md_text.split("\n")
    i = 0
    n = len(lines)
    first_heading_done = False

    while i < n:
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == "---":
            story.append(HRFlowable(width="100%", thickness=0.6,
                                   color=colors.HexColor("#cccccc"), spaceBefore=4, spaceAfter=4))
            i += 1
            continue

        if stripped.startswith("# "):
            story.append(Paragraph(inline(stripped[2:]), styles["name"]))
            first_heading_done = True
            i += 1
            continue

        if stripped.startswith("## "):
            story.append(Paragraph(inline(stripped[3:]), styles["section"]))
            story.append(HRFlowable(width="100%", thickness=0.8,
                                   color=colors.HexColor("#0b5cab"), spaceBefore=1, spaceAfter=4))
            i += 1
            continue

        if stripped.startswith("### "):
            story.append(Paragraph(inline(stripped[4:]), styles["sub"]))
            i += 1
            continue

        # Markdown 表格（连续 | 分隔行）
        if stripped.startswith("|") and stripped.count("|") >= 2:
            table_rows, i = parse_table(lines, i)
            story.append(build_table(table_rows))
            continue

        # 列表项（收集连续列表）
        if re.match(r"^[-*]\s+", stripped):
            items = []
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                content = re.sub(r"^[-*]\s+", "", lines[i].strip())
                # 任务列表 -> 复选框
                content = re.sub(r"^\[ \]\s*", "☐ ", content)
                content = re.sub(r"^\[[xX]\]\s*", "☑ ", content)
                items.append(ListItem(Paragraph(inline(content), styles["bullet"]),
                                      leftIndent=10, value="•"))
                i += 1
            story.append(ListFlowable(items, bulletType="bullet", start="•",
                                       leftIndent=12, bulletColor=colors.HexColor("#0b5cab"),
                                       spaceBefore=1, spaceAfter=3))
            continue

        # 普通段落：标题之后的首段按联系方式居中，其余左对齐
        if not first_heading_done:
            story.append(Paragraph(inline(stripped), styles["contact"]))
        else:
            story.append(Paragraph(inline(stripped), styles["body"]))
        i += 1

    doc = build_doc(out_pdf)
    doc.build(story)


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("用法: python resume_to_pdf.py <input.md> [output.pdf]\n")
        sys.exit(1)
    md_path = sys.argv[1]
    if not os.path.exists(md_path):
        sys.stderr.write(f"[错误] 文件不存在：{md_path}\n")
        sys.exit(1)
    out_pdf = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(md_path)[0] + ".pdf"
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()
    render(md_text, out_pdf)
    sys.stderr.write(f"[完成] 已生成 PDF -> {out_pdf}\n")


if __name__ == "__main__":
    main()
