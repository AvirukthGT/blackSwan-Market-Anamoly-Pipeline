<template>
  <div class="chart-container">
    <div v-if="isWeekend" class="weekend-overlay">
      <span>MARKET CLOSED</span>
    </div>
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js';
import { Bar } from 'vue-chartjs';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const props = defineProps({
  data: {
    type: Array,
    required: true
  }
});

const isWeekend = computed(() => {
  const day = new Date().getDay();
  return day === 0 || day === 6;
});

const chartData = computed(() => {
  return {
    labels: props.data.map(d => d.asset_type || d.ASSET_TYPE),
    datasets: [
      {
        label: 'Avg Sector Performance (%)',
        data: props.data.map(d => (d.avg_sector_return || d.AVG_SECTOR_RETURN) * 100),
        backgroundColor: props.data.map(d => 
          (d.avg_sector_return || d.AVG_SECTOR_RETURN) > 0 ? '#00FF9D' : '#FE2C55'
        ),
        borderRadius: 4
      }
    ]
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: (ctx) => `${ctx.formattedValue}%`
      }
    }
  },
  scales: {
    y: {
      grid: {
        color: '#333'
      },
      ticks: {
        color: '#fff'
      }
    },
    x: {
      grid: {
        display: false
      },
      ticks: {
        color: '#fff'
      }
    }
  }
};
</script>

<style scoped>
.chart-container {
  height: 200px;
  width: 100%;
  position: relative;
}

.weekend-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--accent-danger);
  font-family: 'Rubik Mono One';
  border: 2px dashed var(--accent-danger);
  z-index: 10;
}
</style>
