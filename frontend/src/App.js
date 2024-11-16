import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './HomePage'; // Adjust the import path as necessary

const App = () => {
  return (
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="*" element={<div>404 Not Found</div>} />
        </Routes>
      </Router>
  );
};

export default App;
