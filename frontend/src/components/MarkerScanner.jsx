
import { useEffect, useRef, useState } from "react";
import { API_URL } from "../api";

export default function MarkerScanner({ onDetected }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null); // visible overlay canvas
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [cameraStatus, setCameraStatus] = useState("initializing");
  const [debugInfo, setDebugInfo] = useState("");
  const [stream, setStream] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [lastRawIds, setLastRawIds] = useState([]);
  const [invalidMarkers, setInvalidMarkers] = useState([]);
  const lastResultsRef = useRef([]);

  // Draw a glowing rounded panel with text, inspired by the Python overlay
  const drawNeonPanel = (ctx, x, y, width, height, title, lines) => {
    ctx.save();
    // Backdrop
    ctx.fillStyle = "rgba(15,23,42,0.65)"; // slate-900 with alpha
    ctx.strokeStyle = "#22d3ee"; // cyan-400
    ctx.lineWidth = 2;
    ctx.shadowColor = "rgba(34,211,238,0.85)"; // cyan glow
    ctx.shadowBlur = 18;
    const r = 14;
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + width, y, x + width, y + height, r);
    ctx.arcTo(x + width, y + height, x, y + height, r);
    ctx.arcTo(x, y + height, x, y, r);
    ctx.arcTo(x, y, x + width, y, r);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Title
    ctx.shadowBlur = 0;
    ctx.fillStyle = "#a5f3fc"; // cyan-200
    ctx.font = "bold 20px system-ui, -apple-system, Segoe UI, Roboto, sans-serif";
    ctx.fillText(title, x + 16, y + 28);

    // Divider
    ctx.globalAlpha = 0.25;
    ctx.strokeStyle = "#22d3ee";
    ctx.beginPath();
    ctx.moveTo(x + 14, y + 34);
    ctx.lineTo(x + width - 14, y + 34);
    ctx.stroke();
    ctx.globalAlpha = 1;

    // Lines
    let ty = y + 56;
    ctx.font = "14px system-ui, -apple-system, Segoe UI, Roboto, sans-serif";
    for (const { text, ok } of lines) {
      // status glyph
      ctx.fillStyle = ok ? "#22c55e" : "#ef4444"; // green/red
      ctx.beginPath();
      ctx.arc(x + 18, ty - 10, 6, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = "#e5e7eb"; // gray-200
      ctx.fillText(text, x + 32, ty);
      ty += 24;
    }
    ctx.restore();
  };

  const drawResultsOverlay = (ctx, canvas, results) => {
    if (!results || results.length === 0) return;
    for (const r of results) {
      // Outline on the marker
      if (Array.isArray(r.corners) && r.corners.length === 4) {
        ctx.save();
        ctx.lineWidth = 3;
        ctx.strokeStyle = r.shelf_name === 'Unknown marker' ? '#ef4444' : '#22c55e';
        ctx.beginPath();
        ctx.moveTo(r.corners[0][0], r.corners[0][1]);
        for (let i = 1; i < 4; i++) ctx.lineTo(r.corners[i][0], r.corners[i][1]);
        ctx.closePath();
        ctx.stroke();

        // Place panel near top-left corner, clamped inside canvas
        const anchor = r.corners[0];
        const panelW = Math.min(320, canvas.width * 0.42);
        const baseLines = (r.books || []).slice(0, 4).map(b => ({
          text: `${b.title} — ${b.author}`,
          ok: !!b.available,
        }));
        const title = r.shelf_name && r.shelf_name !== 'Unknown marker' ? r.shelf_name : `❌ Invalid Marker ID: ${r.marker_id}`;
        const panelH = 32 + 12 + Math.max(1, baseLines.length) * 24 + 12;
        let px = anchor[0] + 12;
        let py = anchor[1] - panelH - 12;
        if (px + panelW > canvas.width) px = canvas.width - panelW - 12;
        if (py < 0) py = anchor[1] + 12;
        drawNeonPanel(ctx, px, py, panelW, panelH, title, baseLines.length ? baseLines : [{ text: 'This marker is not registered in the library system', ok: false }]);
        ctx.restore();
      }
    }
  };

  // Debug function to test camera access
  const testCameraAccess = async () => {
    setDebugInfo("Testing camera access...");
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setDebugInfo("❌ getUserMedia not supported");
        return;
      }

      const testStream = await navigator.mediaDevices.getUserMedia({ video: true });
      setDebugInfo("✅ Camera access successful");
      testStream.getTracks().forEach(track => track.stop());
    } catch (e) {
      setDebugInfo(`❌ Camera test failed: ${e.name} - ${e.message}`);
    }
  };

  // Function to capture image and send to backend
  const captureAndDetect = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const overlay = canvasRef.current;
    
    // Ensure overlay size matches video
    overlay.width = video.videoWidth;
    overlay.height = video.videoHeight;
    const ctx = overlay.getContext('2d');
    
    setIsScanning(true);
    setDebugInfo("Processing image...");
    
    try {
      // Capture the current frame to an offscreen canvas for upload
      const capCanvas = document.createElement('canvas');
      capCanvas.width = video.videoWidth;
      capCanvas.height = video.videoHeight;
      capCanvas.getContext('2d').drawImage(video, 0, 0);
      const jpgBlob = await new Promise((resolve) => capCanvas.toBlob(resolve, 'image/jpeg', 0.8));
      if (!jpgBlob) throw new Error('Failed to capture frame');
      const formData = new FormData();
      formData.append('file', jpgBlob, 'capture.jpg');
      
      const response = await fetch(`${API_URL}/detect-marker`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      setLastRawIds(result.raw_marker_ids || []);
      
      // Track invalid markers for notification
      const invalid = (result.results || []).filter(r => r.shelf_name === 'Unknown marker');
      console.log('Debug - All results:', result.results);
      console.log('Debug - Invalid markers found:', invalid);
      setInvalidMarkers(invalid);
      
      setDebugInfo(`✅ Processed: ${result.total_markers_found || 0} markers in frame; ${result.detected_markers} known in DB; ${invalid.length} invalid`);
      
      // Draw richer AR overlay similar to the python script
      // clear overlay and draw
      ctx.clearRect(0, 0, overlay.width, overlay.height);
      drawResultsOverlay(ctx, overlay, result.results || []);
      lastResultsRef.current = result.results || [];

      // If markers detected, call onDetected
      if (result.detected_markers > 0 && result.results.length > 0) {
        const firstMarker = result.results[0];
        onDetected?.(firstMarker.marker_id, firstMarker);
      }
      
    } catch (error) {
      console.error('Detection error:', error);
      setDebugInfo(`❌ Detection failed: ${error.message}`);
    } finally {
      setIsScanning(false);
    }
  };

  // Auto-scan functionality
  useEffect(() => {
    if (!isScanning && stream) {
      const interval = setInterval(() => {
        captureAndDetect();
      }, 2000); // Scan every 2 seconds
      
      return () => clearInterval(interval);
    }
  }, [isScanning, stream]);

  useEffect(() => {
    let currentStream = null;

    async function init() {
      setIsLoading(true);
      setError("");
      setCameraStatus("initializing");
      setDebugInfo("Starting camera initialization...");

      // Check if camera is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError("Camera access is not supported in this browser. Please use a modern browser with camera support.");
        setCameraStatus("camera-not-supported");
        setIsLoading(false);
        setDebugInfo("❌ getUserMedia not supported");
        return;
      }

      setCameraStatus("requesting-camera");
      setDebugInfo("Requesting camera access...");

      try {
        // Try different camera constraints
        const constraints = {
          video: {
            facingMode: "environment", // Prefer back camera
            width: { ideal: 1280, min: 640 },
            height: { ideal: 720, min: 480 }
          },
          audio: false
        };

        currentStream = await navigator.mediaDevices.getUserMedia(constraints);
        setStream(currentStream);
        setDebugInfo("✅ Camera stream obtained");
        
        if (videoRef.current) {
          videoRef.current.srcObject = currentStream;
          
          // Wait for video to be ready
          await new Promise((resolve, reject) => {
            const video = videoRef.current;
            if (!video) {
              reject(new Error("Video element not found"));
              return;
            }

            const onLoadedMetadata = () => {
              video.removeEventListener('loadedmetadata', onLoadedMetadata);
              video.removeEventListener('error', onError);
              resolve();
            };

            const onError = (e) => {
              video.removeEventListener('loadedmetadata', onLoadedMetadata);
              video.removeEventListener('error', onError);
              reject(new Error("Video failed to load"));
            };

            video.addEventListener('loadedmetadata', onLoadedMetadata);
            video.addEventListener('error', onError);
            
            // Start playing
            video.play().catch(reject);
          });

          setCameraStatus("camera-active");
          setIsLoading(false);
          setDebugInfo("✅ Camera ready for scanning");
        }
      } catch (e) {
        console.error("Camera access error:", e);
        setDebugInfo(`❌ Primary camera failed: ${e.name}`);
        
        // Try fallback constraints
        try {
          setCameraStatus("trying-fallback");
          setDebugInfo("Trying fallback camera...");
          const fallbackConstraints = {
            video: true,
            audio: false
          };
          
          currentStream = await navigator.mediaDevices.getUserMedia(fallbackConstraints);
          setStream(currentStream);
          setDebugInfo("✅ Fallback camera successful");
          
          if (videoRef.current) {
            videoRef.current.srcObject = currentStream;
            await videoRef.current.play();
            setCameraStatus("camera-active");
            setIsLoading(false);
            setDebugInfo("✅ Fallback camera ready");
            return;
          }
        } catch (fallbackError) {
          console.error("Fallback camera access failed:", fallbackError);
          setDebugInfo(`❌ Fallback camera failed: ${fallbackError.name}`);
        }

        // Determine specific error
        let errorMessage = "Camera access denied or unavailable.";
        
        if (e.name === "NotAllowedError") {
          errorMessage = "Camera access was denied. Please allow camera access in your browser settings and refresh the page.";
        } else if (e.name === "NotFoundError") {
          errorMessage = "No camera found on this device. Please connect a camera and try again.";
        } else if (e.name === "NotReadableError") {
          errorMessage = "Camera is already in use by another application. Please close other camera apps and try again.";
        } else if (e.name === "OverconstrainedError") {
          errorMessage = "Camera doesn't support the required resolution. Please try a different camera.";
        } else if (e.name === "TypeError") {
          errorMessage = "Camera access is not supported in this browser. Please use HTTPS or localhost.";
        }
        
        setError(errorMessage);
        setCameraStatus("camera-failed");
        setIsLoading(false);
      }
    }

    init();
    return () => {
      if (currentStream) {
        currentStream.getTracks().forEach(track => {
          track.stop();
        });
      }
    };
  }, []);

  return (
    <div className="w-full">
      <div className="rounded-lg overflow-hidden shadow border bg-black relative">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-75 z-10">
            <div className="text-white text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
              <div className="text-sm">
                {cameraStatus === "requesting-camera" && "Requesting camera access..."}
                {cameraStatus === "trying-fallback" && "Trying fallback camera..."}
                {cameraStatus === "camera-active" && "Camera ready"}
              </div>
            </div>
          </div>
        )}
        
        {isScanning && (
          <div className="absolute inset-0 flex items-center justify-center bg-blue-500 bg-opacity-75 z-10">
            <div className="text-white text-center">
              <div className="animate-pulse text-lg font-bold">Scanning...</div>
            </div>
          </div>
        )}
        
        <video 
          ref={videoRef} 
          className="w-full opacity-90" 
          playsInline 
          muted 
          autoPlay
        />
        {/* Make overlay visible above the video */}
        <canvas 
          ref={canvasRef} 
          className="absolute inset-0 w-full h-full pointer-events-none"
        />
      </div>
      
      {/* Debug Information */}
      <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Debug Info:</span>
          <div className="space-x-2">
            <button 
              onClick={testCameraAccess}
              className="px-3 py-1 bg-gray-600 text-white rounded text-xs hover:bg-gray-700"
            >
              Test Camera
            </button>
            <button 
              onClick={captureAndDetect}
              disabled={isScanning}
              className="px-3 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700 disabled:opacity-50"
            >
              {isScanning ? "Scanning..." : "Manual Scan"}
            </button>
          </div>
        </div>
        <p className="text-xs text-gray-600 font-mono">{debugInfo || "No debug info available"}</p>
        {lastRawIds.length > 0 && (
          <p className="text-xs text-blue-700 mt-1">Raw marker IDs in frame: {lastRawIds.join(", ")}</p>
        )}
        {invalidMarkers.length > 0 && (
          <p className="text-xs text-red-700 mt-1">Invalid markers detected: {invalidMarkers.map(m => m.marker_id).join(", ")}</p>
        )}
        <p className="text-xs text-gray-500 mt-1">
          Browser: {navigator.userAgent.includes('Chrome') ? 'Chrome' : navigator.userAgent.includes('Firefox') ? 'Firefox' : navigator.userAgent.includes('Safari') ? 'Safari' : 'Other'} | 
          HTTPS: {window.location.protocol === 'https:' ? 'Yes' : 'No'} | 
          Localhost: {window.location.hostname === 'localhost' ? 'Yes' : 'No'}
        </p>
      </div>
      
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 font-medium mb-2">Camera/Error:</p>
          <p className="text-red-600 text-sm">{error}</p>
          <div className="mt-3 space-x-2">
            <button 
              onClick={() => window.location.reload()} 
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
            >
              Refresh Page
            </button>
            <button 
              onClick={testCameraAccess}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
            >
              Test Camera Access
            </button>
          </div>
        </div>
      )}
      
      {/* Invalid Marker Notifications */}
      {invalidMarkers.length > 0 && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 font-medium mb-2">⚠️ Invalid Markers Detected:</p>
          {invalidMarkers.map((marker, index) => (
            <p key={index} className="text-red-600 text-sm">
              • Marker ID {marker.marker_id} is not registered in the library system
            </p>
          ))}
          <p className="text-red-500 text-xs mt-2">
            Only markers 0, 1, and 2 are currently registered. Please use a valid marker.
          </p>
        </div>
      )}

      {!error && !isLoading && (
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-700 text-sm">
            📱 Point your camera at a 4x4 ArUco marker to scan
          </p>
          <p className="text-blue-600 text-xs mt-1">
            Auto-scanning every 2 seconds • Manual scan available
          </p>
          <p className="text-blue-500 text-xs mt-1">
            Valid markers: 0 (Science Fiction), 1 (Computer Science), 2 (Literature)
          </p>
        </div>
      )}
    </div>
  );
}
