import React, { useState } from 'react';
import { Container, Typography } from '@mui/material';
import FileUpload from './components/FileUpload';
import Chat from './components/Chat';

function App() {
    const [isFileUploaded, setIsFileUploaded] = useState(false);

    return (
        <Container maxWidth="md">
            <Typography variant="h4" component="h1" gutterBottom>
                LLM Chat Application
            </Typography>
            <FileUpload setIsFileUploaded={setIsFileUploaded} />
            {isFileUploaded && <Chat />}
        </Container>
    );
}

export default App;