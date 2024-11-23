import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from "./Header";
import HomePage from './HomePage';
import AdminPanel from "./AdminPanel";
import ModelsPanel from "./ModelsPanel";
import {AuthProvider} from "./AuthContext";
import ProtectedRoute from "./ProtectedRoute";
import LoginPage from "./LoginPage";
import {AuthProviderWrapper} from "./AuthProviderWrapper";

const App = () => {
  return (
      <Router>
          <AuthProviderWrapper>
              <Header />
              <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route
                      path="/admin"
                      element={
                          <ProtectedRoute role="admin">
                              <AdminPanel />
                          </ProtectedRoute>
                      }
                  />
                  <Route
                      path="/models"
                      element={
                          <ProtectedRoute role="admin">
                              <ModelsPanel />
                          </ProtectedRoute>
                      }
                  />
                  <Route path="*" element={<div>404 Not Found</div>} />
              </Routes>
          </AuthProviderWrapper>
      </Router>
  );
};

export default App;
