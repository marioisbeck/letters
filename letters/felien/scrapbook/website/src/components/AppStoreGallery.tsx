import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';

interface MediaItem {
    id: string;
    url: string;
    type: 'image' | 'video';
    rotation: string;
}

type MediaStatus = 'keep' | 'fix' | 'delete';

interface AppStoreGalleryProps {
    items: MediaItem[];
}

export default function AppStoreGallery({ items }: AppStoreGalleryProps) {
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [viewRotation, setViewRotation] = useState<number>(0);
    const [mediaStatuses, setMediaStatuses] = useState<Record<string, MediaStatus>>({});
    const scrollRef = React.useRef<HTMLDivElement>(null);

    // Load statuses from localStorage on mount
    useEffect(() => {
        try {
            const stored = localStorage.getItem('mediaStatuses');
            if (stored) {
                setMediaStatuses(JSON.parse(stored));
            }
        } catch (e) {
            console.error('Failed to load media statuses', e);
        }
    }, []);

    const handleStatusClick = (e: React.MouseEvent, url: string) => {
        e.stopPropagation();
        setMediaStatuses(prev => {
            const currentStatus = prev[url] || 'keep';
            let nextStatus: MediaStatus = 'keep';
            
            if (currentStatus === 'keep') nextStatus = 'fix';
            else if (currentStatus === 'fix') nextStatus = 'delete';
            else if (currentStatus === 'delete') nextStatus = 'keep';
            
            const newStatuses = { ...prev };
            if (nextStatus === 'keep') {
                delete newStatuses[url];
            } else {
                newStatuses[url] = nextStatus;
            }
            
            try {
                localStorage.setItem('mediaStatuses', JSON.stringify(newStatuses));
            } catch (e) {
                console.error('Failed to save media statuses', e);
            }
            
            return newStatuses;
        });
    };

    const getStatusIcon = (status: MediaStatus) => {
        if (status === 'fix') {
            return (
                <div className="bg-yellow-500 text-white rounded-full p-1.5 shadow-md border-2 border-white" title="Not displayed properly">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                </div>
            );
        }
        if (status === 'delete') {
            return (
                <div className="bg-red-500 text-white rounded-full p-1.5 shadow-md border-2 border-white" title="Delete">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                </div>
            );
        }
        return (
            <div className="bg-black/30 text-white rounded-full p-1.5 shadow-sm border-2 border-white/50 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-black/50" title="Keep">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" strokeWidth="2"></circle></svg>
            </div>
        );
    };

    const selectedItem = items.find(item => item.id === selectedId);

    // Reset rotation when a new item is selected
    useEffect(() => {
        if (selectedId) {
            setViewRotation(0);
        }
    }, [selectedId]);

    // Handle escape key
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') setSelectedId(null);
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    // Prevent scrolling when modal is open
    useEffect(() => {
        if (selectedId) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
        return () => {
            document.body.style.overflow = '';
        };
    }, [selectedId]);

    return (
        <div className="relative w-full group/carousel">
            {items.length > 1 && (
                <button 
                    onClick={() => {
                        if (scrollRef.current) scrollRef.current.scrollBy({ left: -600, behavior: 'smooth' });
                    }}
                    className="absolute left-0 top-1/2 -translate-y-1/2 z-20 bg-white/90 backdrop-blur-sm p-3 rounded-full shadow-lg text-[#a89f91] hover:text-[#4a4238] transition-all transform hover:scale-110 opacity-0 group-hover/carousel:opacity-100 md:-ml-4 focus:opacity-100" 
                    aria-label="Previous image"
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7"></path></svg>
                </button>
            )}

            <div ref={scrollRef} className="flex overflow-x-auto snap-x snap-mandatory gap-6 pb-8 pt-4 px-4 no-scrollbar pointer-events-auto carousel-scroll-area" style={{ overscrollBehaviorX: 'contain' }}>
                {/* Group items into chunks of 4 for the collage layout */}
                {Array.from({ length: Math.ceil(items.length / 4) }).map((_, chunkIndex) => {
                    const chunk = items.slice(chunkIndex * 4, (chunkIndex + 1) * 4);
                    
                    return (
                        <div key={`chunk-${chunkIndex}`} className="snap-center shrink-0 w-[85vw] h-[85vw] max-w-[550px] max-h-[550px] md:w-[550px] md:h-[550px] grid grid-cols-5 grid-rows-5 gap-3 md:gap-4">
                            {chunk.map((item, index) => {
                                // Only use variations of the horizontal split (Layout C)
                                // Top row (2 rows high): 3 cols left, 2 cols right
                                // Bottom row (3 rows high): 2 cols left, 3 cols right
                                
                                let gridClass = "col-span-2 row-span-5"; // default
                                
                                // Alternate layouts based on chunk index to make it look organic
                                if (chunkIndex % 2 === 0) {
                                    // Layout C1: 
                                    // Top: Wide Left (3x2), Narrow Right (2x2)
                                    // Bottom: Narrow Left (2x3), Wide Right (3x3)
                                    if (index === 0) gridClass = "col-span-3 row-span-2 col-start-1 row-start-1"; // Wide top left
                                    else if (index === 1) gridClass = "col-span-2 row-span-2 col-start-4 row-start-1"; // Narrow top right
                                    else if (index === 2) gridClass = "col-span-2 row-span-3 col-start-1 row-start-3"; // Narrow bottom left
                                    else if (index === 3) gridClass = "col-span-3 row-span-3 col-start-3 row-start-3"; // Wide bottom right
                                } else {
                                    // Layout C2: Mirrored version
                                    // Top: Narrow Left (2x2), Wide Right (3x2)
                                    // Bottom: Wide Left (3x3), Narrow Right (2x3)
                                    if (index === 0) gridClass = "col-span-2 row-span-2 col-start-1 row-start-1"; // Narrow top left
                                    else if (index === 1) gridClass = "col-span-3 row-span-2 col-start-3 row-start-1"; // Wide top right
                                    else if (index === 2) gridClass = "col-span-3 row-span-3 col-start-1 row-start-3"; // Wide bottom left
                                    else if (index === 3) gridClass = "col-span-2 row-span-3 col-start-4 row-start-3"; // Narrow bottom right
                                }
                                
                                return (
                                    <motion.div
                                        key={item.id}
                                        layoutId={`card-container-${item.id}`}
                                        onClick={() => setSelectedId(item.id)}
                                        className={`relative w-full h-full rounded-[24px] overflow-hidden shadow-md cursor-pointer bg-gray-100 group ${gridClass}`}
                                        whileHover={{ scale: 0.98 }}
                                        whileTap={{ scale: 0.95 }}
                                        transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                    >
                                        {/* Status Toggle Button */}
                                        <div 
                                            className="absolute top-3 right-3 z-30"
                                            onClick={(e) => handleStatusClick(e, item.url)}
                                        >
                                            {getStatusIcon(mediaStatuses[item.url] || 'keep')}
                                        </div>

                                        {item.type === 'video' ? (
                                            <div className="relative w-full h-full pointer-events-none">
                                                <motion.video 
                                                    layoutId={`media-${item.id}`}
                                                    className="absolute inset-0 w-full h-full object-cover pointer-events-none" 
                                                    autoPlay 
                                                    loop 
                                                    muted 
                                                    playsInline
                                                    style={{ margin: 0 }}
                                                >
                                                    <source src={item.url} type={`video/${item.url.split('.').pop()}`} />
                                                </motion.video>
                                                <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />
                                                <div className="absolute inset-0 flex items-center justify-center bg-black/10 group-hover:bg-black/20 transition-colors pointer-events-none">
                                                    <svg className="w-10 h-10 text-white opacity-80" fill="currentColor" viewBox="0 0 20 20"><path d="M4 4l12 6-12 6z"></path></svg>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="relative w-full h-full pointer-events-none">
                                                <motion.img 
                                                    layoutId={`media-${item.id}`}
                                                    src={item.url} 
                                                    alt="Memory" 
                                                    className="absolute inset-0 w-full h-full object-cover pointer-events-none" 
                                                    loading="lazy" 
                                                    style={{ margin: 0 }}
                                                />
                                                <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />
                                            </div>
                                        )}
                                    </motion.div>
                                );
                            })}
                        </div>
                    );
                })}
            </div>

            {items.length > 1 && (
                <button 
                    onClick={() => {
                        if (scrollRef.current) scrollRef.current.scrollBy({ left: 600, behavior: 'smooth' });
                    }}
                    className="absolute right-0 top-1/2 -translate-y-1/2 z-20 bg-white/90 backdrop-blur-sm p-3 rounded-full shadow-lg text-[#a89f91] hover:text-[#4a4238] transition-all transform hover:scale-110 opacity-0 group-hover/carousel:opacity-100 md:-mr-4 focus:opacity-100" 
                    aria-label="Next image"
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"></path></svg>
                </button>
            )}

            <AnimatePresence>
                {selectedId && selectedItem && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setSelectedId(null)}
                        className="fixed inset-0 bg-black/90 backdrop-blur-sm z-[100] flex items-center justify-center p-4 md:p-12"
                    >
                        {/* Controls Container */}
                        <div className="absolute top-6 right-6 flex items-center gap-4 z-[110]">
                            {/* Rotate Button */}
                            <button 
                                onClick={(e) => { 
                                    e.stopPropagation(); 
                                    setViewRotation(prev => (prev + 90) % 360); 
                                }}
                                className="text-white hover:text-gray-300 transition-colors bg-black/50 p-2 rounded-full backdrop-blur-md" 
                                title="Rotate 90°"
                            >
                                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                                </svg>
                            </button>
                            
                            {/* Close Button */}
                            <button 
                                onClick={(e) => { e.stopPropagation(); setSelectedId(null); }}
                                className="text-white hover:text-gray-300 transition-colors bg-black/50 p-2 rounded-full backdrop-blur-md" 
                                title="Close (Esc)"
                            >
                                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                            </button>
                        </div>

                        <motion.div
                            layoutId={`card-container-${selectedItem.id}`}
                            className="relative w-full max-w-md h-[85vh] bg-black rounded-[32px] flex items-center justify-center overflow-hidden shadow-2xl"
                            onClick={(e) => e.stopPropagation()}
                            style={{ margin: 'auto' }}
                        >
                            {selectedItem.type === 'video' ? (
                                <motion.video 
                                    layoutId={`media-${selectedItem.id}`}
                                    controls 
                                    autoPlay
                                    animate={{ rotate: viewRotation }}
                                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                    className="w-full h-full object-contain"
                                    style={{
                                        maxWidth: viewRotation % 180 !== 0 ? '85vh' : '100%',
                                        maxHeight: viewRotation % 180 !== 0 ? '100vw' : '100%',
                                        margin: 'auto'
                                    }}
                                >
                                    <source src={selectedItem.url} type={`video/${selectedItem.url.split('.').pop()}`} />
                                </motion.video>
                            ) : (
                                <motion.img 
                                    layoutId={`media-${selectedItem.id}`}
                                    src={selectedItem.url} 
                                    animate={{ rotate: viewRotation }}
                                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                    className="w-full h-full object-contain" 
                                    style={{
                                        maxWidth: viewRotation % 180 !== 0 ? '85vh' : '100%',
                                        maxHeight: viewRotation % 180 !== 0 ? '100vw' : '100%',
                                        margin: 'auto'
                                    }}
                                />
                            )}
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
