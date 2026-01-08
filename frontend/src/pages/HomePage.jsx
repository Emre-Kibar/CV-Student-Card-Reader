import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUploader from '../components/FileUploader';
import axios from 'axios';
import { ClockIcon } from '@heroicons/react/24/outline';

const HomePage = () => {
    const navigate = useNavigate();
    const [isUploading, setIsUploading] = useState(false);

    const handleFileSelect = async (file) => {
        setIsUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://localhost:8000/api/scan', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            // Navigate to scan details to show progress/result
            navigate(`/scan/${response.data.id}`);
        } catch (error) {
            console.error("Upload failed", error);
            alert("Upload failed. Please try again.");
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
                <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight sm:text-5xl mb-4">
                    Student Card Reader
                </h1>
                <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                    Upload a student ID card to automatically extract information using our advanced OCR technology.
                </p>
            </div>

            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
                <FileUploader onFileSelect={handleFileSelect} isProcessing={isUploading} />

                {isUploading && (
                    <div className="mt-8 text-center text-slate-500 animate-pulse">
                        Uploading and starting analysis...
                    </div>
                )}
            </div>

            <div className="mt-12 text-center">
                <button
                    onClick={() => navigate('/history')}
                    className="inline-flex items-center gap-2 px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-lg transition-colors"
                >
                    <ClockIcon className="w-5 h-5" />
                    View Scan History
                </button>
            </div>
        </div>
    );
};

export default HomePage;
