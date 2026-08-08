import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from './components/layout/Navbar';
import { Dashboard } from './pages/Dashboard';
import { ProjectsPage } from './pages/ProjectsPage';
import { ProjectDetails } from './pages/ProjectDetails';
import { NotFound } from './pages/NotFound';
import { checkBackendHealth } from './services/api';

const parseNavState = () => {
  // Clean up legacy localStorage navigation keys if present
  try {
    localStorage.removeItem('agile_activeTab');
    localStorage.removeItem('agile_selectedProjectId');
  } catch (e) {
    // Ignore storage access errors if any
  }

  const params = new URLSearchParams(window.location.search);
  const urlTab = params.get('tab');
  const urlProjectId = params.get('projectId');

  const storedTab = sessionStorage.getItem('agile_activeTab');
  const storedProjectId = sessionStorage.getItem('agile_selectedProjectId');

  let tab = urlTab || storedTab || 'dashboard';
  let projIdRaw = urlProjectId || storedProjectId || null;

  const validTabs = ['dashboard', 'projects', 'project-details'];
  if (!validTabs.includes(tab)) {
    tab = 'dashboard';
  }

  let projId = null;
  if (tab === 'project-details') {
    const parsed = projIdRaw ? parseInt(projIdRaw, 10) : null;
    if (parsed && !isNaN(parsed) && parsed > 0) {
      projId = parsed;
    } else {
      tab = 'dashboard';
      projId = null;
    }
  }

  return { tab, projId };
};

export function App() {
  const initialState = parseNavState();
  const [activeTab, setActiveTab] = useState(initialState.tab); // 'dashboard' | 'projects' | 'project-details'
  const [selectedProjectId, setSelectedProjectId] = useState(initialState.projId);
  const [projectAction, setProjectAction] = useState(null);
  const [targetProject, setTargetProject] = useState(null);

  const [health, setHealth] = useState({
    loading: true,
    success: false,
    data: null,
    error: null,
  });

  const updateNavState = useCallback((tab, projId = null) => {
    setActiveTab(tab);
    setSelectedProjectId(projId);

    // Persist in sessionStorage
    sessionStorage.setItem('agile_activeTab', tab);
    if (tab === 'project-details' && projId) {
      sessionStorage.setItem('agile_selectedProjectId', String(projId));
    } else {
      sessionStorage.removeItem('agile_selectedProjectId');
    }

    // Sync URL search parameters
    const url = new URL(window.location.href);
    url.searchParams.set('tab', tab);
    if (tab === 'project-details' && projId) {
      url.searchParams.set('projectId', String(projId));
    } else {
      url.searchParams.delete('projectId');
    }
    window.history.replaceState(null, '', url.pathname + url.search);
  }, []);

  useEffect(() => {
    // Initial sync of URL and sessionStorage on mount
    updateNavState(activeTab, selectedProjectId);

    const handlePopState = () => {
      const { tab, projId } = parseNavState();
      setActiveTab(tab);
      setSelectedProjectId(projId);
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const checkHealth = useCallback(async () => {
    setHealth(prev => ({ ...prev, loading: true }));
    const result = await checkBackendHealth();
    if (result.success) {
      setHealth({
        loading: false,
        success: true,
        data: result.data,
        error: null,
      });
    } else {
      setHealth({
        loading: false,
        success: false,
        data: null,
        error: result.error,
      });
    }
  }, []);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  const handleOpenProject = useCallback((projectId) => {
    updateNavState('project-details', projectId);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [updateNavState]);

  const handleNavigateToProjectsWithAction = useCallback((project = null, action = 'create') => {
    setProjectAction(action);
    setTargetProject(project);
    updateNavState('projects');
  }, [updateNavState]);

  const handleBackToProjects = useCallback(() => {
    setProjectAction(null);
    setTargetProject(null);
    updateNavState('projects');
  }, [updateNavState]);

  const handleProjectNotFound = useCallback(() => {
    updateNavState('dashboard');
  }, [updateNavState]);

  const handleCreateNewProject = useCallback(() => {
    handleNavigateToProjectsWithAction(null, 'create');
  }, [handleNavigateToProjectsWithAction]);

  const renderActivePage = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <Dashboard
            onOpenProject={handleOpenProject}
            onNavigateToProjects={handleBackToProjects}
            onCreateNewProject={handleCreateNewProject}
          />
        );
      case 'projects':
        return (
          <ProjectsPage
            onOpenProject={handleOpenProject}
            defaultAction={projectAction}
            targetProject={targetProject}
          />
        );
      case 'project-details':
        if (!selectedProjectId) {
          return <NotFound onGoHome={handleProjectNotFound} />;
        }
        return (
          <ProjectDetails
            projectId={selectedProjectId}
            onBack={handleBackToProjects}
            onNotFound={handleProjectNotFound}
          />
        );
      default:
        return <NotFound onGoHome={handleProjectNotFound} />;
    }
  };

  return (
    <div className="app">
      <Navbar
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setProjectAction(null);
          setTargetProject(null);
          updateNavState(tab);
        }}
        health={health}
      />
      <main className="container main-content py-6">
        {renderActivePage()}
      </main>
    </div>
  );
}

export default App;

