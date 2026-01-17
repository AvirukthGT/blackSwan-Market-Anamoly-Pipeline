<template>
  <div class="app-layout">
    <!-- Sidebar Component -->
    <Sidebar 
      :is-open="isSidebarOpen" 
      :is-dark="isDark"
      @toggle="toggleSidebar"
      @toggle-theme="toggleTheme"
    />

    <!-- Main Content Area -->
    <main 
      class="main-content" 
      :class="{ 'is-shifted': isSidebarOpen }"
    >
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Sidebar from './components/Sidebar.vue';

const isSidebarOpen = ref(true);
const isDark = ref(true);

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
};

const toggleTheme = () => {
  isDark.value = !isDark.value;
  if (isDark.value) {
    document.documentElement.removeAttribute('data-theme');
  } else {
    document.documentElement.setAttribute('data-theme', 'light');
  }
};
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background-color: var(--bg-black);
}

.main-content {
  margin-left: 80px; /* Width of collapsed sidebar */
  transition: margin-left 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  min-height: 100vh;
  padding: 20px;
}

.main-content.is-shifted {
  margin-left: 260px; /* Width of open sidebar */
}

/* Page Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
