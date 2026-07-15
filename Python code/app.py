import sqlite3
import streamlit as st
import pandas as pd
from datetime import date

DB_PATH = "employee_table.db"

# ---------------------------------------------------------
# Database setup
# ---------------------------------------------------------
def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employee_table (
        emp_num INTEGER PRIMARY KEY,
        emp_name TEXT NOT NULL,
        emp_basic_salary REAL NOT NULL,
        housing_allowance REAL NOT NULL,
        transportation_allowance REAL NOT NULL,
        tax REAL NOT NULL,
        insurance REAL NOT NULL,
        tot_income REAL NOT NULL,
        tot_deductions REAL NOT NULL,
        net_salary REAL NOT NULL,
        date TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

def calculate_payroll(basic, housing, transport, tax, insurance):
    tot_income = basic + housing + transport
    tot_deductions = tax + insurance
    net_salary = tot_income - tot_deductions
    return tot_income, tot_deductions, net_salary

# ---------------------------------------------------------
# CRUD operations
# ---------------------------------------------------------
def add_employee(emp_num, name, basic, housing, transport, tax, insurance, dt):
    tot_income, tot_deductions, net_salary = calculate_payroll(basic, housing, transport, tax, insurance)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO employee_table VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (emp_num, name, basic, housing, transport, tax, insurance,
          tot_income, tot_deductions, net_salary, dt))
    conn.commit()
    conn.close()

def get_employee(emp_num):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employee_table WHERE emp_num = ?;", (emp_num,))
    row = cursor.fetchone()
    conn.close()
    return row

