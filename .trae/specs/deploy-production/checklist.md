# 仓酷家部署检查清单

## Phase 1: 服务器基础环境

- [ ] 服务器SSH登录成功
- [ ] 系统更新完成（apt update && apt upgrade）
- [ ] Nginx安装成功（nginx -v显示版本）
- [ ] Git安装成功（git --version显示版本）
- [ ] Python3和pip安装成功（python3 --version和pip3 --version）
- [ ] Python虚拟环境安装成功（python3-venv）
- [ ] 项目目录/var/www/cangkujia/创建成功
- [ ] frontend/、backend/、static/子目录创建成功
- [ ] 目录权限设置正确（755）
- [ ] Python虚拟环境创建成功
- [ ] FastAPI依赖安装成功
- [ ] Swap分区创建成功（2G）
- [ ] Swap分区启用成功（swapon -s显示）
- [ ] Swap开机自动挂载配置完成

## Phase 2: COS模型存储

- [ ] COS存储桶创建成功（上海地域）
- [ ] 存储桶名称正确（cangkujia-models）
- [ ] 存储桶公有读权限配置完成
- [ ] CDN加速开启成功
- [ ] coscmd工具安装成功
- [ ] COS密钥配置成功
- [ ] 80个GLB模型文件上传完成
- [ ] 上传文件完整性验证通过
- [ ] COS访问URL可正常访问
- [ ] ThreeScene.vue模型加载路径修改完成
- [ ] 前端可正常从COS加载模型

## Phase 3: 后端部署

- [ ] main.py健康检查接口添加完成
- [ ] CORS跨域配置完成
- [ ] 环境变量读取配置完成
- [ ] Supabase项目创建成功
- [ ] users表创建成功
- [ ] orders表创建成功
- [ ] user_licenses表创建成功
- [ ] 数据库连接配置完成
- [ ] 数据库连接测试通过
- [ ] Clerk应用创建成功
- [ ] Clerk微信登录配置完成
- [ ] Clerk Publishable Key获取成功
- [ ] Clerk Secret Key获取成功
- [ ] JWT验证中间件添加完成
- [ ] 认证流程测试通过
- [ ] 微信支付参数配置完成
- [ ] 支付订单接口创建成功
- [ ] 支付回调处理配置完成
- [ ] 支付流程测试通过
- [ ] systemd服务配置完成
- [ ] Uvicorn服务启动成功
- [ ] 服务开机自启配置完成
- [ ] API接口测试通过（/api/health）

## Phase 4: Nginx配置

- [ ] SSL证书申请成功（腾讯云免费证书）
- [ ] 证书文件下载完成
- [ ] 证书上传到服务器/etc/nginx/ssl/
- [ ] Nginx配置文件创建成功（/etc/nginx/sites-available/cangkujia）
- [ ] HTTPS 443端口配置完成
- [ ] HTTP 80跳转配置完成
- [ ] API反向代理配置完成（/api/）
- [ ] COS模型代理配置完成（/models/）
- [ ] 前端Vue3项目本地构建成功
- [ ] dist文件上传到服务器/var/www/cangkujia/frontend/dist/
- [ ] Nginx静态文件服务配置完成
- [ ] Nginx配置语法检查通过（nginx -t）
- [ ] Nginx服务重启成功
- [ ] HTTPS访问测试通过
- [ ] API接口测试通过
- [ ] 模型加载测试通过

## Phase 5: 第三方服务集成

- [ ] Clerk应用创建成功（名称：cangkujia）
- [ ] Clerk回调URL配置完成（https://cangkujia666.com）
- [ ] Clerk微信登录配置完成
- [ ] Clerk环境变量配置完成
- [ ] Supabase项目创建成功
- [ ] Supabase数据库表创建完成
- [ ] Supabase RLS策略配置完成
- [ ] Supabase环境变量配置完成
- [ ] 微信支付回调URL配置完成
- [ ] API证书上传到服务器
- [ ] 微信支付环境变量配置完成

## Phase 6: 验证与优化

- [ ] 首页访问正常（https://cangkujia666.com）
- [ ] 2D工作台功能正常
- [ ] 3D场景渲染正常
- [ ] 80个GLB模型加载正常
- [ ] Clerk微信登录功能正常
- [ ] 用户注册功能正常
- [ ] 用户登录功能正常
- [ ] 支付流程端到端测试通过
- [ ] 支付回调处理正常
- [ ] Nginx gzip压缩配置完成
- [ ] 浏览器缓存配置完成
- [ ] 日志轮转配置完成
- [ ] 内存使用监控正常
- [ ] Nginx配置备份完成
- [ ] 环境变量备份完成
- [ ] 部署文档创建完成

## 最终验证清单

- [ ] https://cangkujia666.com 能打开首页
- [ ] https://cangkujia666.com/api/health 返回200状态
- [ ] 2D仓库绘制功能正常
- [ ] 3D场景渲染正常
- [ ] 80个模型可从COS正常加载
- [ ] Clerk微信登录能获取用户信息
- [ ] 支付回调能正确处理CKJ-前缀订单
- [ ] 服务器内存使用稳定在合理范围（<1.5G）
- [ ] SSL证书有效（HTTPS显示安全锁）
- [ ] 移动端访问正常

## 问题记录

| 问题描述 | 发生时间 | 解决方案 | 状态 |
|----------|----------|----------|------|
|          |          |          |      |
|          |          |          |      |
|          |          |          |      |
