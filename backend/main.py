# -*- coding: utf-8 -*-
"""
FardaPack Mini-CRM — Backend API (FastAPI + SQLite)
نسخه نهایی بدون pandas و کاملاً قابل اجرا روی Render
"""

# ====================== 1. وارد کردن کتابخانه‌ها ======================
import sqlite3
from datetime import datetime, date, timedelta
from typing import Optional, List, Tuple, Dict, Any

# ❌ pandas حذف شده (این خط واردات هم حذف شد)
import hashlib
import uuid
import os, io, zipfile, shutil

# 👇 کتابخانه‌های FastAPI
from fastapi import FastAPI, Depends, HTTPException, status, Query, Body, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, HTMLResponse 
from fastapi.staticfiles import StaticFiles 
from pydantic import BaseModel, Field

# ====================== 2. راه‌اندازی FastAPI و CORS ======================

app = FastAPI(
    title="FardaPack CRM API",
    description="API بک‌اند برای مینی CRM فرداپک",
    version="1.0.0"
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ سرو فایل‌های استاتیک
try:
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
    else:
        print("⚠️ پوشه static یافت نشد. (در حالت لوکال مشکلی نیست)")
except Exception as e:
    print(f"⚠️ عدم توانایی در لود static: {e}")


# ====================== 3. مدل‌های داده (Pydantic) ======================
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    token: str
    username: str
    role: str

class UserAuthInfo(BaseModel):
    id: int
    username: str
    role: str
    linked_user_id: Optional[int] = None

class MessageResponse(BaseModel):
    message: str

class CompanyCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    note: Optional[str] = None
    level: str = "هیچکدام"
    status: str = "بدون وضعیت"

class CompanyUpdate(CompanyCreate):
    pass

class UserCreate(BaseModel):
    first_name: str
    last_name: Optional[str] = None 
    phone: str
    role: Optional[str] = None
    company_id: Optional[int] = None
    note: Optional[str] = None
    status: str = "بدون وضعیت"
    domain: Optional[str] = None
    province: Optional[str] = None
    level: str = "هیچکدام"
    owner_id: Optional[int] = None

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    company_id: Optional[int] = None
    note: Optional[str] = None
    status: Optional[str] = None
    domain: Optional[str] = None
    province: Optional[str] = None
    level: Optional[str] = None
    owner_id: Optional[int] = None

class CallCreate(BaseModel):
    user_id: int
    call_datetime: datetime
    status: str
    description: Optional[str] = None

class FollowupCreate(BaseModel):
    user_id: int
    title: str
    details: Optional[str] = None
    due_date: datetime
    status: str = "در حال انجام"

class FollowupStatusUpdate(BaseModel):
    status: str

class ProductCreate(BaseModel):
    category: str
    name: str

class OrderCreate(BaseModel):
    user_id: Optional[int] = None
    company_id: Optional[int] = None
    product_id: int
    order_date: date
    status: str = "در حال پیگیری"
    total_amount: float

class AppUserCreate(BaseModel):
    username: str
    password: str
    role: str
    linked_user_id: Optional[int] = None

class BulkOwnerUpdate(BaseModel):
    user_ids: List[int]
    new_owner_id: Optional[int] = None

class PasswordUpdate(BaseModel):
    new_password: str


# ====================== 4. توابع کمکی (تاریخ شمسی و ...) ======================
try:
    from persiantools.jdatetime import JalaliDate, JalaliDateTime
except Exception:
    JalaliDate = None
    JalaliDateTime = None

def _jalali_supported() -> bool:
    return JalaliDate is not None

def today_jalali_str() -> str:
    return JalaliDate.today().strftime("%Y/%m/%d") if _jalali_supported() else ""

def jalali_str_to_date(s: str) -> Optional[date]:
    if not s or not _jalali_supported(): return None
    try:
        g = JalaliDate.strptime(s.strip(), "%Y/%m/%d").to_gregorian()
        return date(g.year, g.month, g.day)
    except Exception: return None

def date_to_jalali_str(d: date) -> str:
    if not d or not _jalali_supported(): return ""
    try:
        return JalaliDate.fromgregorian(date=d).strftime("%Y/%m/%d")
    except Exception: return ""

def dt_to_jalali_str(dt_iso_or_none: Optional[str]) -> str:
    if not dt_iso_or_none or not _jalali_supported(): return dt_iso_or_none or ""
    try:
        if "T" in dt_iso_or_none: gdt = datetime.fromisoformat(dt_iso_or_none)
        else:
            try: gdt = datetime.strptime(dt_iso_or_none, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try: gdt = datetime.strptime(dt_iso_or_none, "%Y-%m-%d %H:%M")
                except ValueError: gdt = datetime.strptime(dt_iso_or_none, "%Y-%m-%d")
        jdt = JalaliDateTime.fromgregorian(datetime=gdt)
        return jdt.strftime("%Y/%m/%d %H:%M")
    except Exception: return dt_iso_or_none

# ====================== 5. دیتابیس و CRUD ======================
DB_PATH = "crm.db"
CALL_STATUSES = ["ناموفق", "موفق", "خاموش", "رد تماس"]
TASK_STATUSES = ["در حال انجام", "پایان یافته"]
USER_STATUSES = ["بدون وضعیت", "در حال پیگیری", "پیش فاکتور", "مشتری شد", "لغو"]
COMPANY_STATUSES = ["بدون وضعیت", "در حال پیگیری", "پیش فاکتور", "مشتری شد"]
LEVELS = ["هیچکدام", "طلایی", "نقره‌ای", "برنز"]
ORDER_STATUSES = ["در حال پیگیری", "تایید شده", "کنسل شده", "رد شده"]

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    return conn

def sha256(txt: str) -> str:
    return hashlib.sha256((txt or "").encode("utf-8")).hexdigest()

def _column_exists(conn: sqlite3.Connection, table: str, col: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table});").fetchall()
    return any(r[1] == col for r in rows)

def init_db():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, phone TEXT, address TEXT, note TEXT,
            level TEXT NOT NULL DEFAULT 'هیچکدام',
            status TEXT NOT NULL DEFAULT 'بدون وضعیت',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP, created_by INTEGER
        );
    """)
    if not _column_exists(conn, "companies", "status"):
        cur.execute("ALTER TABLE companies ADD COLUMN status TEXT NOT NULL DEFAULT 'بدون وضعیت';")
    if not _column_exists(conn, "companies", "level"):
        cur.execute("ALTER TABLE companies ADD COLUMN level TEXT NOT NULL DEFAULT 'هیچکدام';")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT, last_name TEXT, full_name TEXT NOT NULL,
            phone TEXT UNIQUE, role TEXT, company_id INTEGER, note TEXT,
            status TEXT NOT NULL DEFAULT 'بدون وضعیت',
            domain TEXT, province TEXT,
            level TEXT NOT NULL DEFAULT 'هیچکدام',
            owner_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP, created_by INTEGER,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE SET NULL
        );
    """)
    for col, default in [
        ("first_name", None), ("last_name", None), ("domain", None), ("province", None),
        ("level", "'هیچکدام'"), ("owner_id", None)
    ]:
        if not _column_exists(conn, "users", col):
            cur.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT" + (f" DEFAULT {default}" if default else "") + ";")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, call_datetime TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('ناموفق','موفق','خاموش','رد تماس')),
            description TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, created_by INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS followups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, title TEXT NOT NULL, details TEXT,
            due_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('در حال انجام','پایان یافته')) DEFAULT 'در حال انجام',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP, created_by INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS app_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL, password_sha256 TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','agent')) DEFAULT 'agent',
            linked_user_id INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(linked_user_id) REFERENCES users(id) ON DELETE SET NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            app_user_id INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP, expires_at TEXT,
            FOREIGN KEY(app_user_id) REFERENCES app_users(id) ON DELETE CASCADE
        );
    """)
    cur.execute(""" 
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL,
            name TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, company_id INTEGER,
            product_id INTEGER, order_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'در حال پیگیری',
            total_amount REAL NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE SET NULL,
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE SET NULL
        );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_company ON users(company_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_owner ON users(owner_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_calls_user_datetime ON calls(user_id, call_datetime);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_followups_user_due ON followups(user_id, due_date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(app_user_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_company ON orders(company_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_product ON orders(product_id);")
    if cur.execute("SELECT COUNT(*) FROM app_users;").fetchone()[0] == 0:
        cur.execute("INSERT INTO app_users (username, password_sha256, role) VALUES (?,?,?);",
                    ("admin", sha256("admin123"), "admin"))
    conn.commit(); conn.close()

# --- توابع Auth ---
def create_session(app_user_id: int, days_valid: int = 30) -> str:
    token = uuid.uuid4().hex
    expires = (datetime.utcnow() + timedelta(days=days_valid)).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_conn()
    conn.execute("INSERT INTO sessions (token, app_user_id, expires_at) VALUES (?,?,?);",
                 (token, app_user_id, expires))
    conn.commit(); conn.close()
    return token

def get_session_user(token: str) -> Optional[UserAuthInfo]:
    if not token: return None
    conn = get_conn()
    row = conn.execute("""
        SELECT au.id, au.username, au.role, au.linked_user_id
        FROM sessions s
        JOIN app_users au ON au.id = s.app_user_id
        WHERE s.token=? AND (s.expires_at IS NULL OR s.expires_at >= datetime('now'));
    """, (token,)).fetchone()
    conn.close()
    if not row: return None
    return UserAuthInfo(**row)

def delete_session(token: str):
    if not token: return
    conn = get_conn()
    conn.execute("DELETE FROM sessions WHERE token=?;", (token,))
    conn.commit(); conn.close()

def auth_check(username: str, password: str):
    conn = get_conn()
    row = conn.execute("SELECT id, username, password_sha256, role, linked_user_id FROM app_users WHERE username=?;",
                       ((username or "").strip(),)).fetchone()
    conn.close()
    if not row: return None
    uid, uname, pwh, role, linked_user_id = row
    return {"id": uid, "username": uname, "role": role, "linked_user_id": linked_user_id} if sha256(password) == pwh else None

# --- توابع CRUD ---
def list_companies(_: Optional[int]) -> List[Tuple[int, str]]:
    conn = get_conn()
    rows = conn.execute("SELECT id, name FROM companies ORDER BY name COLLATE NOCASE;").fetchall()
    conn.close(); return [tuple(r) for r in rows]

def list_sales_accounts_including_admins() -> List[Dict]:
    conn = get_conn()
    rows = conn.execute("SELECT id, username, role FROM app_users WHERE role IN ('agent','admin') ORDER BY role DESC, username;").fetchall()
    conn.close(); return [dict(r) for r in rows]

def list_users_basic(only_owner_appuser: Optional[int]) -> List[Tuple[int, str, Optional[int]]]:
    conn = get_conn()
    if only_owner_appuser:
        rows = conn.execute(
            "SELECT id, full_name, company_id FROM users WHERE owner_id=? ORDER BY full_name COLLATE NOCASE;",
            (only_owner_appuser,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT id, full_name, company_id FROM users ORDER BY full_name COLLATE NOCASE;").fetchall()
    conn.close(); return [tuple(r) for r in rows]

def phone_exists(phone: str, ignore_user_id: Optional[int] = None) -> bool:
    ph = (phone or "").strip()
    if not ph: return False
    conn = get_conn()
    if ignore_user_id:
        row = conn.execute("SELECT 1 FROM users WHERE phone=? AND id<>?;", (ph, ignore_user_id)).fetchone()
    else:
        row = conn.execute("SELECT 1 FROM users WHERE phone=?;", (ph,)).fetchone()
    conn.close(); return row is not None

def create_company(company_data: CompanyCreate, creator_id: int):
    conn = get_conn()
    conn.execute(
        "INSERT INTO companies (name, phone, address, note, level, status, created_by) VALUES (?,?,?,?,?,?,?);",
        (
            company_data.name.strip(),
            (company_data.phone or "").strip(),
            (company_data.address or "").strip(),
            (company_data.note or "").strip(),
            company_data.level,
            company_data.status,
            creator_id
        )
    )
    conn.commit(); conn.close()

def update_company(company_id: int, company_data: CompanyUpdate):
    fields = company_data.dict(exclude_unset=True)
    sets, params = [], []
    for k, v in fields.items():
        sets.append(f"{k}=?"); params.append(v)
    if not sets:
        return True, "بدون تغییر"
    params.append(company_id)
    conn = get_conn()
    conn.execute(f"UPDATE companies SET {', '.join(sets)} WHERE id=?;", params)
    conn.commit(); conn.close(); return True, "ذخیره شد."

def create_user(user_data: UserCreate, creator_id: int) -> Tuple[bool, str]:
    if user_data.phone and phone_exists(user_data.phone):
        return False, "شماره تماس تکراری است."
    
    full_name = f"{(user_data.first_name or "").strip()} {(user_data.last_name or "").strip()}".strip()
    
    if not (user_data.first_name or "").strip(): 
        return False, "نام اجباری است."
    
    conn = get_conn()
    conn.execute("""INSERT INTO users
        (first_name,last_name,full_name,phone,role,company_id,note,status,domain,province,level,owner_id,created_by)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);""",
        (
            (user_data.first_name or "").strip(),
            (user_data.last_name or "").strip(),
            full_name,
            (user_data.phone or "").strip(),
            (user_data.role or "").strip(),
            user_data.company_id,
            (user_data.note or "").strip(),
            user_data.status,
            (user_data.domain or "").strip(),
            (user_data.province or "").strip(),
            user_data.level,
            user_data.owner_id,
            creator_id
        ))
    conn.commit(); conn.close(); return True, "کاربر ثبت شد."

def update_user(user_id: int, user_data: UserUpdate):
    if user_data.phone and phone_exists(user_data.phone, ignore_user_id=user_id):
        return False, "شماره تماس تکراری است."
    
    fields = user_data.dict(exclude_unset=True)
    if "first_name" in fields or "last_name" in fields:
        conn_read = get_conn()
        current = conn_read.execute("SELECT first_name, last_name FROM users WHERE id=?", (user_id,)).fetchone()
        conn_read.close()
        fn = fields.get("first_name", current["first_name"])
        ln = fields.get("last_name", current["last_name"])
        fields["full_name"] = f"{(fn or "").strip()} {(ln or "").strip()}".strip()

    sets, params = [], []
    for k, v in fields.items():
        sets.append(f"{k}=?"); params.append(v)
    if not sets:
        return True, "بدون تغییر"
    params.append(user_id)
    
    conn = get_conn()
    conn.execute(f"UPDATE users SET {', '.join(sets)} WHERE id=?;", params)
    conn.commit(); conn.close(); return True, "ذخیره شد."

def update_followup_status(task_id: int, new_status: str):
    conn = get_conn(); conn.execute("UPDATE followups SET status=? WHERE id=?;", (new_status, task_id))
    conn.commit(); conn.close()

def create_call(call_data: CallCreate, creator_id: int):
    conn = get_conn()
    conn.execute("INSERT INTO calls (user_id, call_datetime, status, description, created_by) VALUES (?,?,?,?,?);",
                (
                    call_data.user_id,
                    call_data.call_datetime.isoformat(),
                    call_data.status,
                    (call_data.description or "").strip(),
                    creator_id
                ))
    conn.commit(); conn.close()

def create_followup(fu_data: FollowupCreate, creator_id: int):
    conn = get_conn()
    conn.execute("INSERT INTO followups (user_id, title, details, due_date, status, created_by) VALUES (?,?,?,?,?,?);",
                (
                    fu_data.user_id,
                    (fu_data.title or "").strip(),
                    (fu_data.details or "").strip(),
                    fu_data.due_date.isoformat(),
                    fu_data.status,
                    creator_id
                ))
    conn.commit(); conn.close()

def bulk_update_users_owner(user_ids: List[int], new_owner_id: Optional[int], current_user: UserAuthInfo) -> int:
    """owner_id را برای لیست user_ids به‌صورت گروهی تغییر می‌دهد."""
    if not user_ids: return 0
    
    conn = get_conn()
    placeholders = ",".join(["?"] * len(user_ids))
    
    params: List = [new_owner_id] # 1. new_owner_id
    
    sql_query = f"UPDATE users SET owner_id=? WHERE id IN ({placeholders})"
    
    if current_user.role != 'admin':
        sql_query += " AND owner_id = ?"
        params.append(current_user.id) # 2. current_user.id (if needed)
        
    params.extend([int(x) for x in user_ids]) # 3. user_ids (always last)
    
    cur = conn.execute(sql_query, params)
    conn.commit(); conn.close()
    return cur.rowcount if hasattr(cur, "rowcount") else len(user_ids)

def get_company_id_by_name(name: str) -> Optional[int]:
    if not (name or "").strip(): return None
    conn = get_conn()
    row = conn.execute("SELECT id FROM companies WHERE name=?;", ((name or "").strip(),)).fetchone()
    conn.close()
    return row[0] if row else None

def get_or_create_company(name: str, creator_id: Optional[int]) -> Optional[int]:
    if not (name or "").strip(): return None
    cid = get_company_id_by_name(name)
    if cid: return cid
    comp_data = CompanyCreate(name=name)
    create_company(comp_data, creator_id)
    return get_company_id_by_name(name)

def get_app_user_id_by_username(username: str) -> Optional[int]:
    if not (username or "").strip(): return None
    conn = get_conn()
    row = conn.execute("SELECT id FROM app_users WHERE username=?;", ((username or "").strip(),)).fetchone()
    conn.close()
    return row[0] if row else None

# --- توابع محصولات و سفارشات ---
def list_products() -> List[Dict]:
    conn = get_conn()
    rows = conn.execute("SELECT id, category, name FROM products ORDER BY category, name;").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_product(prod_data: ProductCreate):
    conn = get_conn()
    conn.execute("INSERT INTO products (category, name) VALUES (?, ?);", (prod_data.category.strip(), prod_data.name.strip()))
    conn.commit()
    conn.close()

def update_product(product_id: int, prod_data: ProductCreate):
    conn = get_conn()
    conn.execute("UPDATE products SET category=?, name=? WHERE id=?;", (prod_data.category.strip(), prod_data.name.strip(), product_id))
    conn.commit()
    conn.close()

def create_order(order_data: OrderCreate):
    conn = get_conn()
    conn.execute("""
        INSERT INTO orders (user_id, company_id, product_id, order_date, status, total_amount)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (
        order_data.user_id,
        order_data.company_id,
        order_data.product_id,
        order_data.order_date.isoformat(),
        order_data.status,
        order_data.total_amount
    ))
    conn.commit()
    conn.close()

def update_order_status(order_id: int, new_status: str):
    conn = get_conn()
    conn.execute("UPDATE orders SET status=? WHERE id=?;", (new_status, order_id))
    conn.commit()
    conn.close()

def update_order(order_id: int, order_data: OrderCreate):
    fields = order_data.dict(exclude_unset=True)
    fields['order_date'] = fields['order_date'].isoformat()
    sets, params = [], []
    for k, v in fields.items():
        sets.append(f"{k}=?"); params.append(v)
    if not sets:
        return True, "بدون تغییر"
    params.append(order_id)
    conn = get_conn()
    conn.execute(f"UPDATE orders SET {', '.join(sets)} WHERE id=?;", params)
    conn.commit(); conn.close(); return True, "ذخیره شد."


# --- توابع گزارش‌گیری (بدون pandas) ---
def df_companies_advanced(q_name, f_status, f_level, created_from, created_to,
                          has_open_task, owner_ids_filter: Optional[List[int]], enforce_owner: Optional[int]):
    conn = get_conn(); params, where = [], []
    if q_name: where.append("c.name LIKE ?"); params.append(f"%{q_name.strip()}%")
    if f_status: where.append("c.status IN (" + ",".join(["?"]*len(f_status)) + ")"); params += f_status
    if f_level: where.append("c.level IN (" + ",".join(["?"]*len(f_level)) + ")"); params += f_level
    if created_from: where.append("date(c.created_at) >= ?"); params.append(created_from.isoformat())
    if created_to:    where.append("date(c.created_at) <= ?"); params.append(created_to.isoformat())
    if enforce_owner:
        where.append("EXISTS (SELECT 1 FROM users u WHERE u.company_id=c.id AND u.owner_id=?)")
        params.append(enforce_owner)
    if owner_ids_filter:
        placeholders = ",".join(["?"]*len(owner_ids_filter))
        where.append(f"EXISTS (SELECT 1 FROM users u WHERE u.company_id=c.id AND u.owner_id IN ({placeholders}))")
        params += owner_ids_filter
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    
    # جایگزین ساده بدون pandas
    query = f"""
      SELECT
        c.id AS ID, c.name AS نام_شرکت, COALESCE(c.phone,'') AS تلفن,
        COALESCE(c.status,'') AS وضعیت_شرکت, COALESCE(c.level,'') AS سطح_شرکت,
        c.created_at AS تاریخ_ایجاد,
        EXISTS(SELECT 1 FROM users u JOIN followups f ON f.user_id=u.id 
              WHERE u.company_id=c.id AND f.status='در حال انجام') AS پیگیری_باز_دارد,
        (
          SELECT GROUP_CONCAT(username, '، ')
          FROM (
            SELECT DISTINCT au.username AS username
            FROM users u LEFT JOIN app_users au ON au.id=u.owner_id 
            WHERE u.company_id=c.id AND au.username IS NOT NULL
          ) AS d
        ) AS کارشناس_فروش
      FROM companies c {where_sql} ORDER BY c.created_at DESC, c.id DESC
    """
    
    cur = conn.execute(query, params)
    columns = [description[0] for description in cur.description]
    results = []
    for row in cur.fetchall():
        row_dict = dict(zip(columns, row))
        # تبدیل پیگیری_باز_دارد به متن فارسی
        row_dict["پیگیری_باز_دارد"] = "دارد" if row_dict.get("پیگیری_باز_دارد") == 1 else "ندارد"
        results.append(row_dict)
    
    conn.close()
    return results

def df_users_advanced(first_q, last_q, phone_q, role_q, domain_q, created_from, created_to,
                      has_open_task, last_call_from, last_call_to,
                      statuses, levels, owner_ids_filter: Optional[List[int]], enforce_owner: Optional[int]):
    conn = get_conn(); params, where = [], []
    if first_q: where.append("u.first_name LIKE ?"); params.append(f"%{first_q.strip()}%")
    if last_q:  where.append("u.last_name  LIKE ?"); params.append(f"%{last_q.strip()}%")
    if phone_q: where.append("u.phone LIKE ?"); params.append(f"%{phone_q.strip()}%")
    if role_q:  where.append("u.role LIKE ?"); params.append(f"%{role_q.strip()}%")
    if domain_q: where.append("u.domain LIKE ?"); params.append(f"%{domain_q.strip()}%")
    if created_from: where.append("date(u.created_at) >= ?"); params.append(created_from.isoformat())
    if created_to:    where.append("date(u.created_at) <= ?"); params.append(created_to.isoformat())
    if statuses: where.append("u.status IN (" + ",".join(["?"]*len(statuses)) + ")"); params += statuses
    if levels: where.append("u.level IN (" + ",".join(["?"]*len(levels)) + ")"); params += levels

    if enforce_owner:
        where.append("u.owner_id=?"); params.append(enforce_owner)
    if owner_ids_filter:
        where.append("u.owner_id IN (" + ",".join(["?"]*len(owner_ids_filter)) + ")"); params += owner_ids_filter
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    query = f"""
      SELECT
        u.id AS ID, u.first_name AS نام, u.last_name AS نام_خانوادگی, u.full_name AS نام_کامل,
        COALESCE(c.name,'') AS شرکت, COALESCE(u.phone,'') AS تلفن,
        COALESCE(u.status,'') AS وضعیت_کاربر, COALESCE(u.level,'') AS سطح_کاربر,
        COALESCE(u.domain,'') AS حوزه_فعالیت, COALESCE(u.province,'') AS استان,
        u.created_at AS تاریخ_ایجاد, u.company_id AS ID_شرکت,
        
        (SELECT cl.call_datetime FROM calls cl WHERE cl.user_id=u.id ORDER BY cl.call_datetime DESC LIMIT 1) AS آخرین_تماس,
        (SELECT cl.status FROM calls cl WHERE cl.user_id=u.id ORDER BY cl.call_datetime DESC LIMIT 1) AS آخرین_وضعیت_تماس,
        
        EXISTS(SELECT 1 FROM followups f WHERE f.user_id=u.id AND f.status='در حال انجام') AS پیگیری_باز_دارد,
        (SELECT MAX(f2.due_date) FROM followups f2 WHERE f2.user_id=u.id AND f2.status='در حال انجام') AS آخرین_پیگیری_باز,
        COALESCE(au.username,'') AS کارشناس_فروش
      FROM users u
      LEFT JOIN companies c ON c.id=u.company_id
      LEFT JOIN app_users au ON au.id=u.owner_id
      {where_sql} ORDER BY u.created_at DESC, u.id DESC
    """
    
    cur = conn.execute(query, params)
    columns = [description[0] for description in cur.description]
    results = []
    for row in cur.fetchall():
        row_dict = dict(zip(columns, row))
        
        # فیلتر کردن بر اساس has_open_task
        if has_open_task is not None:
            has_open = row_dict.get("پیگیری_باز_دارد") == 1
            if has_open_task != has_open:
                continue
        
        # فیلتر کردن بر اساس تاریخ آخرین تماس
        if last_call_from and row_dict.get("آخرین_تماس"):
            try:
                last_call_date = datetime.fromisoformat(row_dict["آخرین_تماس"]).date()
                if last_call_date < last_call_from:
                    continue
            except:
                pass
                
        if last_call_to and row_dict.get("آخرین_تماس"):
            try:
                last_call_date = datetime.fromisoformat(row_dict["آخرین_تماس"]).date()
                if last_call_date > last_call_to:
                    continue
            except:
                pass
        
        # تبدیل وضعیت پیگیری به متن فارسی
        if row_dict.get("پیگیری_باز_دارد") == 0 or not row_dict.get("آخرین_پیگیری_باز"):
            row_dict["وضعیت_پیگیری_باز"] = "ندارد"
        else:
            row_dict["وضعیت_پیگیری_باز"] = row_dict.get("آخرین_پیگیری_باز", "")
            
        results.append(row_dict)
    
    conn.close()
    return results

def df_calls_by_filters(name_query, statuses, start, end,
                          owner_ids_filter: Optional[List[int]], enforce_owner: Optional[int]):
    conn = get_conn(); params, where = [], ["1=1"]
    if name_query:
        where.append("(u.full_name LIKE ? OR c.name LIKE ?)"); q=f"%{name_query.strip()}%"; params += [q,q]
    if statuses: where.append("cl.status IN (" + ",".join(["?"]*len(statuses)) + ")"); params += statuses
    if start: where.append("date(cl.call_datetime) >= ?"); params.append(start.isoformat())
    if end:    where.append("date(cl.call_datetime) <= ?"); params.append(end.isoformat())
    if enforce_owner: where.append("u.owner_id=?"); params.append(enforce_owner)
    if owner_ids_filter: where.append("u.owner_id IN (" + ",".join(["?"]*len(owner_ids_filter)) + ")"); params += owner_ids_filter
    
    query = f"""
        SELECT cl.id AS ID, u.full_name AS نام_کاربر, COALESCE(c.name,'') AS شرکت,
                cl.call_datetime AS تاریخ_و_زمان, cl.status AS وضعیت, 
                COALESCE(cl.description,'') AS توضیحات, u.id AS ID_کاربر,
                COALESCE(au.username,'') AS کارشناس_فروش
        FROM calls cl
        JOIN users u ON u.id=cl.user_id
        LEFT JOIN companies c ON c.id=u.company_id
        LEFT JOIN app_users au ON au.id=u.owner_id
        WHERE {' AND '.join(where)}
        ORDER BY cl.call_datetime DESC, cl.id DESC
    """
    
    cur = conn.execute(query, params)
    columns = [description[0] for description in cur.description]
    results = [dict(zip(columns, row)) for row in cur.fetchall()]
    
    conn.close()
    return results

def df_followups_by_filters(name_query, statuses, start, end,
                            owner_ids_filter: Optional[List[int]], enforce_owner: Optional[int]):
    conn = get_conn(); params, where = [], ["1=1"]
    if name_query:
        where.append("(u.full_name LIKE ? OR c.name LIKE ?)"); q=f"%{name_query.strip()}%"; params += [q,q]
    if statuses: where.append("f.status IN (" + ",".join(["?"]*len(statuses)) + ")"); params += statuses
    if start: where.append("date(f.due_date) >= ?"); params.append(start.isoformat())
    if end:    where.append("date(f.due_date) <= ?"); params.append(end.isoformat())
    if enforce_owner: where.append("u.owner_id=?"); params.append(enforce_owner)
    if owner_ids_filter: where.append("u.owner_id IN (" + ",".join(["?"]*len(owner_ids_filter)) + ")"); params += owner_ids_filter
    
    query = f"""
        SELECT f.id AS ID, u.full_name AS نام_کاربر, COALESCE(c.name,'') AS شرکت,
                f.title AS عنوان, COALESCE(f.details,'') AS جزئیات,
                f.due_date AS تاریخ_پیگیری, f.status AS وضعیت, u.id AS ID_کاربر,
                COALESCE(au.username,'') AS کارشناس_فروش
        FROM followups f
        JOIN users u ON u.id=f.user_id
        LEFT JOIN companies c ON c.id=u.company_id
        LEFT JOIN app_users au ON au.id=u.owner_id
        WHERE {' AND '.join(where)}
        ORDER BY f.due_date DESC, f.id DESC
    """
    
    cur = conn.execute(query, params)
    columns = [description[0] for description in cur.description]
    results = [dict(zip(columns, row)) for row in cur.fetchall()]
        
    conn.close()
    return results

def df_orders_by_filters(user_filter: Optional[int] = None, company_filter: Optional[int] = None,
                          product_filter: Optional[int] = None, status_filter: Optional[str] = None):
    conn = get_conn(); params, where = [], ["1=1"]
    if user_filter: where.append("o.user_id = ?"); params.append(user_filter)
    if company_filter: where.append("o.company_id = ?"); params.append(company_filter)
    if product_filter: where.append("o.product_id = ?"); params.append(product_filter)
    if status_filter and status_filter != "همه":
        where.append("o.status = ?"); params.append(status_filter)
    where_sql = "WHERE " + " AND ".join(where)

    query = f"""
        SELECT 
            o.id AS ID, COALESCE(u.full_name, '—') AS کاربر,
            COALESCE(c.name, '—') AS شرکت, p.name AS محصول, p.category AS دسته_بندی,
            o.order_date AS تاریخ_سفارش, o.total_amount AS مبلغ_کل,
            o.status AS وضعیت, o.created_at AS تاریخ_ایجاد
        FROM orders o
        LEFT JOIN users u ON u.id = o.user_id
        LEFT JOIN companies c ON c.id = o.company_id
        LEFT JOIN products p ON p.id = o.product_id
        {where_sql} ORDER BY o.created_at DESC;
    """
    
    cur = conn.execute(query, params)
    columns = [description[0] for description in cur.description]
    results = []
    for row in cur.fetchall():
        row_dict = dict(zip(columns, row))
        # فرمت کردن مبلغ
        if "مبلغ_کل" in row_dict and row_dict["مبلغ_کل"]:
            try:
                row_dict["مبلغ_کل"] = f"{float(row_dict['مبلغ_کل']):,.0f}"
            except:
                pass
        results.append(row_dict)
    
    conn.close()
    return results

# --- توابع بکاپ ---
def extract_db_from_zip(zip_bytes: bytes) -> Optional[bytes]:
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
            for info in zf.infolist():
                if info.filename.lower().endswith(".db"):
                    return zf.read(info)
    except Exception:
        return None
    return None

def validate_db_file(path: str) -> Tuple[bool, str]:
    try:
        conn = sqlite3.connect(path, timeout=5)
        cur = conn.cursor()
        chk = cur.execute("PRAGMA integrity_check;").fetchone()
        if not chk or str(chk[0]).lower() != "ok":
            conn.close()
            return False, f"integrity_check ناموفق: {chk[0] if chk else 'نامشخص'}"
        required = {"companies","users","calls","followups","app_users","sessions","products","orders"}
        rows = cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        have = {r[0] for r in rows}
        missing = required - have
        conn.close()
        if missing:
            if missing - {"sessions"}:
                return False, f"جدول(های) ضروری موجود نیست: {', '.join(sorted(missing))}"
        return True, "ok"
    except Exception as e:
        return False, str(e)


# ====================== 6. سیستم احراز هویت API ======================

token_auth_scheme = HTTPBearer()

def get_current_auth_user(creds: HTTPAuthorizationCredentials = Depends(token_auth_scheme)) -> UserAuthInfo:
    token = creds.credentials
    user_info = get_session_user(token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن نامعتبر یا منقضی شده است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_info

# ✅ تابع get_admin_user اضافه شد
def get_admin_user(current_user: UserAuthInfo = Depends(get_current_auth_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="دسترسی فقط برای مدیر مجاز است",
        )
    return current_user

# ====================== 7. اندپوینت‌های API ======================

@app.on_event("startup")
async def startup_event():
    if not os.path.exists(DB_PATH):
        init_db()
        print("Database initialized with default data.")
    else:
        print("Existing crm.db found.")
    print(f"Database at {DB_PATH} is ready.")

@app.get("/api", tags=["General"])
def get_root():
    return {"message": "FardaPack CRM API در حال اجرا است."}

@app.get("/api/dashboard-stats", tags=["General"])
async def get_dashboard_stats(current_user: UserAuthInfo = Depends(get_current_auth_user)):
    """
    آمار کلی داشبورد را برمی‌گرداند
    """
    conn = get_conn()
    
    owner_clause = ""
    params = ()
    if current_user.role != 'admin':
        owner_clause = f" WHERE owner_id = {current_user.id} "
        owner_clause_joined_calls = f" WHERE u.owner_id = {current_user.id} "
        owner_clause_joined_followups = f" WHERE u.owner_id = {current_user.id} "
    else:
        owner_clause = ""
        owner_clause_joined_calls = ""
        owner_clause_joined_followups = ""


    calls_today = conn.execute(f"""
        SELECT COUNT(cl.id) FROM calls cl 
        JOIN users u ON u.id=cl.user_id 
        {owner_clause_joined_calls}
        {'AND' if owner_clause_joined_calls else 'WHERE'} date(cl.call_datetime)=date('now');
    """).fetchone()[0]
    
    calls_success_today = conn.execute(f"""
        SELECT COUNT(cl.id) FROM calls cl
        JOIN users u ON u.id=cl.user_id
        {owner_clause_joined_calls}
        {'AND' if owner_clause_joined_calls else 'WHERE'} date(cl.call_datetime)=date('now') AND cl.status='موفق';
    """).fetchone()[0]

    last7 = conn.execute(f"""
        SELECT COUNT(cl.id) FROM calls cl
        JOIN users u ON u.id=cl.user_id
        {owner_clause_joined_calls}
        {'AND' if owner_clause_joined_calls else 'WHERE'} date(cl.call_datetime) >= date('now','-7 day');
    """).fetchone()[0]
    
    overdue = conn.execute(f"""
        SELECT COUNT(f.id) FROM followups f
        JOIN users u ON u.id=f.user_id
        {owner_clause_joined_followups}
        {'AND' if owner_clause_joined_followups else 'WHERE'} f.status='در حال انجام' AND date(f.due_date) < date('now');
    """).fetchone()[0]

    total_companies = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    total_users = conn.execute(f"SELECT COUNT(*) FROM users {owner_clause}").fetchone()[0]
    
    conn.close()
    
    return {
        "calls_today": calls_today,
        "calls_success_today": calls_success_today,
        "last_7_days_calls": last7,
        "overdue_followups": overdue,
        "total_companies": total_companies,
        "total_users": total_users,
    }

# --- اندپوینت‌های Auth ---
@app.post("/api/login", response_model=TokenResponse, tags=["Auth"])
async def login_for_access_token(data: LoginRequest):
    user = auth_check(data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="نام کاربری یا رمز عبور اشتباه است",
        )
    token = create_session(app_user_id=user["id"], days_valid=30)
    return TokenResponse(token=token, username=user["username"], role=user["role"])

@app.post("/api/logout", response_model=MessageResponse, tags=["Auth"])
async def logout(current_user: UserAuthInfo = Depends(get_current_auth_user),
                  creds: HTTPAuthorizationCredentials = Depends(token_auth_scheme)):
    delete_session(creds.credentials)
    return {"message": "خروج با موفقیت انجام شد"}

@app.get("/api/me", response_model=UserAuthInfo, tags=["Auth"])
async def read_users_me(current_user: UserAuthInfo = Depends(get_current_auth_user)):
    return current_user

# --- اندپوینت‌های Users ---
@app.get("/api/users", response_model=List[Dict], tags=["Users"])
async def get_users_list(
    first_q: Optional[str] = None,
    last_q: Optional[str] = None,
    phone_q: Optional[str] = None, 
    role_q: Optional[str] = None, 
    domain_q: Optional[str] = None,
    created_from: Optional[date] = None,
    created_to: Optional[date] = None,
    has_open_task: Optional[bool] = None,
    last_call_from: Optional[date] = None,
    last_call_to: Optional[date] = None,
    statuses: Optional[List[str]] = Query(None),
    levels: Optional[List[str]] = Query(None), 
    owner_ids_filter: Optional[List[int]] = Query(None),
    current_user: UserAuthInfo = Depends(get_current_auth_user)
):
    enforce_owner = None if current_user.role == "admin" else current_user.id
    
    users_data = df_users_advanced(
        first_q=first_q, last_q=last_q, 
        phone_q=phone_q, role_q=role_q, 
        domain_q=domain_q,
        created_from=created_from, created_to=created_to,
        has_open_task=has_open_task,
        last_call_from=last_call_from, last_call_to=last_call_to,
        statuses=statuses or [],
        levels=levels or [], 
        owner_ids_filter=owner_ids_filter or [],
        enforce_owner=enforce_owner
    )
    return users_data

@app.post("/api/users", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
async def create_new_user(user_data: UserCreate, current_user: UserAuthInfo = Depends(get_current_auth_user)):
    ok, msg = create_user(user_data, current_user.id)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.put("/api/users/bulk-owner", response_model=MessageResponse, tags=["Users"])
async def bulk_update_owner(data: BulkOwnerUpdate, current_user: UserAuthInfo = Depends(get_current_auth_user)):
    affected = bulk_update_users_owner(data.user_ids, data.new_owner_id, current_user)
    return {"message": f"کارشناس فروش {affected} مخاطب تغییر کرد."}

@app.put("/api/users/{user_id}", response_model=MessageResponse, tags=["Users"])
async def update_existing_user(user_id: int, user_data: UserUpdate, current_user: UserAuthInfo = Depends(get_current_auth_user)):
    ok, msg = update_user(user_id, user_data)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

# ❌ توابع import/export اکسل غیرفعال شدند
@app.get("/api/users/import-template", tags=["Users"])
async def download_excel_template(current_user: UserAuthInfo = Depends(get_admin_user)):
    raise HTTPException(
        status_code=501, 
        detail="امکان دانلود قالب اکسل در حال حاضر وجود ندارد. لطفاً از طریق رابط کاربری اقدام کنید."
    )

@app.post("/api/users/import-excel", response_model=Dict[str, Any], tags=["Users"])
async def import_users_from_excel(
    file: UploadFile = File(...), 
    current_user: UserAuthInfo = Depends(get_admin_user)
):
    raise HTTPException(
        status_code=501, 
        detail="امکان ایمپورت از اکسل در حال حاضر وجود ندارد. لطفاً کاربران را به صورت دستی اضافه کنید."
    )

@app.get("/api/users/{user_id}/profile", tags=["Users"])
async def get_user_profile(user_id: int, current_user: UserAuthInfo = Depends(get_current_auth_user)):
    conn = get_conn()
    u = conn.execute("""
        SELECT u.id, u.first_name, u.last_name, u.full_name, c.name AS company_name, u.phone,
                u.role, u.status, u.level, u.domain, u.province,
                u.note, u.created_at, u.company_id, au.username AS sales_user
        FROM users u
        LEFT JOIN companies c ON c.id=u.company_id
        LEFT JOIN app_users au ON au.id=u.owner_id
        WHERE u.id=?;
    """, (user_id,)).fetchone()
    if not u:
        conn.close()
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")

    calls = conn.execute("SELECT * FROM calls WHERE user_id=? ORDER BY call_datetime DESC", (user_id,)).fetchall()
    followups = conn.execute("SELECT * FROM followups WHERE user_id=? ORDER BY due_date DESC", (user_id,)).fetchall()
    
    colleagues = []
    if u["company_id"]:
        colleagues = conn.execute("SELECT id, full_name, phone, role FROM users WHERE company_id=? AND id<>?", 
                                 (u["company_id"], user_id)).fetchall()
    conn.close()
    
    return {
        "info": dict(u),
        "calls": [dict(c) for c in calls],
        "followups": [dict(f) for f in followups],
        "colleagues": [dict(c) for c in colleagues]
    }

# --- اندپوینت‌های Companies ---
@app.get("/api/companies", response_model=List[Dict], tags=["Companies"])
async def get_companies_list(
    q_name: Optional[str] = None,
    f_status: Optional[List[str]] = Query(None),
    f_level: Optional[List[str]] = Query(None),
    created_from: Optional[date] = None,
    created_to: Optional[date] = None,
    has_open_task: Optional[bool] = None,
    owner_ids_filter: Optional[List[int]] = Query(None),
    current_user: UserAuthInfo = Depends(get_current_auth_user)
):
    enforce_owner = None if current_user.role == "admin" else current_user.id
    companies_data = df_companies_advanced(
        q_name=q_name, f_status=f_status or [], f_level=f_level or [],
        created_from=created_from, created_to=created_to,
        has_open_task=has_open_task,
        owner_ids_filter=owner_ids_filter or [],
        enforce_owner=enforce_owner
    )
    return companies_data

@app.post("/api/companies", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, tags=["Companies"])
async def create_new_company(company_data: CompanyCreate, current_user: UserAuthInfo = Depends(get_current_auth_user)):
    create_company(company_data, current_user.id)
    return {"message": "شرکت ثبت شد"}

@app.get("/api/companies/{company_id}/profile", tags=["Companies"])
async def get_company_profile(company_id: int, current_user: UserAuthInfo = Depends(get_current_auth_user)):
    conn = get_conn()
    c = conn.execute("SELECT * FROM companies WHERE id=?", (company_id,)).fetchone()
    if not c:
        conn.close()
        raise HTTPException(status_code=404, detail="شرکت یافت نشد")

    users = conn.execute("SELECT id, full_name, phone, role FROM users WHERE company_id=?", (company_id,)).fetchall()
    calls = conn.execute("SELECT cl.* FROM calls cl JOIN users u ON u.id=cl.user_id WHERE u.company_id=? ORDER BY cl.call_datetime DESC", (company_id,)).fetchall()
    followups = conn.execute("SELECT f.* FROM followups f JOIN users u ON u.id=f.user_id WHERE u.company_id=? ORDER BY f.due_date DESC", (company_id,)).fetchall()
    conn.close()
    
    return {
        "info": dict(c),
        "users": [dict(u) for u in users],
        "calls": [dict(c) for c in calls],
        "followups": [dict(f) for f in followups]
    }

@app.put("/api/companies/{company_id}", response_model=MessageResponse, tags=["Companies"])
async def update_existing_company(company_id: int, company_data: CompanyUpdate, current_user: UserAuthInfo = Depends(get_current_auth_user)):
    ok, msg = update_company(company_id, company_data)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

# --- اندپوینت‌های Calls ---
@app.get("/api/calls", response_model=List[Dict], tags=["Calls"])
async def get_calls_list(
    name_query: Optional[str] = None,
    statuses: Optional[List[str]] = Query(None),
    start: Optional[date] = None,
    end: Optional[date] = None,
    owner_ids_filter: Optional[List[int]] = Query(None),
    current_user: UserAuthInfo = Depends(get_current_auth_user)
):
    enforce_owner = None if current_user.role == "admin" else current_user.id
    calls_data = df_calls_by_filters(
        name_query=name_query, statuses=statuses or [],
        start=start, end=end,
        owner_ids_filter=owner_ids_filter or [],
        enforce_owner=enforce_owner
    )
    return calls_data

@app.post("/api/calls", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, tags=["Calls"])
async def create_new_call(call_data: CallCreate, current_user: UserAuthInfo = Depends(get_current_auth_user)):
    create_call(call_data, current_user.id)
    return {"message": "تماس ثبت شد"}

# --- اندپوینت‌های Followups ---
@app.get("/api/followups", response_model=List[Dict], tags=["Followups"])
async def get_followups_list(
    name_query: Optional[str] = None,
    statuses: Optional[List[str]] = Query(None),
    start: Optional[date] = None,
    end: Optional[date] = None,
    owner_ids_filter: Optional[List[int]] = Query(None),
    current_user: UserAuthInfo = Depends(get_current_auth_user)
):
    enforce_owner = None if current_user.role == "admin" else current_user.id
    followups_data = df_followups_by_filters(
        name_query=name_query, statuses=statuses or [],
        start=start, end=end,
        owner_ids_filter=owner_ids_filter or [],
        enforce_owner=enforce_owner
    )
    return followups_data

@app.post("/api/followups", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, tags=["Followups"])
async def create_new_followup(fu_data: FollowupCreate, current_user: UserAuthInfo = Depends(get_current_auth_user)):
    create_followup(fu_data, current_user.id)
    return {"message": "پیگیری ثبت شد"}

@app.put("/api/followups/{task_id}/status", response_model=MessageResponse, tags=["Followups"])
async def update_task_status(task_id: int, data: FollowupStatusUpdate, current_user: UserAuthInfo = Depends(get_current_auth_user)):
    if data.status not in TASK_STATUSES:
        raise HTTPException(status_code=400, detail="وضعیت نامعتبر است")
    update_followup_status(task_id, data.status)
    return {"message": "وضعیت پیگیری به‌روزرسانی شد"}

# --- اندپوینت‌های Products ---
@app.get("/api/products", response_model=List[Dict], tags=["Products"])
async def get_products(current_user: UserAuthInfo = Depends(get_current_auth_user)):
    return list_products()

@app.post("/api/products", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, tags=["Products"])
async def create_new_product(prod_data: ProductCreate, current_user: UserAuthInfo = Depends(get_admin_user)):
    create_product(prod_data)
    return {"message": "محصول اضافه شد"}

@app.put("/api/products/{product_id}", response_model=MessageResponse, tags=["Products"])
async def update_existing_product(product_id: int, prod_data: ProductCreate, current_user: UserAuthInfo = Depends(get_admin_user)):
    update_product(product_id, prod_data)
    return {"message": "محصول به‌روزرسانی شد"}

# --- اندپوینت‌های Orders ---
@app.get("/api/orders", response_model=List[Dict], tags=["Orders"])
async def get_orders_list(
    user_filter: Optional[int] = None,
    company_filter: Optional[int] = None,
    product_filter: Optional[int] = None,
    status_filter: Optional[str] = None,
    current_user: UserAuthInfo = Depends(get_current_auth_user)
):
    orders_data = df_orders_by_filters(user_filter, company_filter, product_filter, status_filter)
    return orders_data

@app.post("/api/orders", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, tags=["Orders"])
async def create_new_order(order_data: OrderCreate, current_user: UserAuthInfo = Depends(get_current_auth_user)):
    create_order(order_data)
    return {"message": "سفارش ثبت شد"}

@app.put("/api/orders/{order_id}", response_model=MessageResponse, tags=["Orders"])
async def update_existing_order(order_id: int, order_data: OrderCreate, current_user: UserAuthInfo = Depends(get_current_auth_user)):
    ok, msg = update_order(order_id, order_data)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

# --- اندپوینت‌های Admin ---
@app.get("/api/admin/app-users", response_model=List[Dict], tags=["Admin"])
async def get_app_users(current_user: UserAuthInfo = Depends(get_current_auth_user)):
    return list_sales_accounts_including_admins()

@app.post("/api/admin/app-users", response_model=MessageResponse, tags=["Admin"])
async def create_new_app_user(data: AppUserCreate, current_user: UserAuthInfo = Depends(get_admin_user)):
    try:
        conn = get_conn()
        conn.execute("INSERT INTO app_users (username,password_sha256,role,linked_user_id) VALUES (?,?,?,?);",
                     (data.username.strip(), sha256(data.password), data.role, data.linked_user_id))
        conn.commit(); conn.close()
        return {"message": "کاربر ایجاد شد."}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="این نام کاربری قبلاً وجود دارد.")

@app.put("/api/admin/app-users/{user_id}/password", response_model=MessageResponse, tags=["Admin"])
async def update_app_user_password(user_id: int, data: PasswordUpdate, current_user: UserAuthInfo = Depends(get_admin_user)):
    if not data.new_password or len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="رمز عبور جدید باید حداقل 6 کاراکتر باشد")
    
    new_pass_sha256 = sha256(data.new_password)
    conn = get_conn()
    conn.execute("UPDATE app_users SET password_sha256 = ? WHERE id = ?", (new_pass_sha256, user_id))
    conn.commit()
    conn.close()
    return {"message": "رمز عبور کاربر با موفقیت به‌روزرسانی شد"}

@app.delete("/api/admin/app-users/{user_id}", response_model=MessageResponse, tags=["Admin"])
async def delete_app_user(user_id: int, current_user: UserAuthInfo = Depends(get_admin_user)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="شما نمی‌توانید حساب کاربری خودتان را حذف کنید")
    
    conn = get_conn()
    cur = conn.execute("DELETE FROM app_users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    return {"message": "کاربر با موفقیت حذف شد"}

@app.get("/api/admin/backup-db", tags=["Admin"])
async def download_database_backup(current_user: UserAuthInfo = Depends(get_admin_user)):
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=404, detail="فایل دیتابیس یافت نشد")
    return FileResponse(DB_PATH, media_type="application/octet-stream", filename="crm_backup.db")

@app.post("/api/admin/restore-db", response_model=MessageResponse, tags=["Admin"])
async def restore_database(file: UploadFile = File(...), current_user: UserAuthInfo = Depends(get_admin_user)):
    if not (file.filename.endswith(".db") or file.filename.endswith(".zip")):
        raise HTTPException(status_code=400, detail="فایل باید .db یا .zip باشد")
    
    data = await file.read()
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="فایل خالی است")

    if file.filename.endswith(".zip"):
        extracted = extract_db_from_zip(data)
        if not extracted:
            raise HTTPException(status_code=400, detail="در فایل ZIP هیچ فایل .db یافت نشد")
        data = extracted
    
    tmp_path = "_restore_tmp.db"
    try:
        with open(tmp_path, "wb") as f: f.write(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در نوشتن فایل موقت: {e}")

    ok, msg = validate_db_file(tmp_path)
    if not ok:
        os.remove(tmp_path)
        raise HTTPException(status_code=400, detail=f"اعتبارسنجی بکاپ ناموفق بود: {msg}")
    
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"crm_before_restore_{ts}.db"
        shutil.copyfile(DB_PATH, backup_name)
    except Exception as e:
        print(f"Warning: Could not create backup: {e}")

    try:
        os.replace(tmp_path, DB_PATH)
    except Exception as e:
        if os.path.exists(tmp_path): os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=f"جایگزینی دیتابیس ناموفق بود: {e}")

    return {"message": "بازیابی با موفقیت انجام شد. سرور را ری‌استارت کنید."}

# ====================== 8. سرویس‌دهی فرانت‌اند (Vue.js / dist) ======================
# این بخش باید پس از تعریف تمام اندپوینت‌های API قرار گیرد.

# 1. Mount کردن پوشه 'dist' در روت اصلی ('/') برای سرو کردن دارایی‌های استاتیک (CSS, JS)
# 'html=True' تضمین می‌کند که index.html برای روت '/' سرو شود.
app.mount(
    "/",  
    StaticFiles(directory="dist", html=True), 
    name="frontend_static"
)

# 2. روت Catch-all برای مدیریت SPA History Mode
# اگر روت مورد نظر در API یا StaticFiles یافت نشد (مثل /users یا /settings)، 
# آن را به فایل index.html هدایت می‌کند.
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend_fallback(full_path: str):
    # مسیر فایل index.html که در پوشه dist قرار دارد.
    return FileResponse(os.path.join("dist", "index.html"))


# ====================== 9. اجرای سرور ======================
if __name__ == "__main__":
    import uvicorn
    print("--- سرور FastAPI در حال اجرا روی http://127.0.0.1:8000 ---")
    print("--- برای دیدن مستندات API به http://127.0.0.1:8000/docs بروید ---")
    
    if not os.path.exists(DB_PATH):
        print("دیتابیس یافت نشد. در حال ساخت فایل crm.db...")
        init_db()

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)