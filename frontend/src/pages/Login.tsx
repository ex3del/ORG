import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import {
    Box,
    Button,
    Flex,
    Input,
    Stack,
    Text,
} from '@chakra-ui/react';
import { motion } from 'framer-motion';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const MotionStack = motion(Stack);

const Login: React.FC = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async () => {
        if (!username || !password) {
            alert('Please fill in all fields');
            return;
        }

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    username: username,
                    password: password,
                }),
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('token', data.access_token);

                // Get user data to check if admin
                const userResponse = await fetch('/api/users/me', {
                    headers: {
                        'Authorization': `Bearer ${data.access_token}`
                    }
                });

                if (userResponse.ok) {
                    const userData = await userResponse.json();
                    localStorage.setItem('isAdmin', userData.is_admin ? 'true' : 'false');
                }

                navigate('/dashboard');
            } else {
                const errorData = await response.json();
                alert(errorData.detail || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
            alert('An error occurred during login');
        }
    };

    return (
        <Flex
            minH="100vh"
            align="center"
            justify="center"
            bg="gray.800"
        >
            <MotionStack
                initial={{ opacity: 0, y: -50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ type: "spring", stiffness: 100 }}
                width={{ base: '90%', md: '400px' }}
                gap={4}
                p={8}
                borderRadius="lg"
                boxShadow="lg"
                bg="gray.700"
            >
                <Text fontSize="2xl" fontWeight="bold" color="gray.100">
                    Login
                </Text>

                <Box>
                    <Text mb={2} color="gray.300">Username</Text>
                    <Input
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        color="gray.100"
                        _placeholder={{ color: 'gray.500' }}
                    />
                </Box>

                <Box>
                    <Text mb={2} color="gray.300">Password</Text>
                    <Box position="relative">
                        <Input
                            pr="4.5rem"
                            type={showPassword ? 'text' : 'password'}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            color="gray.100"
                            _placeholder={{ color: 'gray.500' }}
                        />
                        <Button
                            position="absolute"
                            right="0"
                            top="50%"
                            transform="translateY(-50%)"
                            h="1.75rem"
                            size="sm"
                            onClick={() => setShowPassword(!showPassword)}
                            variant="ghost"
                            color="gray.300"
                        >
                            {showPassword ? <ViewOffIcon /> : <ViewIcon />}
                        </Button>
                    </Box>
                </Box>

                <Button
                    colorScheme="blue"
                    width="full"
                    onClick={handleLogin}
                >
                    Login
                </Button>

                <Text color="gray.300">
                    Don't have an account?{' '}
                    <Button
                        onClick={() => navigate('/register')}
                        variant="ghost"
                        color="blue.300"
                        size="sm"
                        _hover={{ color: 'blue.200' }}
                    >
                        Register
                    </Button>
                </Text>
            </MotionStack>
        </Flex>
    );
};

export default Login;