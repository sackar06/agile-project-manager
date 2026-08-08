import React, { useState, useEffect } from 'react';
import { projectService } from '../services/projectService';
import { ProjectCard } from '../components/projects/ProjectCard';
import { ProjectForm } from '../components/projects/ProjectForm';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { Plus, Search, FolderKanban } from 'lucide-react';

export function ProjectsPage({ onOpenProject, defaultAction = null, targetProject = null }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Modals state
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [projectToDelete, setProjectToDelete] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formApiError, setFormApiError] = useState(null);

  const fetchProjects = async () => {
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
    fetchProjects();
  }, []);

  useEffect(() => {
    if (defaultAction === 'create') {
      setEditingProject(null);
      setIsFormOpen(true);
    } else if (defaultAction === 'edit' && targetProject) {
      setEditingProject(targetProject);
      setIsFormOpen(true);
    } else if (defaultAction === 'delete' && targetProject) {
      setProjectToDelete(targetProject);
    }
  }, [defaultAction, targetProject]);

  const handleSaveProject = async (formData) => {
    setIsSubmitting(true);
    setFormApiError(null);

    let res;
    if (editingProject) {
      res = await projectService.updateProject(editingProject.id, formData);
    } else {
      res = await projectService.createProject(formData);
    }

    if (res.success) {
      setIsFormOpen(false);
      setEditingProject(null);
      fetchProjects();
    } else {
      setFormApiError(res.error);
    }
    setIsSubmitting(false);
  };

  const handleDeleteConfirm = async () => {
    if (!projectToDelete) return;
    setIsSubmitting(true);

    const res = await projectService.deleteProject(projectToDelete.id);
    if (res.success) {
      setProjectToDelete(null);
      fetchProjects();
    } else {
      alert(`Failed to delete project: ${res.error}`);
    }
    setIsSubmitting(false);
  };

  // Filter projects by search query and status
  const filteredProjects = projects.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (p.description && p.description.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStatus = statusFilter === 'ALL' || p.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  if (loading) return <LoadingState message="Loading projects..." />;
  if (error) return <ErrorMessage message={error} onRetry={fetchProjects} />;

  return (
    <div className="projects-page">
      <div className="page-header-row">
        <div>
          <h2>Projects</h2>
          <p className="text-muted">Manage all initiatives and project containers</p>
        </div>
        <button
          onClick={() => {
            setEditingProject(null);
            setFormApiError(null);
            setIsFormOpen(true);
          }}
          className="btn btn-primary"
        >
          <Plus size={18} />
          <span>New Project</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="toolbar-row glass-card">
        <div className="search-input-wrap">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            className="form-control search-control"
            placeholder="Search projects by name or description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-wrap">
          <span className="filter-label">Status:</span>
          <select
            className="form-control filter-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="ALL">ALL STATUSES</option>
            <option value="PLANNING">PLANNING</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="COMPLETED">COMPLETED</option>
          </select>
        </div>
      </div>

      {/* Projects Grid */}
      {filteredProjects.length === 0 ? (
        <div className="empty-state-card glass-card">
          <FolderKanban size={48} className="empty-icon" />
          <h3>No Projects Found</h3>
          <p>
            {searchQuery || statusFilter !== 'ALL'
              ? 'No projects match your current filters.'
              : 'No projects created yet. Click below to add one.'}
          </p>
          <button
            onClick={() => {
              setEditingProject(null);
              setFormApiError(null);
              setIsFormOpen(true);
            }}
            className="btn btn-primary mt-3"
          >
            <Plus size={18} />
            <span>Create Project</span>
          </button>
        </div>
      ) : (
        <div className="projects-grid">
          {filteredProjects.map(project => (
            <ProjectCard
              key={project.id}
              project={project}
              onOpen={onOpenProject}
              onEdit={(p) => {
                setEditingProject(p);
                setFormApiError(null);
                setIsFormOpen(true);
              }}
              onDelete={(p) => setProjectToDelete(p)}
            />
          ))}
        </div>
      )}

      {/* Create / Edit Project Form Modal */}
      <ProjectForm
        isOpen={isFormOpen}
        initialData={editingProject}
        onSubmit={handleSaveProject}
        onClose={() => {
          setIsFormOpen(false);
          setEditingProject(null);
        }}
        isSubmitting={isSubmitting}
        apiError={formApiError}
      />

      {/* Delete Confirmation Modal */}
      <ConfirmDialog
        isOpen={!!projectToDelete}
        title="Delete Project"
        message={`Are you sure you want to delete "${projectToDelete?.name}"? Warning: Deleting a project removes all child User Stories and Tasks.`}
        confirmLabel="Delete Project"
        onConfirm={handleDeleteConfirm}
        onCancel={() => setProjectToDelete(null)}
        isSubmitting={isSubmitting}
      />
    </div>
  );
}
