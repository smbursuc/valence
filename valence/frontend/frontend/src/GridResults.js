import React, { useState, useEffect, useRef } from 'react';
import {
    Box, Flex, Heading, Spacer, Button, IconButton, Input, InputGroup, InputLeftElement,
    InputRightElement, Text, ScaleFade, keyframes, Stack, VStack, StackDivider, Card, CardBody, CardHeader, CardFooter,
    CircularProgress, CircularProgressLabel, SimpleGrid, Grid, Modal, ModalOverlay, ModalContent, ModalHeader, ModalFooter, ModalBody, ModalCloseButton, useDisclosure, HStack
} from '@chakra-ui/react';
import { FaSearch, FaSpotify, FaPlay, FaPause } from 'react-icons/fa'
import { ModalWindow } from './ModalWindow';
import { gsap } from 'gsap';

function ColorPicker(score) {
    let color = ""
    if (score >= 0 && score <= 5000) {
        color = "green"
    }
    else if (score > 5000 && score <= 7500) {
        color = "green.300"
    }
    else if (score > 7500 && score <= 10000) {
        color = "yellow"
    }
    else if (score > 10000 && score <= 15000) {
        color = "yellow.300"
    }
    else if (score > 15000 && score <= 20000) {
        color = "orange"
    }
    else if (score > 20000) {
        color = "red"
    }
    return color
}
function getIndex(name, grid) {
    for (let i = 0; i < grid.length; i++) {
        if (grid[i].id === name) {
            return i
        }
    }
}
export function GridResults({ artist, setClicked, setValue, clicked, setShowResults, payload, isDefaultSettings, usingID, artistID }) {
    // let [grid, setGrid] = useState([
    //     { name: "Ariana Grande", score: 10 },
    //     { name: "Taylor Swift", score: 20 },
    //     { name: "Justin Bieber", score: 30 },
    //     { name: "Katy Perry", score: 40 },
    //     { name: "Beyonce", score: 50 },
    //     { name: "Rihanna", score: 60 },
    //     { name: "Lady Gaga", score: 70 },
    // ])
    // grid = grid.sort((a, b) => (a.score > b.score) ? 1 : -1)\
    let [grid, setGrid] = useState([])
    let [oldGrid, setOldGrid] = useState([])

    const isDefaultSettingsRef = useRef();

    useEffect(() => {
        isDefaultSettingsRef.current = isDefaultSettings;
    }, []);

    

    const wsRef = useRef();
    useEffect(() => {
        if (!wsRef.current) {
            if (usingID) {
                console.log(artistID)
                wsRef.current = new WebSocket(`ws://127.0.0.1:8000/ws/some_url/?id=${artistID}/`);
            }
            else
                {
                    wsRef.current = new WebSocket(`ws://127.0.0.1:8000/ws/some_url/?artist_name=${artist}/`);
                }
            wsRef.current.onopen = () => {
                console.log(payload)
                wsRef.current.send(JSON.stringify(payload));
            };
            wsRef.current.onmessage = (event) => {
                const receivedMessage = event.data;
                const parsedData = JSON.parse(receivedMessage);
                if ("status" in parsedData && parsedData["status"] === "done") {
                    setClicked(false)
                }
                else {
                    console.log(receivedMessage);
                    setGrid((prevGrid) => [...prevGrid, parsedData]);
                }
            };
        }

        return () => {
            wsRef.current.close();
        }
    }, [])

    useEffect(() => {
        setOldGrid(grid);
        if (payload["distance"] === "cosine")
            grid = grid.sort((a, b) => (a.score < b.score) ? 1 : -1)
        else
            grid = grid.sort((a, b) => (a.score > b.score) ? 1 : -1)
        // console.log(grid);
    }, [grid]);



    useEffect(() => {
        // console.log(oldGrid);
    }, [oldGrid]);

    let card_refs = useRef([])
    card_refs.current = []

    const addToRefs = (el) => {
        if (el && !card_refs.current.includes(el)) {
            card_refs.current.push(el)
        }
    }

    useEffect(() => {
        card_refs.current.forEach((ref, index) => {
            if (getIndex(ref.id, grid) !== getIndex(ref.id, oldGrid)) {
                gsap.fromTo(ref, { opacity: 0 }, { opacity: 1, duration: 1 })
            }
        })
    }, [grid])


    function handleClick() {
        const temp_array = [...grid]
        const aux = temp_array[1]
        temp_array[1] = temp_array[grid.length - 1]
        temp_array[grid.length - 1] = aux
        let first_elem = card_refs.current[0]
        let last_elem = card_refs.current[card_refs.current.length - 1]

        setOldGrid(grid)
        setGrid(temp_array)
    }

    function stopResults() {
        wsRef.current.close()
        setClicked(false)
        //setValue("")
    }

    const { isOpen, onOpen, onClose } = useDisclosure()
    const [selectedArtist, setSelectedArtist] = useState(null)

    const openModal = (artist) => {
        setSelectedArtist(artist)
        onOpen()
    }

    function truncate(num, places) {
        return Math.trunc(num * Math.pow(10, places)) / Math.pow(10, places);
    }


    return (
        <VStack padding={5}>
            {clicked && <Button onClick={stopResults} marginBottom={"5vh"}>
                Stop generating results
            </Button>}
            {!clicked &&
                <Flex align={"center"} flexDirection={"column"} marginBottom={"5vh"}>
                    <Box bgColor={"teal"} borderRadius={"1em"} padding={"25px"} marginBottom={"25px"} >
                        <Text fontSize="1em" fontWeight="bold" color="white">
                            These are the results for {artist}!
                        </Text>
                    </Box>
                    <Button onClick={() => {
                        setShowResults(false)
                    }}>
                        Search another artist
                    </Button>
                </Flex>}
            <SimpleGrid columns={{sm:1, md:2, lg:3, xl: 5}} spacing={10}>
                {
                    grid.map((artist, index) => {
                        if (index < 10)
                            return (
                                <Card bgColor={isDefaultSettingsRef.current == true ? ColorPicker(artist.score) : "white"} ref={addToRefs} onClick={() => openModal(artist)} key={artist.id} id={artist.id} cursor={"pointer"} minWidth={"150px"} alignItems={"center"}>
                                    <CardHeader>
                                        <Heading size='md'>{artist.name}</Heading>
                                    </CardHeader>
                                    <CardBody>
                                        <Stack divider={<StackDivider />} spacing='4'>
                                            <Text>
                                                Score: {truncate(artist.score, 2)}
                                            </Text>
                                        </Stack>
                                    </CardBody>
                                </Card>
                            );
                    })

                }
            </SimpleGrid>
            {selectedArtist && <ModalWindow isOpen={isOpen} onClose={onClose} artist={selectedArtist} />}
        </VStack>
    )
}