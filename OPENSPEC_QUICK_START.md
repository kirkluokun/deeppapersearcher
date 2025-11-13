# OpenSpec 快速开始提示词

在开始工作前，请先了解本项目使用 OpenSpec 进行规范驱动开发。

## 核心命令

```bash
openspec list --specs          # 查看所有规范
openspec list                  # 查看进行中的变更
openspec show <item>           # 查看详细信息
openspec validate <change-id> --strict  # 验证格式
```

## 工作流程

1. **查看现有规范**：`openspec list --specs` 了解已实现的功能
2. **创建变更提案**：新功能/重大变更需要先创建 proposal（参考 `openspec/changes/add-arxiv-all-categories/`）
3. **实施任务（Stage 2）**：使用实施模板（见下方）按照 `tasks.md` 中的清单逐步实现
4. **归档变更**：完成后使用 `openspec archive <change-id> --yes`

## Stage 2 实施模板

实施 change proposal 时，使用以下提示词：

```
请按照 OpenSpec Stage 2 流程实现 <change-id>：

1. 阅读 @openspec/changes/<change-id>/proposal.md - 理解需求背景
2. 阅读 @openspec/changes/<change-id>/design.md - 了解技术决策（如果存在）
3. 阅读 @openspec/changes/<change-id>/tasks.md - 按顺序实施任务清单
4. 阅读 @openspec/changes/<change-id>/specs/<capability>/spec.md - 理解详细场景

要求：
- 严格按照 tasks.md 中的顺序逐项完成
- 每完成一个任务后确认功能正常再进入下一项
- 所有任务完成后，更新 tasks.md 将所有项标记为 [x]
- 实现过程中如有疑问，优先参考 design.md 中的技术决策
- 确保遵循 specs/<capability>/spec.md 中定义的所有场景
```

**示例**：实现 `add-arxiv-all-categories` 时，将 `<change-id>` 替换为 `add-arxiv-all-categories`，`<capability>` 替换为 `arxiv-search`。

详细模板和更多示例请查看：`openspec/IMPLEMENTATION_TEMPLATE.md`

## 重要规则

- ✅ **需要 proposal**：新功能、架构变更、破坏性变更
- ❌ **不需要 proposal**：bug 修复、拼写错误、注释更新
- 📝 **规范格式**：使用 `## ADDED/MODIFIED/REMOVED Requirements`，每个需求至少一个 `#### Scenario:`
- 📚 **详细文档**：查看 `openspec/AGENTS.md` 获取完整指南

## 项目结构

- `openspec/specs/` - 已实现的规范（真相）
- `openspec/changes/` - 进行中的变更提案
- `openspec/changes/archive/` - 已完成的变更

开始工作前，先运行 `openspec list` 了解项目当前状态。

