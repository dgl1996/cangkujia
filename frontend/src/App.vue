<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { watch } from 'vue'
import { useAuth } from '@clerk/vue'
import { useUserStore } from './stores/user'

const { isSignedIn, userId } = useAuth()
const userStore = useUserStore()

// 监听用户登录状态，自动检查权限
watch(isSignedIn, async (signedIn) => {
  if (signedIn) {
    // 用户已登录，检查订阅状态
    await userStore.checkStatus()
  } else {
    // 用户已登出，清除状态
    userStore.clearStatus()
  }
}, { immediate: true })

// 也监听userId变化（登录用户切换时）
watch(userId, async (newUserId) => {
  if (newUserId) {
    await userStore.checkStatus()
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  width: 100vw;
  height: 100vh;
}
</style>
