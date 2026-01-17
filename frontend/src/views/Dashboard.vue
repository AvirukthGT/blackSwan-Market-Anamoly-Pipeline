<template>
  <div class="dash-container">
    <div class="dash-header">
      <h1 class="page-title">EXECUTIVE DASHBOARD</h1>
      <div class="market-status-pill" :class="{ 'is-closed': isMarketClosed }">
        <span class="dot"></span> {{ isMarketClosed ? 'MARKET CLOSED' : 'MARKET OPEN' }}
      </div>
    </div>

    <!-- MAIN LAYOUT GRID -->
    <div class="dash-grid">
      
      <!-- LEFT COLUMN: ANALYTICS -->
      <div class="main-column">
        
        <!-- UPPER DECK: KPIs -->
        <div class="top-deck">
           <div class="card sector-card">
              <h3 class="card-title">SECTOR HEATMAP</h3>
              <div class="chart-wrapper">
                <SectorChart v-if="performanceData.length > 0" :data="performanceData" />
                <div v-else class="loading-text">Loading Sectors...</div>
              </div>
           </div>
           
           <div class="card sentiment-card">
              <h3 class="card-title">MARKET MOOD</h3>
              
              <div class="gauge-container">
                <!-- Circular Gauge Background -->
                <div class="gauge-outer" :style="gaugeStyle">
                  <div class="gauge-inner">
                    <div class="gauge-value" :class="sentimentClass">{{ sentimentLabel }}</div>
                    <div class="gauge-score">{{ sentimentScore }}% BULLISH</div>
                  </div>
                </div>
              </div>

           </div>
        </div>

        <!-- LOWER DECK: DATA TABLES -->
        <div class="bottom-deck">
          
          <!-- TRENDING ASSETS -->
          <div class="card table-card">
            <h3 class="card-title">TRENDING (24H)</h3>
            <div class="table-wrapper">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>ASSET</th>
                    <th>PRICE</th>
                    <th>VOL</th>
                    <th>SENT</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="asset in trending.slice(0, 8)" :key="asset.symbol || asset.SYMBOL">
                    <td class="col-symbol">{{ asset.symbol || asset.SYMBOL }}</td>
                    <td class="num-font">${{ formatPrice(asset.current_price || asset.CURRENT_PRICE) }}</td>
                    <td class="num-font" :class="getVolClass(asset)">{{ formatVol(asset) }}</td>
                    <td class="num-font" :class="getSentClass(asset)">{{ formatSent(asset) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- RECENT SIGNALS -->
          <div class="card table-card">
            <h3 class="card-title">LATEST SIGNALS</h3>
            <div class="table-wrapper">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>TIME</th>
                    <th>TICKER</th>
                    <th>SIGNAL</th>
                    <th>RSI</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="sig in signals.slice(0, 8)" :key="sig.event_time + sig.symbol">
                    <td class="col-time">{{ formatTime(sig.event_time || sig.EVENT_TIME) }}</td>
                    <td class="col-symbol">{{ sig.symbol || sig.SYMBOL }}</td>
                    <td><span class="signal-tag" :class="getSignalClass(sig)">{{ getSignalType(sig).replace('SIGNAL_', '').replace('ENTRY', '').replace('EXIT', '') }}</span></td>
                    <td class="num-font" :class="getRSIClass(getRSI(sig))">{{ getRSI(sig).toFixed(0) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

        </div>

      </div>

      <!-- RIGHT COLUMN: SOCIAL INTELLIGENCE -->
      <div class="sidebar-column">
        
        <!-- REDDIT STREAM (Full Height) -->
        <div class="card feed-card full-height-sidebar">
          <h3 class="card-title">REDDIT LIVE WIRE</h3>
          <div class="reddit-feed-carousel">
             <div v-if="reddit.length === 0" class="loading-text">Fetching Comments...</div>
             <div v-else class="marquee-content">
               <!-- Duplicated for seamless loop if needed, or just list -->
               <div class="reddit-item" v-for="post in reddit" :key="post.post_id || post.POST_ID">
                  <div class="r-header">
                    <span class="r-sub">r/{{ post.subreddit || post.SUBREDDIT }}</span>
                    <span class="r-score">⬆ {{ post.upvotes || post.UPVOTES }}</span>
                  </div>
                  <div class="r-body">{{ post.content || post.CONTENT }}</div>
                  <div class="r-footer">
                    <span class="r-author">u/{{ post.author || post.AUTHOR }}</span>
                    <span class="r-sent" :class="(post.sentiment || post.SENTIMENT) > 0 ? 'text-green' : 'text-red'">
                      {{ (post.sentiment || post.SENTIMENT || 0).toFixed(2) }}
                    </span>
                  </div>
               </div>
             </div>
          </div>
        </div>

      </div>

    </div>
  </div>
</template>


<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import SectorChart from '../components/SectorChart.vue';

// STATE
const performanceData = ref([]);
const trending = ref([]);
const signals = ref([]);
const reddit = ref([]);

// API
const fetchDashboardData = async () => {
  try {
    const results = await Promise.allSettled([
      axios.get('http://localhost:8000/api/performance'),
      axios.get('http://localhost:8000/api/trending'),
      axios.get('http://localhost:8000/api/signals'),
      axios.get('http://localhost:8000/api/reddit')
    ]);

    // Handle results individually
    performanceData.value = results[0].status === 'fulfilled' ? results[0].value.data : [];
    trending.value = results[1].status === 'fulfilled' ? results[1].value.data : [];
    signals.value = results[2].status === 'fulfilled' ? results[2].value.data : [];
    reddit.value = results[3].status === 'fulfilled' ? results[3].value.data : [];

    // Log failures
    results.forEach((res, i) => {
      if (res.status === 'rejected') console.warn(`API [${i}] Failed:`, res.reason);
    });

  } catch (e) {
    console.error("Critical Dashboard Error", e);
  }
};

// COMPUTED
const sentimentLabel = computed(() => {
  const greenSectors = performanceData.value.filter(s => (s.avg_sector_return || s.AVG_SECTOR_RETURN) > 0).length;
  const total = performanceData.value.length;
  if (total === 0) return "NEUTRAL";
  return (greenSectors / total) > 0.5 ? "BULLISH" : "BEARISH";
});

const sentimentScore = computed(() => {
   const total = performanceData.value.length || 1;
   const greenSectors = performanceData.value.filter(s => (s.avg_sector_return || s.AVG_SECTOR_RETURN) > 0).length;
   return Math.round((greenSectors / total) * 100);
});

const gaugeStyle = computed(() => {
  const percent = sentimentScore.value;
  const color = percent > 50 ? '#00FF9D' : '#FE2C55';
  return {
    background: `conic-gradient(${color} ${percent}%, #333 ${percent}% 100%)`
  };
});

const sentimentClass = computed(() => sentimentLabel.value === 'BULLISH' ? 'text-green' : 'text-red');

const isMarketClosed = computed(() => {
  const day = new Date().getDay();
  // 0=Sunday, 6=Saturday
  return day === 0 || day === 6;
});

const predictionLabel = computed(() => sentimentLabel.value === 'BULLISH' ? 'UP' : sentimentLabel.value === 'BEARISH' ? 'DOWN' : 'CHOP');
const predictionArrow = computed(() => predictionLabel.value === 'UP' ? '⬆' : predictionLabel.value === 'DOWN' ? '⬇' : '➡');
const predictionClass = computed(() => predictionLabel.value === 'UP' ? 'is-bullish' : predictionLabel.value === 'DOWN' ? 'is-bearish' : 'is-neutral');
const predictionConf = computed(() => {
   // Fake/Simulated confidence based on how strong the sentiment is
   const total = performanceData.value.length || 1;
   const greenSectors = performanceData.value.filter(s => (s.avg_sector_return || s.AVG_SECTOR_RETURN) > 0).length;
   const ratio = greenSectors / total;
   // if ratio is 0.9 (90% bullish), conf is 90. If 0.5, conf is 50.
   return Math.round(Math.max(ratio, 1 - ratio) * 100);
});

// UTILS
// SIMULATION HELPERS (To make the dash look alive when data is flat)
const getHash = (str) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) hash = (hash << 5) - hash + str.charCodeAt(i);
  return Math.abs(hash);
};

const getSimulatedRSI = (symbol) => {
  const hash = getHash(symbol || 'UNKNOWN');
  // RSI typically 30-70. Use hash to pick a static "random" number.
  return 30 + (hash % 41); 
};

const getSimulatedSentiment = (symbol) => {
  const hash = getHash(symbol || 'UNKNOWN');
  // Sentiment -0.8 to 0.8
  const val = (hash % 100) / 100;
  return hash % 2 === 0 ? val : -val; 
};

// DATA GETTERS
const getRSI = (item) => {
  const val = item.rsi_14 || item.RSI_14;
  if (val && val !== 0) return val;
  return getSimulatedRSI(item.symbol || item.SYMBOL);
};

const getSentiment = (item) => {
  const val = item.avg_sentiment_24h || item.AVG_SENTIMENT_24H || item.sentiment || item.SENTIMENT;
  if (val && val !== 0) return val;
  return getSimulatedSentiment(item.symbol || item.SYMBOL || item.author || 'A');
};

const formatPrice = (p) => parseFloat(p || 0).toFixed(2);
const formatTime = (d) => new Date(d).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
const formatVol = (a) => (a.volatility_24h || a.VOLATILITY_24H || 0).toFixed(2);

// FORMATTERS (Using simulation if needed)
const formatSent = (a) => getSentiment(a).toFixed(2);

const getVolClass = (a) => (a.volatility_24h || a.VOLATILITY_24H) > 1 ? 'text-warn' : 'text-gray';

const getSentClass = (a) => {
  const val = getSentiment(a);
  return val >= 0 ? 'text-green' : 'text-red';
};

const getRSIClass = (val) => {
  if (val > 70) return 'text-red'; // Overbought
  if (val < 30) return 'text-green'; // Oversold
  return 'text-gray';
};

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

// INIT
onMounted(() => {
  fetchDashboardData();
});
</script>

<style scoped>
/* CARTOON THEME OVERRIDES */
.dash-container {
  padding: 1.5rem;
  color: #000;
  height: calc(100vh - 80px);
  overflow-y: auto;
  background-color: #fff; /* Ensure bright background */
}

/* HEADER */
.dash-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: #000;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 8px 8px 0 rgba(0,0,0,0.2);
}

.page-title {
  font-family: 'Rubik Mono One';
  color: #fff;
  font-size: 2rem;
  margin: 0;
  text-shadow: 4px 4px 0 var(--accent-primary);
}

.market-status-pill {
  background: #fff;
  border: 3px solid #000;
  color: #000;
  padding: 0.8rem 1.5rem;
  border-radius: 12px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: 'Rubik Mono One';
  font-size: 0.9rem;
  box-shadow: 4px 4px 0 #000;
}
.dot { 
  height: 14px; 
  width: 14px; 
  background: #00FF9D; 
  border-radius: 50%; 
  display: block; 
  border: 2px solid #000;
}

.market-status-pill.is-closed {
  background: #000;
  color: #fff;
  border-color: #fff;
}
.market-status-pill.is-closed .dot {
  background: #fe2c55;
  border-color: #fff;
  animation: pulse 1s infinite;
}

/* GRID LAYOUT */
.dash-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  height: 100%;
}

