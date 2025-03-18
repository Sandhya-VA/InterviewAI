import React, { useEffect, useRef, useState } from 'react';
import { ReactMediaRecorder } from 'react-media-recorder';

const QuestionsPage = () => {
  const videoRef = useRef(null);
  const [stream, setStream] = useState(null);

  // Start camera feed but do not record video
  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then((videoStream) => {
        setStream(videoStream);
        if (videoRef.current) {
          videoRef.current.srcObject = videoStream;
        }
      })
      .catch((error) => console.error("Error accessing camera:", error));

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div>
      {/* Live camera preview (not recorded) */}
      <video ref={videoRef} autoPlay playsInline style={{ width: "300px", height: "auto" }} />

      {/* Audio recording */}
      <ReactMediaRecorder
        audio
        render={({ status, startRecording, stopRecording, mediaBlobUrl }) => (
          <div>
            <p>recoding status: {status}</p>
            <button onClick={startRecording}>Start Recording</button>
            <button onClick={stopRecording}>Stop Recording</button>
            <audio src={mediaBlobUrl} controls />
          </div>
        )}
      />
    </div>
  );
};

export default QuestionsPage;
