import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Plans from './components/Plans';
import Painel from './components/Painel';


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/plans" element={<Plans />} />
        <Route path="/painel" element={<Painel />} /> {/* Defina a rota para o Painel */}
      </Routes>
    </Router>
  );
}

export default App;

