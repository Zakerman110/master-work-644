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
    withCredentials: true,
});

apiClient.interceptors.request.use((config) => {
    const csrfToken = document.cookie
        .split("; ")
        .find((row) => row.startsWith("csrftoken="))
        ?.split("=")[1];
    if (csrfToken) {
        config.headers["X-CSRFToken"] = csrfToken;
    }
    const token = localStorage.getItem('accessToken');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default apiClient;
