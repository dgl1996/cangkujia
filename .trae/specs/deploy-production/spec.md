# 仓酷家生产环境部署规格

## 部署目标

将仓酷家项目部署到腾讯云轻量服务器（2核2G），实现生产环境可用。

## 技术架构

```
用户 → cangkujia666.com (Nginx 443)
├── 静态前端：Vue3构建文件 (本地40G SSD)
├── API后端：FastAPI + Uvicorn (1核1G预留)
├── 模型文件：腾讯云COS 50G (CDN加速)
├── 数据库：Supabase云端PostgreSQL
├── 用户认证：Clerk
└── 支付系统：微信支付（复用商户号1743582175）
```

## 资源清单

| 资源 | 配置 | 用途 |
|------|------|------|
| 域名 | cangkujia666.com | 主站入口 |
| 服务器 | 腾讯云2核2G 40G SSD（上海） | Nginx + FastAPI后端 |
| 对象存储 | COS 50G（1元/年） | 80个GLB模型文件 |
| 外部数据库 | Supabase免费版 | PostgreSQL |
| 用户认证 | Clerk免费版 | 微信扫码/手机号登录 |
| 支付系统 | 微信支付（商户号1743582175） | 复用安德森日历配置 |

## 服务器资源分配（2核2G）

| 进程 | 内存占用 | 说明 |
|------|----------|------|
| Nginx | ~50MB | 前端静态文件 + 反向代理 |
| FastAPI (Uvicorn) | ~300-500MB | 4个worker进程 |
| 系统保留 | ~400MB | Linux基础运行 |
| 剩余 | ~1GB | 缓冲/峰值保障 |

## 部署阶段

### Phase 1: 服务器基础环境
- 系统更新与基础依赖安装
- Python虚拟环境配置
- 项目目录结构创建

### Phase 2: COS模型存储
- 创建COS存储桶（上海地域）
- 上传80个GLB模型文件
- 配置CDN加速

### Phase 3: 后端部署
- FastAPI应用配置
- Supabase数据库连接
- Clerk认证集成
- Uvicorn服务启动

### Phase 4: Nginx配置
- HTTPS SSL证书配置
- 前端静态文件服务
- API反向代理
- COS模型代理（可选）

### Phase 5: 第三方服务集成
- Clerk应用创建与配置
- Supabase项目创建
- 微信支付回调配置

## 关键配置

### 环境变量

```bash
# Clerk
CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_SECRET_KEY=sk_live_...

# Supabase
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=eyJ...

# 微信支付
WECHAT_MCH_ID=1743582175
WECHAT_APIV3_KEY=...
WECHAT_APPID=wx3e00623c71d93a65
WECHAT_NOTIFY_URL=https://cangkujia666.com/api/payment/callback

# COS
COS_BUCKET=cangkujia-models
COS_REGION=ap-shanghai
COS_SECRET_ID=...
COS_SECRET_KEY=...
```

### Nginx配置

```nginx
server {
    listen 443 ssl http2;
    server_name cangkujia666.com www.cangkujia666.com;
    
    ssl_certificate /etc/nginx/ssl/cangkujia666.crt;
    ssl_certificate_key /etc/nginx/ssl/cangkujia666.key;
    
    location / {
        root /var/www/cangkujia/frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 7d;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /models/ {
        proxy_pass https://cangkujia-models.cos.ap-shanghai.myqcloud.com/;
        expires 30d;
    }
}

server {
    listen 80;
    server_name cangkujia666.com www.cangkujia666.com;
    return 301 https://$server_name$request_uri;
}
```

## 优化策略

1. **禁止本地数据库**：2G内存跑PostgreSQL会直接OOM，必须用Supabase云端
2. **COS内网流量**：服务器和COS桶都选上海地域，内网流量免费
3. **模型懒加载**：Three.js按货架类型动态加载，不一次性加载80个模型
4. **Swap分区**：建议开2G Swap防止内存溢出
5. **日志轮转**：限制Nginx/Uvicorn日志大小

## 验证清单

- [ ] https://cangkujia666.com 能打开2D工作台
- [ ] https://cangkujia666.com/api/health 返回后端状态
- [ ] 3D场景能加载COS桶里的GLB模型
- [ ] Clerk微信登录能获取用户信息
- [ ] 支付回调能区分CKJ-前缀订单

## 回滚方案

1. 保留每个阶段的备份
2. 使用Git标签标记稳定版本
3. Nginx配置备份在/etc/nginx/sites-available/cangkujia.backup
