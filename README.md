# Student Assignment Tracker

**INF601 – Advanced Programming in Python · Mini Project 6**
**Author:** Coyt Mauch

Student Assignment Tracker is a Django web application that helps students keep track of their
coursework. Each student creates an account, adds assignments with a course, due date, and priority,
and sees everything that is overdue or coming up on a personal dashboard. Every user's assignments
are private: users can only see and manage their own work.

---

## Table of Contents

1. [Features](#features)
2. [Pages](#pages)
3. [Technologies](#technologies)
4. [Requirements](#requirements)
5. [Project Structure](#project-structure)
6. [Installation](#installation)
   - [Windows](#windows-powershell)
   - [Linux (university dev box)](#linux-university-dev-box)
7. [Database Initialization](#database-initialization)
8. [Creating a Superuser](#creating-a-superuser)
9. [Running the Server](#running-the-server)
10. [Using the Application](#using-the-application)
11. [Django Admin](#django-admin)
12. [Running the Tests](#running-the-tests)
13. [Security](#security)
14. [Troubleshooting](#troubleshooting)
15. [Rubric Checklist](#rubric-checklist)
16. [AI Usage](#ai-usage)

---

## Features

- **User accounts** – register with Django's built-in `UserCreationForm`, log in with Django's
  built-in `LoginView`, and log out with a CSRF-protected POST form.
- **Private data** – every assignment belongs to the user who created it. Lists, the dashboard, and
  detail pages only ever show the logged-in user's assignments; another user's assignment returns
  *404 Not Found*.
- **Dashboard** – total, active, completed, and overdue counts; a progress bar showing the percent
  complete; a list of overdue work; and a list of everything due in the next 7 days.
- **Assignment list** – a table of all your assignments with tabs to filter by
  **All / Active / Completed / Overdue**, colored priority and status badges, and
  "Due in 3 days" / "2 days overdue" reminders.
- **Add assignment form** – a Django `ModelForm` with title, course name, description, a date-picker
  for the due date, and a priority (Low / Medium / High). The owner is set automatically to the
  logged-in user. Invalid fields are outlined in red with an error message.
- **Assignment details** – every field plus created/updated timestamps.
- **Delete with confirmation** – a **Delete Assignment** button opens a Bootstrap modal with
  **Cancel** and **Confirm Delete** buttons. Confirm Delete submits a POST form with a CSRF token.
- **Customized Django admin** – columns, filters, search, grouped form sections, a date drill-down,
  an "Overdue" column, and bulk "mark completed / not completed" actions.
- **Responsive Bootstrap 5.3 design** – works on desktop and phone screens, with a collapsible navbar,
  success messages, and Bootstrap Icons.

## Pages

| Page | URL | Login required | Template |
|---|---|---|---|
| Home | `/` | No | `planner/home.html` |
| About | `/about/` | No | `planner/about.html` |
| Register | `/accounts/register/` | No | `registration/register.html` |
| Log in | `/accounts/login/` | No | `registration/login.html` |
| Log out | `/accounts/logout/` (POST only) | Yes | – (redirects to Home) |
| Dashboard | `/dashboard/` | Yes | `planner/dashboard.html` |
| Assignment List | `/assignments/` (optional `?status=active`, `completed`, `overdue`) | Yes | `planner/assignment_list.html` |
| Add Assignment | `/assignments/new/` | Yes | `planner/assignment_form.html` |
| Assignment Detail | `/assignments/<id>/` | Yes | `planner/assignment_detail.html` |
| Delete Assignment | `/assignments/<id>/delete/` (POST only, from the modal) | Yes | – (redirects to the list) |
| Django Admin | `/admin/` | Staff only | Django admin |

Every page template extends a shared layout, `planner/base.html`, using Django template inheritance.

## Technologies

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.10 or newer (developed on 3.13) | Programming language |
| Django | 5.2 | Web framework: models, views, templates, forms, authentication, admin |
| SQLite | Built into Python | Database (`db.sqlite3`) |
| Bootstrap | 5.3.3 (CDN) | Page layout, styling, navbar, and the delete confirmation modal |
| Bootstrap Icons | 1.11.3 (CDN) | Icons |

## Requirements

- **Python 3.10 or newer.** Django 5.2 does not support older versions. Check with
  `python --version` (Windows) or `python3 --version` (Linux).
- **pip** and **venv**, which come with Python.
- **An internet connection in the browser.** Bootstrap's CSS and JavaScript are loaded from the
  jsDelivr CDN. Without it, pages are unstyled and the delete modal will not open.

The Python packages are listed in `requirements.txt`:

| Package | Why it's needed |
|---|---|
| `Django==5.2.18` | The web framework |
| `asgiref==3.13.0` | Required by Django |
| `sqlparse==0.6.1` | Required by Django (formats SQL) |
| `tzdata==2026.6` | Time-zone data. Windows doesn't include it; harmless on Linux |

## Project Structure

```
miniproject6/
├── manage.py                  # Django's command-line tool
├── requirements.txt           # Python packages to install
├── README.md                  # This file
├── .gitignore                 # Keeps .venv, db.sqlite3, and caches out of git
├── config/                    # Project settings package
│   ├── settings.py            # Installed apps, database, login redirects, etc.
│   ├── urls.py                # Root URLs: /admin/ and the planner app
│   ├── asgi.py / wsgi.py      # Server entry points
└── planner/                   # The application
    ├── models.py              # Assignment model
    ├── admin.py               # Customized admin for Assignment
    ├── forms.py               # AssignmentForm, SignUpForm, LoginForm (Bootstrap-styled)
    ├── views.py               # Page views (home, dashboard, list, add, detail, delete, register)
    ├── urls.py                # The app's URL routes
    ├── tests.py               # Automated tests
    ├── apps.py                # App configuration
    ├── migrations/
    │   └── 0001_initial.py    # Creates the Assignment table
    ├── static/planner/css/
    │   └── style.css          # Small custom styles on top of Bootstrap
    └── templates/
        ├── planner/
        │   ├── base.html      # Shared layout: Bootstrap CDN, navbar, messages, footer
        │   ├── home.html, about.html, dashboard.html
        │   ├── assignment_list.html, assignment_form.html, assignment_detail.html
        │   └── includes/      # Reusable snippets: badges, due-date text, form fields
        └── registration/
            ├── login.html     # Used by Django's LoginView
            └── register.html
```

### The `Assignment` model

| Field | Type | Notes |
|---|---|---|
| `owner` | ForeignKey → User | The user the assignment belongs to; set automatically |
| `title` | CharField (200) | Required |
| `course_name` | CharField (100) | e.g. "INF601 - Advanced Programming in Python" |
| `description` | TextField | Optional |
| `due_date` | DateField | Required |
| `priority` | Integer choice | Low (1), Medium (2), High (3); default Medium |
| `is_completed` | Boolean | Completion status; default not completed |
| `created_at` | DateTime | Set automatically when created |
| `updated_at` | DateTime | Updated automatically on every save |

Assignments are ordered with unfinished work first, then by soonest due date, then by highest priority.

---

## Installation

Create a **separate virtual environment on each computer**. A `.venv` folder made on Windows does not
work on Linux, so never copy it between machines.

### Windows (PowerShell)

1. Open PowerShell and go to the project folder:

   ```powershell
   cd path\to\miniproject6
   ```

2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   Your prompt now starts with `(.venv)`. If PowerShell says running scripts is disabled, run
   `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use Command Prompt and run
   `.venv\Scripts\activate.bat` instead.

3. Install the required packages:

   ```powershell
   pip install -r requirements.txt
   ```

### Linux (university dev box)

1. Copy the project to the dev box (for example with `git clone <your-repository-url>`) and go into
   the folder:

   ```bash
   cd ~/miniproject6
   ```

2. Confirm Python is 3.10 or newer:

   ```bash
   python3 --version
   ```

3. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   Your prompt now starts with `(.venv)`. While the environment is active, `python` refers to the
   environment's Python 3, so the commands below are the same on Windows and Linux.

4. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

---

## Database Initialization

The database file, `db.sqlite3`, is **not** included in the repository (see `.gitignore`). Each
computer creates its own by running these commands from the project folder, with the virtual
environment active:

```bash
python manage.py makemigrations
python manage.py migrate
```

- **`makemigrations`** compares the models in `planner/models.py` to the migration files and writes
  a new migration if anything changed. The project already includes
  `planner/migrations/0001_initial.py`, so on a fresh copy this prints **`No changes detected`**.
  That is expected. You only need it again after editing a model.
- **`migrate`** creates `db.sqlite3` and builds every table: Django's users, sessions, and admin
  tables, plus `planner_assignment`. The output includes the line `Applying planner.0001_initial... OK`.

## Creating a Superuser

A superuser can log in to the Django admin at `/admin/` and see every user's data.

```bash
python manage.py createsuperuser
```

Django asks for a username, an email address (optional; press Enter to skip), and a password.
The password is not shown as you type. Credentials are stored only in your local database, never in
the code. Run this on each computer, because each one has its own database.

Regular student accounts are created on the site's **Register** page. They cannot access the admin.

## Running the Server

### On Windows

```powershell
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser. Port 8000 is Django's default.

### On the Linux dev box (port 8000)

**Option A – SSH tunnel (works with the current settings).** From your own computer, connect with
port forwarding:

```bash
ssh -L 8000:127.0.0.1:8000 your-username@dev-box-hostname
```

Then, in that SSH session, start the server:

```bash
cd ~/miniproject6coytmauch
source .venv/bin/activate
python manage.py runserver 8000
```

Open **http://localhost:8000/** in the browser on your own computer.

**Option B – open the dev box by its hostname.** Django only answers requests for host names listed
in `ALLOWED_HOSTS`. The current setting is `ALLOWED_HOSTS = []`, which in development allows only
`localhost` and `127.0.0.1`. To open the site at `http://dev-box-hostname:8000/`, first add the
hostname in `config/settings.py`:

```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'dev-box-hostname']
```

Then start the server listening on all network interfaces:

```bash
python manage.py runserver 0.0.0.0:8000
```

In either case, press **Ctrl+C** to stop the server.

---

## Using the Application

1. **Register.** Click **Register** in the navbar and choose a username and password. Django's
   password rules apply: at least 8 characters, not too common, not entirely numeric, and not too
   similar to the username. You are logged in automatically and taken to your dashboard.
2. **Add assignments.** Click **Add Assignment**, fill in the form, and save. You are taken to the
   new assignment's detail page with a confirmation message.
3. **Check the dashboard.** See your counts, percent complete, overdue work, and what's due in the
   next 7 days.
4. **Browse the list.** **Assignments** shows everything, and the tabs filter to Active, Completed,
   or Overdue. Click a title to open its details.
5. **Delete an assignment.** On a detail page, click **Delete Assignment**. In the modal,
   **Cancel** closes it without changes, and **Confirm Delete** removes the assignment and returns
   you to the list.
6. **Log out.** Click **Log out** in the navbar to return to the home page.

If you visit a private page while logged out, you're sent to the login page. After logging in, you
return to the page you asked for.

## Django Admin

Log in at **http://127.0.0.1:8000/admin/** with your superuser. The **Assignment Planner → Assignments**
section is customized in `planner/admin.py`:

| Customization | What it does |
|---|---|
| `list_display` | Columns for title, course name, owner, due date, priority, completed, and a calculated **Overdue** ✔/✘ column |
| `list_filter` | Sidebar filters for completed, priority, due date, course name, and owner |
| `search_fields` | Search box covering title, course name, description, and owner's username |
| `fieldsets` | Edit form grouped into a main section, **Status**, and a collapsible **Timestamps** section |
| `date_hierarchy` | Year → month → day drill-down by due date |
| `readonly_fields` | Created/updated timestamps are shown but can't be edited |
| `actions` | Bulk **Mark selected as completed / not completed** |
| Site header | Admin title reads "Student Assignment Tracker Admin" |

## Running the Tests

```bash
python manage.py test
```

The test suite in `planner/tests.py` contains 26 tests and uses a temporary database, so your
real data is never touched:

| Group | What it checks |
|---|---|
| Registration (5) | Signup logs in and redirects to the dashboard; mismatched passwords and duplicate usernames are rejected |
| Login / Logout (7) | Login redirects to the dashboard (or the requested page); a wrong password shows an error; logout rejects GET and works with POST |
| Login required (3) | Every assignment page redirects logged-out visitors to the login page |
| Ownership (5) | Lists and the dashboard show only your assignments; another user's detail page is a 404; a forged `owner` field is ignored |
| Delete (6) | The modal and its form are present; the CSRF token is required; GET can't delete; other users and logged-out visitors can't delete |

Test accounts use randomly generated passwords, so no passwords are written into the code.

## Security

- **CSRF protection** – every POST form (add assignment, register, log in, log out, and delete)
  includes `{% csrf_token %}`. Django rejects POSTs without a valid token with *403 Forbidden*.
- **Login required** – the dashboard and all assignment pages use `@login_required`.
- **Per-user data** – every query is filtered by `owner=request.user`, and single assignments are
  loaded with `get_object_or_404(Assignment, pk=pk, owner=request.user)`. Another user's assignment
  returns 404, the same as one that doesn't exist.
- **Owner can't be forged** – `owner` is not a form field; the view sets it from the logged-in user.
- **Safe deletes** – the delete view accepts POST only (`@require_POST`), so a link or page prefetch
  can never delete anything.
- **Passwords** – stored hashed by Django's authentication system and checked against
  `AUTH_PASSWORD_VALIDATORS`. No passwords or server credentials are written in the code; the
  superuser is created interactively.
- **Development settings** – `config/settings.py` uses `DEBUG = True` and the development
  `SECRET_KEY` that `django-admin startproject` generated. This is a development configuration for
  running the project with `runserver`, not for a public production server.

## Troubleshooting

| Problem | Fix |
|---|---|
| `'python' is not recognized` (Windows) | Use `py` instead of `python`, or reinstall Python with "Add to PATH" checked |
| `python: command not found` (Linux) | Use `python3`, or activate the virtual environment first |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, or use `activate.bat` in Command Prompt |
| `ModuleNotFoundError: No module named 'django'` | The virtual environment isn't active, or you skipped `pip install -r requirements.txt` |
| `no such table: planner_assignment` | Run `python manage.py migrate` |
| `Error: That port is already in use.` | Another server is using port 8000. Stop it (Ctrl+C in its terminal), then try again |
| *Bad Request (400)* / `Invalid HTTP_HOST header` | The host name you opened isn't in `ALLOWED_HOSTS`; see [Running the Server](#running-the-server) |
| Pages look unstyled, or the delete modal won't open | Bootstrap loads from a CDN; check the browser's internet connection |
| CSS changes don't appear | Hard-refresh the page (Ctrl+F5) |

---

## AI Usage

<!-- Review this section and edit anything that doesn't match exactly how you worked. -->

I used **Claude Code** while building this project. I wrote the project requirements, chose the features, and directed the work one stage at a time, reviewing each stage before moving on to the next.

**How the AI contributed:** It generated the code for the model, admin, forms, views, URLs,
templates, CSS, and automated tests, explained what each file does and why it is needed, and
ran Django's system checks and the test suite after each change. It also drafted this README.

**How I checked the work:** I reviewed the code from each stage and tested it myself by running the
server, registering accounts, adding assignments, and trying the pages in the browser. I also ran
the automated tests with `python manage.py test`.

**Things that came up along the way:**

- An integrity (SRI) hash for Bootstrap's JavaScript, typed from memory, was wrong and would have
  stopped the browser from loading the script. The AI caught this by downloading the actual CDN files
  and computing the hashes.
- Before the site had its own login page, the navbar temporarily used the admin's login and logout.
  Testing showed the admin logout ignores non-staff users, so it was replaced with Django's
  `LoginView`/`LogoutView` in the authentication stage.
