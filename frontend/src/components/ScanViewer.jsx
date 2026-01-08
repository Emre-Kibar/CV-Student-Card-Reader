import React, { useState } from 'react';
import { MagnifyingGlassPlusIcon } from '@heroicons/react/24/outline';

const ScanViewer = ({ scan }) => {
    const [zoomField, setZoomField] = useState(null);
    const [scale, setScale] = useState(1);
    const imageRef = React.useRef(null);
    const containerRef = React.useRef(null);

    React.useEffect(() => {
        const updateScale = () => {
            if (imageRef.current) {
                const { naturalWidth, width } = imageRef.current;
                if (naturalWidth > 0) {
                    setScale(width / naturalWidth);
                }
            }
        };

        window.addEventListener('resize', updateScale);
        updateScale(); // Initial calculation

        return () => window.removeEventListener('resize', updateScale);
    }, [scan]);

    const handleImageLoad = () => {
        if (imageRef.current) {
            const { naturalWidth, width } = imageRef.current;
            if (naturalWidth > 0) {
                setScale(width / naturalWidth);
            }
        }
    };

    if (!scan) return null;

    const cardImageUrl = `http://localhost:8000/${scan.card_image_path}`;

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Image Viewer */}
            <div className="relative group">
                <h3 className="text-lg font-semibold mb-4 text-slate-800">Detected Card</h3>
                <div ref={containerRef} className="relative rounded-xl overflow-hidden shadow-xl border border-slate-200 bg-slate-900">
                    <img
                        ref={imageRef}
                        src={cardImageUrl}
                        alt="Detected Card"
                        className="w-full h-auto object-contain"
                        onLoad={handleImageLoad}
                    />

                    {/* Bounding Boxes Overlay */}
                    {scan.fields && scan.fields.map((field) => (
                        field.width > 0 && (
                            <div
                                key={field.id}
                                className="absolute border-2 border-green-400 hover:bg-green-400/20 cursor-pointer transition-all"
                                style={{
                                    left: `${field.x * scale}px`,
                                    top: `${field.y * scale}px`,
                                    width: `${field.width * scale}px`,
                                    height: `${field.height * scale}px`
                                }}
                                onClick={() => setZoomField(field)}
                                title={field.text}
                            />
                        )
                    ))}
                </div>
                <p className="text-xs text-slate-400 mt-2 text-center">
                    Hover/Click on highlighted boxes to view details
                </p>
            </div>

            {/* Text Results */}
            <div>
                <h3 className="text-lg font-semibold mb-4 text-slate-800">Extracted Information</h3>
                <div className="space-y-3">
                    {scan.fields && scan.fields.length > 0 ? (
                        scan.fields.map((field, index) => (
                            <div
                                key={index}
                                className="p-4 bg-white border border-slate-200 rounded-lg shadow-sm hover:shadow-md transition-shadow flex items-start gap-3 group"
                                onMouseEnter={() => { /* Highlight logic could pass unique ID to state */ }}
                            >
                                <div className="mt-1 p-1 bg-indigo-50 rounded text-indigo-600">
                                    <MagnifyingGlassPlusIcon className="w-5 h-5" />
                                </div>
                                <div className="flex-1">
                                    <p className="text-sm font-medium text-slate-900">{field.text || "Empty Field"}</p>
                                    <p className="text-xs text-slate-400 mt-1">
                                        Confidence: {(field.confidence * 100).toFixed(1)}% •
                                        Pos: ({field.x}, {field.y})
                                    </p>
                                </div>
                                {field.image_path && (
                                    <img
                                        src={`http://localhost:8000/${field.image_path}`}
                                        alt="Field crop"
                                        className="h-10 w-auto rounded border border-slate-200 object-contain ml-auto"
                                    />
                                )}
                            </div>
                        ))
                    ) : (
                        <div className="text-center p-8 bg-slate-50 rounded-lg border border-slate-200 text-slate-500">
                            No text extracted yet. Image might be unclear or processing failed.
                        </div>
                    )}
                </div>
            </div>

            {/* Zoom Modal */}
            {zoomField && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4" onClick={() => setZoomField(null)}>
                    <div className="bg-white rounded-xl overflow-hidden max-w-lg w-full shadow-2xl animate-in zoom-in-95 duration-200">
                        <div className="p-4 border-b border-slate-100 flex justify-between items-center">
                            <h3 className="font-semibold text-slate-900">Field Detail</h3>
                            <button
                                onClick={() => setZoomField(null)}
                                className="text-slate-400 hover:text-slate-600"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="p-6 text-center">
                            {zoomField.image_path && (
                                <img
                                    src={`http://localhost:8000/${zoomField.image_path}`}
                                    alt="Field Zoom"
                                    className="mx-auto h-32 object-contain mb-4 rounded border"
                                />
                            )}
                            <h4 className="text-2xl font-bold text-slate-800 mb-2">
                                {zoomField.text}
                            </h4>
                            <div className="inline-flex gap-4 text-sm text-slate-500">
                                <span>Confidence: {(zoomField.confidence * 100).toFixed(1)}%</span>
                                <span>Coords: {zoomField.x}, {zoomField.y}</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ScanViewer;
