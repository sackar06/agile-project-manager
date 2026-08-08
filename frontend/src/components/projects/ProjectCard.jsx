import React, { useState, useEffect } from 'react';
import { StatusBadge } from '../common/StatusBadge';
import { Calendar, Layers, ArrowRight, Edit2, Trash2 } from 'lucide-react';
import { storyService } from '../../services/storyService';

export function ProjectCard({ project, onOpen, onEdit, onDelete }) {
  const [storyCount, setStoryCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const fetchStoryCount = async () => {
      if (!project?.id) {
        if (isMounted) {
          setStoryCount(0);
          setLoading(false);
        }
        return;
      }

      setLoading(true);
      try {
        const res = await storyService.getStoriesByProject(project.id);
        if (isMounted) {
          if (res && res.success && Array.isArray(res.data)) {
            setStoryCount(res.data.length);
          } else {
            setStoryCount(0);
          }
        }
      } catch (err) {
        if (isMounted) {
          setStoryCount(0);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchStoryCount();

    return () => {
      isMounted = false;
    };
  }, [project.id]);

  const formattedDate = new Date(project.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

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
          <span>
            {loading
              ? 'Loading...'
              : `${storyCount} ${storyCount === 1 ? 'User Story' : 'User Stories'}`}
          </span>
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
