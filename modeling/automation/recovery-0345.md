# 第一次执行的恢复记录

- 第01批模型与检查点已经保存；执行器在批次结束读取progress.json时遇到UTF-8 BOM，报错并退出。进程消失及runner_error均已确认，属于终止错误。
- 将执行器所有状态/进度JSON读取统一为utf-8-sig，兼容Windows PowerShell写出的BOM，同时仍接受无BOM的UTF-8。
- 当前额度预检查成功，五小时剩余22%，高于5%停止阈值。
- 通过已有的03:30计划任务启动同一执行器，恢复原thread_id与进度；未创建第二个同时写场景的实例。08:40任务继续使用相同的已修复脚本。
- 原场景的外壳正确变换/实际尺寸已独立复核，参见references/batch01_independent_review.md；后续先补充明确的后视端口渲染，再做PCB装配。
