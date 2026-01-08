import React, { useState, useRef } from 'react';
import { ArrowUpTrayIcon, DocumentTextIcon } from '@heroicons/react/24/outline'; // Need to install heroicons

const FileUploader = ({ onFileSelect, isProcessing }) => {
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef(null);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            validateAndPass(files[0]);
        }
    };

    const handleFileInput = (e) => {
        const files = e.target.files;
        if (files.length > 0) {
            validateAndPass(files[0]);
        }
    };

    const validateAndPass = (file) => {
        // Validate type
        const validTypes = ['image/jpeg', 'image/png', 'image/bmp'];
        if (!validTypes.includes(file.type)) {
            alert("Invalid file type. Please upload JPG, PNG, or BMP.");
            return;
        }
        onFileSelect(file);
    };

    return (
        <div
            className={`w-full max-w-xl mx-auto p-8 border-2 border-dashed rounded-xl transition-all duration-300 ${isDragging
                    ? 'border-indigo-500 bg-indigo-50 scale-105 shadow-lg'
                    : 'border-slate-300 hover:border-indigo-400 bg-slate-50'
                } ${isProcessing ? 'opacity-50 pointer-events-none' : 'cursor-pointer'}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
        >
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileInput}
                className="hidden"
                accept=".jpg,.jpeg,.png,.bmp"
            />

            <div className="flex flex-col items-center justify-center text-center space-y-4">
                <div className={`p-4 rounded-full ${isDragging ? 'bg-indigo-100' : 'bg-slate-100'}`}>
                    <ArrowUpTrayIcon className={`w-10 h-10 ${isDragging ? 'text-indigo-600' : 'text-slate-400'}`} />
                </div>

                <div className="space-y-1">
                    <p className="text-lg font-semibold text-slate-700">
                        {isDragging ? 'Drop scanning file here' : 'Upload Student Card'}
                    </p>
                    <p className="text-sm text-slate-500">
                        Drag & drop or click to select
                    </p>
                </div>

                <div className="flex gap-2 justify-center text-xs text-slate-400 uppercase font-medium tracking-wide">
                    <span className="bg-white px-2 py-1 rounded border border-slate-200">JPG</span>
                    <span className="bg-white px-2 py-1 rounded border border-slate-200">PNG</span>
                    <span className="bg-white px-2 py-1 rounded border border-slate-200">BMP</span>
                </div>
            </div>
        </div>
    );
};

export default FileUploader;
