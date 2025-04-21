import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './FileUpload.css';

const FileUpload = ({ setSkills, setQuestions }) => {
  const navigate = useNavigate();
  const [fileName, setFileName] = useState('');
  const [uploadStatus, setUploadStatus] = useState('');
  const fileInputRef = useRef(null);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setFileName(file.name);
    setUploadStatus('Uploading and processing resume...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://127.0.0.1:5000/upload_resume', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        const skills = result.skills || [];
        const questions = result.questions || {};

        setSkills(skills);
        setQuestions(questions);

        localStorage.setItem("skills", JSON.stringify(skills));
        localStorage.setItem("questions", JSON.stringify(questions));

        setUploadStatus('✅ Resume processed. Redirecting...');
        navigate('/tiles');
      } else {
        setUploadStatus(result.error || '⚠️ Server error. Please try again.');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus('❌ Failed to upload resume.');
    }
  };

  return (
    <div className="btn-container">
      <input
        type="file"
        accept="application/pdf"
        ref={fileInputRef}
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />
      <button className="upload-btn" onClick={() => fileInputRef.current.click()}>
        📄 Upload Resume
      </button>

      {fileName && <p className="file-label">Selected File: <strong>{fileName}</strong></p>}
      {uploadStatus && <p className="upload-status">{uploadStatus}</p>}
    </div>
  );
};

export default FileUpload;
