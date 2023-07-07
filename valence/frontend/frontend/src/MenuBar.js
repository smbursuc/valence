import { Box, Heading, Button, HStack } from '@chakra-ui/react';
import { Link } from 'react-router-dom';

function MenuBar() {
    return (
        //<Box bgImage={`url(${header_image})`} bgPosition="center" bgRepeat="no-repeat" bgSize="cover" py={4} px={8}></Box>
        <Box bgColor={"teal"}>
            <HStack spacing={5} padding={1}>
                <Heading as="h1" size="lg" fontWeight="bold" color="white">
                    Valence
                </Heading>
            </HStack>
        </Box>
    );
}

export default MenuBar;