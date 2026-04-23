import { defineStore } from 'pinia'
import { useAuth } from '@clerk/vue'

export const useUserStore = defineStore('user', {
  state: () => ({
    isPro: false,
    planType: null as string | null,
    expireAt: null as string | null,
    userId: null as string | null,
  }),
  actions: {
    async checkStatus() {
      try {
        const { getToken, userId } = useAuth()
        const token = await getToken.value()
        const uid = userId.value
        
        if (!token || !uid) {
          this.isPro = false
          this.userId = null
          return
        }
        
        this.userId = uid
        
        const res = await fetch(`/api/user/subscription?user_id=${uid}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        if (!res.ok) throw new Error('API error')
        
        const data = await res.json()
        
        // 检查是否active且未过期
        const isActive = data.status === 'active'
        const notExpired = data.expire_at ? new Date(data.expire_at) > new Date() : false
        
        this.isPro = isActive && notExpired
        this.planType = data.plan
        this.expireAt = data.expire_at
      } catch (e) {
        console.error('Pro status check failed:', e)
        this.isPro = false
      }
    },
    
    // 清除状态（用于登出）
    clearStatus() {
      this.isPro = false
      this.planType = null
      this.expireAt = null
      this.userId = null
    }
  }
})
