<template>
  <div class="not-found">
    <div class="not-found-content">
      <h1 class="error-code">404</h1>
      <p class="error-message">抱歉，您访问的页面不存在！</p>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.not-found {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f7f7f7;
}
.not-found-content {
  text-align: center;
}
.error-code {
  font-size: 120px;
  font-weight: bold;
  color: #ff4d4f;
}
.error-message {
  font-size: 18px;
  margin: 20px 0;
  color: #666;
}
</style>
