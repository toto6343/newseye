import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User as UserIcon, Loader2 } from 'lucide-react';

const ThreatChat = () => {
    const [messages, setMessages] = useState([
        { role: 'bot', text: 'Hello! I am your AI Security Assistant. Ask me anything about the latest threats.' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMsg = input;
        setInput('');
        setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
        setLoading(true);

        try {
            const response = await fetch('http://localhost:8000/api/v1/analytics/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: userMsg })
            });
            const data = await response.json();
            
            setMessages(prev => [...prev, { 
                role: 'bot', 
                text: data.answer,
                sources: data.sources 
            }]);
        } catch (error) {
            console.error("Chat error:", error);
            setMessages(prev => [...prev, { role: 'bot', text: "Sorry, I'm having trouble connecting to the analysis server." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="threat-chat" style={{ display: 'flex', flexDirection: 'column', height: '600px', backgroundColor: '#1e293b', borderRadius: '12px', border: '1px solid #334155', overflow: 'hidden' }}>
            <div className="chat-header" style={{ padding: '15px 20px', backgroundColor: '#334155', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Bot className="icon-blue" />
                <h3 style={{ margin: 0, fontSize: '1rem' }}>AI Threat Intelligence Chat</h3>
            </div>
            
            <div className="chat-messages" style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
                {messages.map((msg, idx) => (
                    <div key={idx} style={{ 
                        alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                        maxWidth: '80%',
                        backgroundColor: msg.role === 'user' ? '#3b82f6' : '#334155',
                        padding: '12px 16px',
                        borderRadius: msg.role === 'user' ? '18px 18px 0 18px' : '18px 18px 18px 0',
                        color: '#f8fafc',
                        fontSize: '0.95rem',
                        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                    }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '5px', opacity: 0.8, fontSize: '0.75rem' }}>
                            {msg.role === 'user' ? <UserIcon size={12} /> : <Bot size={12} />}
                            {msg.role === 'user' ? 'You' : 'AI Assistant'}
                        </div>
                        <div style={{ whiteSpace: 'pre-line' }}>{msg.text}</div>
                        
                        {msg.sources && msg.sources.length > 0 && (
                            <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid rgba(255,255,255,0.1)', fontSize: '0.8rem' }}>
                                <strong>Sources:</strong>
                                <ul style={{ margin: '5px 0 0 0', paddingLeft: '15px', color: '#94a3b8' }}>
                                    {msg.sources.map((s, i) => (
                                        <li key={i}><a href={s.url} target="_blank" rel="noreferrer" style={{ color: '#60a5fa', textDecoration: 'none' }}>{s.title}</a> ({s.source})</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                ))}
                {loading && (
                    <div style={{ alignSelf: 'flex-start', backgroundColor: '#334155', padding: '12px 16px', borderRadius: '0 18px 18px 18px', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Loader2 className="animate-spin" size={16} /> Analyzing latest news...
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSend} style={{ padding: '20px', borderTop: '1px solid #334155', display: 'flex', gap: '10px' }}>
                <input 
                    type="text" 
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask about a specific threat or asset..."
                    style={{ flex: 1, backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '10px 15px', color: '#f8fafc', outline: 'none' }}
                />
                <button type="submit" disabled={loading} style={{ backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', padding: '0 15px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Send size={18} />
                </button>
            </form>
        </div>
    );
};

export default ThreatChat;
