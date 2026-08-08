import React from 'react';
import { LayoutDashboard, FolderKanban, Activity } from 'lucide-react';

export function Navbar({ activeTab, setActiveTab, health }) {
  return (
    <header className="navbar-header">
      <div className="container navbar-container">
        <div className="navbar-brand" onClick={() => setActiveTab('dashboard')}>
          <div className="brand-icon">
            <FolderKanban size={24} />
          </div>
          <div className="brand-text">
            <span className="brand-title">AgileFlow</span>
            <span className="brand-subtitle">Project Manager</span>
          </div>
        </div>

        <nav className="navbar-nav">
          <button
            className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={18} />
            <span>Dashboard</span>
          </button>
          <button
            className={`nav-btn ${activeTab === 'projects' || activeTab === 'project-details' ? 'active' : ''}`}
            onClick={() => setActiveTab('projects')}
          >
            <FolderKanban size={18} />
            <span>Projects</span>
          </button>
        </nav>

        <div className="navbar-status">
          <div
            className={`health-badge ${
              health.loading
                ? 'health-loading'
                : health.success
                ? 'health-online'
                : 'health-offline'
            }`}
            title={health.success ? 'Backend connected' : 'Backend offline'}
          >
            <Activity size={14} className="pulse-icon" />
            <span>{health.loading ? 'Connecting...' : health.success ? 'API Online' : 'API Offline'}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
