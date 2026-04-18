/**
 * 用户权限检查工具
 * 用于检查用户是否有权限使用特定功能
 */

import { useAuth } from '@clerk/vue';

// 会员等级定义
export const MEMBER_LEVELS = {
  FREE: 'free',           // 免费版
  MONTHLY: 'monthly',     // 月付 ¥19.9/月
  FIRST_MONTH: 'first_month', // 首月特惠 ¥9.9
  QUARTERLY: 'quarterly', // 季度 ¥49/季度
  HALF_YEAR: 'half_year', // 半年 ¥89/半年
  YEARLY: 'yearly',       // 年付 ¥168/年
  THREE_YEAR: 'three_year', // 3年 ¥399/3年
  LIFETIME: 'lifetime'    // 终身版 ¥699+
};

// 会员等级显示名称
export const MEMBER_LEVEL_NAMES = {
  [MEMBER_LEVELS.FREE]: '免费版',
  [MEMBER_LEVELS.MONTHLY]: '月付会员',
  [MEMBER_LEVELS.FIRST_MONTH]: '首月特惠',
  [MEMBER_LEVELS.QUARTERLY]: '季度会员',
  [MEMBER_LEVELS.HALF_YEAR]: '半年会员',
  [MEMBER_LEVELS.YEARLY]: '年付会员',
  [MEMBER_LEVELS.THREE_YEAR]: '3年会员',
  [MEMBER_LEVELS.LIFETIME]: '终身会员'
};

// 检查用户是否已登录
export function isAuthenticated() {
  const { isSignedIn } = useAuth();
  return isSignedIn.value;
}

// 获取当前用户会员等级（从后端API获取）
export async function getUserMemberLevel() {
  try {
    const { userId } = useAuth();
    if (!userId.value) return MEMBER_LEVELS.FREE;
    
    // 调用后端API获取用户会员信息
    const response = await fetch(`/api/users/${userId.value}/license`);
    if (response.ok) {
      const data = await response.json();
      return data.license_type || MEMBER_LEVELS.FREE;
    }
    return MEMBER_LEVELS.FREE;
  } catch (error) {
    console.error('获取用户会员等级失败:', error);
    return MEMBER_LEVELS.FREE;
  }
}

// 检查用户是否有保存权限（付费会员才能保存）
export async function canSave() {
  const level = await getUserMemberLevel();
  return level !== MEMBER_LEVELS.FREE;
}

// 检查用户是否有导出权限（付费会员才能导出）
export async function canExport() {
  const level = await getUserMemberLevel();
  return level !== MEMBER_LEVELS.FREE;
}

// 获取会员到期时间
export async function getLicenseExpiryDate() {
  try {
    const { userId } = useAuth();
    if (!userId.value) return null;
    
    const response = await fetch(`/api/users/${userId.value}/license`);
    if (response.ok) {
      const data = await response.json();
      return data.end_date || null;
    }
    return null;
  } catch (error) {
    console.error('获取会员到期时间失败:', error);
    return null;
  }
}

// 检查会员是否有效
export async function isLicenseValid() {
  const expiryDate = await getLicenseExpiryDate();
  if (!expiryDate) return false;
  return new Date(expiryDate) > new Date();
}

// 获取升级提示信息
export function getUpgradeMessage(feature = '保存') {
  return {
    title: '升级专业版',
    message: `免费用户无法${feature}，升级专业版即可${feature}并享受更多功能`,
    confirmText: '查看定价',
    cancelText: '稍后再说'
  };
}

// 显示升级弹窗（需要在组件中调用）
export function showUpgradeDialog(router, feature = '保存') {
  const message = getUpgradeMessage(feature);
  if (confirm(`${message.title}\n\n${message.message}\n\n点击确定查看定价方案`)) {
    router.push('/pricing');
  }
}
