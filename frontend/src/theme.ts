import { extendTheme, type ThemeConfig } from '@chakra-ui/react';

const config: ThemeConfig = {
    initialColorMode: 'dark',
    useSystemColorMode: false,
};

const theme = extendTheme({
    config,
    colors: {
        navy: {
            900: '#0a192f',
            800: '#112240',
            700: '#1a365d',
            600: '#234e78',
            500: '#2c6493',
        },
    },
});

export default theme;