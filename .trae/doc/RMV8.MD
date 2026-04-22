
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
| 模块2：案例库 | ✅ 验收通过 | 左侧面板新增"🏗️ 案例库"区块，动态读取/cases/cases.json，2个占位案例 |
| 模块3：工作台顶部栏 | ✅ 验收通过 | 版本标签（免费版灰色/Pro版绿色）、升级Pro按钮、退出修复 |
| 模块4：保存+导出报告双拦截 | ✅ 验收通过 | 核心转化点，Free用户保存/报告被拦截，弹出4档定价弹窗 |
| 模块5.1：本地模拟支付闭环 | ✅ 验收通过 | 本地跑通完整变现演示：选择档位→模拟支付→自动变Pro→正常保存 |
| 模块5.2：真实微信支付对接 | 🟡 待部署 | 条件：部署到cangkujia666.com后，对接微信商户号1743582175 |

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

【本地测试Pro状态】
- 设置为Free：localStorage.setItem('cangkujia_user_plan', 'free')
- 设置为Pro：localStorage.setItem('cangkujia_user_plan', 'pro')
- 刷新页面生效
```

### 五、本地变现演示流程（模块5.1验证清单）

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 确认Free状态 + 刷新 | 顶部栏显示「免费版」灰色标签 + 「🔥升级Pro」按钮 |
| 2 | 放置3D对象 → 点击「保存」 | 弹出升级弹窗，年付¥168默认选中（橙色边框高亮） |
| 3 | 点击「立即升级」 | 切换到模拟支付页，显示年付¥168 + 微信支付标题 |
| 4 | 点击「取消支付」 | 返回定价选择页，弹窗不关闭，可重新选择 |
| 5 | 点击「模拟支付成功」 | 提示"🎉支付成功"，页面自动刷新 |
| 6 | 刷新后 | 顶部栏显示「Pro版」绿色标签，升级按钮消失 |
| 7 | 点击「保存」 | 正常下载.ckj文件，无弹窗拦截 |
| 8 | 点击「报告」 | 正常导出项目实施清单，无弹窗拦截 |

### 六、下一步行动

**模块5.2（真实微信支付对接）启动条件：**
1. CEO执行 `./deploy.sh` 将代码部署到 `https://cangkujia666.com`
2. 确认线上环境可正常访问

**模块5.2开发内容：**
- 替换模拟支付为真实微信JSAPI支付（复用商户号1743582175）
- 后端创建 `/api/payment/create-order` 和 `/api/payment/callback`
- 支付成功后后端写入Supabase subscriptions表，替代localStorage本地状态
- 接入真实用户身份与到期管理

---

## V8.1 商业化变现专题 - 部署上线进度（2026-04-22）

### ✅ 已完成并上线（https://www.cangkujia666.com）

| 模块 | 状态 | 说明 |
|------|------|------|
| 模块1：注册/登录页优化 | ✅ 已上线 | Clerk邮箱+密码登录，升级引导文案，Pro版标签 |
| 模块2：案例库 | ✅ 已上线 | 左侧面板2个占位案例（电商标准仓/冷链仓储），动态读取cases.json |
| 模块3：顶部栏改造 | ✅ 已上线 | 免费版标签+🔥升级Pro按钮+定价弹窗+退出修复 |
| 模块4：保存/导出拦截 | ✅ 已上线 | 核心转化点，Free用户仅限制保存和导出报告 |
| 模块5.1：模拟支付闭环 | ✅ 已上线 | 4档定价（月付¥19.9/季付¥49/半年¥89/年付¥168），模拟支付流程 |
| 服务器部署 | ✅ 已完成 | 代码部署到腾讯云服务器，域名cangkujia666.com可访问 |

### 🔧 基础设施配置（已完成）

- **SSH连接GitHub**：服务器ed25519密钥配置成功，deploy.sh一键部署工作流建立
- **Nginx配置**：80/443端口均指向正确dist目录，assets强缓存已删除
- **Clerk Production环境**：域名cangkujia666.com已验证，API Keys已配置
- **前端环境变量**：deploy.sh自动写入Production Publishable Key

### 🐛 已知问题与修复记录

- **[已修复]** 登录页Clerk组件无法加载 → 服务器frontend/.env写入Production Key
- **[已修复]** 首页背景图缺失 → 图片提交并重新部署
- **[已确认]** Clerk新设备登录验证为强制安全策略，无法关闭（同一设备后续免验证）

### ⏳ 下一步：模块5.2 真实微信支付对接

- 复用商户号1743582175
- 后端FastAPI支付接口开发（create-order/callback）
- 微信支付证书上传
- 支付成功后自动升级Pro用户状态

---

**最后更新**: 2026-04-22 - V8.1全部模块已部署上线，等待模块5.2真实支付对接

