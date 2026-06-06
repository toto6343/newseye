import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, Legend } from 'recharts';

const ThreatHeatmap = ({ news }) => {
    const [data, setData] = useState([]);

    useEffect(() => {
        if (!news || news.length === 0) return;

        const counts = {};
        news.forEach(item => {
            const type = item.crime_type || 'unknown';
            counts[type] = (counts[type] || 0) + 1;
        });

        const formattedData = Object.keys(counts).map(key => ({
            name: key.toUpperCase(),
            value: counts[key]
        }));

        setData(formattedData);
    }, [news]);

    const COLORS = ['#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#64748b'];

    return (
        <div className="threat-heatmap" style={{ backgroundColor: '#1e293b', padding: '20px', borderRadius: '12px', border: '1px solid #334155', minWidth: '0' }}>
            <h3 style={{ marginBottom: '15px', fontSize: '1.1rem' }}>Threat Distribution (Heatmap)</h3>
            <div style={{ width: '100%', height: '250px', position: 'relative' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={5}
                            dataKey="value"
                        >
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                        </Pie>
                        <RechartsTooltip 
                            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: '#f8fafc' }}
                        />
                        <Legend />
                    </PieChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default ThreatHeatmap;
