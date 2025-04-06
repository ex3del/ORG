import { Box, Button, Flex, useColorModeValue } from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const Navigation: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const bgColor = useColorModeValue('gray.700', 'navy.900');
    const [isAdmin, setIsAdmin] = useState(false);

    useEffect(() => {
        const checkAdminStatus = async () => {
            const token = localStorage.getItem('token');
            if (!token) return;

            try {
                const response = await fetch('/api/users/me', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                if (response.ok) {
                    const userData = await response.json();
                    setIsAdmin(userData.is_admin);
                }
            } catch (error) {
                console.error('Error checking admin status:', error);
            }
        };

        checkAdminStatus();
    }, []);

    const isActivePath = (path: string) => location.pathname === path;

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('isAdmin');
        navigate('/login');
    };

    return (
        <Box bg={bgColor} px={4} py={2} width="100%">
            <Flex justifyContent="space-between" alignItems="center">
                <Flex gap={4}>
                    <Button
                        colorScheme={isActivePath('/chats') ? 'blue' : 'gray'}
                        onClick={() => navigate('/chats')}
                    >
                        Chats
                    </Button>
                    <Button
                        colorScheme={isActivePath('/documents') ? 'blue' : 'gray'}
                        onClick={() => navigate('/documents')}
                    >
                        Documents
                    </Button>
                    <Button
                        colorScheme={isActivePath('/settings') ? 'blue' : 'gray'}
                        onClick={() => navigate('/settings')}
                    >
                        Settings
                    </Button>
                    {isAdmin && (
                        <Button
                            colorScheme={isActivePath('/admin') ? 'blue' : 'gray'}
                            onClick={() => navigate('/admin')}
                        >
                            Admin
                        </Button>
                    )}
                </Flex>
                <Button
                    colorScheme="red"
                    variant="outline"
                    size="sm"
                    onClick={handleLogout}
                >
                    Logout
                </Button>
            </Flex>
        </Box>
    );
};

export default Navigation;