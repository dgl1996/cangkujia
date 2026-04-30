import { defineStore } from 'pinia'

/**
 * 用户状态管理
 * 替代 Clerk，使用自研 JWT 登录
 */

export const useUserStore = defineStore('user', {
  state: () => ({
    isLoggedIn: false,
    user: null as {
      id: number;
      email: string;
      nickname: string | null;
      avatar_url: string | null;
    } | null,
    isPro: false,
    planType: null as string | null,
    expireAt: null as string | null,
    startedAt: null as string | null,
  }),

  actions: {
    /**
     * 设置用户信息（登录/注册成功后调用）
     */
    setUser(userData: { id: number; email: string; nickname?: string | null; avatar_url?: string | null }) {
      this.user = {
        id: userData.id,
        email: userData.email,
        nickname: userData.nickname || null,
        avatar_url: userData.avatar_url || null,
      }
      this.isLoggedIn = true
      
      // 持久化用户基本信息到 localStorage（用于页面刷新后快速恢复）
      const token = localStorage.getItem('cangkujia_token')
      localStorage.setItem('cangkujia_user', JSON.stringify({
        id: userData.id,
        email: userData.email,
        nickname: userData.nickname || null,
        avatar_url: userData.avatar_url || null,
        token: token
      }))
    },

    /**
     * 检查登录状态（App.vue 启动时调用）
     * - 检查 localStorage 是否有 token
     * - 有 token 则调用 /api/auth/me 获取用户信息
     * - 如果 API 失败但有本地缓存，使用缓存数据
     */
    async checkAuthStatus() {
      const token = localStorage.getItem('cangkujia_token')
      
      if (!token) {
        this.clearUser()
        return false
      }

      // 先尝试从 localStorage 恢复用户数据（避免页面刷新后空白）
      const cachedUser = localStorage.getItem('cangkujia_user')
      if (cachedUser) {
        try {
          const userData = JSON.parse(cachedUser)
          this.user = {
            id: userData.id,
            email: userData.email,
            nickname: userData.nickname || null,
            avatar_url: userData.avatar_url || null,
          }
          this.isLoggedIn = true
        } catch (e) {
          console.error('解析缓存用户数据失败:', e)
        }
      }

      try {
        const response = await fetch('/api/auth/me', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (!response.ok) {
          // Token 无效，清除登录状态
          this.clearUser()
          localStorage.removeItem('cangkujia_token')
          localStorage.removeItem('cangkujia_user')
          return false
        }

        const userData = await response.json()
        this.setUser(userData)
        
        // 同时检查订阅状态
        await this.checkSubscription()
        
        return true
      } catch (error) {
        console.error('检查登录状态失败:', error)
        // API 失败但本地有缓存，保持登录状态（离线模式）
        if (this.user) {
          return true
        }
        this.clearUser()
        return false
      }
    },

    /**
     * 检查订阅状态
     */
    async checkSubscription() {
      if (!this.user) {
        this.isPro = false
        return
      }

      try {
        const token = localStorage.getItem('cangkujia_token')
        const response = await fetch(`/api/user/subscription?user_id=${this.user.id}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (!response.ok) {
          this.isPro = false
          return
        }

        const result = await response.json()

        // 解析后端返回的嵌套数据格式 {code: 0, data: {...}}
        const subscriptionData = result.data || result

        // 检查是否 active 且未过期
        const isActive = subscriptionData.status === 'active'
        const notExpired = subscriptionData.expire_at ? new Date(subscriptionData.expire_at) > new Date() : false

        this.isPro = isActive && notExpired
        this.planType = subscriptionData.plan
        this.expireAt = subscriptionData.expire_at
        this.startedAt = subscriptionData.started_at
      } catch (error) {
        console.error('检查订阅状态失败:', error)
        this.isPro = false
      }
    },

    /**
     * 清除用户状态（登出时调用）
     */
    clearUser() {
      this.isLoggedIn = false
      this.user = null
      this.isPro = false
      this.planType = null
      this.expireAt = null
      this.startedAt = null
      localStorage.removeItem('cangkujia_token')
      localStorage.removeItem('cangkujia_user')
    },

    /**
     * 登出
     * 清除 token 后强制跳转首页
     */
    logout() {
      this.clearUser()
      // 强制跳转首页，确保用户无法继续使用设计工具
      window.location.href = '/'
    }
  }
})
