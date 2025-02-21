// Save settings to the backend
function saveSettings() {
  const form = document.getElementById('settings-form');
  const data = {
    log: form.log.checked,
    print_terminal: form.print_terminal.checked,
    detection_logging: form.detection_logging.checked,
    server_address: form.server_address.value,
    robot_position_key: form.robot_position_key.value,
    robot_rotation_key: form.robot_rotation_key.value,
    input_size: parseInt(form.input_size.value),
    confidence_threshold: parseFloat(form.confidence_threshold.value),
    note_combined_threshold: parseInt(form.note_combined_threshold.value),
    hostname: form.hostname.value,
  };

  fetch('/update_settings', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(result => {
    if (result.status === 'success') {
      addLogMessage('Settings saved successfully!');
    } else {
      addLogMessage('Error saving settings: ' + result.message);
    }
  })
  .catch(error => {
    console.error('Error:', error);
    addLogMessage('An error occurred while saving settings.');
  });
}

// Append messages to the log terminal
function addLogMessage(message) {
  const logTerminal = document.getElementById('logTerminal');
  const timestamp = new Date().toLocaleTimeString();
  const newMessage = document.createElement('div');
  newMessage.textContent = `[${timestamp}] ${message}`;
  logTerminal.appendChild(newMessage);
  // Auto-scroll to the bottom
  logTerminal.scrollTop = logTerminal.scrollHeight;
}

// Subscribe to the log stream from the Python backend via Server-Sent Events
function subscribeToLogs() {
  const eventSource = new EventSource('/log_stream');
  eventSource.onmessage = (event) => {
    addLogMessage(event.data);
  };
  eventSource.onerror = (error) => {
    console.error('EventSource failed:', error);
    eventSource.close();
    setTimeout(subscribeToLogs, 5000);
  };
}

// Fetch available cameras and update the video feeds dynamically
function updateCameraFeeds() {
  fetch('/available_cameras')
    .then(response => response.json())
    .then(cameraNames => {
      const cameraContainer = document.getElementById('cameraContainer');
      cameraContainer.innerHTML = ''; // Clear existing feeds

      if (cameraNames.length === 0) {
        addLogMessage('No cameras detected.');
        return;
      }

      cameraNames.forEach(cameraName => {
        const cameraElement = document.createElement('div');
        cameraElement.classList.add('camera-feed');

        const title = document.createElement('h3');
        title.textContent = cameraName.replace('_', ' ').toUpperCase();

        const videoFeed = document.createElement('img');
        videoFeed.src = `/video_feed/${cameraName}`;
        videoFeed.alt = `${cameraName} feed`;
        videoFeed.classList.add('camera-stream');

        cameraElement.appendChild(title);
        cameraElement.appendChild(videoFeed);
        cameraContainer.appendChild(cameraElement);
      });

      // addLogMessage('Camera feeds updated.');
    })
    .catch(error => {
      console.error('Error fetching camera feeds:', error);
      addLogMessage('Failed to fetch camera feeds.');
    });
}

// Start log subscription and camera feed update on page load
document.addEventListener('DOMContentLoaded', () => {
  addLogMessage('Welcome to the Eagle Eye Interface.');
  subscribeToLogs();
  updateCameraFeeds();

  // Refresh camera feeds every 5 seconds in case of new connections
  setInterval(updateCameraFeeds, 5000);
});
