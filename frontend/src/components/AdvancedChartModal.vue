<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>TECHNICAL ANALYSIS: {{ symbol }}</h2>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <div class="chart-wrapper">
        <Line :data="chartData" :options="chartOptions" />
        
        <!-- SHADED REGIONS OVERLAY -->
        <div class="zone sell-zone"><span>SELL ZONE (OVERBOUGHT)</span></div>
        <div class="zone neutral-zone"><span>ACCUMULATION ZONE</span></div>
        <div class="zone buy-zone"><span>BUY ZONE (OVERSOLD)</span></div>

        <!-- VERTICAL SIGNAL MARKERS (Simulated) -->
        <div class="v-signal v-buy" style="left: 20%"><span>BUY</span></div>
        <div class="v-signal v-sell" style="left: 65%"><span>SELL</span></div>
      </div>

      <div class="indicators-row">
        <div class="ind-box">
          <span class="label">RSI (14)</span>
          <span class="val" :class="rsiClass">{{ rsiValue.toFixed(2) }}</span>
        </div>
        <div class="ind-box">
          <span class="label">MACD</span>
          <span class="val" :class="macdClass">{{ macdText }}</span>
        </div>
        <div class="ind-box">
          <span class="label">VOLATILITY</span>
          <span class="val">{{ volatilityText }}</span>
        </div>
        <div class="ind-box">
          <span class="label">TREND</span>
          <span class="val" :class="trendClass">{{ trendText }}</span>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'vue-chartjs';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const props = defineProps({
  symbol: String,
  data: Array,
  rsiValue: Number
});

// DYNAMIC INDICATORS LOGIC
const rsiClass = computed(() => {
  if (props.rsiValue > 70) return 'text-sell';
  if (props.rsiValue < 30) return 'text-buy';
  return 'text-neutral';
});

const macdText = computed(() => {
  if (props.rsiValue > 65) return 'BEARISH DIV';
  if (props.rsiValue < 35) return 'BULLISH CROSS';
  return 'NEUTRAL';
});

const macdClass = computed(() => {
  if (props.rsiValue > 65) return 'text-sell';
  if (props.rsiValue < 35) return 'text-buy';
  return 'text-neutral';
});

const volatilityText = computed(() => {
  // Simulate volatility based on RSI extremes
  return (props.rsiValue > 75 || props.rsiValue < 25) ? 'EXTREME' : 'NORMAL';
});

const trendText = computed(() => {
  if (props.rsiValue > 60) return 'UPTREND';
  if (props.rsiValue < 40) return 'DOWNTREND';
  return 'CHOPPY';
});

const trendClass = computed(() => {
  if (props.rsiValue > 60) return 'text-buy';
  if (props.rsiValue < 40) return 'text-sell';
  return 'text-neutral';
});

const chartData = computed(() => {
  const prices = props.data.map(d => parseFloat(d.close_price));
  return {
    labels: props.data.map(d => new Date(d.event_time).toLocaleTimeString()),
    datasets: [
      {
        label: 'Price Action',
        data: prices,
        borderColor: '#fff',
        borderWidth: 3, // Thicker line
        shadowColor: 'rgba(255, 255, 255, 0.5)', // Simulated glow via CSS not JS, but ChartJS needs plugin for true shadow. 
        // We will stick to standard properties, but use a brighter color.
        backgroundColor: (context) => {
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, 0, 0, 500);
          gradient.addColorStop(0, 'rgba(254, 44, 85, 0.4)'); // Red top
          gradient.addColorStop(0.5, 'rgba(0, 0, 0, 0.0)');   // Transparent mid
          gradient.addColorStop(1, 'rgba(0, 255, 157, 0.4)'); // Green bottom
          return gradient;
        },
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 8,
        pointBackgroundColor: '#fff'
      }
    ]
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      mode: 'index',
      intersect: false,
      titleColor: '#00FF9D',
      bodyColor: '#fff',
      backgroundColor: 'rgba(0,0,0,0.9)',
      borderColor: '#333',
      borderWidth: 1,
      padding: 10,
      titleFont: { family: 'Rubik Mono One' },
      bodyFont: { family: 'Space Mono' }
    }
  },
  scales: {
    x: {
      grid: { color: '#222', borderDash: [5, 5] },
      ticks: { color: '#666', font: { family: 'Space Mono' } }
    },
    y: {
      grid: { color: '#222', borderDash: [5, 5] },
      ticks: { color: '#888', font: { family: 'Space Mono' } }
    }
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(10px); /* Enhanced blur */
}

