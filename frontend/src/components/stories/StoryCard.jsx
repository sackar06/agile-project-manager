import React, { useState, useEffect, useCallback } from 'react';
import { StatusBadge } from '../common/StatusBadge';
import { PriorityBadge } from '../common/PriorityBadge';
import { TaskCard } from '../tasks/TaskCard';
import { TaskForm } from '../tasks/TaskForm';
import { ConfirmDialog } from '../common/ConfirmDialog';
import { LoadingState } from '../common/LoadingState';
import { ErrorMessage } from '../common/ErrorMessage';
import { taskService } from '../../services/taskService';
import { ChevronDown, ChevronRight, Plus, Edit2, Trash2, CheckCircle2 } from 'lucide-react';

export function StoryCard({
  story,
  onUpdateStory,
  onDeleteStory,
  onRefreshProject,
}) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [tasks, setTasks] = useState([]);
  const [loadingTasks, setLoadingTasks] = useState(false);
  const [taskError, setTaskError] = useState(null);

  // Modals state
  const [isTaskFormOpen, setIsTaskFormOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [taskToDelete, setTaskToDelete] = useState(null);
  const [isSubmittingTask, setIsSubmittingTask] = useState(false);
  const [taskFormError, setTaskFormError] = useState(null);

  const fetchTasks = useCallback(async () => {
    setLoadingTasks(true);
    setTaskError(null);
    const res = await taskService.getTasksByStory(story.id);
    if (res.success) {
      setTasks(res.data || []);
    } else {
      setTaskError(res.error);
    }
    setLoadingTasks(false);
  }, [story.id]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Story inline updates
  const handleStatusChange = (newStatus) => {
    onUpdateStory(story.id, {
      title: story.title,
      description: story.description,
      status: newStatus,
      priority: story.priority,
    });
  };

  const handlePriorityChange = (newPriority) => {
    onUpdateStory(story.id, {
      title: story.title,
      description: story.description,
      status: story.status,
      priority: newPriority,
    });
  };

  // Task actions
  const handleSaveTask = async (formData) => {
    setIsSubmittingTask(true);
    setTaskFormError(null);

    let res;
    if (editingTask) {
      res = await taskService.updateTask(editingTask.id, formData);
    } else {
      res = await taskService.createTask(story.id, formData);
    }

    if (res.success) {
      setIsTaskFormOpen(false);
      setEditingTask(null);
      fetchTasks();
      if (onRefreshProject) onRefreshProject();
    } else {
      setTaskFormError(res.error);
    }
    setIsSubmittingTask(false);
  };

  const handleTaskStatusChange = async (taskId, newStatus) => {
    const targetTask = tasks.find(t => t.id === taskId);
    if (!targetTask) return;

    // Optimistic UI update
    setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: newStatus } : t));

    const res = await taskService.updateTask(taskId, {
      title: targetTask.title,
      description: targetTask.description,
      status: newStatus,
      priority: targetTask.priority,
      assigned_to: targetTask.assigned_to,
    });

    if (!res.success) {
      // Rollback on failure
      fetchTasks();
    } else if (onRefreshProject) {
      onRefreshProject();
    }
  };

  const handleDeleteTaskConfirm = async () => {
    if (!taskToDelete) return;
    setIsSubmittingTask(true);

    const res = await taskService.deleteTask(taskToDelete.id);
    if (res.success) {
      setTaskToDelete(null);
      fetchTasks();
      if (onRefreshProject) onRefreshProject();
    } else {
      alert(`Failed to delete task: ${res.error}`);
    }
    setIsSubmittingTask(false);
  };

  const completedTasksCount = tasks.filter(t => t.status === 'DONE').length;

  return (
    <div className="story-card">
      <div className="story-header">
        <div className="story-title-row">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="btn-icon-subtle"
            aria-label="Toggle story tasks"
          >
            {isExpanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
          </button>

          <h4 className="story-title">{story.title}</h4>
          <PriorityBadge priority={story.priority} />
          <StatusBadge status={story.status} />
        </div>

        <div className="story-actions">
          <select
            className="form-control-sm"
            value={story.status}
            onChange={(e) => handleStatusChange(e.target.value)}
          >
            <option value="TODO">Status: TODO</option>
            <option value="IN_PROGRESS">Status: IN_PROGRESS</option>
            <option value="DONE">Status: DONE</option>
          </select>

          <select
            className="form-control-sm"
            value={story.priority}
            onChange={(e) => handlePriorityChange(e.target.value)}
          >
            <option value="LOW">Priority: LOW</option>
            <option value="MEDIUM">Priority: MEDIUM</option>
            <option value="HIGH">Priority: HIGH</option>
          </select>

          <button
            onClick={() => onUpdateStory(story.id, null, story)}
            className="btn-icon-subtle"
            title="Edit story"
            aria-label="Edit story"
          >
            <Edit2 size={16} />
          </button>

          <button
            onClick={() => onDeleteStory(story)}
            className="btn-icon-subtle text-danger"
            title="Delete story"
            aria-label="Delete story"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      {story.description && (
        <p className="story-desc">{story.description}</p>
      )}

      {/* Embedded Tasks Section */}
      {isExpanded && (
        <div className="tasks-section">
          <div className="tasks-header">
            <div className="tasks-counter">
              <CheckCircle2 size={14} className="text-accent" />
              <span>
                Tasks ({completedTasksCount}/{tasks.length} Done)
              </span>
            </div>

            <button
              onClick={() => {
                setEditingTask(null);
                setTaskFormError(null);
                setIsTaskFormOpen(true);
              }}
              className="btn btn-secondary btn-xs"
            >
              <Plus size={14} />
              <span>Add Task</span>
            </button>
          </div>

          {loadingTasks ? (
            <LoadingState message="Loading tasks..." />
          ) : taskError ? (
            <ErrorMessage message={taskError} onRetry={fetchTasks} />
          ) : tasks.length === 0 ? (
            <div className="empty-state-sm">
              <p>No tasks for this user story yet.</p>
            </div>
          ) : (
            <div className="task-list-grid">
              {tasks.map(task => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onStatusChange={handleTaskStatusChange}
                  onEdit={(t) => {
                    setEditingTask(t);
                    setTaskFormError(null);
                    setIsTaskFormOpen(true);
                  }}
                  onDelete={(t) => setTaskToDelete(t)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Task Form Modal */}
      <TaskForm
        isOpen={isTaskFormOpen}
        initialData={editingTask}
        onSubmit={handleSaveTask}
        onClose={() => {
          setIsTaskFormOpen(false);
          setEditingTask(null);
        }}
        isSubmitting={isSubmittingTask}
        apiError={taskFormError}
      />

      {/* Delete Task Confirmation */}
      <ConfirmDialog
        isOpen={!!taskToDelete}
        title="Delete Task"
        message={`Are you sure you want to delete task "${taskToDelete?.title}"?`}
        onConfirm={handleDeleteTaskConfirm}
        onCancel={() => setTaskToDelete(null)}
        isSubmitting={isSubmittingTask}
      />
    </div>
  );
}
