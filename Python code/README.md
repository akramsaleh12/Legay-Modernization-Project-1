# 💼 Employee Payroll System

A simple payroll management app built with [Streamlit](https://streamlit.io) and SQLite. It lets you add, look up, update, and delete employee payroll records, and automatically calculates total income, total deductions, and net salary.

## Features

- 📋 **List All Employees** — paginated, sortable table view
- ➕ **Add Employee** — form with live net salary preview and duplicate ID checking
- 🔍 **Inquiry Employee** — look up a single employee's full payroll details
- ✏️ **Update Employee** — edit an existing employee's payroll info
- 🗑️ **Delete Employee** — delete with a confirmation step to prevent accidents

## Tech Stack

- [Streamlit](https://streamlit.io) — web UI
- [SQLite](https://www.sqlite.org/) — local database (via Python's built-in `sqlite3`)
- [pandas](https://pandas.pydata.org/) — data display

## Project Structure

```
.
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md
```

The app creates a local SQLite database file (`employee_table.db`) automatically the first time it runs — no manual setup needed.

## Running Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/<your-repo>.git
   cd <your-repo>
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

5. Open the URL Streamlit prints in the terminal (usually `http://localhost:8501`).

## Deploying to Streamlit Community Cloud

1. **Push this project to a GitHub repository** (public or private).
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

2. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with your GitHub account.

3. Click **"New app"**, then select:
   - **Repository:** `<your-username>/<your-repo>`
   - **Branch:** `main`
   - **Main file path:** `app.py`

4. Click **"Deploy"**. Streamlit Cloud will install the packages from `requirements.txt` and launch the app.

### ⚠️ Note on data persistence

This app stores data in a local SQLite file (`employee_table.db`). On Streamlit Community Cloud, the filesystem is **ephemeral** — data will reset whenever the app restarts or redeploys (e.g., after inactivity or a new git push). This is fine for demos, but for production use with data that must persist, consider switching to a hosted database (e.g., PostgreSQL, Supabase, or Turso) and updating `get_connection()` in `app.py` accordingly.

## License

Feel free to use and adapt this project for your own purposes.
