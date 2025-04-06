import { Box, Container, Heading, keyframes } from '@chakra-ui/react';
import React from 'react';

const spinAnimation = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
`;

const pulseAnimation = keyframes`
  0% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 1; }
  100% { transform: scale(1); opacity: 0.5; }
`;

const orbitAnimation = keyframes`
  from { transform: rotate(0deg) translateX(80px) rotate(0deg); }
  to { transform: rotate(360deg) translateX(80px) rotate(-360deg); }
`;

const Dashboard: React.FC = () => {
    const spinningCircle = `${spinAnimation} 2s linear infinite`;
    const pulsing = `${pulseAnimation} 3s ease-in-out infinite`;

    return (
        <Container maxW="container.xl" py={8}>
            <Box
                height="70vh"
                display="flex"
                alignItems="center"
                justifyContent="center"
                position="relative"
            >
                {/* Main rotating circle with gradient */}
                <Box
                    width="200px"
                    height="200px"
                    borderRadius="50%"
                    position="relative"
                    bgGradient="linear(to-r, blue.400, purple.500)"
                    animation={spinningCircle}
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                    _before={{
                        content: '""',
                        position: 'absolute',
                        top: '-3px',
                        right: '-3px',
                        bottom: '-3px',
                        left: '-3px',
                        borderRadius: '50%',
                        background: 'linear-gradient(to right, #60a5fa, #a78bfa)',
                        filter: 'blur(10px)',
                        opacity: 0.7,
                    }}
                >
                    {/* Pulsing inner circle */}
                    <Box
                        width="150px"
                        height="150px"
                        borderRadius="50%"
                        bgGradient="radial(blue.500, transparent)"
                        animation={pulsing}
                        position="relative"
                        display="flex"
                        alignItems="center"
                        justifyContent="center"
                    />
                </Box>

                {/* Orbiting elements */}
                {[0, 120, 240].map((degree) => (
                    <Box
                        key={degree}
                        position="absolute"
                        width="20px"
                        height="20px"
                        borderRadius="50%"
                        bgGradient="linear(to-r, cyan.400, blue.500)"
                        animation={`${orbitAnimation} 4s linear infinite`}
                        sx={{
                            animationDelay: `${degree / 360}s`
                        }}
                        _before={{
                            content: '""',
                            position: 'absolute',
                            top: '-2px',
                            right: '-2px',
                            bottom: '-2px',
                            left: '-2px',
                            borderRadius: '50%',
                            background: 'linear-gradient(to right, #60a5fa, #a78bfa)',
                            filter: 'blur(5px)',
                            opacity: 0.7,
                        }}
                    />
                ))}

                {/* Centered text */}
                <Heading
                    size="2xl"
                    position="absolute"
                    color="white"
                    textShadow="0 0 10px rgba(66, 153, 225, 0.8)"
                    letterSpacing="wider"
                >
                    ORG
                </Heading>
            </Box>
        </Container>
    );
};

export default Dashboard;