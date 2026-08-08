import React, { useState, useEffect } from 'react';
import { X, Check } from 'lucide-react';

export function StoryForm({
  isOpen,
  initialData = null,
  onSubmit,
  onClose,
  isSubmitting = false,
  apiError = null,
}) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState('TODO');
  const [priority, setPriority] = useState('MEDIUM');
  const [validationError, setValidationError] = useState('');

  useEffect(() => {
    if (initialData) {
      setTitle(initialData.title || '');
      setDescription(initialData.description || '');
      setStatus(initialData.status || 'TODO');
      setPriority(initialData.priority || 'MEDIUM');
    } else {
      setTitle('');
      setDescription('');
      setStatus('TODO');
      setPriority('MEDIUM');
    }
    setValidationError('');
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) {
      setValidationError('User Story title is required.');
      return;
    }
    setValidationError('');
    onSubmit({
      title: title.trim(),
      description: description.trim() || null,
      status,
      priority,
    });
  };

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal-card">
        <div className="modal-header">
          <h3>{initialData ? 'Edit User Story' : 'Create User Story'}</h3>
          <button onClick={onClose} className="btn-icon" aria-label="Close modal">
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {(validationError || apiError) && (
              <div className="form-error-alert">
                {validationError || apiError}
              </div>
            )}

            <div className="form-group">
              <label htmlFor="story-title" className="form-label">
                Story Title <span className="text-danger">*</span>
              </label>
              <input
                id="story-title"
                type="text"
                className="form-control"
                placeholder="As a user, I want to..."
                value={title}
                onChange={(e) => {
                  setTitle(e.target.value);
                  if (validationError) setValidationError('');
                }}
                disabled={isSubmitting}
                autoFocus
              />
            </div>

            <div className="form-group">
              <label htmlFor="story-description" className="form-label">
                Description
              </label>
              <textarea
                id="story-description"
                className="form-control"
                rows={3}
                placeholder="Acceptance criteria and detailed requirements..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={isSubmitting}
              />
            </div>

            <div className="form-grid-2">
              <div className="form-group">
                <label htmlFor="story-status" className="form-label">
                  Status
                </label>
                <select
                  id="story-status"
                  className="form-control"
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  disabled={isSubmitting}
                >
                  <option value="TODO">TODO</option>
                  <option value="IN_PROGRESS">IN_PROGRESS</option>
                  <option value="DONE">DONE</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="story-priority" className="form-label">
                  Priority
                </label>
                <select
                  id="story-priority"
                  className="form-control"
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  disabled={isSubmitting}
                >
                  <option value="LOW">LOW</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="HIGH">HIGH</option>
                </select>
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                'Saving...'
              ) : (
                <>
                  <Check size={16} />
                  <span>{initialData ? 'Update Story' : 'Create Story'}</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
