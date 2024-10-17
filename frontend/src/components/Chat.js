import React, { useState } from 'react';
import { TextField, Button, Typography, Paper } from '@mui/material';
import axios from 'axios';

const Chat = () => {
    const [message, setMessage] = useState('');
    const [response, setResponse] = useState('');

    const handleSendMessage = async () => {
        if (!message.trim()) return;

        try {
            const res = await axios.post('http://localhost:5000/chat', { message });
            setResponse(res.data.response);
        } catch (error) {
            setResponse(`Error: ${error.response ? error.response.data.error : error.message}`);
        }
        setMessage('');
    };

    return (
        <div>
            <Paper elevation={3} style={{ padding: '20px', marginTop: '20px' }}>
                <Typography variant="h6">Chat</Typography>
                <TextField
                    fullWidth
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your message here"
                    margin="normal"
                />
                <Button onClick={handleSendMessage} variant="contained" color="primary">
                    Send
                </Button>
                {response && (
                    <Typography style={{ marginTop: '20px' }}>
                        <strong>Response:</strong> {response}
                    </Typography>
                )}
            </Paper>
        </div>
    );
};

export default Chat;