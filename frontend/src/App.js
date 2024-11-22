import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from "./Header";
import HomePage from './HomePage';
import AdminPanel from "./AdminPanel";
import ModelsPanel from "./ModelsPanel";

const App = () => {
  return (
      <Router>
            <Header />
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/admin" element={<AdminPanel />} />
                <Route path="/models" element={<ModelsPanel />} />
                <Route path="*" element={<div>404 Not Found</div>} />
            </Routes>
      </Router>
  );
};

export default App;
