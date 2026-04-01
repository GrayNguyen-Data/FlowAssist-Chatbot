import { useEffect, useRef, useState } from "react";
import { getDocuments, ingestDocument, uploadDocument } from "../api/documentsAPI";

function StatusBadge({ status }) {
  const cls = status === "ingested" ? "badge ingested" : "badge uploaded";
  return <span className={cls}>{status || "unknown"}</span>;
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [loadingList, setLoadingList] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const loadDocuments = async () => {
    try {
      setLoadingList(true);
      const data = await getDocuments();
      setDocuments(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoadingList(false);
    }
  };

  useEffect(() => { loadDocuments(); }, []);

  const handleUploadAndIngest = async () => {
    if (!selectedFile) return;
    try {
      setUploading(true);
      const uploaded = await uploadDocument(selectedFile);
      await ingestDocument(uploaded.doc_id);
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      await loadDocuments();
    } catch (error) {
      console.error(error);
    } finally {
      setUploading(false);
    }
  };

  const handleIngest = async (docId) => {
    try {
      await ingestDocument(docId);
      await loadDocuments();
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="page">
      <div className="page-header" style={{ marginBottom: 24 }}>
        <h1 style={{ margin: "0 0 4px", fontSize: 26, fontWeight: 800, letterSpacing: "-0.5px" }}>Documents</h1>
        <p style={{ margin: 0, color: "var(--text-muted)", fontSize: 14 }}>Upload tài liệu vào MinIO và ingest vào RAG knowledge base.</p>
      </div>

      <div className="docs-upload-card">
        <h3>Upload tài liệu mới</h3>
        <div
          className="file-drop"
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
          />
          <div style={{ fontSize: 32, marginBottom: 8 }}>📂</div>
          <div style={{ fontWeight: 600, fontSize: 14, color: "var(--text)" }}>
            {selectedFile ? selectedFile.name : "Click để chọn file"}
          </div>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>
            {selectedFile ? `${(selectedFile.size / 1024).toFixed(1)} KB` : "Hỗ trợ PDF, TXT, DOCX, ..."}
          </div>
        </div>

        <div style={{ marginTop: 14, display: "flex", gap: 10, alignItems: "center" }}>
          <button
            className="button"
            onClick={handleUploadAndIngest}
            disabled={uploading || !selectedFile}
          >
            {uploading ? "⏳ Đang xử lý..." : "⬆️ Upload & Ingest"}
          </button>
          {selectedFile && (
            <button
              className="button secondary"
              onClick={() => { setSelectedFile(null); if (fileInputRef.current) fileInputRef.current.value = ""; }}
            >
              Hủy
            </button>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-head" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>📚 Danh sách tài liệu</span>
          <button className="button secondary" onClick={loadDocuments} disabled={loadingList} style={{ fontSize: 12, padding: "5px 10px" }}>
            {loadingList ? "⏳" : "🔄 Làm mới"}
          </button>
        </div>

        {loadingList ? (
          <div className="empty">Đang tải danh sách...</div>
        ) : documents.length === 0 ? (
          <div className="empty">Chưa có tài liệu nào. Hãy upload file đầu tiên!</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Doc ID</th>
                  <th>File name</th>
                  <th>Status</th>
                  <th>Source</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => {
                  const meta = doc.doc_metadata || {};
                  return (
                    <tr key={doc.doc_id}>
                      <td><span style={{ fontFamily: "monospace", fontSize: 11, color: "var(--text-faint)" }}>{doc.doc_id?.slice(0, 16)}…</span></td>
                      <td style={{ fontWeight: 600 }}>{meta.file_name || "—"}</td>
                      <td><StatusBadge status={meta.status} /></td>
                      <td style={{ color: "var(--text-muted)" }}>{meta.source || "—"}</td>
                      <td>
                        <button className="button secondary" style={{ fontSize: 12, padding: "5px 10px" }} onClick={() => handleIngest(doc.doc_id)}>
                          🔄 Ingest lại
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
