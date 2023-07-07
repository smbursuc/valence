import React, { useEffect, useState } from 'react';
import { Text } from '@chakra-ui/react';

export function ArtistImage({ artist }) {
    const [image_url, setImageUrl] = useState('');
    useEffect(() => {
        try {
            fetch(`http://127.0.0.1:8000/valence/get_access_token`)
                .then(response => {
                    return response.json()
                })
                .then(
                    data => {
                        const token = data.access_token;
                        return token
                    }
                )
                .then(token => {
                    fetch(`https://api.spotify.com/v1/artists/${artist.id}`,
                        {
                            headers: {
                                'Authorization': 'Bearer ' + token
                            }
                        })
                        .then(response => response.json())
                        .then(data => {
                            console.log(artist.id)
                            let image_url = data.images[0].url;
                            setImageUrl(image_url);
                        }
                        );
                })
        }
        catch (error) {
            console.log(error);
        }

        
    })

    return (
        <Text>
            <img src={image_url} alt={artist.name}/>
        </Text>
    )
}