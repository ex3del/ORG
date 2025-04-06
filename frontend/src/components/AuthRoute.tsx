import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import Navigation from './Navigation';

interface AuthRouteProps {
    children: React.ReactNode;
    requireAdmin?: boolean;
}

const AuthRoute: React.FC<AuthRouteProps> = ({ children, requireAdmin = false }) => {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
    const [isAdmin, setIsAdmin] = useState<boolean>(false);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                setIsAuthenticated(false);
                setIsLoading(false);
                return;
            }

            try {
                const response = await fetch('/api/users/me', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const userData = await response.json();
                    setIsAdmin(userData.is_admin);
                    setIsAuthenticated(true);

                    if (requireAdmin && !userData.is_admin) {
                        setIsAuthenticated(false);
                    }
                } else {
                    setIsAuthenticated(false);
                    localStorage.removeItem('token');
                }
            } catch (error) {
                console.error('Auth check error:', error);
                setIsAuthenticated(false);
                localStorage.removeItem('token');
            }
            setIsLoading(false);
        };

        checkAuth();
    }, [requireAdmin]);

    if (isLoading) {
        return null;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" />;
    }

    if (requireAdmin && !isAdmin) {
        return <Navigate to="/dashboard" />;
    }

    return (
        <>
            <Navigation />
            {children}
        </>
    );
};

export default AuthRoute;