import os
import logging
import subprocess
from pathlib import Path
from collections import defaultdict  
from typing import Optional
import json
import threading
from datetime import datetime

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from my_script import run_task  # your existing import



API_TOKEN = os.getenv("API_TOKEN", "CHANGE_ME_123")
app = FastAPI(title="Selenium Runner (v2)")
JOBS_DIR = Path("/app/jobs")
HISTORY_PATH = Path("run_history.jsonl")
USERS_PATH = Path("users.json")
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
headless_flag = True  # default headless mode

# Track running jobs per user so we can stop them
RUNNING_PROCS = {}

def get_log_path_for_user(username: str) -> Path:
    # Simple: one log file per user (you can make this per-job later if you want)
    safe_name = username.replace("/", "_")
    return LOGS_DIR / f"{safe_name}.log"

def load_users():
    """
    Load users from users.json.

    Supports two formats:
    - Old (simple): { "kyle": "pass123", "assistant": "pass123" }
    - New (structured): { "kyle": {"password": "pass123", "role": "admin"}, ... }
    """
    if USERS_PATH.exists():
        try:
            raw = json.loads(USERS_PATH.read_text())
            users: dict[str, dict] = {}
            for username, value in raw.items():
                if isinstance(value, str):
                    # old format: just password
                    users[username] = {"password": value, "role": "user"}
                elif isinstance(value, dict):
                    users[username] = {
                        "password": value.get("password", ""),
                        "role": value.get("role", "user"),
                        "jobs_folder": value.get("jobs_folder", "SimplyHealth"),
                    }
            return users
        except Exception:
            pass

    # default if file missing or broken
    return {
        "kyle": {
            "password": "pass123",
            "role": "admin",
            "jobs_folder": "SimplyHealth",
        },
        "assistant": {
            "password": "pass123",
            "role": "user",
            "jobs_folder": "SimplyHealth",
        },
    }

def save_users(u: dict):
    """
    Save users in structured format:
    { "username": {"password": "...", "role": "admin" | "user"}, ... }
    """
    USERS_PATH.write_text(json.dumps(u, indent=2))

# load at startup
USERS = load_users()

def is_admin(username: str | None) -> bool:
    if not username:
        return False
    user = USERS.get(username)
    if not user:
        return False
    return user.get("role") == "admin"

def get_jobs_base_for_user(username: Optional[str]) -> Path:
    """
    Return the jobs base directory for a given user based on their assigned jobs_folder.
    Defaults to JOBS_DIR / "SimplyHealth" if configured, else JOBS_DIR.
    """
    if not username:
        return JOBS_DIR

    info = USERS.get(username, {})
    jf = info.get("jobs_folder")
    if jf:
        return JOBS_DIR / jf

    # fallback
    return JOBS_DIR / "SimplyHealth"

def append_history(rec: dict):
    with open(HISTORY_PATH, "a") as f:
        f.write(json.dumps(rec) + "\n")

def iso_now():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def get_username_from_auth(authorization: str | None) -> str | None:
    if authorization and authorization.startswith("Bearer user-"):
        return authorization.replace("Bearer user-", "")
    return None


class RunJob(BaseModel):
    name: Optional[str] = None
    folder: Optional[str] = None  # which jobs folder to use
    headless: Optional[bool] = True  # new: allow admin/global to control headless

class RunRequest(BaseModel):
    url: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordReq(BaseModel):
    old_password: str
    new_password: str

class AdminUser(BaseModel):
    username: str
    password: str
    role: str = "user"  # "user" or "admin"
    jobs_folder: Optional[str] = None  # e.g. "SimplyHealth", "FillmoreChiro"

class DeleteUserReq(BaseModel):
    username: str


# ===== routes =====
@app.post("/login")
def login(req: LoginRequest):
    user = USERS.get(req.username)
    if not user:
        raise HTTPException(status_code=401, detail="Bad credentials")

    if user.get("password") != req.password:
        raise HTTPException(status_code=401, detail="Bad credentials")

    user_token = f"user-{req.username}"
    return {
        "token": user_token,
        "username": req.username,
        "role": user.get("role", "user"),
        "jobs_folder": user.get("jobs_folder", "SimplyHealth"),
    }


@app.post("/change-password")
def change_password(req: ChangePasswordReq, authorization: str | None = Header(None)):
    # must be logged in as a user (not just global token)
    if authorization is None or not authorization.startswith("Bearer user-"):
        raise HTTPException(status_code=401, detail="User token required")

    username = get_username_from_auth(authorization)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid user token")

    user = USERS.get(username)
    if not user:
        raise HTTPException(status_code=401, detail="Unknown user")

    # check old password
    if user.get("password") != req.old_password:
        raise HTTPException(status_code=400, detail="Old password incorrect")

    # update and save
    user["password"] = req.new_password
    USERS[username] = user
    save_users(USERS)
    return {"ok": True}

