import React, { useState } from 'react';
import { Button, Typography, LinearProgress } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';

const FileUpload = () => {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState('');

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleUpload = async () =>{
        if (!file) {
            setUploadStatus('Please select a file first.');
            return;
        }
        const formData = new FormData();
        formData.append('file', file);
        setUploading(true);
        try {
            const response = await axios.post('http://localhost:5000/upload', formData);
            setUploadStatus(response.data.response);
            setIsFileUploader(true);
        } catch (error) {
            setUploadStatus('Upload failed: ${error.response?.data?.error || error.message}');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div>
            <input 
                accept=".pdf, .csv, .xlsx, .docx"
                style = {{display: 'none'}}
                id="raised-button-file"
                type='file'
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
            {uploading && <LinearProgress/>}
            <Typography>{uploadStatus}</Typography>
        </div>
    );
};

export default FileUpload;