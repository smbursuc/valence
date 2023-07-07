import React, { useState, useEffect, useRef } from 'react';
import {
    Box, Flex, Heading, Spacer, Button, IconButton, Input, InputGroup, InputLeftElement,
    InputRightElement, Text, ScaleFade, keyframes, Stack, VStack, StackDivider, Card, CardBody, CardHeader, CardFooter,
    CircularProgress, CircularProgressLabel, SimpleGrid, Grid, Modal, ModalOverlay, ModalContent, ModalHeader, ModalFooter, ModalBody,
    ModalCloseButton, useDisclosure, HStack
} from '@chakra-ui/react';
import { FaSearch, FaSpotify, FaPlay, FaBars } from 'react-icons/fa'
import { SlUser } from 'react-icons/sl'
import header_image from './images/4k_header.jpg';
import search_image from './images/search.jpg';
import { useInViewport } from 'react-in-viewport';
import { motion } from 'framer-motion';
import { gsap } from 'gsap';
import { Flip } from 'gsap/src/Flip'
import { ArtistImage } from './ArtistImage';
import { GridResults } from './GridResults';
import { AdvancedSearchModal } from './AdvancedSearchModal';
import { Link } from 'react-router-dom';
import MenuBar from './MenuBar';

function SearchBar() {
    const handleSearch = () => {
        // Handle search logic here
        console.log('Search clicked');
    };

    const [value, setValue] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [clicked, setClicked] = useState(false);
    const [showResults, setShowResults] = useState(false);
    const [showAdvancedSearch, setShowAdvancedSearch] = useState(false);
    const [payload, setPayload] = useState({});

    const [artistID, setArtistID] = useState(null);
    const [searchByIDResult, setSearchByIDResult] = useState('');
    const [usingID, setUsingID] = useState(false);

    const [searchParams, setSearchParams] = useState({
        key: false,
        tempo: false,
        liveness: false,
        danceability: false,
        energy: false,
        valence: false,
        acousticness: false,
        instrumentalness: false,
        bars: false,
        beats: false,
        sections: true,
        segments: true,
        tatums: false,
        use_genre: false,
        tracks: "10",
        distance: "euclidian"
    });

    const defaultSettings = useRef()
    useEffect(() => {
        defaultSettings.current = searchParams
    }, [])

    const [isDefaultSettings, setIsDefaultSettings] = useState(true);

    useEffect(() => {
        setPayload(searchParams)
        let defaultSettingsFlag = true
        for (const [key, value] of Object.entries(searchParams)) {
            if (value !== defaultSettings.current[key]) {
                console.log(key, value, defaultSettings.current[key])
                defaultSettingsFlag = false;
            }
        }
        setIsDefaultSettings(defaultSettingsFlag)
    }, [searchParams]);


    useEffect(() => {
        console.log(isDefaultSettings)
    }, [isDefaultSettings]);

    useEffect(() => {
        if (!clicked && !showResults) {
            const timeOutId = setTimeout(() => search(value), 1000);
            return () => clearTimeout(timeOutId);
        }
    }, [value, clicked]);

    useEffect(() => {
        console.log(artistID)
        if(artistID === ''){
            setSearchByIDResult('')
        }
        if (artistID !== null) {
            const timeOutId = setTimeout(() => searchByID(artistID), 1000);
            return () => clearTimeout(timeOutId);
        }
    }, [artistID])

    const searchByID = (id) => {
        if (id !== '') {
            fetch(`http://127.0.0.1:8000/valence/search_artist_id/?query=${id}`)
            .then(response => response.json())
            .then(data => {
                console.log(data);
                setSearchByIDResult(data.results.name);
            }
            );
        }
    }




    const search = (searchTerm) => {
        if (searchTerm !== '') {
            fetch(`http://127.0.0.1:8000/valence/search_artist/?query=${searchTerm}`)
            .then(response => response.json())
            .then(data => {
                console.log(data);
                setSearchResults(data.results);
            }
            );
        }
    }

    const handleAdvancedSearch = () => {
        console.log('Advanced search clicked');
        setShowAdvancedSearch(prevState => !prevState);
    };


    return (
        <Flex width="50%" flexDirection={"column"} align="center" minWidth={"350px"}>
            <InputGroup size="md" marginBottom={"3vh"}>
                <InputLeftElement pointerEvents={"none"} children={<FaSearch color="white" />} />
                <Input
                    type="text"
                    placeholder="Search..."
                    size="md"
                    focusBorderColor="blue.500"
                    borderRadius="md"
                    pr="4.5rem"
                    textColor={"white"}
                    value={value}
                    onChange={event => {
                        setShowAdvancedSearch(false);
                        if (!showResults) {
                            setValue(event.target.value)
                            if (event.target.value === "") {
                                setSearchResults([]);
                            }
                        }
                    }}
                />
                <InputRightElement>
                    <FaBars color="white" cursor={"pointer"} onClick={handleAdvancedSearch} />
                </InputRightElement>
            </InputGroup>
            {showAdvancedSearch && <AdvancedSearchModal searchParams={searchParams} setSearchParams={setSearchParams} setPayload={setPayload} />}
            {
                !showResults && value !== "" && !clicked && <Card marginTop={"2vh"} width="100%">
                    <CardHeader>
                        <Heading size='md'>Results</Heading>
                    </CardHeader>

                    <CardBody>
                        {
                            searchResults.map((artist) => {
                                return (
                                    <Stack divider={<StackDivider />} key={artist.id} spacing='4'>
                                        <Box p={2} cursor={"pointer"} onClick={() => {
                                            setClicked(true);
                                            setValue(artist.name);
                                            setShowResults(true);
                                            console.log(artist.name);
                                        }} _hover={{
                                            background: "white",
                                            color: "teal.500",
                                        }}>
                                            <Heading size='xs' textTransform='uppercase'>
                                                {artist.name}
                                            </Heading>
                                        </Box>
                                    </Stack>
                                );
                            }
                            )
                        }
                        {searchResults.length > 0 &&
                            <Stack marginTop={"3vh"} direction={["column","column","row"]} alignItems={"center"}>
                                <Text fontSize="sm" fontWeight="bold" color="black">
                                    Duplicate artists? Try typing the artist's Spotify ID instead:
                                </Text>
                                <Input size={"md"} maxW={"300px"} placeholder='Spotify ID...' onChange={event => {
                                    setArtistID(event.target.value)
                                }} onPaste={event => {
                                    setArtistID(event.target.value)
                                }}/>
                            </Stack>}
                        {searchByIDResult!== '' && searchResults.length > 0 && artistID !== '' &&
                            <Text fontSize="sm" fontWeight="bold" color="black">
                                Are you looking for
                                <Text as={"span"} sx={{
                                    pointerEvents: "auto",
                                    cursor: "pointer",
                                }} color={"teal"} onClick={() => {
                                    setClicked(true);
                                    setValue(searchByIDResult);
                                    setUsingID(true);
                                    setShowResults(true);
                                    setSearchByIDResult('');
                                }} >
                                    {` ${searchByIDResult}`}
                                </Text>
                                ?
                            </Text>}
                    </CardBody>
                </Card>
            }
            {clicked &&
                <VStack padding={"5vh"} spacing={4} align={"center"} >
                    <CircularProgress isIndeterminate color='green.300' />
                    <Box>
                        <Text fontSize="2xl" fontWeight="bold" color="white">
                            Waiting for results...
                        </Text>
                    </Box>
                </VStack>}
            {showResults && <GridResults artist={value} setClicked={setClicked} setValue={setValue}
                clicked={clicked} setShowResults={setShowResults} payload={payload} isDefaultSettings={isDefaultSettings} usingID={usingID}
                artistID={artistID} />}
        </Flex>
    );
}