@app.get("/admin/users")
def admin_list_users(authorization: str | None = Header(None)):
    # must be logged in as admin user
    if authorization is None or not authorization.startswith("Bearer user-"):
        raise HTTPException(status_code=401, detail="User token required")

    username = get_username_from_auth(authorization)
    if not is_admin(username):
        raise HTTPException(status_code=403, detail="Admin only")

    # return users without passwords
    items = []
    for uname, info in USERS.items():
        items.append({
            "username": uname,
            "role": info.get("role", "user"),
            "jobs_folder": info.get("jobs_folder", "SimplyHealth"),
        })
    return {"users": items}


@app.post("/admin/users")
def admin_create_or_update_user(payload: AdminUser, authorization: str | None = Header(None)):
    # must be logged in as admin user
    if authorization is None or not authorization.startswith("Bearer user-"):
        raise HTTPException(status_code=401, detail="User token required")

    admin_name = get_username_from_auth(authorization)
    if not is_admin(admin_name):
        raise HTTPException(status_code=403, detail="Admin only")

    if not payload.username:
        raise HTTPException(status_code=400, detail="Username required")

    # create or update user
    USERS[payload.username] = {
        "password": payload.password,
        "role": payload.role or "user",
        "jobs_folder": payload.jobs_folder or "SimplyHealth",
    }
    save_users(USERS)
    return {"ok": True, "message": f"User '{payload.username}' saved."}


@app.post("/admin/users/delete")
def admin_delete_user(payload: DeleteUserReq, authorization: str | None = Header(None)):
    # must be logged in as admin user
    if authorization is None or not authorization.startswith("Bearer user-"):
        raise HTTPException(status_code=401, detail="User token required")

    admin_name = get_username_from_auth(authorization)
    if not is_admin(admin_name):
        raise HTTPException(status_code=403, detail="Admin only")

    target = payload.username
    if not target:
        raise HTTPException(status_code=400, detail="Username required")

    if target == admin_name:
        raise HTTPException(status_code=400, detail="Admins cannot delete themselves")

    if target not in USERS:
        raise HTTPException(status_code=404, detail="User not found")

    del USERS[target]
    save_users(USERS)
    return {"ok": True, "message": f"User '{target}' deleted."}


@app.get("/jobs")
def list_jobs(folder: Optional[str] = None):
    """
    List available job scripts (.py) in the requested folder under JOBS_DIR.
    If folder is None, list directly under JOBS_DIR (for backward compatibility).
    """
    base = JOBS_DIR
    if folder:
        base = base / folder

    if not base.exists():
        return []

    return [p.stem for p in base.glob("*.py")]

@app.get("/job-folders")
def job_folders():
    """
    Return a list of job folder names under JOBS_DIR.
    e.g. ["SimplyHealth", "FillmoreChiro"]
    """
    if not JOBS_DIR.exists():
        return []
    return [d.name for d in JOBS_DIR.iterdir() if d.is_dir()]

