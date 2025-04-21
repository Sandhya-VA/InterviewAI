import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import HeroPage from './Components/HeroPage/HeroPage';
import Tiles from './Components/Tiles/Tiles';
import QuestionsPage from './Components/QuestionsPage/QuestionsPage';

const App = () => {
  const [skills, setSkills] = useState([]); // Start with fresh empty list
  const [questionsBySkill, setQuestionsBySkill] = useState({});
  const [selectedSkill, setSelectedSkill] = useState(null);

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            <HeroPage
              setSkills={(skills) => {
                setSkills(skills);
                localStorage.setItem('skills', JSON.stringify(skills));
              }}
              setQuestions={(questions) => {
                setQuestionsBySkill(questions);
                localStorage.setItem('questions', JSON.stringify(questions));
              }}
            />
          }
        />
        <Route
          path="/tiles"
          element={<Tiles skills={skills} setSelectedSkill={setSelectedSkill} />}
        />
        <Route
          path="/tiles/questions"
          element={
            selectedSkill ? (
              <QuestionsPage
                selectedSkill={selectedSkill}
                questions={questionsBySkill[selectedSkill] || []}
              />
            ) : (
              <Navigate to="/tiles" replace />
            )
          }
        />
      </Routes>
    </Router>
  );
};

export default App;
