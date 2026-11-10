# Dictionary Builder Skill

让 Agent 为金融、电气工程等领域制作可持续维护的中英专业词典。交付源数据、两种排版的欧路 TXT、HTML 预览及打包说明，不要求复制计算机词条。

## 使用

1. 下载本仓库 ZIP 并解压。
2. 将完整 `skills/dictionary-builder` 文件夹放到你的 Agent 支持的技能目录；或让有本地文件访问能力的 Agent 读取其中的 SKILL.md 并执行。不要只发送 SKILL.md：脚本、模板和 references 都需要保留。
3. 给 Agent 一项任务，例如：

> 使用 dictionary-builder，为电气工程本科生制作 30 个电机学核心术语的中英词典，先展示 5 条样例，再完成源数据、简洁版和增强版，并告诉我如何导入欧路。

支持 Python 3.10+，构建无需第三方包或付费 API。生成词条的 Agent 本身需具备写文件、运行 Python 的能力；需要查证资料时还需网络访问。各 Agent 的安装入口不同，本项目不声称已在所有客户端验证。

## 能力与边界

- 领域、名称、版本、输出文件名可配置，词数不设上限。
- 生成独立工程，后续直接编辑 JSONL 并重新构建。
- .eudic 最后一步需 Windows 欧路构建器，当前不提供跨平台自动编译。
- 自动检查不代表专业内容已被专家审校。

本工具提取自 [CS-AI Dictionary](https://github.com/albertorson/CS-AI-Dictionary)，模板与 Skill 按 [CC BY-NC-SA 4.0](LICENSE) 发布。作者 albertorson，保留署名，仅许可非商业用途。它不是无条件商用的软件授权。
