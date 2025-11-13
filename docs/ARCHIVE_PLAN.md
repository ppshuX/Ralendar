# 📦 文档归档计划

## 📊 当前状况

- **文档总数**: 64个
- **Python代码**: 57个文件
- **问题**: 文档比代码还多 😅

## 🎯 归档策略

### 1. 归档到 `docs/archive/` 目录

#### 开发日志（daily_logs）- 可归档
这些是历史开发记录，对当前开发帮助不大：

- `Day10_SUMMARY.md` - 早期总结
- `Day12_ACWING_LOGIN.md` - 历史实现记录
- `Day13_WEB_ACWING_LOGIN.md` - 历史实现记录
- `Day14_QQ_LOGIN_AND_CLEANUP.md` - 历史实现记录
- `Day15_CODE_REFACTORING.md` - 历史重构记录
- `Day15_SUMMARY.md` - 历史总结
- `Day16_FINAL_SUMMARY.md` - 历史总结
- `Day16_MAJOR_FEATURES_AND_INTEGRATION.md` - 历史总结
- `Day17_QQ_UNIONID_AND_CLEANUP.md` - 历史记录
- `Day18_AUTH_REQUIREMENT_BEFORE_ROAMIO_INTEGRATION.md` - 历史记录
- `Day18_SUMMARY_ROAMIO_INTEGRATION_SUCCESS.md` - 历史总结
- `Day19_EMAIL_REMINDER_SUCCESS.md` - 历史记录
- `Day20_WEATHER_AND_FORTUNE_INTEGRATION.md` - 历史记录

**保留**: 只保留最新的1-2个日志作为参考

#### 计划文档（plans）- 可归档
如果计划已完成或已过时：

- `Day15_PLAN.md` - 已完成
- `MAP_INTEGRATION_PLAN.md` - 检查是否完成
- `CALENDAR_SHARING_PLAN.md` - 检查是否完成
- `AI_ASSISTANT_PLAN.md` - 检查是否完成
- `FUTURE_PLAN.md` - 合并到ROADMAP
- `PRODUCT_ROADMAP.md` - 保留，但定期更新

#### 集成文档（integration）- 合并重复
很多文档内容重复：

- `ROAMIO_INTEGRATION_GUIDE.md` - 保留（主文档）
- `ROAMIO_INTEGRATION_STATUS.md` - 合并到主文档
- `ROAMIO_QUICKSTART.md` - 保留（快速参考）
- `ROAMIO_DELIVERY_PACKAGE.md` - 归档（交付文档）
- `QQ_UNIONID_INTEGRATION.md` - 合并到ROAMIO_INTEGRATION_GUIDE
- `NEXT_STEPS_FOR_UNIONID.md` - 归档（已完成）
- `UNIONID_MATCHING_GUIDE.md` - 合并到QQ_UNIONID_INTEGRATION
- `API_ENDPOINT_CORRECTION.md` - 归档（历史问题）
- `RALENDAR_API_RESPONSE_TO_ROAMIO.md` - 归档（历史响应）
- `RALENDAR_EVENT_EDITING_GUIDE_FOR_ROAMIO.md` - 归档（交付文档）

#### 协作文档（collaboration）- 归档
这些是与Roamio团队的沟通记录：

- `RALENDAR_UPDATE_TO_ROAMIO.md` - 归档
- `REPLY_TO_ROAMIO_AI_UPDATE.md` - 归档

### 2. 保留的核心文档

#### 必须保留（10-15个）：
1. `README.md` - 项目入口
2. `INDEX.md` - 文档索引
3. `PROJECT_OVERVIEW.md` - 项目概览
4. `guides/DEPLOYMENT_GUIDE.md` - 部署指南
5. `guides/QUICK_START.md` - 快速开始
6. `guides/UWSGI_COMMANDS.md` - 运维命令
7. `integration/ROAMIO_INTEGRATION_GUIDE.md` - 集成指南（主文档）
8. `integration/ROAMIO_QUICKSTART.md` - 快速集成
9. `architecture/ARCHITECTURE.md` - 架构设计
10. `standards/API_NAMING.md` - API规范
11. `standards/AUTH_STANDARD.md` - 认证规范
12. `features/DJANGO_ADMIN_GUIDE.md` - 管理后台
13. `guides/ACWING_PLATFORM_CONFIG.md` - 平台配置
14. `guides/BAIDU_MAP_SETUP.md` - 地图配置

## 📋 执行步骤

1. 创建 `docs/archive/` 目录
2. 移动历史日志到 `docs/archive/daily_logs/`
3. 移动已完成计划到 `docs/archive/plans/`
4. 移动交付文档到 `docs/archive/delivery/`
5. 更新 `docs/INDEX.md` 移除归档文档链接
6. 合并重复的集成文档

## 🎯 目标

- **文档数量**: 从64个减少到15-20个核心文档
- **文档结构**: 更清晰，易于查找
- **维护成本**: 降低，只维护核心文档

