import api from './api';

export const documentService = {
  getDocuments: async () => {
    const res = await api.get('/document-history');
    return res.data;
  },

  getDocumentDetails: async (id) => {
    const res = await api.get(`/documents/${id}`);
    return res.data;
  },

  deleteDocument: async (id) => {
    const res = await api.delete(`/documents/${id}`);
    return res.data;
  },

  uploadDocument: async (formData, onProgress) => {
    const res = await api.post('/upload-docs', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percent);
        }
      }
    });
    return res.data;
  },

  askQuestion: async (question, documentId = null) => {
    const payload = { question };
    if (documentId) {
      payload.document_id = documentId;
    }
    const res = await api.post('/ask', payload);
    return res.data;
  },

  getDocumentAnalysis: async (id) => {
    const res = await api.get(`/analysis/${id}`);
    return res.data;
  },

  getDocumentStats: async (id) => {
    const res = await api.get(`/stats/${id}`);
    return res.data;
  },

  batchDeleteDocuments: async (documentIds) => {
    const res = await api.post('/documents/batch-delete', { document_ids: documentIds });
    return res.data;
  },

  reindexDocument: async (id) => {
    const res = await api.post(`/documents/${id}/reindex`);
    return res.data;
  },

  getDocumentSummary: async (id) => {
    const res = await api.get(`/documents/${id}/summary`);
    return res.data;
  },

  searchDocuments: async (query, fileType = null, limit = 20) => {
    const params = { q: query, limit };
    if (fileType && fileType !== 'ALL') {
      params.file_type = fileType;
    }
    const res = await api.get('/documents/search', { params });
    return res.data;
  },

  exportArchive: async (documentIds = [], includeRawFiles = true) => {
    const res = await api.post('/documents/export-archive', {
      document_ids: documentIds,
      include_raw_files: includeRawFiles
    }, {
      responseType: 'blob'
    });
    return res.data;
  },

  getCapabilities: async () => {
    const res = await api.get('/system/capabilities');
    return res.data;
  },

  getTelemetry: async () => {
    const res = await api.get('/system/telemetry');
    return res.data;
  },

  getDetailedHealth: async () => {
    const res = await api.get('/system/health/detailed');
    return res.data;
  }
};

export default documentService;