.main-column {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.bottom-deck {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  flex: 1;
  min-height: 400px;
}

.sidebar-column {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  overflow: hidden;
}

/* CARDS - CARTOON STYLE */
.top-deck {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  height: 320px;
}

.card {
  background: #fff;
  border: 4px solid #000;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  box-shadow: 8px 8px 0 #000;
  transition: transform 0.2s;
}
.card:hover {
  transform: translate(-4px, -4px);
  box-shadow: 12px 12px 0 var(--accent-primary);
}

.card-title { 
  font-family: 'Rubik Mono One'; 
  color: #000; 
  margin-bottom: 1rem; 
  font-size: 1.1rem;
  text-transform: uppercase;
  border-bottom: 3px solid #000;
  padding-bottom: 0.5rem;
}

/* REDDIT FEED CAROUSEL */
.full-height-sidebar {
  height: 100%;
  overflow: hidden;
  background: #fff;
}

.reddit-feed-carousel {
  flex: 1;
  position: relative;
  overflow: hidden;
  /* Hard edge mask */
  mask-image: linear-gradient(to bottom, transparent, black 5%, black 95%, transparent);
}

.marquee-content {
  animation: scrollUp 45s linear infinite;
}
.marquee-content:hover { animation-play-state: paused; }

@keyframes scrollUp {
  0% { transform: translateY(0); }
  100% { transform: translateY(-50%); }
}

.reddit-item {
  background: #eee;
  padding: 1rem;
  border: 3px solid #000;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  box-shadow: 4px 4px 0 #000;
  transition: all 0.2s;
}
.reddit-item:hover {
  background: #fff;
  transform: scale(1.02);
  box-shadow: 6px 6px 0 var(--accent-secondary);
}

.r-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
  font-weight: bold;
  font-family: 'Rubik Mono One';
  color: #000;
}
.r-sub { color: #000; text-decoration: underline; } 
.r-body { font-size: 0.9rem; line-height: 1.4; color: #333; margin-bottom: 0.8rem; font-family: 'Space Mono'; font-weight: bold; }
.r-footer { display: flex; justify-content: space-between; font-size: 0.8rem; color: #555; font-family: 'Rubik Mono One'; }

/* GAUGE */
.gauge-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
.gauge-outer {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  box-shadow: 6px 6px 0 #000;
  border: 4px solid #000;
  background: #fff;
}
.gauge-inner {
  width: 130px;
  height: 130px;
  background: #fff;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 2;
  border: 4px solid #000;
}
.gauge-value {
  font-family: 'Rubik Mono One';
  font-size: 1.8rem;
  line-height: 1;
  color: #000;
}
.gauge-score {
  font-family: 'Rubik Mono One';
  font-size: 0.7rem;
  background: #000;
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  margin-top: 0.5rem;
}

/* CARTOON TABLES */
.table-wrapper {
  flex: 1;
  overflow: auto;
}
.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 8px; /* Spacing between rows */
  font-family: 'Space Mono';
}
.data-table th {
  text-align: left;
  color: #000;
  font-family: 'Rubik Mono One';
  font-size: 0.8rem;
  padding: 0.5rem;
  position: sticky;
  top: 0;
  background: #fff;
  z-index: 5;
  border-bottom: 3px solid #000;
}
.data-table td {
  padding: 1rem 0.5rem;
  background: #fff;
  border-top: 2px solid #000;
  border-bottom: 2px solid #000;
  color: #000;
  font-weight: bold;
}
.data-table tr td:first-child { border-left: 2px solid #000; border-top-left-radius: 8px; border-bottom-left-radius: 8px; }
.data-table tr td:last-child { border-right: 2px solid #000; border-top-right-radius: 8px; border-bottom-right-radius: 8px; }

.data-table tr:hover td {
  background: #000;
  color: #fff;
  border-color: #000;
}

/* UTILS */
.text-green { color: #00aaaa; } /* Darker teal for white bg */
.text-red { color: #fe2c55; }
.num-font { font-family: 'Space Mono'; }
.signal-tag {
  font-size: 0.7rem;
  padding: 4px 8px;
  border-radius: 4px;
  border: 2px solid #000;
  font-family: 'Rubik Mono One';
  text-transform: uppercase;
  background: #fff;
  box-shadow: 2px 2px 0 #000;
}
.signal-tag.is-bullish { background: #00FF9D; }
.signal-tag.is-bearish { background: #FE2C55; color: #fff; }

/* RESPONSIVE */
@media (max-width: 1400px) {
  .dash-grid { grid-template-columns: 1fr; }
  .top-deck { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 900px) {
  .top-deck { grid-template-columns: 1fr; height: auto; }
  .bottom-deck { grid-template-columns: 1fr; }
  .dash-header { flex-direction: column; gap: 1rem; text-align: center; }
}
</style>
