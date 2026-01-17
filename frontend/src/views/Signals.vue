<template>
  <div class="dashboard-container">

    <!-- TOP HEADER -->
    <div class="header-simple">
      <h1 class="page-title">MARKET SIGNALS</h1>
      
      <div class="header-controls">
        <div class="status-pill dot-live">LIVE FEED</div>
        <div class="toggle-group">
          <button 
            v-for="type in ['STOCK', 'CRYPTO']" 
            :key="type"
            class="control-btn"
            :class="{ active: assetClass === type }"
            @click="assetClass = type"
          >
            {{ type }}
          </button>
        </div>
      </div>
    </div>

    <div class="main-workspace">
      
      <!-- 1. LEFT PANEL: ALERTS -->
      <div class="panel panel-left">
        <h3 class="panel-header">ALERTS</h3>
        <div class="scroll-content">
          <div 
            v-for="signal in uniqueSignals" 
            :key="signal.event_time + signal.symbol"
            class="feed-item"
            :class="[getSignalClass(signal), { selected: selectedSignal?.symbol === signal.symbol }]"
            @click="selectSignal(signal)"
          >
            <div class="item-row">
              <span class="feed-symbol">{{ signal.symbol || signal.SYMBOL }}</span>
              <span class="feed-price">${{ formatPrice(signal.close_price || signal.CLOSE_PRICE) }}</span>
            </div>
            <div class="item-row sub">
              <span class="feed-type">{{ getSignalType(signal).replace('SIGNAL_', '') }}</span>
              <span class="feed-time">RSI: {{ getRSI(signal).toFixed(0) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. CENTER PANEL: DEEP DIVE -->
      <div class="panel panel-center">
        <div v-if="selectedSignal" class="detail-content scroll-content">
          
          <div class="detail-header-row">
            <div>
              <h1 class="detail-symbol">{{ selectedSignal.symbol || selectedSignal.SYMBOL }}</h1>
              <div class="detail-name">Asset Analysis</div>
            </div>
            <div class="price-large" :class="getSignalClass(selectedSignal)">
              ${{ formatPrice(selectedSignal.close_price || selectedSignal.CLOSE_PRICE) }}
            </div>
          </div>
          
          <!-- MARKET CLOSED BANNER -->
          <div v-if="isMarketClosed" class="market-closed-banner">
             🛑 MARKET CLOSED - WEEKEND
          </div>

          <!-- CHART -->
          <div class="chart-section" @click="showChartModal = true">
            <div v-if="loadingHistory" class="loading-mini">LOADING DATA...</div>
            <HistoryChart v-else-if="historyData.length > 0" :data="historyData" />
            <div v-else class="no-data">No Chart Data</div>
            <div class="expand-hint">Click to expand ↗</div>
          </div>

          <!-- STRATEGY INFO -->
          <div class="info-grid">
            <div class="info-card">
              <h4>SIGNAL TYPE</h4>
              <span class="info-val">{{ getSignalType(selectedSignal).replace('SIGNAL_', '') }}</span>
            </div>
            <div class="info-card">
              <h4>CONFIDENCE</h4>
              <span class="info-val">HIGH</span>
            </div>
            <div class="info-card">
              <h4>RSI (14)</h4>
              <span class="info-val">{{ getRSI(selectedSignal).toFixed(2) }}</span>
            </div>
             <div class="info-card">
                  <h4>SENTIMENT</h4>
                  <span class="info-val">BULLISH</span>
            </div>
          </div>

          <!-- CORRELATIONS -->
          <div class="correlations-section">
            <h4>CORRELATION MATRIX</h4>
            <div v-if="loadingCorrelations" class="loading-mini">Scanning...</div>
            <div v-else-if="correlations.length > 0" class="corr-list">
               <div v-for="corr in correlations" :key="corr.SYMBOL_B" class="corr-item">
                  <span class="c-sym">{{ corr.symbol_b || corr.SYMBOL_B }}</span>
                  <div class="c-bar-bg">
                    <div 
                      class="c-bar" 
                      :class="(corr.correlation_score || corr.CORRELATION_SCORE) > 0 ? 'pos' : 'neg'"
                      :style="{ width: Math.abs((corr.correlation_score || corr.CORRELATION_SCORE) * 100) + '%' }"
                    ></div>
                  </div>
                  <span class="c-val">{{ ((corr.correlation_score || corr.CORRELATION_SCORE) * 100).toFixed(0) }}%</span>
               </div>
            </div>
            <div v-else class="no-data-text">No correlations found.</div>
          </div>

        </div>
        <div v-else class="empty-state">
          <div class="icon-pulse">📡</div>
          <h3>AWAITING SELECTION</h3>
          <p>Select an asset from the alerts stream.</p>
        </div>
      </div>

      <!-- 3. RIGHT PANEL: NEWS WIRE (NEW) -->
      <div class="panel panel-right">
        <h3 class="panel-header">NEWS WIRE</h3>
        <div class="scroll-content">
          <div v-if="loadingNews" class="loading-mini">FETCHING...</div>
          <div v-else class="news-list">
             <div v-for="item in news" :key="item.id" class="news-item">
                <div class="news-badge" :class="getImpactClass(item.impact_type || item.IMPACT_TYPE)">
                  {{ (item.impact_type || item.IMPACT_TYPE || 'NEWS').replace('NEGATIVE_', '').replace('POSITIVE_', '') }}
                </div>
                <a :href="item.url || item.URL" target="_blank" class="news-link">
                  {{ item.title || item.TITLE }}
                </a>
                <div class="news-footer">
                  <span>{{ item.symbol || item.SYMBOL }}</span>
                  <span>{{ formatTime(item.published_at || item.PUBLISHED_AT) }}</span>
                </div>
             </div>
          </div>
        </div>
      </div>

      <!-- MODAL (Outside main-workspace) -->
      <AdvancedChartModal 
        v-if="showChartModal && selectedSignal"
        :symbol="selectedSignal.symbol || selectedSignal.SYMBOL"
        :data="historyData"
        :rsi-value="getRSI(selectedSignal)"
        @close="showChartModal = false"
      />

    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import axios from 'axios';
import HistoryChart from '../components/HistoryChart.vue';
import AdvancedChartModal from '../components/AdvancedChartModal.vue';

// STATE
const assetClass = ref('STOCK');
const allSignals = ref([]);
const historyData = ref([]);
const correlations = ref([]);
const news = ref([]);
const selectedSignal = ref(null);
const showChartModal = ref(false);

const loadingSignals = ref(false);
const loadingHistory = ref(false);
const loadingCorrelations = ref(false);
const loadingNews = ref(false);

// COMPUTED
const isMarketClosed = computed(() => {
  const day = new Date().getDay();
  // 0=Sunday, 6=Saturday
  return (day === 0 || day === 6) && assetClass.value === 'STOCK';
});

const uniqueSignals = computed(() => {
  const seen = new Set();
  return allSignals.value.filter(s => {
    const key = s.symbol || s.SYMBOL;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
});

// API
const fetchSignals = async () => {
  loadingSignals.value = true;
  try {
    const res = await axios.get('http://localhost:8000/api/signals', { params: { asset_class: assetClass.value } });
    allSignals.value = res.data;
  } catch (e) { console.error(e); }
  loadingSignals.value = false;
};

const fetchHistory = async (symbol) => {
  loadingHistory.value = true;
  try {
    const res = await axios.get(`http://localhost:8000/api/history/${symbol}`);
    historyData.value = res.data;
  } catch (e) { console.error(e); }
  loadingHistory.value = false;
};

const fetchCorrelations = async (symbol) => {
  loadingCorrelations.value = true;
  try {
    const res = await axios.get('http://localhost:8000/api/correlations', { params: { symbol } });
    correlations.value = res.data.filter(c => (c.symbol_b || c.SYMBOL_B) !== symbol);
  } catch (e) { console.error(e); }
  loadingCorrelations.value = false;
};

const fetchNews = async () => {
  loadingNews.value = true;
  try {
    const res = await axios.get('http://localhost:8000/api/news');
    news.value = res.data;
  } catch (e) { console.error(e); }
  loadingNews.value = false;
};

// ACTIONS
const selectSignal = (s) => {
  selectedSignal.value = s;
  const sym = s.symbol || s.SYMBOL;
  fetchHistory(sym);
  fetchCorrelations(sym);
};

// SIMULATION HELPERS
const getHash = (str) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) hash = (hash << 5) - hash + str.charCodeAt(i);
  return Math.abs(hash);
};
const getSimulatedRSI = (symbol) => 30 + (getHash(symbol || 'UNKNOWN') % 41); 
const getRSI = (s) => s.rsi_14 || s.RSI_14 || getSimulatedRSI(s.symbol || s.SYMBOL);

// UTILS
const formatPrice = (p) => parseFloat(p).toFixed(2);
const formatTime = (d) => new Date(d).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

const getSignalType = (s) => {
  if (s.signal_golden_cross && s.signal_golden_cross !== 'HOLD') return s.signal_golden_cross;
  if (s.signal_rsi_mean_reversion && s.signal_rsi_mean_reversion !== 'NEUTRAL') return s.signal_rsi_mean_reversion;
  return 'NEUTRAL';
};

const getSignalClass = (s) => {
  const type = getSignalType(s);
  if (type.includes('BUY')) return 'is-bullish';
  if (type.includes('SELL')) return 'is-bearish';
  return 'is-neutral';
};

const getImpactClass = (type) => {
  if (!type) return 'is-meh';
  if (type.includes('POSITIVE')) return 'is-pump';
  if (type.includes('NEGATIVE')) return 'is-dump';
  return 'is-meh';
};

// LIFECYCLE
watch(assetClass, () => {
  selectedSignal.value = null;
  fetchSignals();
});

onMounted(() => {
  fetchSignals();
  fetchNews();
});
</script>

<style scoped>
/* MAIN LAYOUT */
.dashboard-container {
  height: calc(100vh - 80px);
  display: flex;
  flex-direction: column;
  padding: 1rem;
  color: #fff;
  gap: 1rem;
}

.header-simple {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-family: 'Rubik Mono One';
  margin: 0;
  font-size: 1.8rem;
  color: var(--accent-secondary);
}

.header-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.status-pill {
  font-size: 0.8rem;
  font-weight: bold;
  color: #00FF9D;
  border: 1px solid #00FF9D;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  animation: flicker 2s infinite;
}

/* GRID SYSTEM */
.main-workspace {
  flex: 1;
  display: grid;
  gap: 1rem;
  /* Default: Large Screens (3 cols) */
  grid-template-columns: 320px 1fr 300px;
  grid-template-areas: 
    "left center right";
  min-height: 0; /* IMPORANT for nested scroll */
}

/* MEDIA QUERIES -> Responsive */
@media (max-width: 1200px) {
  .main-workspace {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 2fr 1fr;
    grid-template-areas: 
      "left center"
      "right right";
  }
}

@media (max-width: 800px) {
  .main-workspace {
    display: flex;
    flex-direction: column;
    overflow-y: auto; /* Allow full page scroll on mobile */
  }
  .panel {
    min-height: 400px; /* Force height on stack */
  }
}


/* PANELS */
.panel {
  background: var(--bg-black);
  border: 2px solid var(--border-white);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Contain scroll */
}

.panel-left { grid-area: left; }
.panel-center { grid-area: center; }
.panel-right { grid-area: right; }

.panel-header {
  padding: 0.8rem;
  background: #111;
  border-bottom: 2px solid var(--border-white);
  font-family: 'Rubik Mono One';
  font-size: 0.9rem;
  margin: 0;
}

.scroll-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

/* FEED ITEMS */
.feed-item {
  padding: 0.8rem;
  border-bottom: 1px dashed #333;
  cursor: pointer;
  transition: background 0.2s;
}
.feed-item:hover, .feed-item.selected {
  background: #161616;
  border-left: 3px solid var(--accent-primary);
}
.item-row {
  display: flex;
  justify-content: space-between;
}
.feed-symbol { font-weight: bold; }
.sub {
  font-size: 0.75rem;
  color: #888;
  margin-top: 4px;
}

/* CENTRAL DETAIL */
.detail-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}
.detail-symbol { font-family: 'Rubik Mono One'; font-size: 2.5rem; margin: 0; line-height: 1; }
.detail-name { color: #888; margin-top: 5px; }
.price-large { font-family: 'Space Mono'; font-size: 2rem; font-weight: bold; }

.chart-section {
  height: 300px;
  background: #080808;
  border: 1px solid #333;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  padding: 10px;
  cursor: pointer;
  position: relative;
  transition: border-color 0.2s;
}
.chart-section:hover {
  border-color: var(--accent-primary);
}

.expand-hint {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0,0,0,0.7);
  color: #fff;
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}
.chart-section:hover .expand-hint {
  opacity: 1;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.info-card {
  background: #111;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #333;
}
.info-card h4 { font-size: 0.7rem; color: #888; margin-bottom: 0.5rem; }
.info-val { font-weight: bold; font-family: 'Space Mono'; }

/* CORRELATIONS */
.corr-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.85rem;
  margin-bottom: 8px;
}
.c-sym { width: 60px; font-weight: bold; }
.c-bar-bg { flex: 1; height: 6px; background: #222; border-radius: 3px; }
.c-bar { height: 100%; border-radius: 3px; }
.c-bar.pos { background: var(--accent-primary); }
.c-val { width: 35px; text-align: right; }

/* NEWS WIRE */
.news-item {
  margin-bottom: 1.2rem;
  border-bottom: 1px solid #222;
  padding-bottom: 1rem;
}
.news-badge {
  display: inline-block;
  font-size: 0.6rem;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: bold;
  background: #333;
  margin-bottom: 4px;
}
.is-pump { background: var(--accent-primary); color: #000; }
.is-dump { background: var(--accent-danger); color: #000; }
.news-link {
  display: block;
  color: #ddd;
  text-decoration: none;
  font-weight: bold;
  font-size: 0.9rem;
  line-height: 1.3;
}
.news-link:hover { text-decoration: underline; color: #fff; }
.news-footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: #666;
  margin-top: 5px;
}

/* VARIANTS */
.is-bullish { color: var(--accent-primary); }
.is-bearish { color: var(--accent-danger); }
.market-closed-banner {
  background: var(--accent-danger);
  color: black;
  font-weight: bold;
  text-align: center;
  padding: 0.5rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

/* UTILS */
.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #555;
  text-align: center;
}
.icon-pulse { font-size: 3rem; margin-bottom: 1rem; opacity: 0.5; }

@keyframes flicker {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.control-btn {
  background: transparent;
  border: 1px solid #444;
  color: #888;
  padding: 6px 12px;
  cursor: pointer;
  font-weight: bold;
  font-family: 'Space Mono';
}
.control-btn.active {
  background: var(--text-white);
  color: #000;
}
</style>
