import React, { useState, useEffect } from 'react';
import { AlertTriangle, Car, Video, Clock, MapPin } from 'lucide-react';
import { format } from 'date-fns';

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
    const [violations, setViolations] = useState([]);
    const [stats, setStats] = useState({ total_violations: 0, cameras_active: 0 });

    useEffect(() => {
        const fetchData = async () => {
            try {
                const vRes = await fetch(`${API_URL}/violations`);
                const sRes = await fetch(`${API_URL}/stats`);
                const vData = await vRes.json();
                const sData = await sRes.json();
                setViolations(vData);
                setStats(sData);
            } catch (e) {
                console.error("Failed to fetch data", e);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 2000); // Poll every 2s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="min-h-screen bg-slate-900 text-white p-8 font-sans">
            <header className="mb-8 flex justify-between items-center border-b border-slate-700 pb-4">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3 text-red-500">
                        <AlertTriangle size={32} />
                        Wrong-Way Detection System
                    </h1>
                    <p className="text-slate-400 mt-1">Live Monitoring Dashboard</p>
                </div>
                <div className="flex gap-4">
                    <div className="bg-slate-800 p-4 rounded-lg flex items-center gap-3 border border-slate-700">
                        <div className="bg-red-500/20 p-2 rounded-full text-red-500">
                            <Car size={24} />
                        </div>
                        <div>
                            <div className="text-2xl font-bold">{stats.total_violations}</div>
                            <div className="text-xs text-slate-400 uppercase tracking-wider">Total Incidents</div>
                        </div>
                    </div>
                    <div className="bg-slate-800 p-4 rounded-lg flex items-center gap-3 border border-slate-700">
                        <div className="bg-green-500/20 p-2 rounded-full text-green-500">
                            <Video size={24} />
                        </div>
                        <div>
                            <div className="text-2xl font-bold">{stats.cameras_active}</div>
                            <div className="text-xs text-slate-400 uppercase tracking-wider">Active Cameras</div>
                        </div>
                    </div>
                </div>
            </header>

            <main>
                <h2 className="text-xl font-semibold mb-4 text-slate-200">Recent Violations</h2>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {violations.map((v) => (
                        <div key={v.event_id} className="bg-slate-800 rounded-xl overflow-hidden border border-slate-700 shadow-xl hover:border-red-500/50 transition-colors">
                            <div className="relative aspect-video bg-black group cursor-pointer">
                                {/* For MVP we serve file directly, or use a placeholder if path not accessible by browser */}
                                <img
                                    src={`http://localhost:8000/content/${v.evidence_path.replace(/\\/g, '/').split('/').pop().replace('.mp4', '.jpg')}`}
                                    className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
                                    onError={(e) => { e.target.src = 'https://placehold.co/600x400/1e293b/FFF?text=No+Image' }}
                                    alt="Violation"
                                />
                                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/40">
                                    <Video size={48} className="text-white drop-shadow-lg" />
                                </div>
                            </div>

                            <div className="p-4">
                                <div className="flex justify-between items-start mb-2">
                                    <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded">
                                        WRONG WAY
                                    </span>
                                    <span className="text-slate-400 text-sm flex items-center gap-1">
                                        <Clock size={14} />
                                        {format(new Date(v.timestamp * 1000), 'HH:mm:ss')}
                                    </span>
                                </div>

                                <div className="space-y-1 text-sm text-slate-300">
                                    <div className="flex justify-between">
                                        <span>Camera:</span>
                                        <span className="font-medium text-white">{v.camera_id}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Track ID:</span>
                                        <span className="font-mono text-white">#{v.track_id}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Date:</span>
                                        <span className="text-white">{format(new Date(v.timestamp * 1000), 'MMM dd, yyyy')}</span>
                                    </div>
                                </div>

                                <div className="mt-4 pt-3 border-t border-slate-700">
                                    <div className="text-xs text-slate-500 truncate" title={v.evidence_path}>
                                        ID: {v.event_id}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}

                    {violations.length === 0 && (
                        <div className="col-span-full py-20 text-center text-slate-500 bg-slate-800/50 rounded-xl border border-dashed border-slate-700">
                            <div className="flex justify-center mb-4">
                                <Car size={48} className="opacity-20" />
                            </div>
                            <p className="text-lg">No violations detected yet.</p>
                            <p className="text-sm mt-1">System is monitoring traffic...</p>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}

export default App;