def update_employee(emp_num, name, basic, housing, transport, tax, insurance, dt):
    tot_income, tot_deductions, net_salary = calculate_payroll(basic, housing, transport, tax, insurance)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE employee_table
        SET emp_name=?, emp_basic_salary=?, housing_allowance=?, transportation_allowance=?,
            tax=?, insurance=?, tot_income=?, tot_deductions=?, net_salary=?, date=?
        WHERE emp_num=?
    """, (name, basic, housing, transport, tax, insurance,
          tot_income, tot_deductions, net_salary, dt, emp_num))
    conn.commit()
    conn.close()

def delete_employee(emp_num):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employee_table WHERE emp_num=?;", (emp_num,))
    conn.commit()
    conn.close()

def list_employees():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM employee_table;", conn)
    conn.close()
    return df

# ---------------------------------------------------------
# Shared UI helpers
# ---------------------------------------------------------
FIELD_LABELS = [
    ("emp_num", "Number"),
    ("emp_name", "Name"),
    ("emp_basic_salary", "Basic Salary"),
    ("housing_allowance", "Housing Allowance"),
    ("transportation_allowance", "Transportation Allowance"),
    ("tax", "Tax"),
    ("insurance", "Insurance"),
    ("tot_income", "Total Income"),
    ("tot_deductions", "Total Deductions"),
    ("net_salary", "Net Salary"),
    ("date", "Date"),
]

def render_employee_card_horizontal(data, highlight_key=None):
    """Render employee details as a horizontal (landscape) row of tiles."""
    tiles = []
    for key, label in FIELD_LABELS:
        value = data[key]
        if isinstance(value, float):
            display_value = f"${value:,.2f}" if key != "emp_num" else f"{value:,.0f}"
        else:
            display_value = value
        highlight_class = " tile-highlight" if key == highlight_key else ""
        tiles.append(
            f'<div class="info-tile{highlight_class}">'
            f'<div class="info-label">{label}</div>'
            f'<div class="info-value">{display_value}</div>'
            f'</div>'
        )
    html = '<div class="employee-card-landscape">' + "".join(tiles) + '</div>'
    st.markdown(html, unsafe_allow_html=True)

# ---------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------
def main():
    st.set_page_config(page_title="Employee Payroll System", layout="wide")

    # Custom CSS styling
    st.markdown("""
        <style>
        /* ---------- Global ---------- */
        .main {
            background: linear-gradient(180deg, #f4f7fb 0%, #eef1f8 100%);
        }
        h1, h2, h3 {
            color: #1f2d3d;
            font-weight: 700;
        }
        h1 {
            padding-bottom: 0.2em;
            border-bottom: 3px solid #0078D4;
            display: inline-block;
        }

        /* ---------- Sidebar ---------- */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f2540 0%, #16324f 100%);
        }
        section[data-testid="stSidebar"] * {
            color: #f0f4f8 !important;
        }
        section[data-testid="stSidebar"] label {
            font-weight: 600;
        }

        /* ---------- Buttons ---------- */
        .stButton>button {
            background: linear-gradient(135deg, #0078D4 0%, #0057a8 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5em 1.6em;
            font-weight: 600;
            box-shadow: 0 2px 6px rgba(0,86,168,0.35);
            transition: all 0.15s ease-in-out;
        }
        .stButton>button:hover {
            background: linear-gradient(135deg, #005a9e 0%, #003f75 100%);
            box-shadow: 0 4px 10px rgba(0,86,168,0.45);
            transform: translateY(-1px);
        }
        .stButton>button:disabled {
            background: #b8c2cc;
            color: #eef1f8;
            box-shadow: none;
        }

        /* ---------- Inputs ---------- */
        div[data-baseweb="input"], div[data-baseweb="select"] {
            border-radius: 6px;
        }

        /* ---------- Form section headers ---------- */
        .section-caption {
            color: #57708c;
            font-size: 0.95em;
            margin-bottom: 0.8em;
        }

        /* ---------- Landscape employee card ---------- */
        .employee-card-landscape {
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            background-color: #ffffff;
            border-radius: 12px;
            padding: 22px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.08);
            margin-top: 18px;
            border: 1px solid #e6eaf0;
        }
        .info-tile {
            flex: 1 1 160px;
            background-color: #f7f9fc;
            border-radius: 8px;
            padding: 12px 14px;
            border: 1px solid #e9edf3;
            min-width: 150px;
        }
        .info-tile.tile-highlight {
            background: linear-gradient(135deg, #e8f3ff 0%, #d7ebff 100%);
            border: 1px solid #b6dcff;
        }
        .info-label {
            font-size: 0.78em;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #7488a0;
            margin-bottom: 4px;
            font-weight: 600;
        }
        .info-value {
            font-size: 1.15em;
            color: #1f2d3d;
            font-weight: 700;
        }

        /* ---------- Net salary preview badge ---------- */
        .net-preview {
            display: inline-block;
            background: linear-gradient(135deg, #e8f8f0 0%, #d3f2e2 100%);
            border: 1px solid #b5e6cb;
            border-radius: 8px;
            padding: 10px 18px;
            font-size: 1.05em;
            font-weight: 700;
            color: #1c6b45;
            margin: 10px 0 4px 0;
        }

        /* ---------- Dataframe container ---------- */
        div[data-testid="stDataFrame"] {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        /* ---------- Pagination controls ---------- */
        .page-indicator {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            height: 2.5em;
            background: linear-gradient(135deg, #eef3fa 0%, #e2ebf7 100%);
            border: 1px solid #cfdcec;
            border-radius: 8px;
            padding: 0 18px;
            font-weight: 700;
            color: #1f2d3d;
            margin-top: 2px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("💼 Employee Payroll System")

    init_db()

    menu = st.sidebar.radio(
        "Menu",
        ["List All Employees", "Add Employee", "Inquiry Employee", "Update Employee", "Delete Employee"]
    )

    # ---------------------------------------------------------
    # LIST ALL EMPLOYEES
    # ---------------------------------------------------------
    if menu == "List All Employees":
        st.subheader("📋 All Employees")
        df = list_employees()
        if df.empty:
            st.info("No employees found.")
        else:
            PAGE_SIZE = 10
            total_rows = len(df)
            total_pages = max(1, (total_rows - 1) // PAGE_SIZE + 1)

            # Keep the current page in session state, reset if it's out of range
            if "emp_list_page" not in st.session_state:
                st.session_state.emp_list_page = 1
            st.session_state.emp_list_page = min(max(1, st.session_state.emp_list_page), total_pages)

            current_page = st.session_state.emp_list_page
            start_idx = (current_page - 1) * PAGE_SIZE
            end_idx = min(start_idx + PAGE_SIZE, total_rows)
            page_df = df.iloc[start_idx:end_idx].reset_index(drop=True)

            st.caption(f"Showing employees {start_idx + 1}–{end_idx} of {total_rows}")
            st.dataframe(page_df, use_container_width=True, hide_index=True)

            # ---------------- Pagination controls ----------------
            nav = st.columns([1, 1, 1, 1, 3])
            with nav[0]:
                if st.button("⏮ First", disabled=(current_page == 1), use_container_width=True):
                    st.session_state.emp_list_page = 1
                    st.rerun()
            with nav[1]:
                if st.button("◀ Previous", disabled=(current_page == 1), use_container_width=True):
                    st.session_state.emp_list_page -= 1
                    st.rerun()
            with nav[2]:
                if st.button("Next ▶", disabled=(current_page == total_pages), use_container_width=True):
                    st.session_state.emp_list_page += 1
                    st.rerun()
            with nav[3]:
                if st.button("Last ⏭", disabled=(current_page == total_pages), use_container_width=True):
                    st.session_state.emp_list_page = total_pages
                    st.rerun()
            with nav[4]:
                st.markdown(
                    f'<div class="page-indicator">Page {current_page} of {total_pages}</div>',
                    unsafe_allow_html=True,
                )

    # ---------------------------------------------------------
    # ADD EMPLOYEE (with auto-clear, landscape layout)
    # ---------------------------------------------------------
    elif menu == "Add Employee":
        st.subheader("➕ Add Employee")
        st.markdown('<div class="section-caption">Fill in the employee details below.</div>', unsafe_allow_html=True)

        with st.form("add_employee_form", clear_on_submit=True):
            row1 = st.columns(3)
            with row1[0]:
                emp_num = st.number_input("Employee Number", min_value=1, step=1)
            with row1[1]:
                name = st.text_input("Employee Name")
            with row1[2]:
                dt = st.date_input("Date", value=date.today())

            row2 = st.columns(3)
            with row2[0]:
                basic = st.number_input("Basic Salary", min_value=0.0, step=100.0)
            with row2[1]:
                housing = st.number_input("Housing Allowance", min_value=0.0, step=50.0)
            with row2[2]:
                transport = st.number_input("Transportation Allowance", min_value=0.0, step=50.0)

            row3 = st.columns(3)
            with row3[0]:
                tax = st.number_input("Tax", min_value=0.0, step=10.0)
            with row3[1]:
                insurance = st.number_input("Insurance", min_value=0.0, step=10.0)

            net_salary = basic + housing + transport - tax - insurance
            st.markdown(f'<div class="net-preview">💰 Net Salary Preview: {net_salary:,.2f}</div>', unsafe_allow_html=True)

            submitted = st.form_submit_button("Add Employee")

        if submitted:
            if not name.strip():
                st.error("Employee name is required.")
            elif net_salary < 0:
                st.error("Net salary can't be negative — check tax/insurance amounts.")
            else:
                try:
                    add_employee(emp_num, name.strip(), basic, housing, transport, tax, insurance, dt.isoformat())
                    st.session_state["add_emp_success"] = f"✅ Employee '{name.strip()}' added successfully!"
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error(f"Employee number {emp_num} already exists.")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

        # Show the success message here — after the form, at the bottom of this section
        if "add_emp_success" in st.session_state:
            st.success(st.session_state.pop("add_emp_success"))

    # ---------------------------------------------------------
    # INQUIRY EMPLOYEE (landscape card)
    # ---------------------------------------------------------
    elif menu == "Inquiry Employee":
        st.subheader("🔍 Inquiry Employee")
        emp_num = st.number_input("Employee Number", min_value=1, step=1)

        if st.button("Search"):
            row = get_employee(emp_num)

            if not row:  # catches None, [], (), etc.
                st.error(f"❌ Employee #{emp_num} not found.")
            else:
                cols = [key for key, _ in FIELD_LABELS]

                if len(row) != len(cols):
                    st.error("⚠️ Unexpected data format returned for this employee.")
                else:
                    data = dict(zip(cols, row))
                    st.session_state["inquiry_result"] = data

        if "inquiry_result" in st.session_state:
            st.markdown("#### Employee Details")
            render_employee_card_horizontal(st.session_state["inquiry_result"], highlight_key="net_salary")

    # ---------------------------------------------------------
    # UPDATE EMPLOYEE (landscape layout)
    # ---------------------------------------------------------
    elif menu == "Update Employee":
        st.subheader("✏️ Update Employee")
        emp_num = st.number_input("Employee Number", min_value=1, step=1)

        if st.button("Load"):
            row = get_employee(emp_num)
            if row is None:
                st.error("Employee not found.")
            else:
                _, name0, basic0, housing0, transport0, tax0, insurance0, _, _, _, date0 = row
                st.session_state.upd_name = name0
                st.session_state.upd_basic = basic0
                st.session_state.upd_housing = housing0
                st.session_state.upd_transport = transport0
                st.session_state.upd_tax = tax0
                st.session_state.upd_insurance = insurance0
                st.session_state.upd_date = date.fromisoformat(date0)

        if "upd_name" in st.session_state:
            row1 = st.columns(3)
            with row1[0]:
                name = st.text_input("Employee Name", value=st.session_state.upd_name)
            with row1[1]:
                dt = st.date_input("Date", value=st.session_state.upd_date)
            with row1[2]:
                st.text_input("Employee Number", value=str(emp_num), disabled=True)

            row2 = st.columns(3)
            with row2[0]:
                basic = st.number_input("Basic Salary", min_value=0.0, step=100.0, value=st.session_state.upd_basic)
            with row2[1]:
                housing = st.number_input("Housing Allowance", min_value=0.0, step=50.0, value=st.session_state.upd_housing)
            with row2[2]:
                transport = st.number_input("Transportation Allowance", min_value=0.0, step=50.0, value=st.session_state.upd_transport)

            row3 = st.columns(3)
            with row3[0]:
                tax = st.number_input("Tax", min_value=0.0, step=10.0, value=st.session_state.upd_tax)
            with row3[1]:
                insurance = st.number_input("Insurance", min_value=0.0, step=10.0, value=st.session_state.upd_insurance)

            net_salary = basic + housing + transport - tax - insurance
            st.markdown(f'<div class="net-preview">💰 Net Salary Preview: {net_salary:,.2f}</div>', unsafe_allow_html=True)

            if st.button("Update"):
                update_employee(emp_num, name, basic, housing, transport, tax, insurance, dt.isoformat())
                st.success("Employee updated successfully.")

    # ---------------------------------------------------------
    # DELETE EMPLOYEE (landscape card)
    # ---------------------------------------------------------
    elif menu == "Delete Employee":
        st.subheader("🗑️ Delete Employee")

        # Show pending success message from a previous delete
        if "delete_success" in st.session_state:
            st.success(st.session_state.pop("delete_success"))

        emp_num = st.number_input("Employee Number", min_value=1, step=1)

        # Step 1: Look up the employee first
        if st.button("Search"):
            row = get_employee(emp_num)
            if not row:
                st.session_state.pop("delete_target", None)
                st.error(f"❌ Employee #{emp_num} not found.")
            else:
                cols = [key for key, _ in FIELD_LABELS]
                st.session_state["delete_target"] = dict(zip(cols, row))

        # Step 2: If an employee was found, show details + confirm delete
        if "delete_target" in st.session_state:
            data = st.session_state["delete_target"]

            st.markdown("#### Employee Details")
            render_employee_card_horizontal(data, highlight_key="emp_name")

            st.warning("⚠️ This action cannot be undone.")
            confirm = st.checkbox(f"I confirm I want to delete Employee #{data['emp_num']} ({data['emp_name']})")

            if st.button("Confirm Delete", disabled=not confirm):
                delete_employee(data["emp_num"])
                st.session_state["delete_success"] = f"✅ Employee #{data['emp_num']} ({data['emp_name']}) deleted successfully."
                del st.session_state["delete_target"]
                st.rerun()

# ---------------------------------------------------------
# Run the app
# ---------------------------------------------------------
if __name__ == "__main__":
    main()
