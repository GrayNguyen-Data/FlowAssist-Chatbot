import api from "./axios";

export async function getDocuments() {
  const response = await api.get("/documents");
  return response.data;
}

export async function getDocument(docId) {
  const response = await api.get(`/documents/${docId}`);
  return response.data;
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/documents/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
}

export async function ingestDocument(docId) {
  const response = await api.post(`/documents/${docId}/ingest`);
  return response.data;
}

export default {
  getDocuments,
  getDocument,
  uploadDocument,
  ingestDocument,
};