import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeftIcon, TrashIcon } from '@heroicons/react/24/outline';
import ConfirmationModal from '../components/ConfirmationModal';

const HistoryPage = () => {
    const navigate = useNavigate();
    const [scans, setScans] = useState([]);
    const [loading, setLoading] = useState(true);
    const [deleteModal, setDeleteModal] = useState({ isOpen: false, scanId: null });

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/scans');
            setScans(response.data);
        } catch (error) {
            console.error("Failed to fetch history", error);
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteClick = (e, id) => {
        e.stopPropagation();
        setDeleteModal({ isOpen: true, scanId: id });
    };

    const handleConfirmDelete = async () => {
        if (!deleteModal.scanId) return;
        try {
            await axios.delete(`http://localhost:8000/api/scans/${deleteModal.scanId}`);
            setScans(scans.filter(s => s.id !== deleteModal.scanId));
        } catch (error) {
            console.error("Failed to delete", error);
            alert("Failed to delete scan");
        }
    };

    return (
        <div className="max-w-6xl mx-auto py-8 px-4">
            <ConfirmationModal
                isOpen={deleteModal.isOpen}
                onClose={() => setDeleteModal({ ...deleteModal, isOpen: false })}
                onConfirm={handleConfirmDelete}
                title="Delete Scan"
                message="Are you sure you want to delete this scan? This action cannot be undone."
            />

            <div className="mb-8 flex items-center gap-4">
                <button
                    onClick={() => navigate('/')}
                    className="p-2 -ml-2 text-slate-400 hover:text-slate-800 rounded-full hover:bg-slate-100"
                >
                    <ArrowLeftIcon className="w-6 h-6" />
                </button>
                <h1 className="text-2xl font-bold text-slate-800">Scan History</h1>
            </div>

            {loading ? (
                <div className="text-center py-20 text-slate-400">Loading history...</div>
            ) : scans.length === 0 ? (
                <div className="text-center py-20 bg-slate-50 rounded-2xl border border-dotted border-slate-300">
                    <p className="text-slate-500 mb-4">No scans found</p>
                    <button onClick={() => navigate('/')} className="text-indigo-600 font-medium hover:underline">
                        Create your first scan
                    </button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {scans.map((scan) => (
                        <div
                            key={scan.id}
                            onClick={() => navigate(`/scan/${scan.id}`)}
                            className="bg-white rounded-xl border border-slate-200 overflow-hidden hover:shadow-lg transition-all cursor-pointer group relative"
                        >
                            <div className="aspect-video bg-slate-100 relative">
                                {scan.card_image_path ? (
                                    <img
                                        src={`http://localhost:8000/${scan.card_image_path}`}
                                        className="w-full h-full object-cover"
                                        alt="Scan thumbnail"
                                    />
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center text-slate-300">
                                        No Image
                                    </div>
                                )}
                                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors" />

                                <span className={`absolute top-2 right-2 px-2 py-0.5 rounded text-xs font-bold uppercase shadow-sm ${scan.status === 'completed' ? 'bg-green-500 text-white' : 'bg-yellow-500 text-white'
                                    }`}>
                                    {scan.status}
                                </span>
                            </div>

                            <div className="p-4">
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="font-medium text-slate-900 truncate pr-2">{scan.filename}</h3>
                                    <button
                                        onClick={(e) => handleDeleteClick(e, scan.id)}
                                        className="text-slate-400 hover:text-red-500 p-1 rounded hover:bg-red-50 transition-colors"
                                    >
                                        <TrashIcon className="w-4 h-4" />
                                    </button>
                                </div>
                                <p className="text-xs text-slate-500">
                                    {new Date(scan.created_at).toLocaleString()}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default HistoryPage;
