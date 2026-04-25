import React from 'react';
import './Tiles.css';
import { useNavigate } from 'react-router-dom';

const Tiles = ({ skills, setSelectedSkill }) => {
  const navigate = useNavigate();

  const handleClick = (skill) => {
    setSelectedSkill(skill);
    localStorage.setItem("selectedSkill", skill); // store for reload safety
    navigate('/tiles/questions');
  };

  return (
<div className="skill-wrapper">
  <h2>Select a skill to begin your mock interview</h2>

  {skills && skills.length > 0 ? (
    <div className="skill-container">
      {skills.map((skill, index) => (
        <div
          key={index}
          className="skill-tile"
          onClick={() => handleClick(skill)}
        >
          {skill}
        </div>
      ))}
    </div>
  ) : (
    <p className="no-skills">No valid skills found. Please upload a valid resume.</p>
  )}
</div>
  );
};

export default Tiles;
