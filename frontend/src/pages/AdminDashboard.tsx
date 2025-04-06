import {
    Badge,
    Box,
    Button,
    Card,
    CardBody,
    Container,
    Heading,
    SimpleGrid,
    Stat,
    StatLabel,
    StatNumber,
    Table,
    Tbody,
    Td,
    Th,
    Thead,
    Tr,
    useToast,
} from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';

interface User {
    id: number;
    username: string;
    email: string;
    is_active: boolean;
    is_approved: boolean;
    created_at: string;
    is_admin: boolean;
}

const AdminDashboard: React.FC = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const toast = useToast();

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                return;
            }

            const response = await fetch('/api/users', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setUsers(data);
            }
        } catch (error) {
            console.error('Error fetching users:', error);
            toast({
                title: "Error",
                description: "Failed to fetch users",
                status: "error",
                duration: 3000,
                isClosable: true,
            });
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async (userId: number) => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`/api/approve_user/${userId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                toast({
                    title: "Success",
                    description: "User has been approved",
                    status: "success",
                    duration: 3000,
                    isClosable: true,
                });
                fetchUsers();
            } else {
                throw new Error('Failed to approve user');
            }
        } catch (error) {
            console.error('Error approving user:', error);
            toast({
                title: "Error",
                description: "Failed to approve user",
                status: "error",
                duration: 3000,
                isClosable: true,
            });
        }
    };

    const handleDisapprove = async (userId: number) => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`/api/disapprove_user/${userId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                toast({
                    title: "Success",
                    description: "User has been disapproved",
                    status: "success",
                    duration: 3000,
                    isClosable: true,
                });
                fetchUsers();
            } else {
                throw new Error('Failed to disapprove user');
            }
        } catch (error) {
            console.error('Error disapproving user:', error);
            toast({
                title: "Error",
                description: "Failed to disapprove user",
                status: "error",
                duration: 3000,
                isClosable: true,
            });
        }
    };

    const pendingUsers = users.filter(user => !user.is_approved).length;
    const totalUsers = users.length;
    const approvedUsers = users.filter(user => user.is_approved).length;

    return (
        <Container maxW="container.xl" py={8}>
            <Heading mb={6}>Admin Dashboard</Heading>

            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} mb={8}>
                <Card>
                    <CardBody>
                        <Stat>
                            <StatLabel>Total Users</StatLabel>
                            <StatNumber>{totalUsers}</StatNumber>
                        </Stat>
                    </CardBody>
                </Card>
                <Card>
                    <CardBody>
                        <Stat>
                            <StatLabel>Pending Approval</StatLabel>
                            <StatNumber>{pendingUsers}</StatNumber>
                        </Stat>
                    </CardBody>
                </Card>
                <Card>
                    <CardBody>
                        <Stat>
                            <StatLabel>Approved Users</StatLabel>
                            <StatNumber>{approvedUsers}</StatNumber>
                        </Stat>
                    </CardBody>
                </Card>
            </SimpleGrid>

            <Box overflowX="auto">
                <Table variant="simple">
                    <Thead>
                        <Tr>
                            <Th>ID</Th>
                            <Th>Username</Th>
                            <Th>Email</Th>
                            <Th>Status</Th>
                            <Th>Created At</Th>
                            <Th>Action</Th>
                        </Tr>
                    </Thead>
                    <Tbody>
                        {users.map((user) => (
                            <Tr key={user.id}>
                                <Td>{user.id}</Td>
                                <Td>{user.username}</Td>
                                <Td>{user.email}</Td>
                                <Td>
                                    <Badge
                                        colorScheme={user.is_approved ? 'green' : 'yellow'}
                                    >
                                        {user.is_approved ? 'Approved' : 'Pending'}
                                    </Badge>
                                </Td>
                                <Td>{new Date(user.created_at).toLocaleDateString()}</Td>
                                <Td>
                                    {user.is_approved ? (
                                        <Button
                                            colorScheme="red"
                                            size="sm"
                                            onClick={() => handleDisapprove(user.id)}
                                            isDisabled={user.is_admin}
                                        >
                                            Disapprove
                                        </Button>
                                    ) : (
                                        <Button
                                            colorScheme="blue"
                                            size="sm"
                                            onClick={() => handleApprove(user.id)}
                                        >
                                            Approve
                                        </Button>
                                    )}
                                </Td>
                            </Tr>
                        ))}
                    </Tbody>
                </Table>
            </Box>
        </Container>
    );
};

export default AdminDashboard;