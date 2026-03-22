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

- ระบบสมาชิก — Register / Login (email หรือ username) / Logout / Edit Profile / Change Password / Upload Profile Picture
- Dashboard — สรุปรายรับ-รายจ่ายเดือนนี้, ยอดรวม All-time, Savings Rate, Doughnut Chart, Bar Chart 6 เดือน, Top 3 Spending, Budget Progress
- Transactions — บันทึกรายรับ-รายจ่าย, เลือก Date & Time, แนบสลิป (Pillow resize), ค้นหา, filter ตามประเภท, Pagination
- Categories — จัดการหมวดหมู่ + emoji icon, แยก Income / Expense, ค้นหา
- Budget — ตั้งงบประมาณรายเดือนต่อหมวดหมู่, Progress bar แสดง % การใช้จ่าย
- Landing Page — หน้าแรกสำหรับผู้ที่ยังไม่ได้ login
- UX — Loading spinner, Confirm modal ก่อนลบ, Flash messages, Responsive design, Error pages 404/500

---

## Database

มี 4 ตาราง ได้แก่ `user`, `category`, `transaction`, `budget`