import { AddIcon, DeleteIcon, ViewIcon } from '@chakra-ui/icons';
import {
    AlertDialog,
    AlertDialogBody,
    AlertDialogContent,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogOverlay,
    Box,
    Button,
    Container,
    Flex,
    Heading,
    IconButton,
    Table,
    Tbody,
    Td,
    Text,
    Th,
    Thead,
    Tr,
    useToast,
} from '@chakra-ui/react';
import { AnimatePresence, motion } from 'framer-motion';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useDropzone } from 'react-dropzone';

const MotionBox = motion(Box);

interface Document {
    id: number;
    file_name: string;
    uploaded_at: string;
    file_path: string;
}

const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB in bytes
const MAX_DOCUMENTS = 10;

const DocumentsPage: React.FC = () => {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [isUploading, setIsUploading] = useState(false);
    const [deleteDocId, setDeleteDocId] = useState<number | null>(null);
    const toast = useToast();
    const cancelRef = useRef<any>(null);

    const fetchDocuments = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/documents', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setDocuments(data);
            }
        } catch (error) {
            console.error('Error fetching documents:', error);
            toast({
                title: "Error",
                description: "Failed to fetch documents",
                status: "error",
                duration: 3000,
                isClosable: true,
            });
        }
    };

    useEffect(() => {
        fetchDocuments();
    }, []);

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        if (documents.length + acceptedFiles.length > MAX_DOCUMENTS) {
            toast({
                title: "Error",
                description: `You can only upload up to ${MAX_DOCUMENTS} documents`,
                status: "error",
                duration: 3000,
                isClosable: true,
            });
            return;
        }

        for (const file of acceptedFiles) {
            if (file.size > MAX_FILE_SIZE) {
                toast({
                    title: "Error",
                    description: `File ${file.name} exceeds 20MB limit`,
                    status: "error",
                    duration: 3000,
                    isClosable: true,
                });
                continue;
            }

            if (!file.name.toLowerCase().endsWith('.pdf')) {
                toast({
                    title: "Error",
                    description: `File ${file.name} is not a PDF`,
                    status: "error",
                    duration: 3000,
                    isClosable: true,
                });
                continue;
            }

            try {
                setIsUploading(true);
                const formData = new FormData();
                formData.append('file', file);

                const token = localStorage.getItem('token');
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    body: formData
                });

                if (response.ok) {
                    await fetchDocuments();
                    toast({
                        title: "Success",
                        description: `${file.name} uploaded successfully`,
                        status: "success",
                        duration: 3000,
                        isClosable: true,
                    });
                }
            } catch (error) {
                console.error('Error uploading file:', error);
                toast({
                    title: "Error",
                    description: `Failed to upload ${file.name}`,
                    status: "error",
                    duration: 3000,
                    isClosable: true,
                });
            } finally {
                setIsUploading(false);
            }
        }
    }, [documents.length, toast]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf']
        },
        noClick: true // Disable click handling on the wrapper
    });

    const handleDelete = async (docId: number) => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`/api/documents/${docId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                setDocuments(docs => docs.filter(doc => doc.id !== docId));
                toast({
                    title: "Success",
                    description: "Document deleted successfully",
                    status: "success",
                    duration: 3000,
                    isClosable: true,
                });
            }
        } catch (error) {
            console.error('Error deleting document:', error);
            toast({
                title: "Error",
                description: "Failed to delete document",
                status: "error",
                duration: 3000,
                isClosable: true,
            });
        } finally {
            setDeleteDocId(null);
        }
    };

    const viewDocument = async (filePath: string) => {
        try {
            // Remove /app prefix if it exists since it's only used in the container
            const cleanPath = filePath.replace('/app/', '');
            const token = localStorage.getItem('token');
            const response = await fetch(`/api/view/${cleanPath}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                window.open(url, '_blank');
            } else {
                toast({
                    title: "Error",
                    description: "Failed to open document",
                    status: "error",
                    duration: 3000,
                    isClosable: true,
                });
            }
        } catch (error) {
            console.error('Error viewing document:', error);
            toast({
                title: "Error",
                description: "Failed to open document",
                status: "error",
                duration: 3000,
                isClosable: true,
            });
        }
    };

    return (
        <Container maxW="container.xl" py={8}>
            <Heading mb={6}>Documents</Heading>

            <Box
                {...getRootProps()}
                position="relative"
                cursor="pointer"
            >
                <MotionBox
                    border="2px dashed"
                    borderColor={isDragActive ? "blue.500" : "gray.300"}
                    borderRadius="lg"
                    p={10}
                    mb={6}
                    textAlign="center"
                    bg={isDragActive ? "blue.50" : "transparent"}
                    _hover={{ borderColor: "blue.500" }}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{
                        opacity: 1,
                        y: 0,
                        transition: { duration: 0.2 }
                    }}
                    whileHover={{
                        scale: 1.01,
                        transition: { duration: 0.2 }
                    }}
                    onClick={() => {
                        // Manually trigger file input click
                        const input = document.createElement('input');
                        input.type = 'file';
                        input.accept = '.pdf';
                        input.multiple = true;
                        input.onchange = (e) => {
                            const files = (e.target as HTMLInputElement).files;
                            if (files) {
                                onDrop(Array.from(files));
                            }
                        };
                        input.click();
                    }}
                >
                    <input {...getInputProps()} />
                    <Flex direction="column" align="center" justify="center">
                        <AddIcon mb={2} w={8} h={8} color={isDragActive ? "blue.500" : "gray.500"} />
                        {isDragActive ? (
                            <Text color="blue.500" fontSize="lg">Drop the files here</Text>
                        ) : (
                            <>
                                <Text color="gray.500" fontSize="lg">Drag & drop PDF files here, or click to select</Text>
                                <Text color="gray.400" mt={2}>Maximum file size: 20MB</Text>
                                <Text color="gray.400">Documents allowed: {MAX_DOCUMENTS - documents.length} of {MAX_DOCUMENTS}</Text>
                            </>
                        )}
                    </Flex>
                </MotionBox>
            </Box>

            <AnimatePresence>
                {documents.length > 0 ? (
                    <Box overflowX="auto">
                        <Table variant="simple">
                            <Thead>
                                <Tr>
                                    <Th>Name</Th>
                                    <Th>Uploaded At</Th>
                                    <Th>Actions</Th>
                                </Tr>
                            </Thead>
                            <Tbody>
                                {documents.map((doc) => (
                                    <Tr key={doc.id}>
                                        <Td>{doc.file_name}</Td>
                                        <Td>{new Date(doc.uploaded_at).toLocaleString()}</Td>
                                        <Td>
                                            <IconButton
                                                aria-label="View document"
                                                icon={<ViewIcon />}
                                                mr={2}
                                                colorScheme="blue"
                                                onClick={() => viewDocument(doc.file_path)}
                                            />
                                            <IconButton
                                                aria-label="Delete document"
                                                icon={<DeleteIcon />}
                                                colorScheme="red"
                                                onClick={() => setDeleteDocId(doc.id)}
                                            />
                                        </Td>
                                    </Tr>
                                ))}
                            </Tbody>
                        </Table>
                    </Box>
                ) : (
                    <MotionBox
                        textAlign="center"
                        p={8}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                    >
                        <Text color="gray.500">No documents uploaded yet</Text>
                    </MotionBox>
                )}
            </AnimatePresence>

            <AlertDialog
                isOpen={deleteDocId !== null}
                leastDestructiveRef={cancelRef}
                onClose={() => setDeleteDocId(null)}
            >
                <AlertDialogOverlay>
                    <AlertDialogContent>
                        <AlertDialogHeader>Delete Document</AlertDialogHeader>
                        <AlertDialogBody>
                            Are you sure? This action cannot be undone.
                        </AlertDialogBody>
                        <AlertDialogFooter>
                            <Button ref={cancelRef} onClick={() => setDeleteDocId(null)}>
                                Cancel
                            </Button>
                            <Button
                                colorScheme="red"
                                onClick={() => deleteDocId && handleDelete(deleteDocId)}
                                ml={3}
                            >
                                Delete
                            </Button>
                        </AlertDialogFooter>
                    </AlertDialogContent>
                </AlertDialogOverlay>
            </AlertDialog>
        </Container>
    );
};

export default DocumentsPage;