import React, { useState } from 'react';
import { Button, Typography, LinearProgress } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';

const FileUpload = ({ setIsFileUploaded }) => {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState('');

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) {
            setUploadStatus('Please select a file first.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        setUploading(true);
        try {
            const response = await axios.post('http://localhost:5000/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                timeout: 30000, // 30 seconds timeout
            });
            console.log('Upload response:', response);
            setUploadStatus(response.data.response);
            setIsFileUploaded(true);
        } catch (error) {
            console.error('Upload error:', error);
            if (error.response) {
                // The request was made and the server responded with a status code
                // that falls out of the range of 2xx
                console.error('Error data:', error.response.data);
                console.error('Error status:', error.response.status);
                console.error('Error headers:', error.response.headers);
                setUploadStatus(`Upload failed: ${error.response.data.error || error.response.statusText}`);
            } else if (error.request) {
                // The request was made but no response was received
                console.error('Error request:', error.request);
                setUploadStatus('Upload failed: No response received from server');
            } else {
                // Something happened in setting up the request that triggered an Error
                console.error('Error message:', error.message);
                setUploadStatus(`Upload failed: ${error.message}`);
            }
        } finally {
            setUploading(false);
        }
    };

    return (
        <div>
            <input
                accept=".pdf,.csv,.xlsx,.docx"
                style={{ display: 'none' }}
                id="raised-button-file"
                type="file"
                onChange={handleFileChange}
            />
            <label htmlFor="raised-button-file">
                <Button variant="contained" component="span" startIcon={<CloudUploadIcon />}>
                    Select File
                </Button>
            </label>
            {file && <Typography>{file.name}</Typography>}
            <Button onClick={handleUpload} disabled={!file || uploading} variant="contained" color="primary">
                Upload
            </Button>
            {uploading && <LinearProgress />}
            <Typography>{uploadStatus}</Typography>
        </div>
    );
};

export default FileUpload;