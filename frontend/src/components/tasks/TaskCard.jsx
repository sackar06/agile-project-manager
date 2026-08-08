import React from 'react';
import { PriorityBadge } from '../common/PriorityBadge';
import { User, Edit2, Trash2 } from 'lucide-react';

export function TaskCard({ task, onStatusChange, onEdit, onDelete }) {
  return (
    <div className={`task-card task-status-${task.status.toLowerCase()}`}>
      <div className="task-header">
        <div className="task-title-area">
          <h5 className="task-title">{task.title}</h5>
          <PriorityBadge priority={task.priority} />
        </div>

        <div className="task-actions">
          <select
            className={`task-status-select select-status-${task.status.toLowerCase()}`}
            value={task.status}
            onChange={(e) => onStatusChange(task.id, e.target.value)}
          >
            <option value="TODO">TODO</option>
            <option value="IN_PROGRESS">IN_PROGRESS</option>
            <option value="DONE">DONE</option>
          </select>

          <button
            onClick={() => onEdit(task)}
            className="btn-icon-subtle"
            title="Edit task"
            aria-label="Edit task"
          >
            <Edit2 size={14} />
          </button>
          <button
            onClick={() => onDelete(task)}
            className="btn-icon-subtle text-danger"
            title="Delete task"
            aria-label="Delete task"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {task.description && (
        <p className="task-desc">{task.description}</p>
      )}

      <div className="task-footer">
        {task.assigned_to ? (
          <div className="task-assignee">
            <User size={12} />
            <span>{task.assigned_to}</span>
          </div>
        ) : (
          <span className="task-unassigned">Unassigned</span>
        )}
      </div>
    </div>
  );
}