.modal-content {
  background: #0a0a0a;
  border: 4px solid #fff; /* Retro thick border */
  width: 90%;
  max-width: 1200px;
  height: 85vh;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  padding: 2rem;
  box-shadow: 0 0 100px rgba(0, 255, 157, 0.1); /* Subtle neon glow */
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #222;
  padding-bottom: 1rem;
}

.modal-header h2 {
  font-family: 'Rubik Mono One', sans-serif;
  color: #fff;
  margin: 0;
  font-size: 2rem;
  letter-spacing: -1px;
}

.close-btn {
  background: none;
  border: 2px solid #333;
  color: #fff;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  transition: all 0.2s;
}
.close-btn:hover {
  border-color: #fff;
  background: #fff;
  color: #000;
}

.chart-wrapper {
  flex: 1;
  position: relative;
  background: #050505;
  border: 1px solid #222;
  border-radius: 12px;
  overflow: hidden;
}

/* SHADED REGIONS */
.zone {
  position: absolute;
  left: 0;
  width: 100%;
  pointer-events: none;
  display: flex;
  align-items: center;
  padding-left: 1rem;
  font-weight: bold;
  font-size: 0.7rem;
  letter-spacing: 2px;
  font-family: 'Rubik Mono One';
  opacity: 0.6;
}
.sell-zone {
  top: 0;
  height: 15%;
  background: linear-gradient(to bottom, rgba(254, 44, 85, 0.2), transparent);
  color: #fe2c55;
  border-bottom: 1px dashed rgba(254, 44, 85, 0.5);
}
.buy-zone {
  bottom: 0;
  height: 15%;
  background: linear-gradient(to top, rgba(0, 255, 157, 0.2), transparent);
  color: #00ff9d;
  border-top: 1px dashed rgba(0, 255, 157, 0.5);
}
.neutral-zone {
  top: 45%;
  height: 10%;
  border-top: 1px dashed #333;
  border-bottom: 1px dashed #333;
  justify-content: center;
  color: #444;
}

/* VERTICAL SIGNALS */
.v-signal {
  position: absolute;
  top: 0;
  height: 100%;
  width: 2px;
  pointer-events: none;
  opacity: 0.5;
}
.v-signal span {
  position: absolute;
  top: 50%;
  left: 4px;
  font-size: 0.7rem;
  font-weight: bold;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  letter-spacing: 2px;
}
.v-buy {
  background: linear-gradient(to top, #00FF9D, transparent);
}
.v-buy span { color: #00FF9D; }

.v-sell {
  background: linear-gradient(to bottom, #FE2C55, transparent);
}
.v-sell span { color: #FE2C55; }


/* INDICATORS */
.indicators-row {
  display: flex;
  gap: 1.5rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 2px solid #1a1a1a;
}

.ind-box {
  flex: 1;
  background: #0f0f0f;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #222;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: transform 0.2s;
}
.ind-box:hover {
  transform: translateY(-2px);
  border-color: #444;
}

.label {
  font-size: 0.7rem;
  color: #666;
  margin-bottom: 8px;
  font-weight: bold;
  font-family: 'Rubik Mono One';
}

.val {
  font-family: 'Space Mono', monospace;
  font-weight: bold;
  font-size: 1.1rem;
  color: #fff;
}

.text-buy { color: #00FF9D; }
.text-sell { color: #FF0055; }
.text-neutral { color: #fff; }
</style>
