---
name: resume-optimizer
description: "This skill tailors an existing resume for a specific job posting. It takes a job description (JD) and the user's original resume, aligns terminology and wording to the target role using the STAR method, and produces an optimized resume (PDF) plus a diagnosis card and matching card, with optional cover letter and interview prep. It does not restructure or fabricate content. Use it when the user wants to optimize, adjust, or fine-tune a resume for a particular position, or says things like 根据这份JD优化简历, 针对这个岗位改一下我的简历, 简历针对性微调, 帮我把简历改得匹配这个招聘要求, 顺手写个求职信, 帮我准备这个岗位的面试."
agent_created: true
---

# Resume Optimizer（简历针对性优化）

## Overview

针对用户投递的具体岗位，对已有简历做**关键词对齐与措辞打磨**，用 STAR 法重写经历，产出优化后简历 PDF、诊断卡/匹配卡，并可选附求职信与面试准备。本 skill 定位为**微调**：保留原简历结构与时间顺序，不重排、不虚构。

## When to use

- 用户给了「招聘职位 / JD」+「自己的简历」，要求针对该岗位优化。
- 用户原话含："优化简历 / 改简历 / 匹配这个岗位 / 针对性微调 / 刷简历关键词"。
- 衍生需求："顺手写个求职信"、"帮我准备这个岗位的面试"——同一次调用一并产出。
- 不用于：从零写简历、虚构经历、代写与事实不符的材料。

## Inputs（输入与采集）

三种输入来源，按需组合：

1. **粘贴文本**：对话里贴出 JD 文本和/或简历原文。
2. **截图 / 图片**：贴图或拖入图片（JD 截图、简历截图）。用多模态直接读图，转写为文本后再处理。
3. **上传文件**：`.md` / `.docx` / `.pdf`。文件优先，用 `scripts/extract_text.py` 提取纯文本。

附加输入：**语气（tone）**——默认「正式 / 专业」，用户可指定「亲和 / 紧迫 / 学术」等，改写与求职信随之调整。

采集：JD 与简历任缺一项都要追问；确定后按 Workflow 执行。

## Workflow（工作流）

1. **采集**：拿到 JD 文本 + 简历文本（见 Inputs），确认语气。
2. **读方法论**：读取 `references/optimization-guide.md`，按 JD 解析清单、STAR 法、诊断卡/匹配卡、关键词对齐、措辞升级、量化与诚实边界执行。
3. **解析 JD**：套用 JD 解析清单，提取硬性要求、核心技能关键词、职责动词、优先项、软技能、ATS 关键词，按优先级排序。
4. **解析简历**：拆为标准模块（顺序不变），记录已有关键词与量化数据。
5. **STAR 重写**：每条经历强制走 STAR（S/T/A/R），优先补齐量化 Result；未提供数字用 `[待补充：…]` 占位，**绝不臆造**。
6. **对齐 + 改写**：关键词映射、同义升级、缺口仅在卡中标出、不相关经历弱化不删、结构顺序不变。
7. **产出简历 Markdown**：参考 `assets/resume_template.md`，写 `优化后简历.md`。
8. **转 PDF**：用 `scripts/resume_to_pdf.py` 生成 `优化后简历.pdf`。
9. **产出诊断卡 + 匹配卡**：写 `优化说明.md`，含 ①诊断卡 ②匹配卡 ③逐处改写对照 ④`[待补充]`汇总 ⑤投递前核对清单。
10. **（可选）求职信**：参照 `assets/cover_letter_template.md` 写 `求职信.md`；缺口大时改写为坦诚的转岗动机，不假装匹配。
11. **（可选）面试准备**：参照 `assets/interview_prep_template.md` 写 `面试准备.md`，含高频问题、STAR 故事库、缺口预案、反向提问。
12. **交付**：用 present_files 同时给出上述文件（PDF + 说明 + 求职信 + 面试准备）。

## Hard rules（诚实边界，不可逾越）

- 不虚构公司、职位、时间、项目、技能、数据。
- 不改事实（时间线、级别、学历保持原样）。
- 保留真实经历，不相关者只弱化/精简，不删除。
- 不改结构顺序（仅做关键词与措辞微调）。
- 不替用户说谎："可能具备但未写明"的能力只在诊断卡/匹配卡提示，不进简历正文。

## Scripts

### scripts/extract_text.py
从 `.md/.txt/.docx/.pdf` 提取纯文本。
```bash
python scripts/extract_text.py <input_file> [output_file]
```
无 `output_file` 时直接打印到 stdout。依赖：`python-docx`、`pypdf`。

### scripts/resume_to_pdf.py
将 Markdown 简历/说明渲染为排版干净的中文 PDF（自动选微软雅黑，回退 STSong-Light）。
```bash
python scripts/resume_to_pdf.py <input.md> [output.pdf]
```
依赖：`reportlab`。

支持以下 Markdown 语法：
- `#` / `##` / `###` 标题与分隔线
- `-` 列表，`**加粗**`，`[text](url)` 链接
- **Markdown 表格**（`| 列 | 列 |`）：渲染为带边框、表头底色、斑马纹的真表格，列宽按内容视觉宽度自适应，中文自动换行（用于诊断卡、匹配卡）
- **任务列表**（`- [ ]` / `- [x]`）：渲染为 ☐ / ☑ 复选框（用于投递前核对清单）

简历模块无关——任意组合「教育经历 / 项目经历 / 专业技能 / 资格证书 / 培训经历 / 语言能力 / 个人作品 / 学生干部经历 / 自我评价」等通用 markdown 标签均可正常渲染。

### 依赖安装（隔离 venv，不污染用户环境）
```bash
python -m venv .venv
.venv/Scripts/pip install reportlab python-docx pypdf markdown
.venv/Scripts/python scripts/extract_text.py resume.docx resume.txt
.venv/Scripts/python scripts/resume_to_pdf.py 优化后简历.md
```
> 本机已预置隔离 venv：`C:\Users\李铭壕\.workbuddy\binaries\python\envs\default`，含上述依赖，可直接用其 python 执行脚本。

## References

- `references/optimization-guide.md`：JD 解析清单、STAR 简历法、诊断卡/匹配卡、关键词对齐、措辞升级、量化规则、求职信与面试准备、诚实边界、避雷清单。
- `assets/resume_template.md`：干净的 Markdown 简历结构模板。
- `assets/cover_letter_template.md`：求职信模板。
- `assets/interview_prep_template.md`：面试准备模板。
