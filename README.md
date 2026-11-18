# AI Excel Dashboard

Upload an Excel or CSV file and get a plain-language summary, alerts, charts and a
downloadable report. Built for people who never open Excel or have no time for it.

## What it does

- **Business Dashboard**: matches your columns automatically (English or Spanish names),
  tidies the data, compares the latest period with the one before, raises alerts
  (a product stopped selling, a region dropped, an unusual day) and draws charts.
- **Generic Dashboard**: works with any dataset, whatever the columns are.
- **Reports**: download a web page or PDF report, and the tidied data as CSV.
- **AI explanations (optional)**: a local AI reads the calculated numbers and explains them
  in plain words. Every number comes from Python, never from the AI.

No file? Click **Try it with sample data**.

## Run it on your computer

Needs Python 3.12 or newer.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m streamlit run app.py
```

Then open http://localhost:8501.

## Turn on the AI explanations (free, runs on your computer)

1. Install [Ollama](https://ollama.com).
2. Download a model once: `ollama pull qwen3:1.7b`
3. Start the app as above. The **Explain with AI** button appears when Ollama is running.

For better answers use a bigger model, for example `ollama pull qwen3:4b`, and start the app with:

```bash
OLLAMA_MODEL=qwen3:4b python -m streamlit run app.py      # Windows (PowerShell): $env:OLLAMA_MODEL="qwen3:4b"
```

Settings you can change with environment variables: `OLLAMA_MODEL` (default `qwen3:1.7b`)
and `OLLAMA_URL` (default `http://localhost:11434`).

On the public website the AI button is hidden, because the AI program runs on your own
computer. Everything else works there.

## Publish it (free) on Streamlit Community Cloud

1. Put this folder on GitHub (keep `app.py` in the root of the repository).
2. Go to https://share.streamlit.io and click **Create app**.
3. Choose your repository, the branch (`main`) and the main file (`app.py`).
4. In **Advanced settings** pick a Python version (3.12 or newer).
5. Click **Deploy**. When you push changes to GitHub the app updates.

If the deploy log shows `ModuleNotFoundError: No module named 'xyz'`, add `xyz` to `requirements.txt`.

## Privacy and safety (free test version)

- Uploaded files are processed in memory during your visit. This app does not save them
  or write them to a database. The website host (Streamlit Community Cloud) runs the
  server, so do not upload data you are not allowed to share.
- Columns that look like personal data (emails, phones, addresses, ID numbers, people's
  names) are flagged and, by default, removed before analysis. Please do not upload
  personal data.
- Limits protect the free server: files up to 25 MB, up to 100,000 rows and 200 columns.
  Excel files that unpack to something huge are refused. Change the upload size in
  `.streamlit/config.toml`.
- Downloaded CSV files are made safe for Excel: text that would run as a formula
  (starting with `=`, `+`, `-` or `@`) gets an apostrophe in front.
- Text from uploaded files that goes into the AI prompt (names of products, regions...)
  is flattened to one short plain line, so it cannot add instructions of its own.
- Never put API keys or passwords in the code. Use the host's secrets settings.

Not legal advice: if you collect or process other people's personal data, check the
rules that apply to you (in Colombia, Ley 1581 de 2012) and write a privacy policy.

## Project layout

```
app.py                      page selector (Business, Generic, classic)
src/business/               Business Dashboard: engine, page, report, sample data
src/generic/                Generic Dashboard: analysis, page, AI insights
src/ai/                     local AI connection, prompt, validation
src/security/               upload limits, safe downloads, personal-data checks
src/data/                   reading, validating and cleaning for the classic page
.streamlit/config.toml      upload size limit
requirements.txt            packages to install
```
# Ai-excel
# Ai-excel
