**Purpose**: 帮助 AI 代码助手快速理解并在此代码库中高效工作：架构要点、常用命令、项目特有约定与变更风险点。

**Project Overview**:
- **简介**: 本仓库是一个用于把 D&D 5e 英文 JSON 数据本地化为简体中文的翻译/处理管线，集成了 embedding（Chroma）、LLM 翻译、和数据库（MySQL/Redis）存储。
- **主要目录**:
  - `main.py`: CLI 入口，常用子命令：`translate`、`embed`、`search`、`transform`。
  - `app/`: 应用实现。注意 `app/core/translator/` 下有翻译流水线（`JobProcessor`、`LLMFactory`、`siliconflow_adapter`）。
  - `config/settings.py`: 全局配置与 LLM 提示模板（PROMOT_*）、正则、常量（如 `BESTIARY_FILE_MAP`、`RETRY_TIMES`）。
  - `app/core/utils/`：包含 `Job`（占位符处理/验证）、解析工具与状态枚举等。
  - `app/core/embedding/`：embedding 实现（`SiliconAIEmbeddings`，使用 `DS_KEY` + `netease-youdao/bce-embedding-base_v1`）。
  - `output/`、`output-tmp/`: 翻译结果输出目录结构。

**How to run (developer quick commands)**:
- 安装依赖:
```bash
pip install -r requirements.txt
```
- 配置 `.env`（必需）: 参见 `README.md`，关键变量：`CHM_ROOT_DIR`、`CHROMA_PERSIST_DIR`、`5ETOOLS_EN_PATH`、`OUTPUT_PATH`、`DS_KEY`、MySQL 配置（`DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_DATABASE`）。
- 运行翻译主流程（小批量调试请用 `--thread_num 1`）:
```bash
python main.py translate --en /path/to/data --thread_num 1 --byhand
```
- 运行 embedding（先运行一次）:
```bash
python main.py embed --dir "/data/DND5e_chm/xxx"
```
- 搜索/验证召回:
```bash
python main.py search --query "关键词"
```

**Key patterns & conventions (must-know for edits)**:
- 占位符格式: 所有需要保留/对齐的占位符都采用 `{@tag value}`。翻译后必须**保持占位符数量与英文一致且顺序不变**。
  - 检查点：`app/core/utils/job.py` 中 `validate()` / `__replace_sub_jobs()` 做数量与结构校验。
  - 正则与常量定义在 `config/settings.py`：`SUBJOB_PATTERN`, `ONLY_SUBJOB_PATTERN`, `TAG_PATTERN`。
- LLM 交互:
  - 系统提示模板在 `config/settings.py`（`PROMOT`, `SIMPLE_PROMOT`, `PROMOT_KNOWLEDGE`, `PROMOT_CORRECT_TAG` 等）。修改提示文本请仅改 `settings.py` 中模板。
  - 用户消息（payload）由 `Job.to_llm_question()` 生成（不同情形会返回不同 JSON 结构，例如 `{"parents":..., "reference":..., "trans_str":...}`）。LLM 适配器 `app/core/translator/siliconflow_adapter.py` 的 `sendText()` 使用 `langchain` 的 `SystemMessage` + `HumanMessage` 发送（system=PROMOT_*, user=payload string）。
- 并发/重试:
  - LLM 多线程由 `app/core/translator/llm_factory.py` 控制。错误重试逻辑在 `LLMFactory.reset_job`（最大尝试次数约为 3，会记录 error_count）。另外全局 `RETRY_TIMES` 在 `config/settings.py`。
- Embedding:
  - `app/core/embedding/silicon_embeddings.py` 使用 `DS_KEY` 与 `netease-youdao/bce-embedding-base_v1`。Embedding 存储/召回逻辑在 `app/cli` 的 Chroma 相关命令里。

**Where to change behavior safely**:
- 修改 LLM 提示（目的性语言）: 编辑 `config/settings.py` 的 PROMOT_ 模板。
- 修改 LLM 请求/响应封装: 编辑 `app/core/translator/siliconflow_adapter.py`（发送/解析、错误处理、节流）。
- 修改占位符校验/替换策略: 编辑 `app/core/utils/job.py` 的 `to_llm_question()`（payload 结构）和 `__replace_sub_jobs()`（校验/替换逻辑）。记得同时更新 `PROMOT_CORRECT_TAG` 的期望输入/输出格式。
- 修改并发/重试: 编辑 `app/core/translator/llm_factory.py`（线程/队列/重试计数逻辑）。

**Examples / concrete snippets to consult**:
- 生成 prompt: `Job.to_llm_question()`（`app/core/utils/job.py`） → 返回 `(json_str, PROMOT_ ...)`。
- LLM 发送: `SiliconFlowAdapter.sendText(text, promot)`（`app/core/translator/siliconflow_adapter.py`）使用 `ChatOpenAI` 的 `invoke`。
- 并发消费: `LLMFactory.start_work()` 与 `kimi_work` 中会根据 `TranslatorStatus` 决定 `reset_job` 或 `done_job`。

**Testing & debugging tips**:
- 本地调试先使用 `--thread_num 1` 与 `--byhand`，便于观察单条 Job 的输入输出。
- 日志文件位于 `log/`，日志器配置在 `logger_config.py`。
- 小范围回归：在 `main.py` 的 pipeline 中通过 `--en` 指定单个文件或子目录来缩小测试范围。
- 如果修改占位符逻辑，编写一个短脚本创建 `Job` 实例并调用 `to_llm_question()` 与 `validate()` 进行单元级验证。

**Common pitfalls & gotchas**:
- 若缺少 `.env` 中的 `DS_KEY` 或未部署本地 Chroma/数据库，流程会失败/不可用。
- 不要在 PROMOT_* 中加入会改变占位符顺序或自动替换的示例（会误导 LLM）。
- 占位符错位通常出现在把 `last_answer` 直接覆盖 `cn_str` 的场景（检查 `Job.to_llm_question()` 的重试分支）。

如果你想，我可以：
- 把本指南合并为仓库的 Pull Request；或
- 基于此生成一个短的 PR 模板/变更清单，帮助后续修改（例如：修改 PROMOT_CORRECT_TAG 需要配套变更的文件列表）。

请告诉我是否需要把某一部分展开为更详细的修改步骤或示例代码片段。