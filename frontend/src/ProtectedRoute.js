import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from './AuthContext';

const ProtectedRoute = ({ children, role }) => {
    const { user, loading } = useContext(AuthContext);

    if (loading) return <p>Loading...</p>;

    if (!user || (role && user.role !== role)) {
        return <Navigate to="/login" />;
    }

    return children;
};

export default ProtectedRoute;
