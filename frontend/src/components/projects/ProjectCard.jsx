import React from 'react';
import { StatusBadge } from '../common/StatusBadge';
import { Calendar, Layers, ArrowRight, Edit2, Trash2 } from 'lucide-react';

export function ProjectCard({ project, onOpen, onEdit, onDelete }) {
  const formattedDate = new Date(project.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

  const storyCount = project.user_stories ? project.user_stories.length : 0;

  return (
    <div className="project-card">
      <div className="project-card-header">
        <h3 className="project-card-title" onClick={() => onOpen(project.id)}>
          {project.name}
        </h3>
        <StatusBadge status={project.status} />
      </div>

      <p className="project-card-desc">
        {project.description || 'No description provided.'}
      </p>

      <div className="project-card-meta">
        <div className="meta-item">
          <Calendar size={14} />
          <span>{formattedDate}</span>
        </div>
        <div className="meta-item">
          <Layers size={14} />
          <span>{storyCount} {storyCount === 1 ? 'User Story' : 'User Stories'}</span>
        </div>
      </div>

      <div className="project-card-actions">
        <button
          onClick={() => onOpen(project.id)}
          className="btn btn-primary btn-sm flex-1"
        >
          <span>Open Project</span>
          <ArrowRight size={14} />
        </button>
        <button
          onClick={() => onEdit(project)}
          className="btn-icon-subtle"
          title="Edit project"
          aria-label="Edit project"
        >
          <Edit2 size={15} />
        </button>
        <button
          onClick={() => onDelete(project)}
          className="btn-icon-subtle text-danger"
          title="Delete project"
          aria-label="Delete project"
        >
          <Trash2 size={15} />
        </button>
      </div>
    </div>
  );
}
