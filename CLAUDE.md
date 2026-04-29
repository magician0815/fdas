# 上下文管理规则

## 本项目特殊要求

- 优先使用 memory 系统记录长期信息
- 大型工具输出（如完整文件内容）仅保留关键摘要
- 多步骤任务完成后主动使用 /compact
- 使用 /context-budget 定期检查上下文消耗
- 优先使用 context7 (/docs) 获取文档而非预加载

## 压缩策略

根据任务类型选择压缩级别：

- `/compact` 或 `/compact full` - 完整压缩（默认）
- `/compact debug` - 保留调试信息（排查问题时使用）
- `/compact minimal` - 最小化压缩

## 注意事项

- 不主动过滤错误详情（traceback）- 可能影响问题排查
- Debug/排查问题时保留完整输出
- 正常开发时可精简工具输出