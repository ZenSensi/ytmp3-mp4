document.addEventListener('DOMContentLoaded', () => {
    const btnMp4 = document.getElementById('btn-mp4');
    const btnMp3 = document.getElementById('btn-mp3');
    const formatToggle = document.querySelector('.format-toggle');
    const convertBtn = document.getElementById('convert-btn');
    const urlInput = document.getElementById('video-url');
    const loader = document.getElementById('loader');
    const errorMsg = document.getElementById('error-msg');

    let currentFormat = 'mp4'; // Default format

    // Format selection logic
    btnMp4.addEventListener('click', () => {
        formatToggle.classList.remove('mp3-active');
        btnMp4.classList.add('active');
        btnMp3.classList.remove('active');
        currentFormat = 'mp4';
    });

    btnMp3.addEventListener('click', () => {
        formatToggle.classList.add('mp3-active');
        btnMp3.classList.add('active');
        btnMp4.classList.remove('active');
        currentFormat = 'mp3';
    });

    // YouTube URL Validation Regex
    const ytRegex = /^(https?:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$/;

    convertBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();

        // Basic validation
        if (!url) {
            showError('Please enter a YouTube URL.');
            return;
        }

        if (!ytRegex.test(url)) {
            showError('Please enter a valid YouTube URL format.');
            return;
        }

        // Hide error and show loader
        errorMsg.style.display = 'none';
        loader.style.display = 'flex';
        convertBtn.disabled = true;
        urlInput.disabled = true;

        try {
            // We'll call our backend service
            // Expecting an endpoint like GET /api/download?url=...&format=mp4
            const response = await fetch(`http://localhost:8000/api/download?url=${encodeURIComponent(url)}&format=${currentFormat}`, {
                method: 'GET'
            });

            if (!response.ok) {
                let errText = 'Failed to convert video.';
                try {
                    const errorData = await response.json();
                    if (errorData.detail) errText = errorData.detail;
                } catch (e) { }

                throw new Error(errText);
            }

            // Extract filename from headers if possible
            let filename = `converted_video.${currentFormat}`;
            const disposition = response.headers.get('content-disposition');
            if (disposition && disposition.includes('attachment')) {
                const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                const matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) {
                    filename = matches[1].replace(/['"]/g, '');
                }
            }

            // Trigger file download
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(downloadUrl);
            document.body.removeChild(a);

            // Reset UI
            loader.style.display = 'none';
            convertBtn.disabled = false;
            urlInput.disabled = false;
            urlInput.value = '';

        } catch (error) {
            showError(error.message || 'An error occurred during conversion.');
            loader.style.display = 'none';
            convertBtn.disabled = false;
            urlInput.disabled = false;
        }
    });

    function showError(message) {
        errorMsg.textContent = message;
        errorMsg.style.display = 'block';
    }
});
