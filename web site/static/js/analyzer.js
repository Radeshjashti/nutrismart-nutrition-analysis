/**
 * NutriSmart - Food Analyzer Script
 * Handles drag-and-drop file upload, live image previews, WebRTC camera capture,
 * visual loading states, and smooth auto-scrolling to results.
 */

document.addEventListener('DOMContentLoaded', function() {
    const dropzone = document.getElementById('dropzoneArea');
    const fileInput = document.getElementById('foodImageInput');
    const defaultState = document.getElementById('dropzoneDefaultState');
    const previewState = document.getElementById('dropzonePreviewState');
    const imagePreview = document.getElementById('imagePreview');
    const fileNameDisplay = document.getElementById('imageFileName');
    const form = document.getElementById('imageUploadForm');
    const analyzeBtn = document.getElementById('analyzeBtn');

    // Camera elements
    const startCameraBtn = document.getElementById('startCameraBtn');
    const stopCameraBtn = document.getElementById('stopCameraBtn');
    const captureBtn = document.getElementById('capturePhotoBtn');
    const cameraSection = document.getElementById('cameraSection');
    const videoElem = document.getElementById('cameraVideo');
    let videoStream = null;

    // 1. Drag & Drop Handling
    if (dropzone && fileInput) {
        dropzone.addEventListener('dragenter', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
            if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                handleFileSelect(e.dataTransfer.files);
            }
        });

        // Click on dropzone opens file dialog if not clicking input directly
        dropzone.addEventListener('click', function(e) {
            if (e.target !== fileInput) {
                fileInput.click();
            }
        });

        // File selected handler
        fileInput.addEventListener('change', function() {
            handleFileSelect(this.files);
        });
    }

    function handleFileSelect(files) {
        if (!files || files.length === 0) return;
        const file = files[0];

        if (!file.type.match('image.*')) {
            alert('Please select a valid image file (JPG, PNG, or WEBP).');
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            fileNameDisplay.textContent = file.name + ' (' + (file.size / 1024).toFixed(1) + ' KB)';
            defaultState.classList.add('d-none');
            previewState.classList.remove('d-none');
        };
        reader.readAsDataURL(file);
    }

    // 2. WebRTC Live Camera Integration
    if (startCameraBtn && videoElem) {
        startCameraBtn.addEventListener('click', async function() {
            try {
                if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                    videoStream = await navigator.mediaDevices.getUserMedia({ 
                        video: { facingMode: 'environment', width: { ideal: 640 }, height: { ideal: 480 } } 
                    });
                    videoElem.srcObject = videoStream;
                    videoElem.play();
                    cameraSection.classList.remove('d-none');
                    dropzone.classList.add('d-none');
                    startCameraBtn.classList.add('d-none');
                } else {
                    alert('Camera access is not supported by your browser or environment.');
                }
            } catch (err) {
                console.error("Camera access error:", err);
                alert('Could not access camera. Please ensure camera permissions are allowed in your browser.');
            }
        });
    }

    if (stopCameraBtn && videoElem) {
        stopCameraBtn.addEventListener('click', function() {
            if (videoStream) {
                videoStream.getTracks().forEach(track => track.stop());
                videoStream = null;
            }
            cameraSection.classList.add('d-none');
            dropzone.classList.remove('d-none');
            startCameraBtn.classList.remove('d-none');
        });
    }

    if (captureBtn && videoElem) {
        captureBtn.addEventListener('click', function() {
            const canvas = document.createElement('canvas');
            canvas.width = videoElem.videoWidth || 640;
            canvas.height = videoElem.videoHeight || 480;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(videoElem, 0, 0, canvas.width, canvas.height);

            canvas.toBlob(function(blob) {
                const file = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
                
                // Set file to input using DataTransfer
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                fileInput.files = dataTransfer.files;

                // Stop camera
                if (videoStream) {
                    videoStream.getTracks().forEach(track => track.stop());
                    videoStream = null;
                }
                cameraSection.classList.add('d-none');
                dropzone.classList.remove('d-none');
                startCameraBtn.classList.remove('d-none');

                // Update preview
                imagePreview.src = canvas.toDataURL('image/jpeg');
                fileNameDisplay.textContent = "Live Camera Capture (" + (file.size / 1024).toFixed(1) + " KB)";
                defaultState.classList.add('d-none');
                previewState.classList.remove('d-none');
            }, 'image/jpeg');
        });
    }

    // 3. Form Submission Handling with Feedback
    if (form && analyzeBtn) {
        form.addEventListener('submit', function(e) {
            if (!fileInput.files || fileInput.files.length === 0) {
                e.preventDefault();
                alert('Please choose or snap a food photo before clicking Analyze Image.');
                return;
            }
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span> Analyzing Food Image with AI...';
        });
    }

    // 4. Smooth Auto-Scroll to Results if analysis was returned
    const resultSection = document.getElementById('analysisResultsSection');
    if (resultSection) {
        setTimeout(function() {
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 200);
    }
});
