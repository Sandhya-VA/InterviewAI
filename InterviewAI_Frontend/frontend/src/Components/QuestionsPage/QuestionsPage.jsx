import React, { useState, useEffect, useRef } from "react";
import RecordRTC from "recordrtc";
import "./QuestionsPage.css";
import FeedbackPage from "../FeedbackPage/FeedbackPage";

const QuestionsPage = ({ selectedSkill, questions }) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [isPreparing, setIsPreparing] = useState(true);
  const [prepSecondsLeft, setPrepSecondsLeft] = useState(20);
  const [isRecording, setIsRecording] = useState(false);
  const [recordSecondsLeft, setRecordSecondsLeft] = useState(90);
  const [recorder, setRecorder] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [stream, setStream] = useState(null);

  const videoRef = useRef(null);
  const recordTimerRef = useRef(null);
  const currentQuestion = questions[currentQuestionIndex];

  // Initialize media stream (audio + dummy video)
  useEffect(() => {
    const initMedia = async () => {
      try {
        const media = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        setStream(media);
        if (videoRef.current) {
          videoRef.current.srcObject = media;
        }
      } catch (err) {
        console.error("Media access error:", err);
      }
    };
    initMedia();

    return () => {
      if (stream) stream.getTracks().forEach((track) => track.stop());
      clearInterval(recordTimerRef.current);
    };
  }, []);

  // Prep countdown
  useEffect(() => {
    if (isPreparing) {
      const interval = setInterval(() => {
        setPrepSecondsLeft((prev) => {
          if (prev <= 1) {
            clearInterval(interval);
            setIsPreparing(false);
            return 20;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [isPreparing]);

  // Start recording when prep ends and stream is ready
  useEffect(() => {
    if (!isPreparing && stream && !isRecording) {
      startRecording();
    }
  }, [isPreparing, stream]);

  // Recording countdown
  useEffect(() => {
    if (isRecording) {
      recordTimerRef.current = setInterval(() => {
        setRecordSecondsLeft((prev) => {
          if (prev <= 1) {
            clearInterval(recordTimerRef.current);
            stopRecording();
            return 90;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => clearInterval(recordTimerRef.current);
  }, [isRecording]);

  const startRecording = () => {
    try {
      if (stream) {
        const audioOnlyStream = new MediaStream(stream.getAudioTracks());
        const recorderInstance = new RecordRTC(audioOnlyStream, {
          type: "audio",
          mimeType: "audio/webm",
        });
  
        recorderInstance.startRecording();
        setRecorder(recorderInstance);
        setIsRecording(true);
        console.log("🎙️ Recording started.");
      } else {
        console.warn("⚠️ No stream available.");
      }
    } catch (err) {
      console.error("Failed to start recorder:", err);
    }
  };
  
  

  const stopRecording = () => {
    if (!recorder || recorder.getState() !== "recording") {
      console.warn("⚠️ Recorder state should be 'recording', however current state is:", recorder?.getState());
      return;
    }
  
    console.log("🛑 Stopping recording...");
    recorder.stopRecording(() => {
      setIsRecording(false);
      const blob = recorder.getBlob();
  
      uploadAudio(blob, currentQuestionIndex, currentQuestion).then(() => {
        if (currentQuestionIndex < questions.length - 1) {
          setCurrentQuestionIndex((prev) => prev + 1);
          setIsPreparing(true);
          setPrepSecondsLeft(20);
          setRecordSecondsLeft(90);
        } else {
          handleSubmitForEvaluation();
          if (stream) {
            stream.getTracks().forEach((track) => track.stop());
            setStream(null);
          }
        }
      });      
    });
  };
  

  const uploadAudio = async (blob, questionIndex, questionText) => {
    const formData = new FormData();
    formData.append("file", blob, `question_${questionIndex + 1}.webm`);
  
    try {
      const res = await fetch("http://127.0.0.1:5000/upload_audio", {
        method: "POST",
        body: formData,
      });
      const result = await res.json();
      if (res.ok) {
        setAnswers((prev) => ({
          ...prev,
          [questionIndex]: {
            question: typeof questionText === "string"
              ? questionText
              : questionText?.question || JSON.stringify(questionText),
            answer: result.transcription,
          },
        }));
      } else {
        console.error("Transcription error:", result.error);
      }
    } catch (err) {
      console.error("Audio upload failed:", err);
    }
  };
  

  const handleSubmitForEvaluation = async () => {
    const responsePayload = Object.values(answers).filter(
      (r) => r.answer && r.answer.trim().length > 0
    );
  
    if (responsePayload.length === 0) {
      console.warn("🚫 No valid responses to evaluate.");
      return;
    }
  
    try {
      const res = await fetch("http://127.0.0.1:5000/evaluate_answers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ responses: responsePayload }),
      });
      const result = await res.json();
      if (res.ok) {
        setFeedback(result);
      } else {
        console.error("Evaluation failed", result.error);
      }
    } catch (err) {
      console.error("Error during evaluation:", err);
    }
  };
  

  if (feedback) {
    return <FeedbackPage feedback={feedback} selectedSkill={selectedSkill} />;
  }

  return (
    <div className="interview-layout">
      <div className="question-panel">
        <h3>Skill: {selectedSkill || "Unknown Skill"}</h3>
        <div className="question-box">
          <p><strong>Question {currentQuestionIndex + 1} of {questions.length}:</strong></p>
          <p>{typeof currentQuestion === "string" ? currentQuestion : currentQuestion?.question}</p>
        </div>
      </div>

      <div className="record-panel">
        <video ref={videoRef} autoPlay muted className="video-preview" />
        {isPreparing ? (
          <div className="timer-label big">🕒 Prepare: {prepSecondsLeft}s</div>
        ) : isRecording ? (
          <>
            <div className="timer-label big recording">🔴 Recording: {recordSecondsLeft}s</div>
            <button className="stop-button" onClick={stopRecording}>Stop</button>
          </>
        ) : null}
      </div>
    </div>
  );
};

export default QuestionsPage;
