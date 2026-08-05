<div align="center">

# 🎯 面向职位简历优化

### workbuddy-resume-optimizer · 简历定向优化 Skill

针对**具体招聘 JD（职位描述）**定向微调简历的 [WorkBuddy](https://www.codebuddy.cn) Skill。
核心方法论、模板、Python 脚本**与平台无关**，也可被 Codex / 豆包 / Claude 等任意 agent 复用，
见文末「在其他 agent 中使用」与 [`PORTABILITY.md`](./PORTABILITY.md)。

输入一份 JD 和你的原简历，输出：

- **优化后简历（PDF）** —— 只做关键词对齐 + 措辞打磨，保留原结构、不改顺序、不虚构。
- **优化说明（PDF）** —— 结构化「诊断卡」（JD 硬性要求 vs 你现状）+「匹配卡」（原词 → JD 词 → 命中类型），含缺口与投递前核对清单。
- **求职信（可选）** —— 针对该岗位的求职信；跨领域投递时坦诚转岗动机。
- **面试准备（可选）** —— 高频问题应答 + STAR 故事库 + 缺口预案 + 反向提问清单。

---

## 特性

- **JD 解析**：拆成硬性门槛 / 核心技能 / 职责 / 优先项 / 软技能 / ATS 关键词。
- **STAR 强制改写流程**：每条经历走 Situation / Task / Action / Result，优先补量化 Result。
- **真实 PDF 交付**：用 `reportlab` 渲染中文简历与说明，蓝头斑马纹真表格、自适应列宽、链接可点击。
- **多模态输入**：粘贴文本、截图（WorkBuddy 多模态读图取字）、上传 `.md` / `.docx` / `.pdf`。
- **多模块兼容**：通用 Markdown → PDF 渲染器，对任意简历模块标签（资格证书 / 专业技能 / 培训经历 / 语言能力 / 个人作品 / 学生干部经历 …）均正常。
- **诚实护栏**：绝不虚构公司 / 职位 / 时间 / 数据；未提供的量化数字用 `[待补充]` 占位；可能具备但未写明的能力只在报告提示，不进简历正文。

## 安装（WorkBuddy）

```bash
# 1. 克隆到 WorkBuddy 用户级 skills 目录
git clone https://github.com/baihuaqishi/workbuddy-resume-optimizer.git \
  ~/.workbuddy/skills/resume-optimizer

# 2. 安装 Python 依赖（建议使用隔离 venv）
pip install -r requirements.txt
```

## 用法（WorkBuddy）

在 WorkBuddy 对话中说，例如：

> 根据这份 JD 优化我的简历

然后贴出 JD 文本 + 原简历（或拖入 `.md` / `.docx` / `.pdf` 文件 / 截图）。Skill 自动跑完并交付 PDF + 说明。

## 目录结构

```
resume-optimizer/
├── SKILL.md                      # 入口：用途、触发词、工作流、诚实边界（YAML frontmatter 为 WorkBuddy 专属）
├── README.md                     # 本文件
├── PORTABILITY.md                # 跨 agent 使用指南（Codex / 豆包 / Claude …）
├── requirements.txt              # Python 依赖清单
├── references/
│   └── optimization-guide.md     # 核心方法论：JD 解析、STAR、诊断卡/匹配卡、避雷
├── scripts/
│   ├── extract_text.py           # .md/.docx/.pdf → 文本
│   └── resume_to_pdf.py          # Markdown → 中文 PDF（真表格）
├── assets/
│   ├── resume_template.md        # 简历骨架模板
│   ├── cover_letter_template.md  # 求职信模板
│   └── interview_prep_template.md# 面试准备模板
└── prompt-only/
    └── SYSTEM_PROMPT.md          # 纯提示词版（给无脚本执行能力的聊天 agent：豆包 / ChatGPT / Claude 网页版）
```

## 在其他 agent 中使用（Codex / 豆包 / Claude …）

本 skill 除 `SKILL.md` 的 YAML 触发头和「截图多模态读图」外，**完全平台中立**。
按 agent 能力分两类接入：

- **A 类（能跑脚本）**：Codex、Claude Code、本地 agent、Coze 代码节点。
  让 agent 读 `SKILL.md` 正文 + `references/optimization-guide.md`，用 `scripts/` 调用 Python。
  详见 [`PORTABILITY.md`](./PORTABILITY.md#二按-agent-能力分两类接入)。
- **B 类（纯聊天）**：豆包网页版、ChatGPT 网页版、Claude 网页版等**无本地代码执行**的 agent。
  用 [`prompt-only/SYSTEM_PROMPT.md`](./prompt-only/SYSTEM_PROMPT.md) 作为 system prompt，
  agent 在对话里直接产出 Markdown，用户自行用 `scripts/resume_to_pdf.py` 转 PDF。

## 诚实边界

本 Skill 的硬规则：**只优化，不注水**。

- 不重排简历结构、不改变项目顺序。
- 不向简历正文添加你未实际具备的 JD 关键词。
- 不虚构任何经历、数据或时间。
- 当 JD 与简历硬性不匹配时，会在说明中**明确告知不建议投递**，并给出补足路径，而非伪造匹配。

## License

MIT
