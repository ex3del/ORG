import React from 'react';
import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import AuthRoute from './components/AuthRoute';
import AdminDashboard from './pages/AdminDashboard';
import ChatsPage from './pages/ChatsPage';
import Dashboard from './pages/Dashboard';
import DocumentsPage from './pages/DocumentsPage';
import Login from './pages/Login';
import Register from './pages/Register';
import SettingsPage from './pages/SettingsPage';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected Routes */}
        <Route path="/dashboard" element={
          <AuthRoute>
            <Dashboard />
          </AuthRoute>
        } />
        <Route path="/admin" element={
          <AuthRoute requireAdmin>
            <AdminDashboard />
          </AuthRoute>
        } />
        <Route path="/chats" element={
          <AuthRoute>
            <ChatsPage />
          </AuthRoute>
        } />
        <Route path="/documents" element={
          <AuthRoute>
            <DocumentsPage />
          </AuthRoute>
        } />
        <Route path="/settings" element={
          <AuthRoute>
            <SettingsPage />
          </AuthRoute>
        } />
      </Routes>
    </Router>
  );
};

export default App;