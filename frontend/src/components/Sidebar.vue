<template>
  <aside 
    class="sidebar" 
    :class="{ 'is-collapsed': !isOpen }"
  >
    <!-- Toggle Button (Absolute to stick out) -->
    <button class="toggle-btn" @click="$emit('toggle')">
      <component :is="isOpen ? 'ChevronsLeft' : 'ChevronsRight'" size="24" />
    </button>

    <!-- Logo Area -->
    <div class="logo-area">
      <div class="logo-circle">
        <Bird v-if="isOpen" size="32" color="white" />
        <Bird v-else size="24" color="white" />
      </div>
      <span v-if="isOpen" class="brand-name">blackSwan</span>
    </div>

    <!-- Navigation Links -->
    <nav class="nav-links">
      <router-link to="/" class="nav-item">
        <Home size="20" />
        <span v-if="isOpen">Home</span>
      </router-link>
      
      <router-link to="/dashboard" class="nav-item">
        <LayoutDashboard size="20" />
        <span v-if="isOpen">Dashboard</span>
      </router-link>

      <router-link to="/signals" class="nav-item">
        <Activity size="20" />
        <span v-if="isOpen">Signals</span>
      </router-link>

      <router-link to="/news" class="nav-item">
        <Newspaper size="20" />
        <span v-if="isOpen">News</span>
      </router-link>
    </nav>

    <!-- Footer / User -->
    <div class="sidebar-footer">
      <div class="user-avatar">
        <User size="20" />
      </div>
      <div v-if="isOpen" class="user-info">
        <span class="username">Trader Joe</span>
        <span class="status">Level 99</span>
      </div>
    </div>

    <!-- Theme Toggle -->
    <button v-if="isOpen" class="theme-toggle" @click="$emit('toggle-theme')">
      <component :is="isDark ? 'Sun' : 'Moon'" size="20" />
      <span>{{ isDark ? 'Light Mode' : 'Dark Mode' }}</span>
    </button>
  </aside>
</template>

<script setup>
import { 
  ChevronsLeft, 
  ChevronsRight, 
  Bird, 
  Home, 
  LayoutDashboard, 
  Activity, 
  Newspaper,
  User,
  Sun,
  Moon
} from 'lucide-vue-next';

defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  isDark: {
    type: Boolean,
    default: true
  }
});

defineEmits(['toggle', 'toggle-theme']);
</script>

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  background-color: var(--bg-black);
  border-right: 3px solid var(--border-white);
  width: 260px;
  transition: width 0.4s cubic-bezier(0.34, 1.56, 0.64, 1); /* Bouncy transition */
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  z-index: 50;
  box-shadow: 5px 0 0 rgba(255, 255, 255, 0.1);
}

.sidebar.is-collapsed {
  width: 80px;
  padding: 1.5rem 0.5rem;
}

/* --- LOGO --- */
.logo-area {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 3rem;
  overflow: hidden;
  white-space: nowrap;
}

.logo-circle {
  width: 50px;
  height: 50px;
  background: var(--bg-black);
  border: 3px solid var(--border-white);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 4px 4px 0 var(--border-white); /* Retro shadow */
}

.brand-name {
  font-family: 'Rubik Mono One', sans-serif; /* We'll add this font */
  font-size: 1.2rem;
  color: var(--text-white);
  letter-spacing: -1px;
}

/* --- NAV --- */
.nav-links {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 3px solid transparent;
  border-radius: 12px;
  color: var(--text-gray);
  text-decoration: none;
  font-weight: bold;
  transition: all 0.2s;
  overflow: hidden;
  white-space: nowrap;
}

.nav-item:hover {
  background: var(--text-white);
  color: var(--bg-black);
  transform: translate(-2px, -2px);
  box-shadow: 4px 4px 0 var(--border-white);
  border: 3px solid var(--bg-black);
}

.nav-item.router-link-active {
  background: var(--accent-primary);
  color: var(--bg-black);
  border: 3px solid var(--border-white);
  box-shadow: 4px 4px 0 var(--border-white);
}

/* --- TOGGLE BUTTON --- */
.toggle-btn {
  position: absolute;
  right: -20px;
  top: 40px;
  background: var(--bg-black);
  border: 3px solid var(--border-white);
  color: var(--text-white);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.toggle-btn:hover {
  transform: scale(1.1);
}

/* --- FOOTER --- */
.sidebar-footer {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 3px solid var(--border-white);
  overflow: hidden;
  white-space: nowrap;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-white);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: bold;
}

.status {
  font-size: 0.8rem;
  color: var(--accent-primary);
}
.status {
  font-size: 0.8rem;
  color: var(--accent-primary);
}

.theme-toggle {
  margin-top: 1rem;
  background: transparent;
  border: 3px solid var(--border-white);
  color: var(--text-white);
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-family: var(--font-body);
  font-weight: bold;
}

.theme-toggle:hover {
  background: var(--text-white);
  color: var(--bg-black);
}
</style>
