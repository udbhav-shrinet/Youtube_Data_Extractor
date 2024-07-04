<h1>YouTube Live Data Fetcher</h1>

<p>This script fetches live YouTube video data from specified channel IDs, uploads the data to Google Cloud Storage (GCS), and loads it into BigQuery for analysis.</p>

<h2>Setup</h2>

<ol>
  <li>Install dependencies:</li>
  <pre><code>pip install -r requirements.txt</code></pre>
  
  <li>Obtain API key from Google Cloud Console and update <code>config.json</code>.</li>
  
  <li>Set up Google Cloud credentials:
    <ul>
      <li>Download service account credentials JSON file and update <code>config.json</code> with the file path.</li>
    </ul>
  </li>
</ol>

<h2>Usage</h2>

<p>Run the script <code>main.py</code> to fetch live video data, upload CSV files to GCS, and load data into BigQuery.</p>

<pre><code>python main.py</code></pre>

<h2>Notes</h2>

<ul>
  <li>Ensure proper setup of API key, credentials, and configuration variables in <code>config.json</code>.</li>
  <li>Make sure your environment has necessary permissions to access Google Cloud services.</li>
</ul>

<h2>.gitignore</h2>

<pre><code>
# Ignore credentials JSON file
your_google_application_credentials.json

# Ignore temporary files
*.csv
</code></pre>

<h2>Directory Structure</h2>

<ul>
  <li>main.py</li>
  <li>config.json</li>
  <li>requirements.txt</li>
  <li>README.md</li>
  <li>.gitignore</li>
</ul>

<p>This setup will help you organize your project on GitHub effectively, making it clear and easy for others to understand and use your YouTube live data fetching script with Google Cloud services. Adjust paths and configurations as per your actual project setup before committing to GitHub.</p>


<h2>License</h2>

<p>This project is licensed under the MIT License - see the <a href="LICENSE">LICENSE</a> file for details.</p>
