import React, { createContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from './axiosConfig';

export const AuthContext = createContext();

export const AuthProvider = ({ children, navigate }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const login = async (username, password) => {
        try {
            const response = await apiClient.post('/api/token/', { username, password });
            const { access, refresh } = response.data;

            localStorage.setItem('accessToken', access);
            localStorage.setItem('refreshToken', refresh);

            const userResponse = await apiClient.get('/api/user/');
            setUser(userResponse.data);
            navigate('/');
        } catch (err) {
            console.error('Login failed:', err);
        }
    };

    const logout = () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        setUser(null);
        navigate('/login');
    };

    const refreshToken = async () => {
        try {
            const refresh = localStorage.getItem('refreshToken');
            const response = await apiClient.post('/api/token/refresh/', { refresh });
            localStorage.setItem('accessToken', response.data.access);
        } catch (err) {
            console.error('Token refresh failed:', err);
            logout();
        }
    };

    useEffect(() => {
        const initializeUser = async () => {
            try {
                const response = await apiClient.get('/api/user/');
                setUser(response.data);
            } catch (err) {
                console.error('Failed to fetch user:', err);
                logout();
            } finally {
                setLoading(false);
            }
        };

        initializeUser();
    }, []);

    return (
        <AuthContext.Provider value={{ user, login, logout, refreshToken, loading }}>
            {children}
        </AuthContext.Provider>
    );
};
