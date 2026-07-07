# PRD: 扩展测试覆盖

## 目标

为新实现的 D2/D3 检查添加单元测试，确保新的 humanization 维度有完整测试覆盖。

## 背景

- 已完成 D1/D4/D5 的自动化单元测试（TestD1SentenceLength, TestD4Connectors, TestD5TermVariety）
- D2 和 D3 刚实现，尚无测试覆盖
- 测试模式遵循 `test_validate_report.py` 中的模式（class + 多种案例）

## 验收标准

1. `TestD2ParagraphStructure` 测试类包含：
   - 空 HTML 跳过
   - 相邻同结构检测
   - 总结句结尾检测
   - 干净文本通过
2. `TestD3InfoDensity` 测试类包含：
   - 空 HTML 跳过
   - 连续高密度检测
   - 连续低密度检测
   - 交替段落通过
3. 全部 443+ 测试通过
