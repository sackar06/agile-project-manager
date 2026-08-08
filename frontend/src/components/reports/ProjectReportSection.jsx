import React, { useState, useEffect, useRef, useCallback } from 'react';
import { StatusBadge } from '../common/StatusBadge';
import { reportService } from '../../services/reportService';
import { FileText, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';

export function ProjectReportSection({ projectId }) {
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const timerRef = useRef(null);

  const stopPolling = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const pollJobStatus = useCallback(async (currentJobId) => {
    const res = await reportService.getReportStatus(currentJobId);

    if (res.success) {
      const job = res.data;
      setJobStatus(job.status);

      if (job.status === 'COMPLETED') {
        setReportData(job.report_data);
        setIsGenerating(false);
        stopPolling();
      } else if (job.status === 'FAILED') {
        setErrorMessage(job.error_message || 'Report generation failed on the server.');
        setIsGenerating(false);
        stopPolling();
      }
    } else {
      setErrorMessage(res.error);
      setIsGenerating(false);
      stopPolling();
    }
  }, [stopPolling]);

  const handleTriggerReport = async () => {
    setIsGenerating(true);
    setErrorMessage(null);
    setReportData(null);
    setJobStatus('PENDING');

    const res = await reportService.requestReport(projectId);

    if (res.success) {
      const newJobId = res.data.job_id;
      setJobId(newJobId);
      setJobStatus(res.data.status);

      // Start interval polling every 2 seconds
      stopPolling();
      pollJobStatus(newJobId);
      timerRef.current = setInterval(() => {
        pollJobStatus(newJobId);
      }, 2000);
    } else {
      setErrorMessage(res.error);
      setIsGenerating(false);
    }
  };

  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);

  return (
    <div className="report-section-card glass-card">
      <div className="report-header">
        <div className="report-title-group">
          <FileText className="text-accent" size={22} />
          <div>
            <h3>Project Progress Report</h3>
            <p className="text-muted text-sm">
              Asynchronously calculate story breakdowns and overall task completion statistics.
            </p>
          </div>
        </div>

        <button
          onClick={handleTriggerReport}
          disabled={isGenerating}
          className="btn btn-accent"
        >
          <RefreshCw className={isGenerating ? 'spin-icon' : ''} size={16} />
          <span>{isGenerating ? 'Generating...' : 'Generate Report'}</span>
        </button>
      </div>

      {jobStatus && (
        <div className="report-job-status-bar">
          <span className="text-sm text-muted">Background Job Status:</span>
          <StatusBadge status={jobStatus} />
        </div>
      )}

      {errorMessage && (
        <div className="form-error-alert mt-3">
          <AlertCircle size={16} />
          <span>{errorMessage}</span>
        </div>
      )}

      {reportData && (
        <div className="report-results-panel">
          <div className="report-summary-bar">
            <div className="completion-rate-box">
              <span className="rate-label">Overall Completion</span>
              <span className="rate-value">{reportData.task_completion_percentage}%</span>
            </div>

            <div className="progress-bar-container">
              <div
                className="progress-bar-fill"
                style={{ width: `${Math.min(100, Math.max(0, reportData.task_completion_percentage))}%` }}
              />
            </div>
          </div>

          <div className="report-grid-2">
            {/* User Stories Breakdown */}
            <div className="report-metric-card">
              <h4>User Stories Summary</h4>
              <div className="metric-row main">
                <span>Total Stories:</span>
                <strong>{reportData.user_stories.total}</strong>
              </div>
              <div className="metric-row">
                <span>TODO:</span>
                <span className="badge-slate-sm">{reportData.user_stories.todo}</span>
              </div>
              <div className="metric-row">
                <span>IN PROGRESS:</span>
                <span className="badge-amber-sm">{reportData.user_stories.in_progress}</span>
              </div>
              <div className="metric-row">
                <span>DONE:</span>
                <span className="badge-emerald-sm">{reportData.user_stories.done}</span>
              </div>
            </div>

            {/* Tasks Breakdown */}
            <div className="report-metric-card">
              <h4>Tasks Summary</h4>
              <div className="metric-row main">
                <span>Total Tasks:</span>
                <strong>{reportData.tasks.total}</strong>
              </div>
              <div className="metric-row">
                <span>TODO:</span>
                <span className="badge-slate-sm">{reportData.tasks.todo}</span>
              </div>
              <div className="metric-row">
                <span>IN PROGRESS:</span>
                <span className="badge-amber-sm">{reportData.tasks.in_progress}</span>
              </div>
              <div className="metric-row">
                <span>DONE:</span>
                <span className="badge-emerald-sm">{reportData.tasks.done}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
