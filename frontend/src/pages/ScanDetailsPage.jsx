import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import ScanViewer from '../components/ScanViewer';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';

const ScanDetailsPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [scan, setScan] = useState(null);
    const [progress, setProgress] = useState({ status: 'loading', percent: 0 });
    const pollInterval = useRef(null);

    const fetchScan = async () => {
        try {
            const response = await axios.get(`http://localhost:8000/api/scans/${id}`);
            setScan(response.data);

            if (response.data.status === 'completed' || response.data.status === 'failed') {
                clearInterval(pollInterval.current);
                setProgress({ status: response.data.status, percent: 100 });
            }
        } catch (error) {
            console.error("Failed to fetch scan", error);
        }
    };

    const fetchProgress = async () => {
        try {
            const response = await axios.get(`http://localhost:8000/api/scan/${id}/progress`);
            setProgress(response.data);
            if (response.data.status === 'completed' || response.data.status === 'failed') {
                fetchScan(); // Get final data
            }
        } catch (error) {
            console.error("Failed to fetch progress", error);
        }
    };

    useEffect(() => {
        fetchScan();
        // Start polling
        pollInterval.current = setInterval(() => {
            fetchScan(); // Check DB status
            // Also check progress memory ?? 
            // Our backend updates DB status at the end. 
            // But progress endpoint reads from memory tracker.
            fetchProgress();
        }, 1000);

        return () => clearInterval(pollInterval.current);
    }, [id]);

    if (!scan) return <div className="p-10 text-center text-slate-500">Loading scan details...</div>;

    const isProcessing = scan.status === 'pending' || scan.status === 'processing';

    return (
        <div className="max-w-6xl mx-auto py-8 px-4">
            <div className="mb-6 flex items-center justify-between">
                <button
                    onClick={() => navigate('/')}
                    className="flex items-center gap-2 text-slate-500 hover:text-slate-800 transition-colors"
                >
                    <ArrowLeftIcon className="w-4 h-4" /> Back to Upload
                </button>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide 
          ${scan.status === 'completed' ? 'bg-green-100 text-green-700' :
                        scan.status === 'failed' ? 'bg-red-100 text-red-700' :
                            'bg-blue-100 text-blue-700 animate-pulse'}`}>
                    {scan.status}
                </span>
            </div>

            {isProcessing ? (
                <div className="max-w-xl mx-auto text-center mt-20">
                    <div className="mb-8 relative pt-1">
                        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-indigo-100">
                            <div
                                style={{ width: `${progress.percent}%` }}
                                className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-500 transition-all duration-500"
                            ></div>
                        </div>
                        <p className="text-xl font-medium text-slate-700 text-center animate-pulse capitalize">
                            {progress.status.replace(/_/g, ' ')}...
                        </p>
                    </div>
                    <p className="text-slate-400 text-sm">Please wait while we analyze the card</p>
                </div>
            ) : (
                <ScanViewer scan={scan} />
            )}
        </div>
    );
};

export default ScanDetailsPage;
