<!DOCTYPE html>
<html lang="en">

<body>
  <h1>YouTube Live Data Fetcher 📹</h1>

  <p>This script fetches live YouTube video data from specified channel IDs, uploads the data to Google Cloud Storage (GCS), and loads it into BigQuery for analysis.</p>

  <h2>Setup ⚙️</h2>

  <ol>
    <li>Install dependencies:</li>
    <pre><code>pip install -r requirements.txt</code></pre>

    <li>Obtain API key from Google Cloud Console and update <code>config.json</code>.</li>

    <li>Set up Google Cloud credentials:</li>
    <ul>
      <li>Download service account credentials JSON file and update <code>config.json</code> with the file path.</li>
    </ul>
  </ol>

  <h2>Usage ▶️</h2>

  <p>Run the script <code>main.py</code> to fetch live video data, upload CSV files to GCS, and load data into BigQuery.</p>

  <pre><code>python main.py</code></pre>

  <p>If running on Google Cloud Functions with Pub/Sub, ensure the appropriate changes are made for the Pub/Sub trigger.</p>

  <p>If running locally in Python, remove the Pub/Sub trigger and event handling.</p>

  <h3>Example Script (main.py)</h3>

  <pre><code> <!-- Your Python script content here --> </code></pre>

  <h2>Notes 📝</h2>

  <ul>
    <li>Ensure proper setup of API key, credentials, and configuration variables in <code>config.json</code>.</li>
    <li>Make sure your environment has necessary permissions to access Google Cloud services.</li>
    <li>Make sure your Big Query Schema mathces the one in the code.</li>
    <li>Make sure your PubSub, BigQuery and Cloud Storage are in the same region server.</li>
    <li>In order to fetch data regarding likes, comments, etc. View the Youtube API V3 Documentation</li>
  
    
  </ul>

  <h2>.gitignore 🔒</h2>

  <p>Ignore credentials JSON file:</p>

  <pre><code>your_google_application_credentials.json</code></pre>

  <p>Ignore temporary files:</p>

  <pre><code>*.csv</code></pre>

  <h2>Directory Structure 📂</h2>

  <pre><code>
main.py
config.json
requirements.txt
README.md
.gitignore
  </code></pre>

  <p>This setup will help you organize your project on GitHub effectively, making it clear and easy for others to understand and use your YouTube live data fetching script with Google Cloud services. Adjust paths and configurations as per your actual project setup before committing to GitHub.</p>

  <h2>License ⚖️</h2>

  <p>This project is licensed under the MIT License - see the <a href="LICENSE">LICENSE</a> file for details.</p>

</body>
</html>
