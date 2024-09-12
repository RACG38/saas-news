import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import MainPage from './components/MainPage';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import Register from './components/Register';
import ForgotPassword from './components/ForgotPassword';  
import TokenVerification from './components/TokenVerification';
import ResetPassword from './components/ResetPassword';
import Feedback from './components/Feedback';
import CheckoutForm from './components/CheckoutForm';
import TermoDeUso from './components/TermoDeUso';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';

const stripePromise = loadStripe('pk_test_51Pn4lyFoYdflkG65WPti0iFUvKpCaTa4xSoGu9Zu2JvIAwbKhHfA73F9b2cO7DddKbrF6PXE05IXQ5o8DqFvQwE1007moBnRIJ');

const isAuthenticated = () => {
    return localStorage.getItem('authToken') !== null;
};

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/mainpage" element={<MainPage />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                
                {/* Envolver o CheckoutForm no Elements */}
                <Route 
                    path="/checkout" 
                    element={
                        isAuthenticated() ? (
                            <Elements stripe={stripePromise}>
                                <CheckoutForm />
                            </Elements>
                        ) : (
                            <Navigate to="/mainpage" />
                        )
                    }
                />
                
                <Route 
                    path="/dashboard" 
                    element={
                        isAuthenticated() ? <Dashboard /> : <Navigate to="/mainpage" />
                    }
                />
                
                {/* Proteger a rota de Feedback */}
                <Route 
                    path="/feedback" 
                    element={
                        isAuthenticated() ? <Feedback /> : <Navigate to="/login" />
                    } 
                />
                
                <Route path="/forgotpassword" element={<ForgotPassword />} />
                <Route path="/verify-token" element={<TokenVerification />} />
                <Route path="/reset-password" element={<ResetPassword />} />
                <Route path="/termo-de-uso" element={<TermoDeUso />} />
                <Route path="*" element={<Navigate to="/mainpage" />} />
            </Routes>
        </Router>
    );
};

export default App;
