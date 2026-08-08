import React, { useState, useEffect } from 'react';
import { X, Check } from 'lucide-react';

export function ProjectForm({
  isOpen,
  initialData = null,
  onSubmit,
  onClose,
  isSubmitting = false,
  apiError = null,
}) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState('PLANNING');
  const [validationError, setValidationError] = useState('');

  useEffect(() => {
    if (initialData) {
      setName(initialData.name || '');
      setDescription(initialData.description || '');
      setStatus(initialData.status || 'PLANNING');
    } else {
      setName('');
      setDescription('');
      setStatus('PLANNING');
    }
    setValidationError('');
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim()) {
      setValidationError('Project name is required.');
      return;
    }
    setValidationError('');
    onSubmit({
      name: name.trim(),
      description: description.trim() || null,
      status,
    });
  };

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal-card">
        <div className="modal-header">
          <h3>{initialData ? 'Edit Project' : 'Create New Project'}</h3>
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
              <label htmlFor="project-name" className="form-label">
                Project Name <span className="text-danger">*</span>
              </label>
              <input
                id="project-name"
                type="text"
                className="form-control"
                placeholder="e.g. E-Commerce Platform"
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  if (validationError) setValidationError('');
                }}
                disabled={isSubmitting}
                autoFocus
              />
            </div>

            <div className="form-group">
              <label htmlFor="project-description" className="form-label">
                Description
              </label>
              <textarea
                id="project-description"
                className="form-control"
                rows={3}
                placeholder="Provide high-level context or initiative goals..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={isSubmitting}
              />
            </div>

            <div className="form-group">
              <label htmlFor="project-status" className="form-label">
                Status
              </label>
              <select
                id="project-status"
                className="form-control"
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                disabled={isSubmitting}
              >
                <option value="PLANNING">PLANNING</option>
                <option value="ACTIVE">ACTIVE</option>
                <option value="COMPLETED">COMPLETED</option>
              </select>
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
                  <span>{initialData ? 'Update Project' : 'Create Project'}</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
