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
- Limits protect the free server: files up to 25 MB, up to 250,000 rows and 200 columns (a notice appears above 100,000 rows). Change them with the `MAX_ROWS` and `MAX_COLUMNS` environment variables, in one place: `src/security/upload_guard.py`.
- Reading and tidying a file is cached for 15 minutes, so clicking around does not redo the slow steps.
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

## Feedback

The sidebar has a "Send feedback" box. Where answers go:

1. **Best for the public site:** set `FEEDBACK_WEBHOOK_URL` (an https address, for example a free Google Apps Script or Formspree form) in Streamlit Cloud under Settings > Secrets:
   ```toml
   FEEDBACK_WEBHOOK_URL = "https://..."
   FEEDBACK_ISSUES_URL = "https://github.com/YOUR_USER/YOUR_REPO/issues"   # optional link
   ```
2. With no webhook, answers are appended to `feedback_data/feedback.jsonl` on the server. On the free Streamlit host this file is erased when the app restarts, so use option 1 there.

Only what the visitor types in the box is saved, never their uploaded data.

## AI on the public website (free online AI)

On your own computer the AI runs with Ollama and nothing leaves your machine. On the public site there is no Ollama, so the app can use a free online AI (Groq) instead, but only if you set a key:

1. Create a free account and an API key at console.groq.com. In its Data Controls you can turn on Zero Data Retention.
2. In Streamlit Cloud open your app > Settings > Secrets and add `GROQ_API_KEY = "..."` (see `.streamlit/secrets.toml.example`). Never put the key in the code or in GitHub.
3. Check your limits in the Groq console (Settings > Limits). Set `GROQ_DAILY_CAP` below your daily allowance. The default is 45 requests a day, 4 per visitor visit, and at most 2 per minute for the whole app. One AI report can use up to 2 requests.

Rules the app follows: Ollama is always used first when it is running; visitors must tick a box agreeing that a summary (totals, group names, alerts and any text they typed, never the file) is sent to the online AI; when a limit is reached the AI button is replaced by a friendly message and the rest of the app keeps working. The daily counter is kept in the server's memory, so it starts again from zero if the app restarts.

## Languages (English / Español)

The sidebar has a language switch. It starts from the visitor's browser language. The Business Dashboard and the Generic Dashboard are in both languages (the "Business (classic)" page is English only). Spanish texts live in `src/locales/es.py`: the English sentence is the key. A text with no Spanish entry just shows in English. When the language is Spanish, numbers use `12.345,67`, dates use `5 mar 2026`, and the AI is asked to write in Spanish.

## Your email in the feedback box

To show "You can also write to us: your@gmail.com" under the feedback form, add it to Streamlit Secrets (not to the code, so it does not sit in your public GitHub repo for spam bots):

```toml
FEEDBACK_EMAIL = "your@gmail.com"
```

## Look and feel

A calm light theme lives in `.streamlit/config.toml` (colours, font), and `src/ui/style.py` adds spacing, rounded cards, the three-step strip ("Add your file, Read the results, Save or share") and hides Streamlit's own menu. The sidebar has two pages: **Sales analysis** and **Any other data**. The old "Business (classic)" page is hidden; set the environment variable `SHOW_CLASSIC=1` to show it again. Advanced settings (cleaning options, column roles, analysis settings) are folded away in "(optional)" boxes, because the app already chooses sensible values.
