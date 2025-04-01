import React, { useState, useRef, useEffect } from "react";
import RecordRTC from "recordrtc";

const AudioRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [recorder, setRecorder] = useState(null);
  const videoRef = useRef(null); 
  const [stream, setStream] = useState(null); 


  useEffect(() => {
    const startStream = async () => {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
        setStream(mediaStream);
        

        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
      } catch (error) {
        console.error("Error accessing media devices", error);
      }
    };

    startStream();


    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);


  const startRecording = async () => {
    if (stream) {
      const recorderInstance = new RecordRTC(stream, {
        type: "audio",
        mimeType: "audio/wav", 
        recorderType: RecordRTC.StereoAudioRecorder,
      });

      recorderInstance.startRecording();
      setRecorder(recorderInstance);
      setIsRecording(true);
    }
  };

  const stopRecording = () => {
    if (recorder) {
      recorder.stopRecording(() => {
        setIsRecording(false);
        const audioBlob = recorder.getBlob();
        const audioUrl = URL.createObjectURL(audioBlob);
        setAudioUrl(audioUrl);

  
        uploadAudio(audioBlob);
      });
    }
  };


  const uploadAudio = async (blob) => {
    if (!blob) {
      console.warn("No audio blob available for upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", blob, "recorded_audio.wav");

    try {
      const response = await fetch("http://localhost:5000/upload_audio", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        console.log(result.message);
      } else {
        console.error(result.error);
      }
    } catch (error) {
      console.error("Upload failed:", error);
    }
  };

  const downloadAudio = () => {
    if (audioUrl) {
      const a = document.createElement("a");
      a.href = audioUrl;
      a.download = "test_recording.wav";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  return (
    <div>
      <h2>Audio Recorder</h2>
      <button onClick={startRecording} disabled={isRecording}>
        Start Recording
      </button>
      <button onClick={stopRecording} disabled={!isRecording}>
        Stop Recording
      </button>
      <button onClick={downloadAudio} disabled={!audioUrl}>
        Download Audio
      </button>

      <div>
        <h3>Video Feed</h3>
        <video ref={videoRef} autoPlay muted width="320" height="240" />
      </div>

      {/* {audioUrl && (
        <div>
          <h3>Recorded Audio</h3>
          <audio controls src={audioUrl} />
        </div>
      )} */}
    </div>
  );
};

export default AudioRecorder;
