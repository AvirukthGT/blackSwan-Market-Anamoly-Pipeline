<template>
  <div class="chart-container">
    <Line :data="chartData" :options="chartOptions" />
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
  Legend
} from 'chart.js';
import { Line } from 'vue-chartjs';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const props = defineProps({
  data: {
    type: Array,
    required: true
  }
});

const chartData = computed(() => {
  return {
    labels: props.data.map(d => new Date(d.event_time).toLocaleTimeString()),
    datasets: [
      {
        label: 'Price',
        backgroundColor: '#00FF9D',
        borderColor: '#00FF9D',
        data: props.data.map(d => parseFloat(d.close_price)),
        tension: 0.1,
        pointRadius: 0
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
      intersect: false
    }
  },
  scales: {
    x: {
      display: false
    },
    y: {
      grid: {
        color: '#222'
      },
      ticks: {
        color: '#888'
      }
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
.chart-container {
  height: 100%;
  width: 100%;
}
</style>
