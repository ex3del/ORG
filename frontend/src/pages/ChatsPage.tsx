import { AddIcon, ChatIcon, EditIcon, HamburgerIcon } from '@chakra-ui/icons';
import {
    Box,
    Button,
    Drawer,
    DrawerBody,
    DrawerContent,
    DrawerHeader,
    DrawerOverlay,
    Flex,
    Heading,
    Icon,
    IconButton,
    Input,
    List,
    ListItem,
    Text,
    useBreakpointValue,
    useDisclosure,
    useToast
} from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';

interface Message {
    id: number;
    message_text: string;
    timestamp: string;
    is_user: boolean;
}

interface ChatSession {
    id: number;
    session_name: string;
    created_at: string;
    messages: Message[];
}

const ChatsPage: React.FC = () => {
    const [chats, setChats] = useState<ChatSession[]>([]);
    const [selectedChat, setSelectedChat] = useState<ChatSession | null>(null);
    const [newMessage, setNewMessage] = useState('');
    const [editingName, setEditingName] = useState<{ id: number; name: string } | null>(null);
    const { isOpen, onOpen, onClose } = useDisclosure();
    const toast = useToast();
    const isMobile = useBreakpointValue({ base: true, md: false });

    useEffect(() => {
        fetchChats();
    }, []);

    const fetchChats = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/chat_sessions', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setChats(data);
                if (data.length > 0 && !selectedChat) {
                    setSelectedChat(data[0]);
                }
            }
        } catch (error) {
            console.error('Error fetching chats:', error);
        }
    };

    const createNewChat = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/chat_sessions', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_name: 'New Chat'
                })
            });

            if (response.ok) {
                const newChat = await response.json();
                setChats([...chats, newChat]);
                setSelectedChat(newChat);
                if (isMobile) {
                    onClose();
                }
            }
        } catch (error) {
            console.error('Error creating chat:', error);
            toast({
                title: "Error",
                description: "Failed to create new chat",
                status: "error",
                duration: 3000,
                isClosable: true,
            });
        }
    };

    const updateChatName = async (chatId: number, newName: string) => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`/api/chat_sessions/${chatId}`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_name: newName
                })
            });

            if (response.ok) {
                setChats(chats.map(chat =>
                    chat.id === chatId ? { ...chat, session_name: newName } : chat
                ));
                if (selectedChat?.id === chatId) {
                    setSelectedChat({ ...selectedChat, session_name: newName });
                }
                setEditingName(null);
            }
        } catch (error) {
            console.error('Error updating chat name:', error);
            toast({
                title: "Error",
                description: "Failed to update chat name",
                status: "error",
                duration: 3000,
                isClosable: true,
            });
        }
    };

    const sendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedChat || !newMessage.trim()) return;

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`/api/chat_sessions/${selectedChat.id}/messages`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message_text: newMessage,
                    is_user: true
                })
            });

            if (response.ok) {
                const message = await response.json();
                setSelectedChat({
                    ...selectedChat,
                    messages: [...selectedChat.messages, message]
                });
                setNewMessage('');

                // If this is the first message and chat name is "New Chat", update the name
                if (selectedChat.messages.length === 0 && selectedChat.session_name === 'New Chat') {
                    const defaultName = newMessage.slice(0, 30) + (newMessage.length > 30 ? '...' : '');
                    updateChatName(selectedChat.id, defaultName);
                }
            }
        } catch (error) {
            console.error('Error sending message:', error);
            toast({
                title: "Error",
                description: "Failed to send message",
                status: "error",
                duration: 3000,
                isClosable: true,
            });
        }
    };

    const ChatSidebar = () => (
        <Box
            w={isMobile ? "full" : "300px"}
            h="full"
            borderRight="1px"
            borderColor="gray.200"
            bg="gray.50"
        >
            <Flex direction="column" h="full">
                <Flex justify="space-between" align="center" p={4} borderBottom="1px" borderColor="gray.200">
                    <Heading size="md">Chats</Heading>
                    <IconButton
                        aria-label="New chat"
                        icon={<AddIcon />}
                        onClick={createNewChat}
                        size="sm"
                    />
                </Flex>
                <List spacing={1} p={2} overflowY="auto" flex={1}>
                    {chats.map((chat) => (
                        <ListItem
                            key={chat.id}
                            p={2}
                            bg={selectedChat?.id === chat.id ? 'blue.100' : 'transparent'}
                            borderRadius="md"
                            cursor="pointer"
                            _hover={{ bg: selectedChat?.id === chat.id ? 'blue.100' : 'gray.100' }}
                            onClick={() => {
                                setSelectedChat(chat);
                                if (isMobile) onClose();
                            }}
                        >
                            <Flex align="center" justify="space-between">
                                {editingName?.id === chat.id ? (
                                    <Input
                                        value={editingName.name}
                                        onChange={(e) => setEditingName({ ...editingName, name: e.target.value })}
                                        onBlur={() => updateChatName(chat.id, editingName.name)}
                                        onKeyPress={(e) => {
                                            if (e.key === 'Enter') {
                                                updateChatName(chat.id, editingName.name);
                                            }
                                        }}
                                        size="sm"
                                    />
                                ) : (
                                    <>
                                        <Flex align="center" flex={1}>
                                            <Icon as={ChatIcon} mr={2} />
                                            <Text isTruncated>{chat.session_name}</Text>
                                        </Flex>
                                        <IconButton
                                            aria-label="Edit chat name"
                                            icon={<EditIcon />}
                                            size="xs"
                                            variant="ghost"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setEditingName({ id: chat.id, name: chat.session_name });
                                            }}
                                        />
                                    </>
                                )}
                            </Flex>
                        </ListItem>
                    ))}
                </List>
            </Flex>
        </Box>
    );

    return (
        <Flex h="calc(100vh - 120px)">
            {isMobile ? (
                <>
                    <IconButton
                        aria-label="Open chats"
                        icon={<HamburgerIcon />}
                        position="fixed"
                        top="80px"
                        left={4}
                        onClick={onOpen}
                    />
                    <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
                        <DrawerOverlay>
                            <DrawerContent>
                                <DrawerHeader borderBottomWidth="1px">Chats</DrawerHeader>
                                <DrawerBody p={0}>
                                    <ChatSidebar />
                                </DrawerBody>
                            </DrawerContent>
                        </DrawerOverlay>
                    </Drawer>
                </>
            ) : (
                <ChatSidebar />
            )}

            <Flex flex={1} direction="column">
                {selectedChat ? (
                    <>
                        <Box flex={1} p={4} overflowY="auto">
                            {selectedChat.messages.map((message, index) => (
                                <Flex
                                    key={index}
                                    justify={message.is_user ? 'flex-end' : 'flex-start'}
                                    mb={4}
                                >
                                    <Box
                                        maxW="70%"
                                        bg={message.is_user ? 'blue.500' : 'gray.200'}
                                        color={message.is_user ? 'white' : 'black'}
                                        p={3}
                                        borderRadius="lg"
                                    >
                                        <Text>{message.message_text}</Text>
                                    </Box>
                                </Flex>
                            ))}
                        </Box>
                        <Box p={4} borderTop="1px" borderColor="gray.200">
                            <form onSubmit={sendMessage}>
                                <Flex gap={2}>
                                    <Input
                                        value={newMessage}
                                        onChange={(e) => setNewMessage(e.target.value)}
                                        placeholder="Type your message..."
                                    />
                                    <Button type="submit" colorScheme="blue">
                                        Send
                                    </Button>
                                </Flex>
                            </form>
                        </Box>
                    </>
                ) : (
                    <Flex justify="center" align="center" h="full">
                        <Button leftIcon={<AddIcon />} onClick={createNewChat}>
                            Start a new chat
                        </Button>
                    </Flex>
                )}
            </Flex>
        </Flex>
    );
};

export default ChatsPage;