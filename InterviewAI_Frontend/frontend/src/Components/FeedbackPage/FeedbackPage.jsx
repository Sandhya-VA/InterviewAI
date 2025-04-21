import React from "react";
import "./FeedbackPage.css";

const FeedbackPage = ({ feedback, selectedSkill }) => {
  if (!feedback) {
    return <div className="loader">🔄 Generating feedback...</div>;
  }

  return (
    <div className="results">
      <h2>Feedback Summary for {selectedSkill}</h2>
      {feedback.evaluations.map((item, i) => (
        <div key={i} className="feedback-tile">
          <p><strong>Q:</strong> {item.question}</p>
          <p><strong>Your Answer:</strong> {item.answer}</p>
          <p><strong>Score:</strong> {item.score}/10</p>
          <p><strong>Feedback:</strong> {item.feedback}</p>
        </div>
      ))}
      <h3>Overall Score: {feedback.overall_score}/10</h3>
      <p><strong>Summary:</strong> {feedback.overall_feedback}</p>
    </div>
  );
};

export default FeedbackPage;