function UpperDescription() {
    const welcome_animationKeyframes = keyframes`
    0% { transform: scale(0); transform: translate3d(0, 90px, 0); opacity: 0;}
    50% { transform: scale(1);  transform: translate3d(0, 90px, 0); opacity: 1; }
    100% { transform: translate3d(0, 0, 0);  }
    `;

    const welcome_animation = `${welcome_animationKeyframes} 3s`;

    const description_animationKeyframes = keyframes`
    0% { transform: scale(0); opacity: 0;}
    50% { transform: scale(0); opacity: 0; }
    100% { transform: scale(1) opacity: 1;  }
    `;

    const description_animation = `${description_animationKeyframes} 3s`;

    return (
        <Flex justifyContent={"center"} flexDirection={"column"} align={"center"} marginTop={"10vh"} width="50%" minWidth={"350px"}>
            <Box borderRadius={"1em"} padding={"25px"}
                as={motion.div}
                animation={welcome_animation}>
                <Text fontSize="2xl" fontWeight="bold" color="white">
                    Welcome to Valence!
                </Text>
            </Box>
            <Spacer />
            <Box bgColor={"teal"} borderRadius={"1em"} padding={"25px"} marginBottom={"25px"}
                as={motion.div}
                animation={description_animation}
                minWidth={"350px"}>
                <Text fontSize="1em" fontWeight="bold" color="white">
                    To get started type in an artist and wait for results to generate!
                </Text>
            </Box>
        </Flex>
    );
}


function PageContent() {

    const ref = React.useRef(null);
    const { enterCount } = useInViewport(ref, { rootMargin: "-300px" }, { disconnectOnLeave: false }, {});

    return (
        <Flex
            height="100%" align="center" bgImage={`url(${search_image})`}
            bgPosition="center" bgRepeat="no-repeat" bgSize="cover" position={"relative"} zIndex={1} flexDirection={"column"} overflow={"auto"}>
            <UpperDescription />
            <SearchBar />
            <Box
                position="fixed"
                top="0"
                left="0"
                right="0"
                bottom="0"
                bg="gray.500"
                opacity="0.8"
                filter="brightness(10%)"
                zIndex="-1"
            />
        </Flex>
    );
}


export default function App() {
    return (
        <Box>
            <Box height="200vh">
                <PageContent />
            </Box>
        </Box>
    );
}
