document.addEventListener('DOMContentLoaded', () => {
    const btnMp4 = document.getElementById('btn-mp4');
    const btnMp3 = document.getElementById('btn-mp3');
    const formatToggle = document.querySelector('.format-toggle');
    const convertBtn = document.getElementById('convert-btn');
    const urlInput = document.getElementById('video-url');
    const loader = document.getElementById('loader');
    const errorMsg = document.getElementById('error-msg');

    let currentFormat = 'mp4'; // Default format

    // ── Format toggle ──────────────────────────────────────────────────────────
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

    // ── URL validation ─────────────────────────────────────────────────────────
    const ytRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|shorts\/|embed\/)|youtu\.be\/).+/i;

    // ── Convert button ─────────────────────────────────────────────────────────
    convertBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();

        hideError();

        if (!url) {
            showError('⚠️ Please paste a YouTube URL first.');
            return;
        }

        if (!ytRegex.test(url)) {
            showError('⚠️ Please enter a valid YouTube URL (e.g. https://www.youtube.com/watch?v=...)');
            return;
        }

        // Show loading state
        loader.style.display = 'flex';
        convertBtn.disabled = true;
        convertBtn.textContent = 'Converting…';
        urlInput.disabled = true;

        try {
            // Use a relative path — works both locally and when served by Flask
            const apiUrl = `/api/download?url=${encodeURIComponent(url)}&format=${currentFormat}`;

            const response = await fetch(apiUrl, { method: 'GET' });

            if (!response.ok) {
                // Parse JSON error from our Flask server
                let errText = 'Conversion failed. Please try again.';
                try {
                    const data = await response.json();
                    // Flask server returns { "error": "..." }
                    if (data.error) errText = data.error;
                } catch (_) { /* ignore JSON parse errors */ }
                throw new Error(errText);
            }

            // ── Trigger file download ────────────────────────────────────────
            let filename = `converted_video.${currentFormat}`;
            const disposition = response.headers.get('content-disposition');
            if (disposition) {
                // Match both quoted and unquoted filenames
                const match = disposition.match(/filename[^;=\n]*=["']?([^"';\n]+)["']?/i);
                if (match && match[1]) {
                    filename = match[1].trim();
                }
            }

            const blob = await response.blob();
            const downloadUrl = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            URL.revokeObjectURL(downloadUrl);
            document.body.removeChild(a);

            // Reset UI on success
            resetUI();
            urlInput.value = '';

        } catch (err) {
            showError(err.message || '❌ An unexpected error occurred. Is the server running?');
            resetUI();
        }
    });

    // ── Helpers ────────────────────────────────────────────────────────────────
    function resetUI() {
        loader.style.display = 'none';
        convertBtn.disabled = false;
        convertBtn.textContent = 'Convert';
        urlInput.disabled = false;
    }

    function showError(msg) {
        errorMsg.textContent = msg;
        errorMsg.style.display = 'block';
    }

    function hideError() {
        errorMsg.style.display = 'none';
        errorMsg.textContent = '';
    }
});
