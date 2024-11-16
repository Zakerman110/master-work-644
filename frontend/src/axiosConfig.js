import axios from 'axios';

// Determine the base URL based on the environment
const baseURL =
    process.env.NODE_ENV === 'development'
        ? 'http://localhost:8000'
        : window.location.origin; // Uses the current host for production

// Create an Axios instance
const apiClient = axios.create({
    baseURL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export default apiClient;
