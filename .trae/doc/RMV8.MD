
---

## 仓酷家V8.1商业化变现专题 - 2026.04.21 进度总结

### 一、总体目标
建立本地开发→Git管理→服务器部署的正规工作流，完成仓酷家商业化变现5模块开发，实现"免费体验+付费保存"的核心商业模式。

### 二、执行方案

| 阶段 | 行动 |
|------|------|
| 环境重建 | 服务器代码下载→本地清理→Git初始化→推送GitHub |
| 源码恢复 | 从V7.1恢复Vue 3前端源码到V8.1，补齐3D模型和静态资源 |
| Clerk配置 | Production环境（线上）+ Development环境（本地），均关闭邮箱验证 |
| 模块开发 | 按顺序执行5个模块，本地测试→Git推送→验收→下一模块 |
| 部署规范 | 禁止SSH服务器改代码，本地build测试通过后统一部署 |

### 三、当前进度

| 模块 | 状态 | 关键成果 |
|------|------|----------|
| 环境搭建 | ✅ 完成 | 本地V8.1仓库、GitHub私有仓库、Git代理（v2rayN:10809） |
| 源码恢复 | ✅ 完成 | Vue 3源码从V7.1恢复，模型文件归位到public/assets/models/ |
| Clerk双环境 | ✅ 完成 | Development Key配置.env.local，Production Key用于线上，均无邮箱验证 |
| 模块1：注册/登录页优化 | ✅ 验收通过 | SignIn.vue/SignUp.vue添加升级引导文案+Pro版¥168标签 |
| 模块2：案例库 | 🟡 待开发 | 左侧面板动态读取/cases/cases.json |
| 模块3：工作台顶部栏 | 🔴 未开始 | 版本标签（免费版/Pro版）、保存/加载按钮 |
| 模块4：保存拦截弹窗 | 🔴 未开始 | 核心转化点，4档定价默认年付168元 |
| 模块5：支付流程 | 🔴 未开始 | 复用微信支付商户号1743582175 |

### 四、关键配置信息

```
【本地开发】
- 代码路径：C:\Users\dgl19\Desktop\OPC\cangkujia V8.1
- 启动命令：cd frontend && pnpm install && pnpm run dev
- 访问地址：http://localhost:5173（或5174）
- Clerk Development Key：pk_test_Y2hlZXJmdWwtZmx5LTc0LmNsZXJrLmFjY291bnRzLmRldiQ
- .env.local：VITE_CLERK_PUBLISHABLE_KEY=Development_Key

【Git推送】
- 代理配置：git config --global http.proxy http://127.0.0.1:10809
- 仓库地址：https://github.com/dgl1996/cangkujia.git

【Clerk后台】
- Production：cangkujia666.com（线上使用，关闭邮箱验证）
- Development：cheerful-fly-74.clerk.accounts.dev（本地开发使用，关闭邮箱验证+关闭泄露密码检测）

【定价策略（严格4档）】
- 月付：¥19.9
- 季付：¥49
- 半年：¥89（🏷️推荐）
- 年付：¥168（🔥最佳性价比，默认选中）
```

### 五、下一步行动
1. trae执行模块2（案例库）开发
2. CEO制作2个案例文件（电商仓、冷链仓），导出.ckj上传到服务器/cases/目录
3. 模块2验收通过后继续模块3→4→5

---

**最后更新**: 2026-04-21 - 商业化变现专题启动，模块1完成，Clerk双环境配置完成