@app.post("/run")
def run_job(payload: Optional[RunJob] = None, authorization: str | None = Header(None)):
    """
    Run a user script.

    - If Authorization is a user token (e.g., 'Bearer user-kyle'):
        runs /app/jobs/<username>.py
    - If Authorization is the global API token:
        runs /app/jobs/<payload.name>.py (payload.name required)
    - Captures stdout/stderr into run.log
    - Records start/finish into run_history.jsonl
    - Prevents starting a new job if one is already running for that user.
    """
    # Auth: allow global token OR per-user token
    valid_global = (authorization == f"Bearer {API_TOKEN}")
    valid_user = (authorization is not None and authorization.startswith("Bearer user-"))

    if not (valid_global or valid_user):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Determine who is running
    username = get_username_from_auth(authorization) if valid_user else "global"
    who = username or "global"

    # 🚫 NEW: block if there's already a running process for this user
    existing = RUNNING_PROCS.get(who)
    if existing and existing.poll() is None:
        # process is still running
        raise HTTPException(
            status_code=409,
            detail=f"Job already running for user '{who}'. Please stop it before starting a new one."
        )

    # Determine which script to run and which folder it lives in
    if valid_user and username:
        if is_admin(username) and payload and payload.name:
            # Admin can choose both folder and script
            chosen_folder = payload.folder or "SimplyHealth"
            base_dir = JOBS_DIR / chosen_folder
            script_name = f"{payload.name}.py"
        else:
            # Normal user: always run main_script.py from their assigned jobs_folder
            base_dir = get_jobs_base_for_user(username)
            script_name = "main_script.py"
    else:
        # Global token: must supply a job name; optional folder
        if not payload or not payload.name:
            raise HTTPException(status_code=400, detail="Missing 'name' for global token run")
        chosen_folder = payload.folder
        base_dir = JOBS_DIR / chosen_folder if chosen_folder else JOBS_DIR
        script_name = f"{payload.name}.py"


    script_path = base_dir / script_name
    if not script_path.exists():
        raise HTTPException(status_code=404, detail=f"Script not found: {script_path}")

    # Decide headless vs non-headless
    headless_flag = True
    if valid_user and username:
        if is_admin(username) and payload is not None and payload.headless is not None:
            headless_flag = payload.headless
        else:
            headless_flag = True
    else:
        if payload is not None and payload.headless is not None:
            headless_flag = payload.headless
        else:
            headless_flag = True

    # Log file dedicated to *this user*'s script output
    run_log_path = get_log_path_for_user(who)
    run_log_file = run_log_path.open("a")

    # Visible separator for each run
    run_log_file.write(f"--- started script: {script_name} (user={who}) ---\n")
    run_log_file.flush()

    # Prepare environment for the subprocess
    env = os.environ.copy()
    env["HEADLESS"] = "1" if headless_flag else "0"

    proc = subprocess.Popen(
        ["python", str(script_path)],
        cwd=str(JOBS_DIR),
        stdout=run_log_file,
        stderr=run_log_file,
        env=env,
    )

    # Remember this process for this user so we can stop it later
    RUNNING_PROCS[who] = proc

    # History: write "started"
    append_history({
        "username": who,
        "script": script_name,
        "status": "started",
        "pid": proc.pid,
        "started_at": iso_now()
    })

    # Background waiter to record finish/error and clear tracking
    def waiter(p: subprocess.Popen, user: str, sname: str):
        rc = p.wait()
        if RUNNING_PROCS.get(user) is p:
            RUNNING_PROCS.pop(user, None)
        append_history({
            "username": user,
            "script": sname,
            "status": "finished" if rc == 0 else f"error({rc})",
            "pid": p.pid,
            "finished_at": iso_now(),
            "returncode": rc
        })

    threading.Thread(target=waiter, args=(proc, who, script_name), daemon=True).start()

    logging.info(f"started script: {script_name} (user={who}, pid={proc.pid})")

    return {"status": "started", "script": script_name}


@app.post("/stop")
def stop_job(authorization: str | None = Header(None)):
    """
    Stop the currently running job for this user (if any).
    """
    valid_global = (authorization == f"Bearer {API_TOKEN}")
    valid_user = (authorization is not None and authorization.startswith("Bearer user-"))

    if not (valid_global or valid_user):
        raise HTTPException(status_code=401, detail="Unauthorized")

    username = get_username_from_auth(authorization) if valid_user else "global"
    proc = RUNNING_PROCS.get(username)

    if not proc:
        return {"ok": False, "message": "No running process for this user."}

    # If it's already finished, clean up and tell the user
    if proc.poll() is not None:
        RUNNING_PROCS.pop(username, None)
        return {"ok": False, "message": "Process already finished."}

    # Ask the process to terminate
    try:
        proc.terminate()
        logging.info(f"Stop requested for user={username}, pid={proc.pid}")
        return {"ok": True, "message": "Stop signal sent."}
    except Exception as e:
        logging.error(f"Error stopping process for {username}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
def get_logs(authorization: str | None = Header(None)):
    # allow global token OR user token
    valid_global = authorization == f"Bearer {API_TOKEN}"
    valid_user = authorization is not None and authorization.startswith("Bearer user-")
    if not (valid_global or valid_user):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # figure out who is asking (same logic as /run)
    username = get_username_from_auth(authorization) if valid_user else "global"
    who = username or "global"

    run_log_path = get_log_path_for_user(who)
    if not run_log_path.exists():
        return {"logs": ["<no script log yet>"]}

    with run_log_path.open("r", errors="ignore") as f:
        lines = f.readlines()

    tail = lines[-200:]  # show last 200 script lines for THIS user
    return {"logs": tail}

@app.post("/logs/clear")
def clear_logs(authorization: str | None = Header(None)):
    valid_global = authorization == f"Bearer {API_TOKEN}"
    valid_user = authorization is not None and authorization.startswith("Bearer user-")
    if not (valid_global or valid_user):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # figure out who is asking (same logic as /run and /logs)
    username = get_username_from_auth(authorization) if valid_user else "global"
    who = username or "global"

    run_log_path = get_log_path_for_user(who)
    if run_log_path.exists():
        # Truncate the file
        run_log_path.write_text("")

    return {"status": "cleared"}

@app.get("/history")
def history(authorization: str | None = Header(None)):
    valid_global = authorization == f"Bearer {API_TOKEN}"
    valid_user = authorization is not None and authorization.startswith("Bearer user-")
    if not (valid_global or valid_user):
        raise HTTPException(status_code=401, detail="Unauthorized")

    items = []
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH, "r") as f:
            for line in f:
                try:
                    items.append(json.loads(line))
                except:
                    pass

    # filter to this user if user token
    if valid_user:
        username = get_username_from_auth(authorization)
        items = [x for x in items if x.get("username") == username]

    # return last 50 records
    return {"history": items[-50:]}

