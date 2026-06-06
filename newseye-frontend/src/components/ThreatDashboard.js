import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ThreatDashboard = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch from the new analytics endpoint
        fetch('http://127.0.0.1:8000/api/v1/analytics/forecast')
            .then(res => res.json())
            .then(json => {
                if (!json.error) {
                    setData(json);
                }
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch forecast:", err);
                setLoading(false);
            });
    }, []);

    if (loading) return <div>Loading Forecast Data...</div>;
    if (data.length === 0) return <div>No forecast data available.</div>;

    return (
        <div className="threat-dashboard" style={{ padding: '20px', backgroundColor: '#fff', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', margin: '20px 0', minWidth: '0' }}>
            <h3 style={{ marginBottom: '20px', color: '#333' }}>Cybersecurity Threat Forecast (Prophet ML)</h3>
            <div style={{ width: '100%', height: '350px', position: 'relative' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                        <XAxis 
                            dataKey="year" 
                            stroke="#888" 
                            interval={0}
                            tick={{ fontSize: 11 }}
                            padding={{ left: 10, right: 10 }}
                        />
                        <YAxis stroke="#888" />
                        <Tooltip 
                            contentStyle={{ backgroundColor: '#fff', border: '1px solid #ddd' }}
                            itemStyle={{ color: '#8884d8' }}
                        />
                        <Legend />
                        <Line 
                            name="Predicted Threat Count"
                            type="monotone" 
                            dataKey="threats" 
                            stroke="#8884d8" 
                            strokeWidth={3}
                            dot={{ r: 6 }}
                            activeDot={{ r: 8 }} 
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
            <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#eef2ff', borderRadius: '6px' }}>
                <p style={{ fontSize: '0.9em', color: '#4f46e5', margin: 0 }}>
                    <strong>Insight:</strong> The model predicts a continued {data[data.length-1].threats > data[0].threats ? 'upward' : 'downward'} trend in global cybersecurity threats over the next 5 years.
                </p>
            </div>
            <p style={{ marginTop: '10px', fontSize: '0.8em', color: '#999', textAlign: 'right' }}>
                Data source: Global Cybersecurity Threats Dataset (2015-2024)
            </p>
        </div>
    );
};

export default ThreatDashboard;
