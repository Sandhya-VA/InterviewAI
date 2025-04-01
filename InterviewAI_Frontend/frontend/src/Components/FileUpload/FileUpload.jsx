
import React, { useState, useRef } from 'react';
import { useNavigate } from "react-router-dom";

const FileUpload = ({ setSkills }) => {
  const navigate = useNavigate();
  const [fileName, setFileName] = useState("");
  const [uploadStatus, setUploadStatus] = useState(""); // To show success/error message
  const fileInputRef = useRef(null);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];

    if (file) {
      setFileName(file.name);

      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await fetch("http://127.0.0.1:5000/upload_resume", {
          method: "POST",
          body: formData,
        });

        const result = await response.json();
        if (response.ok) {
          setUploadStatus(result.message);
          setSkills(["Python", "JS", "SQL", "Docker", "Kubernetes", "AWS"]);
          navigate("/tiles");
        } else {
          setUploadStatus(result.error);
        }
      } catch (error) {
        setUploadStatus("Failed to upload file");
      }
    }
  };

  return (
    <div className="btn-container">
      <input
        type="file"
        ref={fileInputRef}
        style={{ display: "none" }}
        onChange={handleFileChange}
      />
      <button className="btn" onClick={() => fileInputRef.current.click()}>
        <span>Upload File</span>
      </button>
      {fileName && <p>Selected File: {fileName}</p>}
      {uploadStatus && <p>{uploadStatus}</p>}
    </div>
  );
};

export default FileUpload;
