import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Signals from '../views/Signals.vue'
import News from '../views/News.vue'
import Dashboard from '../views/Dashboard.vue'
import Placeholder from '../views/Placeholder.vue'

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home
    },
    {
        path: '/signals',
        name: 'Signals',
        component: Signals
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard
    },
    {
        path: '/news',
        name: 'News',
        component: News
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
