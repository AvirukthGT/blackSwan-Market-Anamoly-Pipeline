<template>
  <div class="newspaper-container">
    
    <!-- MASTHEAD -->
    <header class="newspaper-header">
      <div class="header-meta">
        <span>VOL. 1 | NO. {{ news.length }}</span>
        <span>${{ new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }).toUpperCase() }}</span>
        <span>FINAL EDITION</span>
      </div>
      <h1 class="brand-title">The BlackSwan Times</h1>
      <div class="header-border-double"></div>
    </header>

    <div v-if="loading" class="loading-spinner">
      EXTRA! EXTRA! READ ALL ABOUT IT...
    </div>

    <!-- NEWSPAPER LAYOUT -->
    <div v-else class="paper-grid">
      
      <!-- LEFT MAIN COLUMN -->
      <div class="main-column">
        
        <!-- HERO ARTICLE (First Item) -->
        <article v-if="news.length > 0" class="article-hero" :class="getImpactClass(news[0].impact_type)">
          <div class="hero-content">
            <div class="impact-stamp">{{ formatImpact(news[0].impact_type) }}</div>
            <h2 class="hero-headline">
              <a :href="news[0].url" target="_blank">{{ news[0].title }}</a>
            </h2>
            <div class="article-meta">
              <span class="author">By MARKET_BOT</span> — <span class="location">NEW YORK</span>
            </div>
            <p class="article-summary">
              {{ news[0].symbol }} is moving. Analysts are scrambling as price shifts from ${{ formatPrice(news[0].start_price) }} to ${{ formatPrice(news[0].end_price) }}. 
              This represents a {{ (news[0].impact_pct * 100).toFixed(2) }}% change in value.
            </p>
          </div>
        </article>

        <!-- SUB-STORIES (Items 2-4) -->
        <div v-if="news.length > 1" class="sub-stories-section">
          <div class="mid-divider">
            <span>ALSO IN THE NEWS</span>
          </div>
          <div class="sub-grid">
            <article 
              v-for="item in news.slice(1, 4)" 
              :key="item.news_id"
              class="sub-article-item"
            >
              <h4 class="sub-headline">
                <a :href="item.url" target="_blank">{{ item.title }}</a>
              </h4>
               <div class="article-meta-mini">
                <span class="mini-tag">{{ item.symbol }}</span>
                <span :class="item.impact_pct > 0 ? 'text-up' : 'text-down'">{{ (item.impact_pct * 100).toFixed(2) }}%</span>
              </div>
            </article>
          </div>
        </div>

      </div>

      <div class="separator-line"></div>

      <!-- SIDEBAR COLUMN (Remaining Items) -->
      <div class="article-columns">
        <h5 class="sidebar-header">MARKET WIRE</h5>
        <article 
          v-for="item in news.slice(4)" 
          :key="item.news_id"
          class="article-item"
        >
          <div class="article-header">
            <span class="mini-tag">{{ item.symbol }}</span>
            <span class="impact-mini" :class="getImpactClass(item.impact_type)">{{ formatImpact(item.impact_type) }}</span>
          </div>
          <h3 class="article-headline">
            <a :href="item.url" target="_blank">{{ item.title }}</a>
          </h3>
        </article>
      </div>

    </div>

    <footer class="paper-footer">
      BLACK SWAN INTELLIGENCE • PRINTED IN THE METAVERSE
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const news = ref([]);
const loading = ref(false);

const fetchNews = async () => {
  loading.value = true;
  try {
    const response = await axios.get('http://localhost:8000/api/news');
    news.value = response.data;
  } catch (err) {
    console.error("Failed to fetch news", err);
  } finally {
    loading.value = false;
  }
};

const formatImpact = (type) => {
  if (!type) return 'MARKET NEWS';
  if (type.includes('POSITIVE')) return 'MARKET RALLY';
  if (type.includes('NEGATIVE')) return 'MARKET CRASH';
  return 'LATEST UPDATE';
};

const getImpactClass = (type) => {
  if (!type) return 'style-neutral';
  if (type.includes('POSITIVE')) return 'style-pump';
  if (type.includes('NEGATIVE')) return 'style-dump';
  return 'style-neutral';
};

const formatPrice = (p) => parseFloat(p || 0).toFixed(2);

onMounted(() => {
  fetchNews();
});
</script>

<style scoped>
/* PAPER THEME VARIABLES */
.newspaper-container {
  background-color: #f4f1ea; 
  color: #1a1a1a;
  height: calc(100vh - 80px); /* Fixed height to enable internal scroll */
  padding: 2rem;
  font-family: 'Space Mono', monospace; 
  overflow: hidden; /* Disable page scroll */
  display: flex;
  flex-direction: column;
}

/* HEADER / MASTHEAD */
.newspaper-header {
  text-align: center;
  border-bottom: 4px solid #000;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  flex-shrink: 0; /* Keep header rigid */
}

/* ... existing styles ... */

.brand-title {
  font-family: 'Rubik Mono One', sans-serif; 
  font-size: 3rem;
  margin: 0.5rem 0;
  text-transform: uppercase;
  letter-spacing: -2px;
  line-height: 1;
  text-shadow: 4px 4px 0 rgba(0,0,0,0.1);
}

.header-meta {
  display: flex;
  justify-content: space-between;
  border-bottom: 2px solid #000;
  padding-bottom: 0.5rem;
  font-weight: bold;
  font-size: 0.9rem;
  text-transform: uppercase;
  font-family: 'Rubik Mono One';
}

.header-border-double {
  border-top: 2px solid #000;
  margin-top: 4px; 
  width: 100%;
}

