import React, { useState, useEffect, useRef } from 'react';
import {
    Box, Flex, Heading, Spacer, Button, IconButton, Input, InputGroup, InputLeftElement,
    InputRightElement, Text, ScaleFade, keyframes, Stack, VStack, StackDivider, Card, CardBody, CardHeader, CardFooter,
    CircularProgress, CircularProgressLabel, SimpleGrid, Grid, Modal, ModalOverlay, ModalContent, ModalHeader, ModalFooter, ModalBody, ModalCloseButton, useDisclosure, HStack, Image
} from '@chakra-ui/react';
import { FaSearch, FaSpotify, FaPlay, FaPause } from 'react-icons/fa'

export function ModalWindow({ isOpen, onClose, artist }) {
    const audioRefs = useRef([])
    audioRefs.current = []

    const [isPlaying, setIsPlaying] = useState([]);
    const [artistInfo, setArtistInfo] = useState({});
    const addToAudioRefs = (el) => {
        if (el && !audioRefs.current.includes(el)) {
            audioRefs.current.push(el)
        }
    }

    function onCloseModal() {
        setIsPlaying([])
        onClose()
    }

    useEffect(() => {
        getArtistInfo(artist)
    }, [artist])


    const playSound = (index) => {
        console.log(audioRefs.current[index])
        var isPlaying = audioRefs.current[index].currentTime > 0 && !audioRefs.current[index].paused && !audioRefs.current[index].ended && audioRefs.current[index].readyState > audioRefs.current[index].HAVE_CURRENT_DATA;
        if (audioRefs.current[index] && !isPlaying) {
            audioRefs.current[index].play();
            setIsPlaying((prevData) => {
                const updatedData = [...prevData];
                updatedData[index] = true;
                return updatedData;
            });
        }
    };

    const pauseSound = (index) => {
        if (audioRefs.current[index]) {
            audioRefs.current[index].pause();
            setIsPlaying((prevData) => {
                const updatedData = [...prevData];
                updatedData[index] = false;
                return updatedData;
            });
        }
    };

    const getArtistInfo = (artist) => {
        fetch(`http://127.0.0.1:8000/valence/artist_info_lastfm/?query=${artist.name}`)
            .then(response => response.json())
            .then(data => {
                let results = data.results.artist
                let bio = results.bio.summary
                let genres = results.tags.tag.map((tag) => tag.name)
                let listeners = results.stats.listeners
                let playcount = results.stats.playcount
                let artistInfo = {
                    bio: bio,
                    genres: genres,
                    listeners: listeners,
                    playcount: playcount
                }
                setArtistInfo(artistInfo)
            }
            )
    }


    return (
        <Modal isOpen={isOpen}
            onClose={onCloseModal} isCentered size={"xl"}>
            <ModalOverlay />
            <ModalContent maxW="1200px" height={["100%", "100%", "75%", "75%"]} overflowY={["scroll", "scroll", "scroll", "hidden"]}>
                <ModalHeader>General information</ModalHeader>
                <ModalCloseButton />
                <ModalBody>
                    <HStack justifyContent={"center"} align={"center"} flexWrap={["wrap","wrap","wrap","nowrap"]} spacing={5}>
                        <Stack>
                            <HStack>
                                <Card justifyContent={"center"} align={"center"}>
                                    <CardHeader>
                                        <Heading size='md'>{artist.name}</Heading>
                                    </CardHeader>
                                    <CardBody>
                                        <Stack divider={<StackDivider />} spacing='4' alignItems={"center"}>
                                            <Image src={artist.image_url} alt={artist.name} boxSize={[100, 150, 200]} />
                                            <Button leftIcon={<FaSpotify />} onClick={() => window.open(artist.spotify_link)}>
                                                Spotify Page
                                            </Button>
                                            <Text>
                                                ID: {artist.id}
                                            </Text>
                                        </Stack>
                                    </CardBody>
                                </Card>
                            </HStack>
                        </Stack>
                        <Stack maxW={"500px"} maxH={"600px"} spacing={5}>
                            <Text as="b" fontSize={"lg"}>
                                Score: {Math.trunc(artist.score)}
                            </Text>
                            {
                                Object.entries(artistInfo).map(([key, value]) => {
                                    let val = ''
                                    if(value instanceof Array){
                                        for(let i = 0; i < value.length; i++){
                                            val = val + value[i] + ', '
                                        }
                                        val = val.slice(0, -2)
                                    }
                                    else{
                                        if(key === 'bio')
                                        {
                                            let toCut = value.indexOf('<a href')
                                            val = value.slice(0, toCut)
                                        }
                                        else if(key === 'listeners' || key === 'playcount'){
                                            val = parseInt(value).toLocaleString()
                                        }
                                        else
                                            val = value
                                    }
                                    if (key) {
                                        return (
                                            <Text key={key}>
                                                {key.charAt(0).toUpperCase() + key.slice(1)}: {val}
                                            </Text>
                                        )
                                    }
                                }
                                )
                            }
                        </Stack>
                        <Card>
                            <CardHeader>
                                <Heading size='md'>Top Tracks</Heading>
                            </CardHeader>
                            <CardBody>
                                <Stack divider={<StackDivider />} spacing='4'>
                                    {
                                        artist && artist.top_tracks.map((track, index) => {
                                            return (
                                                <HStack key={index} flexWrap={"wrap"}>
                                                    {track.preview_url && <IconButton icon={!isPlaying[index] ? <FaPlay /> : <FaPause />} onClick={() => {
                                                        if (!isPlaying[index])
                                                            playSound(index)
                                                        else
                                                            pauseSound(index)
                                                    }} />}
                                                    <img src={track.image_url} alt={track.name} style={{ width: '50px', height: 'auto' }} />
                                                    <Text>
                                                        {index + 1}. {track.name}
                                                    </Text>
                                                    <audio ref={addToAudioRefs} src={track.preview_url} />
                                                </HStack>
                                            )
                                        }
                                        )
                                    }
                                </Stack>
                            </CardBody>
                        </Card>
                    </HStack>
                </ModalBody>

                <ModalFooter>
                    <Button colorScheme='blue' mr={3} onClick={onClose}>
                        Close
                    </Button>
                    {/* <Button variant='ghost'>Secondary Action</Button> */}
                </ModalFooter>
            </ModalContent>
        </Modal>
    )
}