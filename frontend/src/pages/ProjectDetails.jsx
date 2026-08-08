import React, { useState, useEffect, useCallback } from 'react';
import { projectService } from '../services/projectService';
import { storyService } from '../services/storyService';
import { StatusBadge } from '../components/common/StatusBadge';
import { ProjectForm } from '../components/projects/ProjectForm';
import { StoryCard } from '../components/stories/StoryCard';
import { StoryForm } from '../components/stories/StoryForm';
import { ProjectReportSection } from '../components/reports/ProjectReportSection';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { ArrowLeft, Plus, Edit2, Calendar, Layers } from 'lucide-react';

export function ProjectDetails({ projectId, onBack, onNotFound }) {
  const [project, setProject] = useState(null);
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Modals state
  const [isEditProjectOpen, setIsEditProjectOpen] = useState(false);
  const [isSubmittingProject, setIsSubmittingProject] = useState(false);
  const [projectFormError, setProjectFormError] = useState(null);

  const [isStoryFormOpen, setIsStoryFormOpen] = useState(false);
  const [editingStory, setEditingStory] = useState(null);
  const [storyToDelete, setStoryToDelete] = useState(null);
  const [isSubmittingStory, setIsSubmittingStory] = useState(false);
  const [storyFormError, setStoryFormError] = useState(null);

  const loadProjectData = useCallback(async () => {
    setLoading(true);
    setError(null);

    const [projRes, storiesRes] = await Promise.all([
      projectService.getProjectById(projectId),
      storyService.getStoriesByProject(projectId),
    ]);

    if (projRes.success && projRes.data) {
      setProject(projRes.data);
    } else {
      setError(projRes.error || 'Project not found');
      setLoading(false);
      if (onNotFound) {
        onNotFound();
      }
      return;
    }

    if (storiesRes.success) {
      setStories(storiesRes.data || []);
    } else {
      setError(storiesRes.error);
    }

    setLoading(false);
  }, [projectId, onNotFound]);

  useEffect(() => {
    loadProjectData();
  }, [loadProjectData]);

  // Update Project handler
  const handleSaveProject = async (formData) => {
    setIsSubmittingProject(true);
    setProjectFormError(null);

    const res = await projectService.updateProject(projectId, formData);
    if (res.success) {
      setProject(res.data);
      setIsEditProjectOpen(false);
    } else {
      setProjectFormError(res.error);
    }
    setIsSubmittingProject(false);
  };

  // User Story Actions
  const handleSaveStory = async (formData) => {
    setIsSubmittingStory(true);
    setStoryFormError(null);

    let res;
    if (editingStory) {
      res = await storyService.updateStory(editingStory.id, formData);
    } else {
      res = await storyService.createStory(projectId, formData);
    }

    if (res.success) {
      setIsStoryFormOpen(false);
      setEditingStory(null);
      loadProjectData();
    } else {
      setStoryFormError(res.error);
    }
    setIsSubmittingStory(false);
  };

  const handleUpdateStoryInline = async (storyId, updateData, fullStory = null) => {
    if (fullStory) {
      setEditingStory(fullStory);
      setStoryFormError(null);
      setIsStoryFormOpen(true);
      return;
    }

    const res = await storyService.updateStory(storyId, updateData);
    if (res.success) {
      loadProjectData();
    } else {
      alert(`Failed to update user story: ${res.error}`);
    }
  };

  const handleDeleteStoryConfirm = async () => {
    if (!storyToDelete) return;
    setIsSubmittingStory(true);

    const res = await storyService.deleteStory(storyToDelete.id);
    if (res.success) {
      setStoryToDelete(null);
      loadProjectData();
    } else {
      alert(`Failed to delete user story: ${res.error}`);
    }
    setIsSubmittingStory(false);
  };

  if (loading) return <LoadingState message="Loading project details..." />;
  if (error) return <ErrorMessage message={error} onRetry={loadProjectData} />;
  if (!project) return <ErrorMessage message="Project not found." />;

  const formattedDate = new Date(project.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="project-details-page">
      {/* Top Back Navigation */}
      <button onClick={onBack} className="btn btn-secondary btn-sm mb-4">
        <ArrowLeft size={16} />
        <span>Back to Projects</span>
      </button>

      {/* Project Header Banner Card */}
      <div className="project-header-card glass-card mb-6">
        <div className="project-header-main">
          <div className="project-title-area">
            <div className="project-title-wrap">
              <h2>{project.name}</h2>
              <StatusBadge status={project.status} />
            </div>

            <p className="project-desc">
              {project.description || 'No description provided for this project.'}
            </p>

            <div className="project-meta-row">
              <div className="meta-item">
                <Calendar size={15} />
                <span>Created {formattedDate}</span>
              </div>
              <div className="meta-item">
                <Layers size={15} />
                <span>{stories.length} User Stories</span>
              </div>
            </div>
          </div>

          <div className="project-header-actions">
            <button
              onClick={() => {
                setProjectFormError(null);
                setIsEditProjectOpen(true);
              }}
              className="btn btn-outline"
            >
              <Edit2 size={16} />
              <span>Edit Project</span>
            </button>
          </div>
        </div>
      </div>

      {/* Asynchronous Progress Report Section */}
      <ProjectReportSection projectId={project.id} />

      {/* User Stories Hierarchy Section */}
      <div className="stories-section mt-6">
        <div className="section-header-row">
          <div>
            <h3>User Stories</h3>
            <p className="text-muted text-sm">Features and requirements belonging to this project</p>
          </div>

          <button
            onClick={() => {
              setEditingStory(null);
              setStoryFormError(null);
              setIsStoryFormOpen(true);
            }}
            className="btn btn-primary"
          >
            <Plus size={18} />
            <span>Create User Story</span>
          </button>
        </div>

        {stories.length === 0 ? (
          <div className="empty-state-card glass-card">
            <Layers size={48} className="empty-icon" />
            <h3>No User Stories</h3>
            <p>Create your first user story to break down project requirements into tasks.</p>
            <button
              onClick={() => {
                setEditingStory(null);
                setStoryFormError(null);
                setIsStoryFormOpen(true);
              }}
              className="btn btn-primary mt-3"
            >
              <Plus size={18} />
              <span>Add User Story</span>
            </button>
          </div>
        ) : (
          <div className="stories-list">
            {stories.map(story => (
              <StoryCard
                key={story.id}
                story={story}
                onUpdateStory={handleUpdateStoryInline}
                onDeleteStory={(s) => setStoryToDelete(s)}
                onRefreshProject={loadProjectData}
              />
            ))}
          </div>
        )}
      </div>

      {/* Edit Project Form Modal */}
      <ProjectForm
        isOpen={isEditProjectOpen}
        initialData={project}
        onSubmit={handleSaveProject}
        onClose={() => setIsEditProjectOpen(false)}
        isSubmitting={isSubmittingProject}
        apiError={projectFormError}
      />

      {/* Create / Edit User Story Form Modal */}
      <StoryForm
        isOpen={isStoryFormOpen}
        initialData={editingStory}
        onSubmit={handleSaveStory}
        onClose={() => {
          setIsStoryFormOpen(false);
          setEditingStory(null);
        }}
        isSubmitting={isSubmittingStory}
        apiError={storyFormError}
      />

      {/* Delete User Story Confirmation Modal */}
      <ConfirmDialog
        isOpen={!!storyToDelete}
        title="Delete User Story"
        message={`Are you sure you want to delete user story "${storyToDelete?.title}"? Warning: Deleting a story removes all its associated tasks.`}
        onConfirm={handleDeleteStoryConfirm}
        onCancel={() => setStoryToDelete(null)}
        isSubmitting={isSubmittingStory}
      />
    </div>
  );
}
