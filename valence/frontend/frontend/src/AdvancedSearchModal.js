import React, { useState, useEffect, useRef } from 'react';
import {
    Box, Flex, Heading, Spacer, Button, IconButton, Input, InputGroup, InputLeftElement,
    InputRightElement, Text, ScaleFade, keyframes, Stack, VStack, StackDivider, Card, CardBody, CardHeader, CardFooter,
    CircularProgress, CircularProgressLabel, SimpleGrid, Grid, Modal, ModalOverlay, ModalContent, ModalHeader, ModalFooter, ModalBody, ModalCloseButton, useDisclosure, HStack, Switch,
    NumberInput, NumberInputField, NumberInputStepper, NumberIncrementStepper, NumberDecrementStepper, RadioGroup, Radio
} from '@chakra-ui/react';
import { FaQuestionCircle, FaCheck } from 'react-icons/fa'

export function AdvancedSearchModal({ searchParams, setSearchParams, setPayload }) {

    const [activeSearchParams, setActiveSearchParams] = useState(searchParams);


    // useEffect(() => {
    //     console.log(algorithmUSed);
    // }, [algorithmUSed]);

    useEffect(() => {
        console.log(searchParams);
    }, [activeSearchParams]);


    const handleSwitchChange = (key) => {
        setActiveSearchParams((prevData) => ({
            ...prevData,
            [key]: !prevData[key],
        }));
    };

    const handleDistanceChange = (value) => {
        setActiveSearchParams((prevData) => ({
            ...prevData,
            ["distance"]: value,
        }));
    };

    const handleNumberChange = (value) => {
        console.log(value)
        setActiveSearchParams((prevData) => ({
            ...prevData,
            ["tracks"]: value,
        }));
    };

    const handleContainerChange = (event) => {
        const { id } = event.target;
        if (!String(id).startsWith("radio")) {
            handleSwitchChange(id)
        }
    };

    const { isOpen, onOpen, onClose } = useDisclosure();

    const settingsChanged = () => {
        for (const [key, value] of Object.entries(activeSearchParams)) {
            if (value !== searchParams[key]) {
                return true;
            }
        }
    }

    return (
        <Stack bgColor={"white"} width="100%" borderRadius={"3px"} flexDirection={"column"}>
            <Stack padding={7} spacing={5}>
                <Flex onChange={handleContainerChange} id="search-options" flexWrap={"wrap"} gap={"1vw"}>
                    <Stack>
                        <HStack>
                            <Text as="b">
                                Audio features
                            </Text>
                            <IconButton icon={<FaQuestionCircle />} onClick={
                                () => {
                                    window.open("https://developer.spotify.com/documentation/web-api/reference/get-audio-features", "_blank")
                                }
                            }/>
                        </HStack>
                        <Switch size="sm" id="key" isChecked={activeSearchParams["key"]}>
                            Key
                        </Switch>
                        <Switch size="sm" id="tempo" isChecked={activeSearchParams["tempo"]}>
                            Tempo
                        </Switch>
                        <Switch size="sm" id="liveness" isChecked={activeSearchParams["liveness"]}>
                            Liveness
                        </Switch>
                        <Switch size="sm" id="danceability" isChecked={activeSearchParams["danceability"]}>
                            Danceability
                        </Switch>
                        <Switch size="sm" id="energy" isChecked={activeSearchParams["energy"]}>
                            Energy
                        </Switch>
                        <Switch size="sm" id="valence" isChecked={activeSearchParams["valence"]}>
                            Valence
                        </Switch>
                        <Switch size="sm" id="acousticness" isChecked={activeSearchParams["acousticness"]}>
                            Acousticness
                        </Switch>
                        <Switch size="sm" id="instrumentalness" isChecked={activeSearchParams["instrumentalness"]}>
                            Instrumentalness
                        </Switch>
                    </Stack>
                    <Stack>
                        <HStack>
                            <Text as="b">
                                Audio analysis
                            </Text>
                            <IconButton icon={<FaQuestionCircle />} onClick={
                                () => {
                                    window.open("https://developer.spotify.com/documentation/web-api/reference/get-audio-analysis", "_blank")
                                }
                            }/>
                        </HStack>
                        <Switch size="sm" id="bars" isChecked={activeSearchParams["bars"]}>
                            Bars
                        </Switch>
                        <Switch size="sm" id="beats" isChecked={activeSearchParams["beats"]}>
                            Beats
                        </Switch>
                        <Switch size="sm" id="sections" isChecked={activeSearchParams["sections"]}>
                            Sections
                        </Switch>
                        <Switch size="sm" id="segments" isChecked={activeSearchParams["segments"]}>
                            Segments
                        </Switch>
                        <Switch size="sm" id="tatums" isChecked={activeSearchParams["tatums"]}>
                            Tatums
                        </Switch>
                    </Stack>
                    <Stack>
                    <HStack>
                            <Text as="b">
                                Algorithm/distance used
                            </Text>
                        </HStack>
                        <RadioGroup value={activeSearchParams["distance"]} onChange={handleDistanceChange}>
                            <Stack>
                                <Radio value='euclidian'>Euclidian</Radio>
                                <Radio value='cosine'>Cosine</Radio>
                                <Radio value='manhattan'>Manhattan</Radio>
                                <Radio value='minkowski'>Minkowski</Radio>
                                <Radio value='dtw'>Fast DTW</Radio>
                            </Stack>
                        </RadioGroup>

                    </Stack>
                    <Stack>
                        <Text as="b">
                            Other
                        </Text>
                        <Switch size="sm" id="use_genre" isChecked={activeSearchParams["use_genre"]}>
                            Use common genre as filter
                        </Switch>
                        <HStack>
                            <Text>
                                Number of tracks analyzed:
                            </Text>
                            <NumberInput size='sm' maxW={20} id="tracks"
                                value={activeSearchParams["tracks"]} min={1} onChange={handleNumberChange}>
                                <NumberInputField />
                                <NumberInputStepper>
                                    <NumberIncrementStepper />
                                    <NumberDecrementStepper />
                                </NumberInputStepper>
                            </NumberInput>
                        </HStack>
                    </Stack>
                    {/* <Stack>
                        <Text as="b">
                            The search will use:
                        </Text>
                        {
                            Object.entries(searchParams).map(([key, value]) => {
                                if (value === true) {
                                    return <Text key={key}>{key}</Text>;
                                }
                                return null;
                            })
                        }

                    </Stack> */}
                </Flex>
                <HStack spacing={3}>
                    <Button size={"md"} colorScheme='blue' onClick={() => {
                        setSearchParams(activeSearchParams)
                    }} rightIcon={settingsChanged() ? <FaCheck/> : null}>
                        Apply
                    </Button>
                    <Button size={"md"} onClick={() => {
                        setActiveSearchParams({
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
                        })
                    }}>
                        Use recommended settings
                    </Button>
                </HStack>
            </Stack>
        </Stack>)
}