@app.post("/run-url")
def run_url(req: RunRequest, authorization: str | None = Header(None)):
    """
    Protected endpoint that calls your custom my_script.run_task(url)
    """
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        result = run_task(req.url)
        return {"ok": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/healthz")
def healthz():
    # lightweight liveness check for load balancers/monitors
    return {"status": "ok"}


# ===== logging =====
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@app.middleware("http")
async def log_requests(request, call_next):
    logging.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Response status: {response.status_code}")
    return response

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
      <head>
        <meta charset="utf-8">
        <title>ChiroNoteHelper (CNH)</title>
      </head>

      <body>
        <h2>ChiroNoteHelper (CNH)</h2>

        <!-- LOGIN AREA -->
        <div id="login-box">
          <h3>Login</h3>
          <label>Username:
            <input id="username" onkeydown="enterLogin(event)" />
          </label><br><br>
          <label>Password:
            <input id="password" type="password" onkeydown="enterLogin(event)" />
          </label><br><br>
          <button onclick="login()">Login</button>
          <p id="login-status" style="color:red;"></p>
        </div>

        <!-- APP AREA (hidden until login) -->
        <div id="app-box" style="display:none;">
          <p>
            Logged in as: <span id="who"></span>
            &nbsp; | &nbsp;
            Status: <span id="status-indicator" style="font-weight:bold;">IDLE</span>
          </p>


          <button onclick="runMine()">Run My Script</button>
          <button onclick="stopMine()" style="margin-left:8px;">Stop My Script</button>
          <button onclick="viewLogs()">View Logs</button>
          <button onclick="viewHistory()">View History</button>

          <span id="headless-wrapper">
            <label>
              <input type="checkbox" id="headless-toggle" checked>
              Run headless
            </label>
          </span>


          <label style="margin-left:8px;">
            <input type="checkbox" id="auto" onchange="toggleAuto()"> Auto-refresh (3s)
          </label>

          <button onclick="clearLogs()" style="margin-left:8px;">Clear Logs</button>
          <button type="button" id="logoutBtn">Logout</button>


          <!-- Admin-only script selector (hidden by default) -->
          <span id="script-selector-wrapper" style="display:none; margin-left:8px;">
            Folder:
            <select id="folder-select" onchange="onFolderChange()">
              <option value="">-- folder --</option>
            </select>
            Script:
            <select id="script-select" style="margin-left:4px;">
              <option value="">-- script --</option>
            </select>
          </span>


          <p id="status" style="font-family: monospace;"></p>
          <pre id="out"></pre>

          <!-- Main output area: Logs + History side by side -->
          <div style="display:flex; gap:16px; align-items:flex-start; margin-top:16px;">
            <!-- Logs column -->
            <div style="flex:1; min-width:0;">
              <h4>Logs</h4>
              <pre id="logs" style="background:#eee; padding:8px; max-height:500px; overflow:auto;"></pre>
            </div>

            <!-- History column -->
            <div style="flex:1; min-width:0;">
              <h4>History</h4>
              <pre id="history" style="background:#eef; padding:8px; max-height:500px; overflow:auto;"></pre>
            </div>
          </div>

          <!-- Account & admin section underneath -->
          <div style="margin-top:20px;">
            <h4>Change My Password</h4>
            <label>Old:
              <input id="oldpw" type="password">
            </label>
            <label style="margin-left:8px;">New:
              <input id="newpw" type="password">
            </label>
            <button onclick="changePw()">Update</button>
            <pre id="pwout"></pre>

            <!-- Admin Panel (hidden by default; shown only for admins) -->
            <h4 id="admin-header" style="display:none; margin-top:16px;">Admin Panel</h4>
            <div id="admin-box" style="display:none; border:1px solid #ccc; padding:8px; margin-top:8px;">
              <p>Admin tools: manage CNH users</p>

              <button onclick="loadUsers()">Refresh User List</button>
              <pre id="userlist" style="background:#f7f7f7; padding:8px; max-height:200px; overflow:auto;"></pre>

              <h5>Create / Update User</h5>
              <label>Username:
                <input id="newuser" />
              </label>
              <label style="margin-left:8px;">Password:
                <input id="newpass" type="password" />
              </label>
              <label style="margin-left:8px;">Role:
                <select id="newrole">
                  <option value="user">user</option>
                  <option value="admin">admin</option>
                </select>
              </label>
              <label style="margin-left:8px;">Jobs Folder:
                <select id="newjobsfolder">
                  <option value="SimplyHealth">SimplyHealth</option>
                  <option value="FillmoreChiro">FillmoreChiro</option>
                </select>
              </label>

              <button onclick="saveUser()" style="margin-left:8px;">Save User</button>


              <h5 style="margin-top:12px;">Delete User</h5>
              <label>Username:
                <input id="deluser" />
              </label>
              <button onclick="deleteUser()" style="margin-left:8px;">Delete</button>

              <pre id="adminout" style="background:#eef; padding:8px; max-height:150px; overflow:auto;"></pre>
            </div>
          </div>


        </div>

        <script>
          // Global state
          var authToken = null;
          var autoTimer = null;
          var currentRole = "user";
          var currentJobsFolder = null;

          document.addEventListener("DOMContentLoaded", function () {
            var btn = document.getElementById("logoutBtn");
            if (btn) {
              btn.addEventListener("click", function (e) {
                e.preventDefault();
                e.stopPropagation();
                logout();   // call your existing logout()
              });
            }
          });

          // -----------------------
          // LOGIN / LOGOUT
          // -----------------------
          function login() {
            var u = document.getElementById('username').value;
            var p = document.getElementById('password').value;
            var status = document.getElementById('login-status');

            status.textContent = "";

            fetch('/login', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({username: u, password: p})
            })
            .then(function(res) {
              if (!res.ok) {
                return res.text().then(function(txt) {
                  status.textContent = "Login failed (" + res.status + "): " + txt;
                  throw new Error("login failed");
                });
              }
              return res.json();
            })
            .then(function(data) {
              authToken = data.token;
              currentRole = data.role || (data.username === 'kyle' ? 'admin' : 'user');
              currentJobsFolder = data.jobs_folder || null;

              // ⭐ Show headless toggle ONLY for admins
              var headlessWrapper = document.getElementById('headless-wrapper');
              if (headlessWrapper) {
                if (currentRole === "admin") {
                  headlessWrapper.style.display = "inline-block";
                } else {
                  headlessWrapper.style.display = "none";
                }
              }

              document.getElementById('login-box').style.display = 'none';
              document.getElementById('app-box').style.display = 'block';
              document.getElementById('who').textContent = data.username;

              var adminBox = document.getElementById('admin-box');
              var adminHeader = document.getElementById('admin-header');
              var scriptWrapper = document.getElementById('script-selector-wrapper');
              var headlessWrapper = document.getElementById('headless-wrapper');

              if (currentRole === 'admin') {
                if (adminHeader) adminHeader.style.display = 'block';
                if (adminBox) adminBox.style.display = 'block';
                if (scriptWrapper) scriptWrapper.style.display = 'inline-block';

                loadUsers();
                loadJobFolders(currentJobsFolder);
                populateJobsFolderDropdown();
              } else {
                if (adminHeader) adminHeader.style.display = 'none';
                if (adminBox) adminBox.style.display = 'none';
                if (scriptWrapper) scriptWrapper.style.display = 'none';
              }

              var autoCb = document.getElementById('auto');
              if (autoCb) {
                autoCb.checked = true;
                toggleAuto();
              }
              viewLogs();
            })
            .catch(function(err) {
              if (status.textContent === "") {
                status.textContent = "Network error";
              }
            });
          }

          function logout(event) {
            if (event) event.preventDefault();

            // ✅ define this inside logout so it exists here
            var headlessWrapper = document.getElementById('headless-wrapper');

            var autoCb = document.getElementById('auto');
            if (autoTimer !== null) {
              clearInterval(autoTimer);
              autoTimer = null;
            }
            if (autoCb) autoCb.checked = false;

            authToken = null;
            currentRole = "user";
            currentJobsFolder = null;

            var statusEl = document.getElementById('status');
            var outEl = document.getElementById('out');
            var logsEl = document.getElementById('logs');
            var historyEl = document.getElementById('history');
            var adminBox = document.getElementById('admin-box');
            var adminHeader = document.getElementById('admin-header');
            var scriptWrapper = document.getElementById('script-selector-wrapper');

            if (statusEl) statusEl.textContent = "";
            if (outEl) outEl.textContent = "";
            if (logsEl) logsEl.textContent = "";
            if (historyEl) historyEl.textContent = "";

            if (adminHeader) adminHeader.style.display = 'none';
            if (adminBox) adminBox.style.display = 'none';
            if (scriptWrapper) scriptWrapper.style.display = 'none';
            if (headlessWrapper) headlessWrapper.style.display = 'none';

            // ✅ THESE are the lines that were not being reached before
            document.getElementById('login-box').style.display = 'block';
            document.getElementById('app-box').style.display = 'none';

            document.getElementById('username').value = "";
            document.getElementById('password').value = "";
            document.getElementById('login-status').textContent = "";
          }


          // -----------------------
          // RUN / STOP
          // -----------------------
          function runMine() {
            var statusEl = document.getElementById('status');
            var outEl = document.getElementById('out');
            statusEl.textContent = "Running your script...";
            outEl.textContent = "";

            var payload = {};

            if (currentRole === 'admin') {
              var selScript = document.getElementById('script-select');
              var selFolder = document.getElementById('folder-select');
              var headlessCb = document.getElementById('headless-toggle');

              if (!selFolder || !selFolder.value) {
                statusEl.textContent = "Please select a folder first.";
                return;
              }
              if (!selScript || !selScript.value) {
                statusEl.textContent = "Please select a script first.";
                return;
              }
              // default headless = true if checkbox is missing for some reason
              var headless = headlessCb ? headlessCb.checked : true;

              payload = { name: selScript.value, folder: selFolder.value, headless: headless };
            }

            fetch('/run', {
              method: 'POST',
              headers: Object.assign(
                {'Content-Type': 'application/json'},
                authToken ? {'Authorization': 'Bearer ' + authToken} : {}
              ),
              body: JSON.stringify(payload)
            })
            .then(function(res) {
              return res.text().then(function(text) {
                outEl.textContent = text;
                if (res.ok) {
                  statusEl.textContent = "Job started (ok)";
                  setStatus('RUNNING', 'green');
                  viewLogs();

                  // Only load history if this is NOT the FillmoreChiro jobs folder
                  if (currentJobsFolder !== "FillmoreChiro") {
                    viewHistory();
                  }
                } else {

                  statusEl.textContent = "ERROR " + text;
                  setStatus('ERROR', 'red');
                }
              });
            })
            .catch(function(err) {
              statusEl.textContent = "Network error";
              outEl.textContent = String(err);
              setStatus('ERROR', 'red');
            });
          }

          function stopMine() {
            var statusEl = document.getElementById('status');
            var outEl = document.getElementById('out');
            statusEl.textContent = "Stopping your script...";
            outEl.textContent = "";

            fetch('/stop', {
              method: 'POST',
              headers: authToken ? {'Authorization': 'Bearer ' + authToken} : {}
            })
            .then(function(res) {
              return res.text().then(function(text) {
                outEl.textContent = text;
                if (res.ok) {
                  statusEl.textContent = "Stop signal sent";
                  setStatus('IDLE', 'gray');
                  viewLogs();

                  // Only load history if this is NOT the FillmoreChiro jobs folder
                  if (currentJobsFolder !== "FillmoreChiro") {
                    viewHistory();
                  }
                } else {
                  statusEl.textContent = "Error stopping: " + res.status;
                }
              });
            })
            .catch(function(e) {
              statusEl.textContent = "Network error while stopping";
              outEl.textContent = String(e);
            });
          }

          // -----------------------
          // LOGS / HISTORY
          // -----------------------
          function viewLogs(silent) {
            if (silent === undefined) silent = false;
            var logsEl = document.getElementById('logs');
            if (!silent) {
              logsEl.textContent = "Loading logs...";
            }

            fetch('/logs', {
              headers: authToken ? {'Authorization': 'Bearer ' + authToken} : {}
            })
            .then(function(res) {
              if (!res.ok) {
                if (!silent) {
                  logsEl.textContent = "Error fetching logs: " + res.status;
                }
                return null;
              }
              return res.json();
            })
            .then(function(data) {
              if (!data) return;
              var newText = data.logs.join('');
              if (logsEl.textContent === newText) {
                return;
              }
              logsEl.textContent = newText;
              logsEl.scrollTop = logsEl.scrollHeight;

              if (newText.indexOf("error(") !== -1) {
                setStatus('ERROR', 'red');
              } else if (newText.indexOf("finished") !== -1) {
                setStatus('IDLE', 'gray');
              }
            })
            .catch(function(e) {
              if (!silent) {
                logsEl.textContent = "Network error";
              }
            });
          }

          function viewHistory() {
            var el = document.getElementById('history');
            el.textContent = "Loading history...";

            fetch('/history', {
              headers: authToken ? {'Authorization': 'Bearer ' + authToken} : {}
            })
            .then(function(res) {
              if (!res.ok) {
                el.textContent = "Error fetching history: " + res.status;
                return null;
              }
              return res.json();
            })
            .then(function(data) {
              if (!data) return;
              var lines = [];
              for (var i = 0; i < data.history.length; i++) {
                lines.push(JSON.stringify(data.history[i]));
              }
              el.textContent = lines.join("\\n");

            })
            .catch(function(e) {
              el.textContent = "Network error";
            });
          }

          function toggleAuto() {
            var cb = document.getElementById('auto');
            if (cb.checked) {
              autoTimer = setInterval(function() {
                viewLogs(true);
              }, 3000);
            } else {
              if (autoTimer !== null) {
                clearInterval(autoTimer);
                autoTimer = null;
              }
            }
          }

          function setStatus(text, color) {
            var el = document.getElementById('status-indicator');
            if (!el) return;
            el.textContent = text;
            el.style.color = color;
          }

          async function clearLogs() {
            const logsEl = document.getElementById("logs");

            // Clear the UI immediately
            if (logsEl) {
              logsEl.textContent = "";
            }

            try {
              await fetch("/logs/clear", {
                method: "POST",
                headers: authToken
                  ? { "Authorization": "Bearer " + authToken }
                  : {},
              });
            } catch (err) {
              console.error("Failed to clear logs on server:", err);
            }
          }


          // -----------------------
          // PASSWORD CHANGE
          // -----------------------
          function changePw() {
            var oldpw = document.getElementById('oldpw').value;
            var newpw = document.getElementById('newpw').value;
            var out = document.getElementById('pwout');
            out.textContent = "";

            if (!oldpw || !newpw) {
              out.textContent = "Please fill in both fields.";
              return;
            }

            fetch('/change-password', {
              method: 'POST',
              headers: Object.assign(
                {'Content-Type': 'application/json'},
                authToken ? {'Authorization': 'Bearer ' + authToken} : {}
              ),
              body: JSON.stringify({old_password: oldpw, new_password: newpw})
            })
            .then(function(res) {
              if (res.ok) {
                out.textContent = "Password updated";
                document.getElementById('oldpw').value = "";
                document.getElementById('newpw').value = "";
              } else {
                return res.text().then(function(text) {
                  out.textContent = "ERROR" + text;
                });
              }
            })
            .catch(function(e) {
              out.textContent = "Network error";
            });
          }

          // -----------------------
          // ADMIN: USERS
          // -----------------------
          function loadUsers() {
            var out = document.getElementById('userlist');
            out.textContent = "Loading users...";

            fetch('/admin/users', {
              headers: authToken ? {'Authorization': 'Bearer ' + authToken} : {}
            })
            .then(function(res) {
              return res.text().then(function(txt) {
                if (!res.ok) {
                  out.textContent = "Error from /admin/users (" + res.status + "): " + txt;
                  throw new Error("bad /admin/users");
                }
                var data;
                try {
                  data = JSON.parse(txt);
                } catch (e) {
                  out.textContent = "Bad JSON from /admin/users: " + txt;
                  throw e;
                }
                if (!data.users || !Array.isArray(data.users)) {
                  out.textContent = "Unexpected /admin/users payload: " + txt;
                  throw new Error("bad structure");
                }
                var lines = [];
                for (var i = 0; i < data.users.length; i++) {
                  var u = data.users[i];
                  var role = u.role || "user";
                  var folder = u.jobs_folder || "SimplyHealth";
                  lines.push(u.username + " (" + role + ", " + folder + ")");
                }
                out.textContent = lines.join("\\n");
              });
            })
            .catch(function(e) {
              if (out.textContent.indexOf("Error from /admin/users") === -1 &&
                  out.textContent.indexOf("Bad JSON") === -1 &&
                  out.textContent.indexOf("Unexpected /admin/users") === -1) {
                out.textContent = "Network error: " + e;
              }
            });
          }

          function populateJobsFolderDropdown() {
            var sel = document.getElementById('newjobsfolder');
            if (!sel) return;

            fetch('/job-folders')
            .then(function(res) {
              if (!res.ok) return null;
              return res.json();
            })
            .then(function(folders) {
              if (!folders) return;
              sel.innerHTML = '';
              if (!folders || folders.length === 0) {
                var opt = document.createElement('option');
                opt.value = 'SimplyHealth';
                opt.textContent = 'SimplyHealth';
                sel.appendChild(opt);
                return;
              }
              for (var i = 0; i < folders.length; i++) {
                var name = folders[i];
                var opt2 = document.createElement('option');
                opt2.value = name;
                opt2.textContent = name;
                sel.appendChild(opt2);
              }
            })
            .catch(function(e) {
              // ignore
            });
          }

          function saveUser() {
            var uname = document.getElementById('newuser').value.trim();
            var upass = document.getElementById('newpass').value;
            var urole = document.getElementById('newrole').value;
            var ujobs = (document.getElementById('newjobsfolder').value.trim() || "SimplyHealth");
            var out = document.getElementById('adminout');
            out.textContent = "";

            if (!uname || !upass) {
              out.textContent = "Please provide username and password.";
              return;
            }

            fetch('/admin/users', {
              method: 'POST',
              headers: Object.assign(
                {'Content-Type': 'application/json'},
                authToken ? {'Authorization': 'Bearer ' + authToken} : {}
              ),
              body: JSON.stringify({
                username: uname,
                password: upass,
                role: urole,
                jobs_folder: ujobs
              })
            })
            .then(function(res) {
              return res.text().then(function(text) {
                out.textContent = text;
                if (res.ok) {
                  loadUsers();
                  document.getElementById('newpass').value = "";
                }
              });
            })
            .catch(function(e) {
              out.textContent = "Network error";
            });
          }

          function deleteUser() {
            var uname = document.getElementById('deluser').value.trim();
            var out = document.getElementById('adminout');
            out.textContent = "";

            if (!uname) {
              out.textContent = "Please provide username.";
              return;
            }

            fetch('/admin/users/delete', {
              method: 'POST',
              headers: Object.assign(
                {'Content-Type': 'application/json'},
                authToken ? {'Authorization': 'Bearer ' + authToken} : {}
              ),
              body: JSON.stringify({username: uname})
            })
            .then(function(res) {
              return res.text().then(function(text) {
                out.textContent = text;
                if (res.ok) {
                  loadUsers();
                  document.getElementById('deluser').value = "";
                }
              });
            })
            .catch(function(e) {
              out.textContent = "Network error";
            });
          }

          // -----------------------
          // ADMIN: FOLDERS & SCRIPTS
          // -----------------------
          function loadJobFolders(defaultFolder) {
            var folderSel = document.getElementById('folder-select');
            var scriptSel = document.getElementById('script-select');
            if (!folderSel || !scriptSel) return;

            fetch('/job-folders')
            .then(function(res) {
              if (!res.ok) return null;
              return res.json();
            })
            .then(function(folders) {
              if (!folders) return;
              folderSel.innerHTML = '';
              var placeholder = document.createElement('option');
              placeholder.value = '';
              placeholder.textContent = '-- folder --';
              folderSel.appendChild(placeholder);

              var i;
              for (i = 0; i < folders.length; i++) {
                var name = folders[i];
                var opt = document.createElement('option');
                opt.value = name;
                opt.textContent = name;
                folderSel.appendChild(opt);
              }

              var selected = '';
              if (defaultFolder && folders.indexOf(defaultFolder) !== -1) {
                selected = defaultFolder;
              } else if (folders.length > 0) {
                selected = folders[0];
              }

              if (selected) {
                folderSel.value = selected;
                loadJobs(selected);
              } else {
                scriptSel.innerHTML = '';
                var ph = document.createElement('option');
                ph.value = '';
                ph.textContent = '-- script --';
                scriptSel.appendChild(ph);
              }
            })
            .catch(function(e) {
              // ignore
            });
          }

          function loadJobs(folderName) {
            var sel = document.getElementById('script-select');
            if (!sel) return;

            fetch('/jobs?folder=' + encodeURIComponent(folderName))
            .then(function(res) {
              if (!res.ok) return null;
              return res.json();
            })
            .then(function(jobs) {
              if (!jobs) return;

              sel.innerHTML = '';
              var placeholder = document.createElement('option');
              placeholder.value = '';
              placeholder.textContent = '-- script --';
              sel.appendChild(placeholder);

              for (var i = 0; i < jobs.length; i++) {
                var name = jobs[i];
                var opt = document.createElement('option');
                opt.value = name;
                opt.textContent = name + '.py';
                sel.appendChild(opt);
              }
              // ⭐ Automatically select main_script if present
              if (jobs.includes("main_script")) {
                sel.value = "main_script";
              }
            })
            .catch(function(e) {
              // ignore
            });
          }

          function onFolderChange() {
            var folderSel = document.getElementById('folder-select');
            if (!folderSel) return;
            var folder = folderSel.value;

            var scriptSel = document.getElementById('script-select');

            if (!folder) {
              if (scriptSel) {
                scriptSel.innerHTML = '';
                var ph = document.createElement('option');
                ph.value = '';
                ph.textContent = '-- script --';
                scriptSel.appendChild(ph);
              }
              return;
            }

            loadJobs(folder);
          }
        </script>



      </body>
    </html>
    """

