import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import Register from './components/Register';
import Plans from './components/Plans';
import ForgotPassword from './components/ForgotPassword';  
import TokenVerification from './components/TokenVerification';
import ResetPassword from './components/ResetPassword';
import 'bootstrap/dist/css/bootstrap.min.css';

const isAuthenticated = () => {
    return localStorage.getItem('authToken') !== null;
};

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route 
                    path="/plans" 
                    element={
                        isAuthenticated() ? <Plans /> : <Navigate to="/login" />
                    }
                />
                <Route 
                    path="/dashboard" 
                    element={
                        isAuthenticated() ? <Dashboard /> : <Navigate to="/login" />
                    }
                />
                <Route path="/forgotpassword" element={<ForgotPassword />} />
                <Route path="/verify-token" element={<TokenVerification />} />
                <Route path="/reset-password" element={<ResetPassword />} />
                <Route path="*" element={<Navigate to="/login" />} />
            </Routes>
        </Router>
    );
};

export default App;
