import React, { useState, useEffect } from 'react';
import './App.css';
import { Shield, AlertTriangle, Newspaper, Activity, Lock, User, ExternalLink, MessageSquare, Layout, Settings as SettingsIcon, Bell, List, Maximize2, X } from 'lucide-react';
import ThreatDashboard from './components/ThreatDashboard';
import ThreatKnowledgeGraph from './components/ThreatKnowledgeGraph';
import ThreatHeatmap from './components/ThreatHeatmap';
import ThreatChat from './components/ThreatChat';
import NewsEyeLogo from './components/NewsEyeLogo';

const API_BASE = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api/v1';
const WS_BASE = API_BASE.replace('http', 'ws');

function App() {
  const [activeView, setActiveView] = useState('overview'); // overview, analysis, settings
  const [news, setNews] = useState([]);
  const [trend, setTrend] = useState({ labels: [], values: [] });
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState([]);
  const [viewMode, setViewMode] = useState('full'); // full, compact
  const [selectedEntity, setSelectedEntity] = useState(null); // For drill-down
  
  // Mock Personal Risk Profile State
  const [assets, setAssets] = useState(['Windows', 'Crypto']);
  const [newAsset, setNewAsset] = useState('');
  const [personalRiskScore, setPersonalRiskScore] = useState(5.0);

  useEffect(() => {
    // Fetch news
    fetch(`${API_BASE}/news/latest?count=15`)
      .then(res => res.json())
      .then(data => setNews(data.data || []))
      .catch(console.error);

    // Fetch trend forecast
    fetch(`${API_BASE}/analytics/yearly-trend`)
      .then(res => res.json())
      .then(data => {
        setTrend(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });

    // WebSocket for real-time alerts
    const socket = new WebSocket(`${WS_BASE}/ws`);
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setAlerts(prev => [data, ...prev].slice(0, 5));
    };

    return () => socket.close();
  }, []);

  useEffect(() => {
    if (news.length === 0) return;
    let baseScore = 5.0;
    const lowerAssets = assets.map(a => a.toLowerCase());
    
    let matchedAssets = 0;
    news.forEach(item => {
      const content = (item.title + " " + (item.summary || "")).toLowerCase();
      lowerAssets.forEach(a => {
        if (content.includes(a)) matchedAssets++;
      });
    });
    
    const newScore = Math.min(10.0, baseScore + (matchedAssets * 0.3));
    setPersonalRiskScore(newScore.toFixed(1));
  }, [news, assets]);

  const addAsset = (e) => {
    e.preventDefault();
    if (newAsset && !assets.includes(newAsset)) {
      setAssets([...assets, newAsset]);
      setNewAsset('');
    }
  };

  const removeAsset = (assetToRemove) => {
    setAssets(assets.filter(a => a !== assetToRemove));
  };

  const handleGraphNodeClick = (node) => {
    setSelectedEntity(node);
  };

  const getFilteredNews = () => {
    if (!selectedEntity) return [];
    const term = selectedEntity.name.toLowerCase();
    return news.filter(item => 
      item.title.toLowerCase().includes(term) || 
      (item.content && item.content.toLowerCase().includes(term)) ||
      (item.crime_type && item.crime_type.toLowerCase() === term)
    );
  };

  return (
    <div className="dashboard">
      <header className="header">
        <div className="logo">
          <NewsEyeLogo size={42} />
          <h1 style={{ marginLeft: '10px' }}>NewsEye Dashboard</h1>
        </div>
        <nav className="nav-tabs">
          <button 
            onClick={() => setActiveView('overview')} 
            className={`nav-btn ${activeView === 'overview' ? 'active' : ''}`}
            style={{ background: 'none', border: 'none', color: activeView === 'overview' ? '#3b82f6' : '#94a3b8', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 'bold' }}
          >
            <Layout size={18} /> Overview
          </button>
          <button 
            onClick={() => setActiveView('analysis')} 
            className={`nav-btn ${activeView === 'analysis' ? 'active' : ''}`}
            style={{ background: 'none', border: 'none', color: activeView === 'analysis' ? '#3b82f6' : '#94a3b8', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 'bold' }}
          >
            <Activity size={18} /> Deep Analysis
          </button>
          <button 
            onClick={() => setActiveView('settings')} 
            className={`nav-btn ${activeView === 'settings' ? 'active' : ''}`}
            style={{ background: 'none', border: 'none', color: activeView === 'settings' ? '#3b82f6' : '#94a3b8', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 'bold' }}
          >
            <SettingsIcon size={18} /> Settings
          </button>
        </nav>
        <div className="status">
          <span className="online-indicator"></span>
          System Online
        </div>
      </header>

      {alerts.length > 0 && (
        <div 
          className="real-time-alerts" 
          style={{ 
            backgroundColor: alerts[0].targeted_assets_found?.length > 0 ? '#7f1d1d' : '#fee2e2', 
            padding: '12px 20px', 
            borderBottom: '2px solid #ef4444',
            animation: 'fadeIn 0.5s ease'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <AlertTriangle color={alerts[0].targeted_assets_found?.length > 0 ? '#fca5a5' : '#ef4444'} size={24} className={alerts[0].targeted_assets_found?.length > 0 ? 'animate-pulse' : ''} />
              <div>
                <strong style={{ color: alerts[0].targeted_assets_found?.length > 0 ? '#fecaca' : '#b91c1c', fontSize: '1.1rem' }}>
                  {alerts[0].targeted_assets_found?.length > 0 ? '🚨 TARGETED ASSET THREAT:' : 'Real-time Threat Alert:'}
                </strong>
                <span style={{ color: alerts[0].targeted_assets_found?.length > 0 ? '#f8fafc' : '#7f1d1d', marginLeft: '10px' }}>
                  {alerts[0].message || alerts[0].title}
                  {alerts[0].targeted_assets_found?.length > 0 && (
                    <span style={{ marginLeft: '10px', padding: '2px 8px', backgroundColor: '#ef4444', borderRadius: '4px', fontWeight: 'bold' }}>
                      Impact: {alerts[0].targeted_assets_found.join(', ')}
                    </span>
                  )}
                </span>
              </div>
            </div>
            <button onClick={() => setAlerts([])} style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', opacity: 0.7 }}>
              <X size={18} />
            </button>
          </div>
        </div>
      )}

      <main className="content">
        {activeView === 'overview' && (
          <>
            <section className="stats-grid">
              <div className="stat-card">
                <User className="icon-purple" />
                <div className="stat-info">
                  <h3>Personal Risk Score</h3>
                  <p className={`stat-value ${personalRiskScore > 7 ? 'high' : personalRiskScore > 4 ? 'medium' : 'low'}`}>
                    {personalRiskScore} / 10
                  </p>
                </div>
              </div>
              <div className="stat-card">
                <Activity className="icon-green" />
                <div className="stat-info">
                  <h3>Live Threat Level</h3>
                  <p className="stat-value medium">Moderate</p>
                </div>
              </div>
              <div className="stat-card">
                <Newspaper className="icon-blue" />
                <div className="stat-info">
                  <h3>Tracked Articles</h3>
                  <p className="stat-value">{news.length}</p>
                </div>
              </div>
              <div className="stat-card">
                <AlertTriangle className="icon-red" />
                <div className="stat-info">
                  <h3>Trend Prediction</h3>
                  <p className="stat-value high">Rising</p>
                </div>
              </div>
            </section>

            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px', marginBottom: '20px' }}>
              <ThreatDashboard />
              <ThreatHeatmap news={news} />
            </div>

            <section className="news-section">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ margin: 0 }}><Newspaper /> Latest Security News</h2>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button 
                    className={`view-toggle-btn ${viewMode === 'full' ? 'active' : ''}`}
                    onClick={() => setViewMode('full')}
                  >
                    <Maximize2 size={14} /> Full
                  </button>
                  <button 
                    className={`view-toggle-btn ${viewMode === 'compact' ? 'active' : ''}`}
                    onClick={() => setViewMode('compact')}
                  >
                    <List size={14} /> Compact
                  </button>
                </div>
              </div>

              {loading ? (
                <p>Loading news intelligence...</p>
              ) : (
                <div className={`news-list ${viewMode}`}>
                  {news.map((item, idx) => (
                    <div key={idx} className={`news-item ${viewMode} ${item.risk_level >= 8 ? 'high-risk' : ''}`}>
                      <div className="news-meta">
                        <span className={`badge ${item.crime_type}`}>
                          {item.crime_type}
                        </span>
                        {viewMode === 'full' && <span className="news-source">{item.source}</span>}
                        <span style={{ fontWeight: 'bold', color: item.risk_level >= 8 ? '#ef4444' : '#94a3b8' }}>
                          Risk: {item.risk_level}/10
                        </span>
                      </div>
                      <h3>{item.title}</h3>
                      
                      {viewMode === 'full' && (
                        <>
                          {item.cve_ids && item.cve_ids.length > 0 && (
                            <div className="cve-container" style={{ display: 'flex', gap: '8px', marginBottom: '10px', flexWrap: 'wrap' }}>
                              {item.cve_ids.map(cve => (
                                <a 
                                  key={cve}
                                  href={`https://nvd.nist.gov/vuln/detail/${cve}`} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="cve-badge"
                                  style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '2px 8px', borderRadius: '4px', fontSize: '0.85em', fontWeight: 'bold', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}
                                >
                                  {cve} <ExternalLink size={12} />
                                </a>
                              ))}
                            </div>
                          )}

                          <p className="news-excerpt">
                            {item.summary ? item.summary : item.content?.substring(0, 150) + '...'}
                          </p>
                          
                          {item.mitre_attack && item.mitre_attack.length > 0 && (
                            <div style={{ marginTop: '10px', fontSize: '0.85em', color: '#8b5cf6' }}>
                              <strong>MITRE ATT&CK:</strong> {item.mitre_attack.join(', ')}
                            </div>
                          )}

                          <a href={item.url} target="_blank" rel="noopener noreferrer" className="read-more">Read Full Article</a>
                        </>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </section>
          </>
        )}

        {activeView === 'analysis' && (
          <div className="analysis-container">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <ThreatKnowledgeGraph onNodeClick={handleGraphNodeClick} />
              <ThreatChat />
            </div>
            
            <div className="drill-down-panel">
              <div className="drill-down-header">
                <h3>{selectedEntity ? `Targeted Analysis: ${selectedEntity.name}` : 'Threat Drill-down'}</h3>
                {selectedEntity && (
                  <button onClick={() => setSelectedEntity(null)} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
                    <X size={20} />
                  </button>
                )}
              </div>
              
              {!selectedEntity ? (
                <div style={{ textAlign: 'center', color: '#94a3b8', marginTop: '100px' }}>
                  <Maximize2 size={48} style={{ opacity: 0.2, marginBottom: '20px' }} />
                  <p>지식 그래프에서 노드를 클릭하여<br/>상세 위협 정보를 탐색하세요.</p>
                </div>
              ) : (
                <div className="drill-down-content">
                  <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#334155', borderRadius: '8px' }}>
                    <h4 style={{ margin: '0 0 5px 0', color: '#3b82f6' }}>개체 정보</h4>
                    <p style={{ margin: 0, fontSize: '0.9rem' }}>유형: {selectedEntity.label}</p>
                    <p style={{ margin: 0, fontSize: '0.9rem' }}>관련 뉴스: {getFilteredNews().length}건</p>
                  </div>
                  
                  <h4>연관 뉴스 목록</h4>
                  {getFilteredNews().length === 0 ? (
                    <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>연관된 상세 뉴스가 없습니다.</p>
                  ) : (
                    <div className="news-list compact">
                      {getFilteredNews().map((item, idx) => (
                        <div key={idx} className="news-item compact">
                          <span className={`badge ${item.crime_type}`} style={{ padding: '2px 6px', fontSize: '0.65rem' }}>
                            {item.crime_type}
                          </span>
                          <h3>{item.title}</h3>
                          <a href={item.url} target="_blank" rel="noreferrer" style={{ color: '#3b82f6' }}>
                            <ExternalLink size={14} />
                          </a>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {activeView === 'settings' && (
          <section className="profile-section" style={{ backgroundColor: '#1e293b', padding: '30px', borderRadius: '12px', border: '1px solid #334155' }}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '25px' }}><SettingsIcon /> Personal Security Settings</h2>
            
            <div className="setting-group" style={{ marginBottom: '30px' }}>
              <h3><Lock size={20} style={{ verticalAlign: 'middle', marginRight: '10px' }} /> Monitored Assets</h3>
              <p style={{ color: '#94a3b8', marginBottom: '15px' }}>Add keywords for your technology stack to receive prioritized risk scoring and alerts.</p>
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '15px' }}>
                {assets.map((asset, idx) => (
                  <span key={idx} style={{ padding: '8px 16px', backgroundColor: '#334155', border: '1px solid #475569', borderRadius: '20px', fontSize: '0.9em', display: 'flex', alignItems: 'center', gap: '10px' }}>
                    {asset}
                    <button onClick={() => removeAsset(asset)} style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#ef4444', fontWeight: 'bold' }}>&times;</button>
                  </span>
                ))}
              </div>
              <form onSubmit={addAsset} style={{ display: 'flex', gap: '10px' }}>
                <input 
                  type="text" 
                  value={newAsset} 
                  onChange={(e) => setNewAsset(e.target.value)} 
                  placeholder="e.g. AWS, Kubernetes, Python" 
                  style={{ padding: '10px 15px', borderRadius: '8px', border: '1px solid #334155', backgroundColor: '#0f172a', color: 'white', flex: '1', maxWidth: '400px' }}
                />
                <button type="submit" style={{ padding: '10px 20px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}>Add Asset</button>
              </form>
            </div>

            <div className="setting-group">
              <h3><Bell size={20} style={{ verticalAlign: 'middle', marginRight: '10px' }} /> Notification Preferences</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', color: '#94a3b8' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}>
                  <input type="checkbox" defaultChecked /> Real-time Browser Alerts (WebSocket)
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}>
                  <input type="checkbox" defaultChecked /> High Risk Email Reports
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}>
                  <input type="checkbox" /> Weekly Security Summary
                </label>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
