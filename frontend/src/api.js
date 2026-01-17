import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000', // Backend URL
    timeout: 5000,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getSignals = async (symbol) => {
    try {
        const response = await api.get('/api/signals', { params: { symbol } });
        return response.data;
    } catch (error) {
        console.error(`Error fetching signals for ${symbol}:`, error);
        return [];
    }
};

export default api;
