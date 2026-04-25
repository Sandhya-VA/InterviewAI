import React from 'react';
import Navbar from '../NavBar/Navbar';
import '../HeroPage/HeroPage.css';
import FileUpload from '../FileUpload/FileUpload';

const HeroPage = ({ setSkills, setQuestions }) => {
  return (
    <div className="hero-container">
      <Navbar />
      <div className="hero-text">
        <h1>Welcome to InterviewAI</h1>
        <p>
          Upload your resume to begin your personalized mock interview experience.
        </p>
        <p>
          We'll extract the technical skills mentioned in your resume and generate
          interview questions for each skill.
        </p>
        <p>
          Practice answering questions through audio, receive real-time feedback, and improve your confidence before the real interview!
        </p>
        <p>
          Ready to get started? Upload your resume now!
        </p>

        <FileUpload setSkills={setSkills} setQuestions={setQuestions} />
      </div>
    </div>
  );
};

export default HeroPage;
