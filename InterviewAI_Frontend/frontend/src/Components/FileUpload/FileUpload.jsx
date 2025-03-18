import React, { useState,useRef } from 'react'
import { useNavigate } from "react-router-dom";

const FileUpload = ({setSkills}) => {
  const navigate = useNavigate();
    const [fileName,setFileName]=useState("")
    const fileInputRef=useRef(null)
    const handleFileChange=(event)=>{
        const file= event.target.files[0]
        if(file){
            setFileName(file.name)
            const newSkills=['Python','JS','SQL','Docker','Kubernetes','AWS']
            setSkills(newSkills)
            navigate("/tiles")
        }
    }
  return (
    <div className="btn-container">
        <input
        type="file"
        ref={fileInputRef}
        style={{display:"none"}}
        onChange={handleFileChange}
        />
        <button className="btn" onClick={() => fileInputRef.current.click()}> <span>Upload File</span>

        </button>
        {fileName && <p>Selected File: {fileName}</p>}
    </div>
  )
}

export default FileUpload
