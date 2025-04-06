import { Box, Container, Heading } from '@chakra-ui/react';
import React from 'react';

const DocumentsPage: React.FC = () => {
    return (
        <Container maxW="container.xl" py={8}>
            <Heading mb={6}>Documents</Heading>
            <Box>Document management coming soon...</Box>
        </Container>
    );
};

export default DocumentsPage;