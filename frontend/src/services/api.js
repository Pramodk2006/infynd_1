/**
 * API service for communicating with the Python backend
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 10 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Company API
 */
export const companyAPI = {
  // Get all companies
  getAll: async () => {
    const response = await api.get('/companies');
    return response.data;
  },

  // Get company details (skip enhanced extraction by default for fast loading)
  getByName: async (name) => {
    const response = await api.get(`/companies/${encodeURIComponent(name)}?enhanced=false`);
    return response.data;
  },

  // Get company sources
  getSources: async (name) => {
    const response = await api.get(`/companies/${encodeURIComponent(name)}/sources`);
    return response.data;
  },
};

/**
 * Extraction API
 */
export const extractionAPI = {
  // Submit single extraction
  extract: async (data) => {
    const response = await api.post('/extract', data);
    return response.data;
  },

  // Submit batch extraction
  batch: async (data) => {
    const response = await api.post('/batch', data);
    return response.data;
  },

  // Get extraction status
  getStatus: async (jobId) => {
    const response = await api.get(`/extract/${jobId}`);
    return response.data;
  },
};

/**
 * Source API
 */
export const sourceAPI = {
  // Get source document
  getDocument: async (documentId) => {
    const response = await api.get(`/sources/${documentId}`);
    return response.data;
  },

  // Get source by filepath
  getByPath: async (companyName, filename) => {
    const response = await api.get(`/sources/${encodeURIComponent(companyName)}/${filename}`);
    return response.data;
  },
};

// Mock API for development (when backend is not available)
export const mockAPI = {
  companies: [
    {
      name: 'Acme Corporation',
      sources: 3,
      lastUpdated: '2025-12-17T13:09:36',
    },
    {
      name: 'TechVision Inc',
      sources: 1,
      lastUpdated: '2025-12-17T13:12:12',
    },
    {
      name: 'Example Company',
      sources: 1,
      lastUpdated: '2025-12-17T13:09:48',
    },
  ],

  companyDetails: {
    name: 'Acme Corporation',
    totalSources: 3,
    created: '2025-12-17T13:06:56',
    lastUpdated: '2025-12-17T13:09:36',
    sources: [
      {
        type: 'html',
        title: 'Acme Corporation - Innovative Solutions',
        uri: 'C:\\test_data\\acme_about.html',
        extracted_at: '2025-12-17T13:06:56',
        document_id: '314ccfef-ccf8-4c52-a36a-f821cdc15eac',
      },
      {
        type: 'text',
        title: 'acme_overview',
        uri: 'C:\\test_data\\acme_overview.txt',
        extracted_at: '2025-12-17T13:09:36',
        document_id: 'b5565b3e-fcd3-4b2e-bba5-1cf1f54c8483',
      },
    ],
  },
};

export default api;
