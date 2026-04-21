/**
 * 用户权限检查工具
 * 用于检查用户是否有权限使用特定功能
 */

import { useAuth } from '@clerk/vue';

// 用户计划存储key
const USER_PLAN_KEY = 'cangkujia_user_plan';

// 会员等级定义
export const MEMBER_LEVELS = {
  FREE: 'free',           // 免费版
  PRO: 'pro'             // Pro版（所有付费用户统一为pro）
};

// 检查用户是否是Pro用户（基于localStorage）
export function isProUser() {
  if (typeof window === 'undefined') return false;
  return localStorage.getItem(USER_PLAN_KEY) === 'pro';
}

// 设置用户计划（用于测试或支付后升级）
export function setUserPlan(plan) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(USER_PLAN_KEY, plan);
}

// 获取用户计划
export function getUserPlan() {
  if (typeof window === 'undefined') return 'free';
  return localStorage.getItem(USER_PLAN_KEY) || 'free';
}

// 检查用户是否有保存权限（Pro会员才能保存）
export function canSave() {
  return isProUser();
}

// 检查用户是否有导出权限（Pro会员才能导出）
export function canExport() {
  return isProUser();
}

// 获取升级提示信息
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

// 显示升级弹窗（简化版，返回是否点击确认）
export function showUpgradeDialog(type = 'save') {
  const message = getUpgradeMessage(type);
  return confirm(`${message.title}\n\n${message.message}`);
}

// 兼容旧版API的异步接口
export async function getUserMemberLevel() {
  return getUserPlan();
}

// 兼容旧版API的异步canSave
export async function canSaveAsync() {
  return canSave();
}

// 兼容旧版API的异步canExport
export async function canExportAsync() {
  return canExport();
}
