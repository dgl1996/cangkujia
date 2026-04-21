module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended'
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  plugins: [
    'vue'
  ],
  rules: {
    // 开发时允许 console，生产环境由 vite 配置移除
    'no-console': 'off',
    
    // 未使用变量警告（不报错，避免开发时干扰）
    'no-unused-vars': ['warn', { 
      'vars': 'all', 
      'args': 'after-used',
      'ignoreRestSiblings': true 
    }],
    
    // 允许单字组件名（如 Home.vue）
    'vue/multi-word-component-names': 'off',
    
    // Vue 模板格式宽松
    'vue/html-indent': 'off',
    'vue/max-attributes-per-line': 'off',
    
    // 允许 debugger（开发时使用）
    'no-debugger': 'off'
  },
  globals: {
    // 全局变量
    'THREE': 'readonly',
    'defineProps': 'readonly',
    'defineEmits': 'readonly',
    'defineExpose': 'readonly',
    'withDefaults': 'readonly'
  }
}
