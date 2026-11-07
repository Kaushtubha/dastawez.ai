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
  }
};