/* LOADING */
.loading-spinner {
  text-align: center;
  font-size: 1.5rem;
  font-weight: bold;
  padding: 4rem;
  font-family: 'Rubik Mono One';
  animation: flash 1s infinite alternate;
}
@keyframes flash { from { opacity: 0.5; } to { opacity: 1; } }

/* LAYOUT GRID - SPLIT SCROLL */
.paper-grid {
  display: grid;
  grid-template-columns: 2fr 1px 1fr; /* Hero | Line | Sidebar */
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  flex: 1; /* Take remaining height */
  overflow: hidden;
  width: 100%;
}

.separator-line {
  background: #000;
  width: 2px;
  height: 100%;
}

/* HERO ARTICLE - FIXED LEFT */
.main-column {
  display: flex;
  flex-direction: column;
  overflow-y: auto; /* ALLOW SCROLL if content overflows */
  padding-bottom: 2rem;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}
.main-column::-webkit-scrollbar { 
  display: none; /* Chrome/Safari */
}

.article-hero {
  padding-bottom: 2rem;
}

/* ... existing styles ... */

.hero-headline {
  font-family: 'Rubik Mono One', sans-serif;
  font-size: 2.2rem;
  line-height: 1.1;
  margin: 0.5rem 0;
  text-shadow: 3px 3px 0 #ddd;
}
.hero-headline a {
  text-decoration: none;
  color: #000;
  transition: color 0.2s;
}
.hero-headline a:hover {
  color: #555;
  text-decoration: underline;
}

.impact-stamp {
  display: inline-block;
  border: 4px solid #000;
  padding: 0.5rem 1rem;
  font-weight: bold;
  font-family: 'Rubik Mono One';
  transform: rotate(-2deg);
  margin-bottom: 1rem;
  background: #fff;
  box-shadow: 4px 4px 0 #000;
}
.style-pump .impact-stamp { color: #00aaaa; border-color: #00aaaa; }
.style-dump .impact-stamp { color: #fe2c55; border-color: #fe2c55; }

.article-meta {
  font-style: italic;
  font-weight: bold;
  margin-bottom: 1.5rem;
  color: #444;
  border-top: 1px solid #000;
  border-bottom: 1px solid #000;
  padding: 0.5rem 0;
}

.article-summary {
  font-size: 1.2rem;
  line-height: 1.6;
  text-align: justify;
}
.article-summary::first-letter {
  font-size: 3.5rem;
  font-weight: bold;
  float: left;
  line-height: 1;
  margin-right: 0.5rem;
  font-family: 'Rubik Mono One';
}

/* SUB STORIES */
.mid-divider {
  border-top: 4px double #000;
  border-bottom: 1px solid #000;
  padding: 0.5rem 0;
  text-align: center;
  font-family: 'Rubik Mono One';
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
  color: #000;
}
.sub-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1.5rem;
}
.sub-article-item {
  border-right: 1px solid #000;
  padding-right: 1rem;
}
.sub-article-item:last-child { border-right: none; }

.sub-headline {
  font-family: 'Rubik Mono One';
  font-size: 1rem;
  line-height: 1.2;
  margin-bottom: 0.5rem;
}
.sub-headline a { text-decoration: none; color: #000; }
.sub-headline a:hover { text-decoration: underline; }

.article-meta-mini {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  font-weight: bold;
  color: #555;
  margin-top: 5px;
}

/* SIDEBAR COLUMNS - SCROLLABLE RIGHT */
.article-columns {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow-y: auto; /* ENABLE SCROLL */
  padding-right: 1rem; /* Space for scrollbar */
  padding-bottom: 4rem;
}

.sidebar-header {
  font-family: 'Rubik Mono One';
  border-bottom: 4px solid #000;
  margin: 0;
  padding-bottom: 10px;
  font-size: 1.2rem;
  position: sticky;
  top: 0;
  background: #f4f1ea;
  z-index: 2;
}

/* FOOTER - FIXED BOTTOM LEFT */
.paper-footer {
  margin-top: auto; /* Push to bottom of flex container if needed, or put in left col */
  border-top: 4px double #000;
  padding-top: 1rem;
  text-align: center;
  font-weight: bold;
  font-size: 0.8rem;
  text-transform: uppercase;
  /* If we want footer at bottom of left column effectively */
}

.article-item {
  border-bottom: 1px solid #000;
  padding-bottom: 1.5rem;
}
.article-item:last-child { border-bottom: none; }

.article-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  align-items: center;
}
.mini-tag {
  background: #000;
  color: #fff;
  padding: 2px 6px;
  font-weight: bold;
  font-family: 'Rubik Mono One';
  font-size: 0.7rem;
}
.impact-mini {
  font-weight: bold;
  font-size: 0.8rem;
  text-transform: uppercase;
}
.style-pump .impact-mini { color: #00aaaa; }
.style-dump .impact-mini { color: #fe2c55; }

.article-headline {
  font-family: 'Rubik Mono One';
  font-size: 1.2rem;
  margin: 0 0 0.5rem 0;
  line-height: 1.3;
}
.article-headline a {
  text-decoration: none;
  color: #000;
}
.article-headline a:hover {
  text-decoration: underline;
}

.text-up { color: #00aaaa; }
.text-down { color: #fe2c55; }

/* RESPONSIVE */
@media (max-width: 1000px) {
  .paper-grid {
    grid-template-columns: 1fr;
    overflow-y: auto; /* Revert to normal scroll on mobile */
  }
  .article-columns {
    overflow-y: visible;
  }
  .main-column {
    overflow-y: visible;
  }
  
  .sub-grid {
    grid-template-columns: 1fr;
  }
  .sub-article-item {
    border-right: none;
    border-bottom: 1px dashed #000;
    padding-bottom: 1rem;
    margin-bottom: 1rem;
  }
  .separator-line { display: none; }
  .brand-title { font-size: 2.5rem; }
}
</style>
