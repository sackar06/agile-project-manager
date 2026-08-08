import React, { useState, useEffect } from 'react';
import { projectService } from '../services/projectService';
import { ProjectCard } from '../components/projects/ProjectCard';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { FolderKanban, PlayCircle, CheckCircle2, Clock, Plus } from 'lucide-react';

export function Dashboard({ onOpenProject, onNavigateToProjects, onCreateNewProject }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    const res = await projectService.getAllProjects();
    if (res.success) {
      setProjects(res.data || []);
    } else {
      setError(res.error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Compute stats dynamically from real backend data
  const totalProjects = projects.length;
  const activeProjects = projects.filter(p => p.status === 'ACTIVE').length;
  const completedProjects = projects.filter(p => p.status === 'COMPLETED').length;
  const planningProjects = projects.filter(p => p.status === 'PLANNING').length;

  if (loading) return <LoadingState message="Loading dashboard statistics..." />;
  if (error) return <ErrorMessage message={error} onRetry={fetchDashboardData} />;

  return (
    <div className="dashboard-page">
      <div className="page-header-row">
        <div>
          <h2>Project Dashboard</h2>
          <p className="text-muted">Overview of agile team projects and work status</p>
        </div>
        <button onClick={onCreateNewProject} className="btn btn-primary">
          <Plus size={18} />
          <span>New Project</span>
        </button>
      </div>

      {/* Real Summary Metrics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon icon-blue">
            <FolderKanban size={22} />
          </div>
          <div className="stat-details">
            <span className="stat-label">Total Projects</span>
            <span className="stat-value">{totalProjects}</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon icon-green">
            <PlayCircle size={22} />
          </div>
          <div className="stat-details">
            <span className="stat-label">Active Projects</span>
            <span className="stat-value">{activeProjects}</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon icon-purple">
            <CheckCircle2 size={22} />
          </div>
          <div className="stat-details">
            <span className="stat-label">Completed Projects</span>
            <span className="stat-value">{completedProjects}</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon icon-amber">
            <Clock size={22} />
          </div>
          <div className="stat-details">
            <span className="stat-label">In Planning</span>
            <span className="stat-value">{planningProjects}</span>
          </div>
        </div>
      </div>

      {/* Projects List Grid */}
      <div className="section-header">
        <h3>Recent Projects</h3>
        {totalProjects > 0 && (
          <button onClick={onNavigateToProjects} className="btn btn-link">
            View All ({totalProjects})
          </button>
        )}
      </div>

      {projects.length === 0 ? (
        <div className="empty-state-card glass-card">
          <FolderKanban size={48} className="empty-icon" />
          <h3>No Projects Yet</h3>
          <p>Create your first project to start tracking user stories and tasks.</p>
          <button onClick={onCreateNewProject} className="btn btn-primary mt-3">
            <Plus size={18} />
            <span>Create Project</span>
          </button>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.slice(0, 6).map(project => (
            <ProjectCard
              key={project.id}
              project={project}
              onOpen={onOpenProject}
              onEdit={() => onNavigateToProjects(project, 'edit')}
              onDelete={() => onNavigateToProjects(project, 'delete')}
            />
          ))}
        </div>
      )}
    </div>
  );
}
