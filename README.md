# 💸 MoneyTracker เว็บแอปบันทึกและติดตามรายรับ-รายจ่าย
 Mini Project วิชา Web Application Development

---

## Tech Stack

- **Backend:** Python 3.11, Flask, Flask-Blueprint, Flask-Login, Flask-Bcrypt, Flask-WTF, Flask-Migrate
- **Frontend:** Bootstrap 5.3, Chart.js, Jinja2
- **Database:** PostgreSQL (Render.com)
- **Tools:** uv, Git, Gunicorn

---

## Features

- ระบบสมาชิก — Register / Login (email หรือ username) / Logout / Edit Profile
- Dashboard — สรุปรายรับ-รายจ่าย, Chart รายเดือน, Budget Progress
- Transactions — บันทึกรายรับ-รายจ่าย, แนบสลิป, ค้นหา, filter
- Categories — จัดการหมวดหมู่ + emoji icon
- Budget — ตั้งงบประมาณรายเดือน พร้อม progress bar

---

## Database

มี 4 ตาราง ได้แก่ `user`, `category`, `transaction`, `budget`