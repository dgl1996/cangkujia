# 仓酷家部署任务清单

## Phase 1: 服务器基础环境（预计2小时）

- [ ] Task 1.1: 登录腾讯云轻量服务器并更新系统
  - [ ] 使用SSH登录服务器
  - [ ] 运行apt update && apt upgrade
  - [ ] 安装基础依赖：nginx git python3-pip python3-venv

- [ ] Task 1.2: 创建项目目录结构
  - [ ] 创建/var/www/cangkujia/目录
  - [ ] 创建frontend/、backend/、static/子目录
  - [ ] 设置目录权限

- [ ] Task 1.3: 配置Python虚拟环境
  - [ ] 创建venv虚拟环境
  - [ ] 安装依赖：fastapi uvicorn[standard] psycopg2-binary python-jose python-multipart requests
  - [ ] 测试Python环境

- [ ] Task 1.4: 配置Swap分区
  - [ ] 创建2G Swap文件
  - [ ] 启用Swap
  - [ ] 配置开机自动挂载

## Phase 2: COS模型存储（预计3小时）

- [ ] Task 2.1: 创建COS存储桶
  - [ ] 登录腾讯云控制台
  - [ ] 创建存储桶（上海地域，名称cangkujia-models）
  - [ ] 配置公有读权限
  - [ ] 开启CDN加速

- [ ] Task 2.2: 上传GLB模型文件
  - [ ] 安装coscmd工具
  - [ ] 配置COS密钥
  - [ ] 上传80个GLB模型到/standard/目录
  - [ ] 验证上传完整性

- [ ] Task 2.3: 配置前端模型加载路径
  - [ ] 修改ThreeScene.vue模型加载逻辑
  - [ ] 添加COS域名配置
  - [ ] 测试模型加载

## Phase 3: 后端部署（预计4小时）

- [ ] Task 3.1: 配置FastAPI应用
  - [ ] 更新main.py添加健康检查接口
  - [ ] 配置CORS允许跨域
  - [ ] 添加环境变量读取

- [ ] Task 3.2: 集成Supabase数据库
  - [ ] 创建Supabase项目
  - [ ] 创建数据库表结构
  - [ ] 配置数据库连接
  - [ ] 测试数据库连接

- [ ] Task 3.3: 集成Clerk认证
  - [ ] 创建Clerk应用
  - [ ] 配置微信登录
  - [ ] 添加JWT验证中间件
  - [ ] 测试认证流程

- [ ] Task 3.4: 配置微信支付
  - [ ] 配置微信支付参数
  - [ ] 创建支付订单接口
  - [ ] 配置回调处理
  - [ ] 测试支付流程

- [ ] Task 3.5: 启动Uvicorn服务
  - [ ] 配置systemd服务
  - [ ] 启动服务并设置开机自启
  - [ ] 测试API接口

## Phase 4: Nginx配置（预计3小时）

- [ ] Task 4.1: 申请SSL证书
  - [ ] 使用腾讯云免费证书
  - [ ] 下载证书文件
  - [ ] 上传到服务器/etc/nginx/ssl/

- [ ] Task 4.2: 配置Nginx
  - [ ] 创建cangkujia配置文件
  - [ ] 配置HTTPS 443端口
  - [ ] 配置HTTP 80跳转
  - [ ] 配置API反向代理
  - [ ] 配置COS模型代理

- [ ] Task 4.3: 构建前端项目
  - [ ] 本地构建Vue3项目
  - [ ] 上传dist文件到服务器
  - [ ] 配置Nginx静态文件服务

- [ ] Task 4.4: 测试部署
  - [ ] 测试HTTPS访问
  - [ ] 测试API接口
  - [ ] 测试模型加载

## Phase 5: 第三方服务集成（预计2小时）

- [ ] Task 5.1: Clerk应用配置
  - [ ] 创建Clerk应用（cangkujia）
  - [ ] 配置允许的回调URL
  - [ ] 获取Publishable Key和Secret Key
  - [ ] 配置微信登录

- [ ] Task 5.2: Supabase项目配置
  - [ ] 创建Supabase项目
  - [ ] 创建users、orders、user_licenses表
  - [ ] 配置RLS策略
  - [ ] 获取URL和Key

- [ ] Task 5.3: 微信支付配置
  - [ ] 配置回调URL
  - [ ] 上传API证书
  - [ ] 测试支付回调

## Phase 6: 验证与优化（预计2小时）

- [ ] Task 6.1: 功能验证
  - [ ] 验证首页访问
  - [ ] 验证2D工作台
  - [ ] 验证3D场景
  - [ ] 验证模型加载
  - [ ] 验证登录功能
  - [ ] 验证支付功能

- [ ] Task 6.2: 性能优化
  - [ ] 配置Nginx gzip压缩
  - [ ] 配置浏览器缓存
  - [ ] 配置日志轮转
  - [ ] 监控内存使用

- [ ] Task 6.3: 备份配置
  - [ ] 备份Nginx配置
  - [ ] 备份环境变量
  - [ ] 创建部署文档

# 任务依赖关系

```
Phase 1 (基础环境)
    ↓
Phase 2 (COS存储) → Phase 3 (后端部署)
    ↓                    ↓
Phase 4 (Nginx配置) ←──┘
    ↓
Phase 5 (第三方集成)
    ↓
Phase 6 (验证优化)
```

# 预计总时间

- 总预计时间：约16小时
- 可分阶段执行，每阶段独立可验证
