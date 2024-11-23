import React from "react";
import { useNavigate } from "react-router-dom";
import { AuthProvider } from "./AuthContext";

export const AuthProviderWrapper = ({ children }) => {
    const navigate = useNavigate();
    return <AuthProvider navigate={navigate}>{children}</AuthProvider>;
};
