/**
 * 用户权限检查工具
 * 用于检查用户是否有权限使用特定功能
 * 
 * 注意：此版本已改为从 Pinia Store 读取权限状态，不再依赖 Clerk
 */

import { useUserStore } from '../stores/user'

// 会员等级定义
export const MEMBER_LEVELS = {
  FREE: 'free',           // 免费版
  PRO: 'pro'             // Pro版（所有付费用户统一为pro）
};

/**
 * 检查用户是否是Pro用户
 * 基于 Pinia Store 的 isPro 状态
 */
export function isProUser() {
  const store = useUserStore();
  return store.isPro;
}

/**
 * 检查用户是否已登录
 */
export function isLoggedIn() {
  const store = useUserStore();
  return store.isLoggedIn;
}

/**
 * 获取当前登录用户
 */
export function getCurrentUser() {
  const store = useUserStore();
  return store.user;
}

/**
 * 获取用户计划类型
 */
export function getUserPlan() {
  const store = useUserStore();
  return store.isPro ? 'pro' : 'free';
}

/**
 * 检查用户是否有保存权限（Pro会员才能保存）
 */
export function canSave() {
  return isProUser();
}

/**
 * 检查用户是否有导出权限（Pro会员才能导出）
 */
export function canExport() {
  return isProUser();
}

/**
 * 获取升级提示信息
 */
export function getUpgradeMessage(type = 'save') {
  const messages = {
    save: {
      title: '保存项目需要Pro版',
      message: '免费版可自由设计，保存项目需升级Pro。支持导出 .ckj 文件随时恢复。',
      confirmText: '立即升级',
      cancelText: '稍后再说'
    },
    report: {
      title: '导出项目报告需要Pro版',
      message: '免费版可自由设计，导出实施清单需升级Pro。包含设备清单、布局说明、预算参考。',
      confirmText: '立即升级',
      cancelText: '稍后再说'
    }
  };
  return messages[type] || messages.save;
}

/**
 * 显示升级弹窗（简化版，返回是否点击确认）
 */
export function showUpgradeDialog(type = 'save') {
  const message = getUpgradeMessage(type);
  return confirm(`${message.title}\n\n${message.message}`);
}

/**
 * 获取请求头（带 Token）
 * 用于所有需要认证的 API 请求
 */
export function getAuthHeaders() {
  const token = localStorage.getItem('cangkujia_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
}

/**
 * 带认证的 fetch 封装
 */
export async function authFetch(url, options = {}) {
  const token = localStorage.getItem('cangkujia_token');
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    }
  };
  
  // 合并 headers
  const mergedOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...(options.headers || {})
    }
  };
  
  const response = await fetch(url, mergedOptions);
  
  // 处理 401 未授权
  if (response.status === 401) {
    // Token 无效，清除登录状态
    localStorage.removeItem('cangkujia_token');
    const store = useUserStore();
    store.clearUser();
    // 可以在这里添加跳转登录页的逻辑
  }
  
  return response;
}

// 兼容旧版API的异步接口
export async function getUserMemberLevel() {
  return getUserPlan();
}

export async function canSaveAsync() {
  return canSave();
}

export async function canExportAsync() {
  return canExport();
}
