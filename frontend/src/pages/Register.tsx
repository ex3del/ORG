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

const Register: React.FC = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const navigate = useNavigate();

    const handleRegister = async () => {
        if (!username || !email || !password) {
            alert('Please fill in all fields');
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('Please enter a valid email');
            return;
        }

        if (password.length < 6) {
            alert('Password must be at least 6 characters');
            return;
        }

        // TODO: Implement actual registration logic
        alert('Registration successful');
        navigate('/login');
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
                    Register
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
                    <Text mb={2} color="gray.300">Email</Text>
                    <Input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
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
                    onClick={handleRegister}
                >
                    Register
                </Button>

                <Text color="gray.300">
                    Already have an account?{' '}
                    <Button
                        onClick={() => navigate('/login')}
                        variant="ghost"
                        color="blue.300"
                        size="sm"
                        _hover={{ color: 'blue.200' }}
                    >
                        Login
                    </Button>
                </Text>
            </MotionStack>
        </Flex>
    );
};

export default Register;