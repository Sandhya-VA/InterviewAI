import React from 'react'
import HeroPage from './Components/HeroPage/HeroPage'
import FileUpload from './Components/FileUpload/FileUpload'
import Tiles from './Components/Tiles/Tiles'
import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import { useState,useEffect } from 'react';
import QuestionsPage from './Components/QuestionsPage/QuestionsPage';

const App = () => {
  // const skills=['Python','JS','SQL','Docker','Kubernetes']
  const [skills, setSkills] = useState(() => {
    return JSON.parse(localStorage.getItem("skills")) || [];
  });

  useEffect(() => {
    localStorage.setItem("skills", JSON.stringify(skills));
  }, [skills]);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<HeroPage setSkills={setSkills} />} />
        <Route path="/tiles" element={<Tiles skills={skills} />} />
        <Route path="/tiles/questions" element={<QuestionsPage/>} />
        {/* </Route> */}
      </Routes>
    </Router>
  )
}

export default App
