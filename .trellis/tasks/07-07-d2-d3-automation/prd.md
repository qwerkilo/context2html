# PRD: D2/D3 自动化检查

## 目标

实现 D2（段落结构）和 D3（信息密度）的自动化检查，填补验证器空白。

## 背景

- D1/D4/D5 已有自动化检查，标注为 warnings
- D2（段落骨架模板）和 D3（信息密度交替）目前仅依赖人工审查
- 逻辑定义在 `humanize_matrix.md` 的 #6-#9（D2）和 #10-#12（D3）

## 验收标准

1. `check_d2_paragraph_structure(html)` 在 `scripts/checks/report.py` 和 `context2html/validator/report.py` 中实现，检测：
   - 相邻两段同结构（数据→阐释 vs 数据→阐释）
   - 连续段落以"值得注意的是"等 AI 连接词开头
   - 每段结尾为总结句模板（"这显示了..."）
   - "综上所述"等模板化总结句
2. `check_d3_info_density(html)` 在上述两个文件中实现，检测：
   - 连续两段以上高信息密度（每句跟数据）
   - 连续两段以上低密度（空话连篇）
   - 缺少过渡段导致密度无交替
3. 两个新检查注册到 `validate-report.py` 的 warnings 列表
4. 测试通过

```
