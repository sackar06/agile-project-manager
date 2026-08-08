const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Core HTTP Request Wrapper
 */
export async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  const defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body);
  }

  try {
    const response = await fetch(url, config);

    // Handle 204 No Content
    if (response.status === 204) {
      return { success: true, data: null, status: 204 };
    }

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      let errorMessage = 'An unexpected error occurred.';
      if (data.detail) {
        if (Array.isArray(data.detail)) {
          errorMessage = data.detail.map(err => err.msg || `${err.loc?.join('.')} is invalid`).join(', ');
        } else {
          errorMessage = data.detail;
        }
      }
      return {
        success: false,
        error: errorMessage,
        status: response.status,
      };
    }

    return { success: true, data, status: response.status };
  } catch (error) {
    return {
      success: false,
      error: 'Unable to connect to the server. Please verify the backend is running.',
      status: 0,
    };
  }
}

/**
 * Health status check helper
 */
export async function checkBackendHealth() {
  const rootUrl = API_BASE_URL.replace(/\/api\/v1\/?$/, '');
  try {
    const res = await fetch(`${rootUrl}/health`);
    if (res.ok) {
      const data = await res.json();
      return { success: true, data };
    }
    return { success: false, error: 'Health check failed' };
  } catch (err) {
    return { success: false, error: 'Server unreachable' };
  }
}
