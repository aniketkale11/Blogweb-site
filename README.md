
# 📝 FastAPI Blog Website

A full-stack **FastAPI blog website** where users can create posts, like, comment, and manage their accounts.
Built with FastAPI, SQLAlchemy, Jinja2, and modern HTML/CSS.

---

## 🔹 Features

* User Authentication (Login / Logout / Register / Forgot Password)
* Create, Edit, Delete Posts
* Like / Unlike Posts ❤️
* Comment System 💬 (Edit / Delete) only by owner
* Follow / Unfollow Users 🔄
* Add Images, Videos, and Audio to Posts 📸🎥🎵
* Search Posts 🔍
* Flash Messages & Proper Redirects
* Session Management to prevent stale sessions
* Responsive and modern UI

---

## 🔹 Tech Stack

* **Backend:** FastAPI, SQLAlchemy
* **Frontend:** HTML, CSS, Jinja2 Templates
* **Database:** SQLite
* **Server:** Uvicorn
* **Session Management:** Starlette SessionMiddleware

---

## 🔹 Installation

1. Clone the repository:

```bash
git clone https://github.com/aniketkale11/Blogweb-site.git
cd Blogweb-site
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the FastAPI server:

```bash
uvicorn main:app --reload
```

