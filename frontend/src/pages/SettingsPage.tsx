import { Box, Container, Heading } from '@chakra-ui/react';
import React from 'react';

const SettingsPage: React.FC = () => {
    return (
        <Container maxW="container.xl" py={8}>
            <Heading mb={6}>Settings</Heading>
            <Box>Settings options coming soon...</Box>
        </Container>
    );
};

export default SettingsPage;