# 跨 Agent 使用指南（Codex / 豆包 / Claude / 任意 agent）

`resume-optimizer` 的核心方法论、模板、Python 脚本**与 WorkBuddy 平台无关**。
只有 `SKILL.md` 的 YAML frontmatter 和"截图多模态读图"这两处是 WorkBuddy 专属外壳，
正文工作流、参考文献、模板全部是通用 Markdown / Python，任何 agent 都能复用。

---

## 一、这个 skill 由什么组成（平台中立性拆解）

| 文件 | 平台绑定 | 说明 |
|---|---|---|
| `references/optimization-guide.md` | 无 | 方法论（JD 解析、STAR 改写、诊断卡/匹配卡、诚实护栏），纯文本 |
| `scripts/extract_text.py` | 无 | 提取 .md/.docx/.pdf 文本，纯 Python |
| `scripts/resume_to_pdf.py` | 无 | Markdown -> 中文 PDF，纯 Python + reportlab |
| `assets/*.md` | 无 | 简历/求职信/面试准备模板，纯 Markdown |
| `SKILL.md` 正文 | 无 | 工作流描述，任何 agent 都能读懂并执行 |
| `SKILL.md` 的 YAML frontmatter | **WorkBuddy 专属** | name/description 触发元数据，其他 agent 忽略即可 |
| "截图多模态读图" | WorkBuddy 特有能力 | 其他支持多模态的 agent（豆包/GPT-4o/Claude）等价替换；不支持的退化成"粘贴文本 / 上传文件" |

**结论**：把 `references/` `scripts/` `assets/` 三个目录 + `SKILL.md` 正文丢给任意 agent，它就能干活。

---

## 二、按 agent 能力分两类接入

### A 类：能读文件 + 执行本地命令/Python（推荐）

代表：Codex、Claude Code、本地 agent、Coze 代码节点、有 Terminal 的 agent。

接入方式：让 agent **直接读 `SKILL.md` 然后按工作流调用脚本**。

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 提取简历 / JD 文本（可选，若用户给的是文件）
python scripts/extract_text.py 简历.pdf resume.txt
python scripts/extract_text.py JD.pdf jd.txt

# 3. 让 agent 按 SKILL.md 流程产出优化后简历.md / 优化说明.md / 求职信.md / 面试准备.md

# 4. 渲染 PDF
python scripts/resume_to_pdf.py 优化后简历.md 优化后简历.pdf
python scripts/resume_to_pdf.py 优化说明.md 优化说明.pdf
```

给这类 agent 的指令示例（直接粘贴即可）：

> 请按仓库里的 `SKILL.md` 工作流，用 `references/optimization-guide.md` 方法论和
> `assets/` 模板，处理我提供的 JD 和简历。先读 `SKILL.md` 和 `references/optimization-guide.md`，
> 产出 Markdown，再用 `scripts/resume_to_pdf.py` 渲染 PDF。

### B 类：只能聊天、不能跑脚本（纯提示词版）

代表：豆包网页版、ChatGPT 网页版、Claude 网页版等**无本地代码执行**的聊天 agent。

这类 agent 跑不了 Python，所以用 `prompt-only/` 目录里的**纯提示词版**：
把方法论浓缩成一段 system prompt，让 agent 在对话里直接生成 Markdown 简历与说明，
用户自己复制去转 PDF（也可把 Markdown 交给 A 类 agent / 本地跑 `resume_to_pdf.py`）。

用法：
1. 打开 `prompt-only/SYSTEM_PROMPT.md`，复制全文作为 system prompt（或首条长指令）。
2. 把你的 JD 原文 + 简历原文粘贴进对话。
3. agent 按提示词产出优化后简历 + 诊断卡/匹配卡 +（可选）求职信 + 面试准备。
4. 想要 PDF：把 agent 输出的 Markdown 保存为 `.md`，用 A 类方式或本地 `python scripts/resume_to_pdf.py xxx.md xxx.pdf` 转即可。

---

## 三、不可移除的部分（无论哪个 agent）

- **诚实护栏**：绝不虚构公司/职位/时间/数据；JD 关键词只在你确实具备时才写入正文；
  缺失量化数字用 `[待补充]` 占位；不删除真实经历。这是 skill 的底线，移植时一并保留。
- **中文 PDF 字体**：`resume_to_pdf.py` 自动优先用系统微软雅黑，否则回退内置 STSong-Light；
  在非 Windows 平台若无微软雅黑，中文仍可用 STSong-Light 正常显示（无需额外装字体）。

---

## 四、一个 agent 接好的最小检查清单

- [ ] agent 能读到 `SKILL.md` 正文 + `references/optimization-guide.md`
- [ ] A 类：能调用 `scripts/resume_to_pdf.py`；B 类：用户手头有 `prompt-only/SYSTEM_PROMPT.md`
- [ ] 产出含：优化后简历 + 诊断卡/匹配卡
- [ ] 未出现"编造 JD 工具栈/年限"等注水内容
- [ ] 中文 PDF 标题、表格、复选框渲染正常
