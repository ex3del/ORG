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
import { AnimatePresence, motion } from 'framer-motion';
import React, { useEffect, useRef, useState } from 'react';

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

const MotionFlex = motion(Flex);
const MotionBox = motion(Box);

const ChatsPage: React.FC = () => {
    const [chats, setChats] = useState<ChatSession[]>([]);
    const [selectedChat, setSelectedChat] = useState<ChatSession | null>(null);
    const [newMessage, setNewMessage] = useState('');
    const [editingName, setEditingName] = useState<{ id: number; name: string } | null>(null);
    const { isOpen, onOpen, onClose } = useDisclosure();
    const toast = useToast();
    const isMobile = useBreakpointValue({ base: true, md: false });
    const inputRef = useRef<HTMLInputElement>(null);
    const chatListRef = useRef<HTMLDivElement>(null);

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
                setChats(prevChats => [newChat, ...prevChats]);
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
        if (!newName.trim()) return;

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
                    setSelectedChat(prev => prev ? { ...prev, session_name: newName } : null);
                }
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
        } finally {
            setEditingName(null);
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

    const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>, chatId: number, name: string) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            updateChatName(chatId, name);
        }
    };

    const ChatSidebar = () => (
        <Box
            w={isMobile ? "full" : "300px"}
            h="full"
            borderRight="1px"
            borderColor="gray.600"
            bg="gray.800"
            overflowY="auto"
            ref={chatListRef}
        >
            <Flex direction="column" h="full">
                <Flex
                    justify="space-between"
                    align="center"
                    p={4}
                    borderBottom="1px"
                    borderColor="gray.600"
                    bg="gray.900"
                >
                    <Heading size="md" color="gray.100">Chats</Heading>
                    <IconButton
                        aria-label="New chat"
                        icon={<AddIcon />}
                        onClick={createNewChat}
                        size="sm"
                        colorScheme="blue"
                    />
                </Flex>
                <List spacing={1} p={2} overflowY="auto" flex={1}>
                    <AnimatePresence>
                        {chats.map((chat) => (
                            <MotionBox
                                key={chat.id}
                                initial={{ opacity: 0, y: -20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                transition={{ duration: 0.2 }}
                            >
                                <ListItem
                                    p={2}
                                    bg={selectedChat?.id === chat.id ? 'gray.700' : 'transparent'}
                                    borderRadius="md"
                                    cursor="pointer"
                                    _hover={{ bg: selectedChat?.id === chat.id ? 'gray.700' : 'gray.700' }}
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
                                                onKeyPress={(e) => handleKeyPress(e, chat.id, editingName.name)}
                                                size="sm"
                                                ref={inputRef}
                                                autoFocus
                                                color="white"
                                                bg="gray.700"
                                                _focus={{
                                                    bg: "gray.700",
                                                    borderColor: "blue.500"
                                                }}
                                            />
                                        ) : (
                                            <>
                                                <Flex align="center" flex={1}>
                                                    <Icon as={ChatIcon} mr={2} color="gray.300" />
                                                    <Text isTruncated color="gray.100">{chat.session_name}</Text>
                                                </Flex>
                                                <IconButton
                                                    aria-label="Edit chat name"
                                                    icon={<EditIcon />}
                                                    size="xs"
                                                    variant="ghost"
                                                    colorScheme="blue"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        setEditingName({ id: chat.id, name: chat.session_name });
                                                    }}
                                                />
                                            </>
                                        )}
                                    </Flex>
                                </ListItem>
                            </MotionBox>
                        ))}
                    </AnimatePresence>
                </List>
            </Flex>
        </Box>
    );

    return (
        <Flex h="calc(100vh - 120px)" bg="gray.900">
            {isMobile ? (
                <>
                    <IconButton
                        aria-label="Open chats"
                        icon={<HamburgerIcon />}
                        position="fixed"
                        top="80px"
                        left={4}
                        onClick={onOpen}
                        colorScheme="blue"
                    />
                    <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
                        <DrawerOverlay>
                            <DrawerContent bg="gray.800">
                                <DrawerHeader borderBottomWidth="1px" color="gray.100">Chats</DrawerHeader>
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

            <Flex flex={1} direction="column" bg="gray.900">
                <AnimatePresence mode="wait">
                    {selectedChat ? (
                        <MotionFlex
                            key="chat"
                            flex={1}
                            direction="column"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            transition={{ duration: 0.2 }}
                        >
                            <Box flex={1} p={4} overflowY="auto">
                                {selectedChat.messages.map((message, index) => (
                                    <MotionFlex
                                        key={index}
                                        justify={message.is_user ? 'flex-end' : 'flex-start'}
                                        mb={4}
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ duration: 0.3 }}
                                    >
                                        <Box
                                            maxW="70%"
                                            bg={message.is_user ? 'blue.600' : 'gray.700'}
                                            color="white"
                                            p={3}
                                            borderRadius="lg"
                                        >
                                            <Text>{message.message_text}</Text>
                                        </Box>
                                    </MotionFlex>
                                ))}
                            </Box>
                            <Box p={4} borderTop="1px" borderColor="gray.700">
                                <form onSubmit={sendMessage}>
                                    <Flex gap={2}>
                                        <Input
                                            value={newMessage}
                                            onChange={(e) => setNewMessage(e.target.value)}
                                            placeholder="Type your message..."
                                            bg="gray.800"
                                            color="white"
                                            _placeholder={{ color: 'gray.400' }}
                                            _focus={{
                                                borderColor: "blue.500",
                                                bg: "gray.800"
                                            }}
                                        />
                                        <Button type="submit" colorScheme="blue">
                                            Send
                                        </Button>
                                    </Flex>
                                </form>
                            </Box>
                        </MotionFlex>
                    ) : (
                        <MotionFlex
                            key="empty"
                            justify="center"
                            align="center"
                            h="full"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            transition={{ duration: 0.2 }}
                        >
                            <Button
                                leftIcon={<AddIcon />}
                                onClick={createNewChat}
                                colorScheme="blue"
                                size="lg"
                            >
                                Start a new chat
                            </Button>
                        </MotionFlex>
                    )}
                </AnimatePresence>
            </Flex>
        </Flex>
    );
};

export default ChatsPage;