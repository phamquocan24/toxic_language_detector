# 🔐 Web Dashboard Login Credentials

## 📍 URL

**Web Dashboard**: `http://localhost:8080`

---

## 👤 DEFAULT ACCOUNTS

Hệ thống có **2 tài khoản mặc định** được tạo sẵn trong database seeders:

### 1️⃣ Admin Account (Full Access)

```
📧 Email:    admin@example.com
🔑 Password: password
👑 Role:     Administrator
```

**Quyền hạn**:
- ✅ Full access to all modules
- ✅ User management
- ✅ Statistics & analytics
- ✅ Predictions management
- ✅ Logs viewing
- ✅ Comments moderation
- ✅ System configuration

---

### 2️⃣ Regular User Account (Limited Access)

```
📧 Email:    anpham25052004@gmail.com
👤 Username: hung123
🔑 Password: password2
👤 Role:     Regular User
```

**Quyền hạn**:
- ✅ View own predictions
- ✅ View statistics
- ✅ Limited access
- ❌ No user management
- ❌ No system configuration

---

## 🚀 QUICK START

### Step 1: Start Dashboard

```bash
./scripts/start-all.sh
# OR
cd webdashboard && php artisan serve --port=8080
```

### Step 2: Open Browser

```
http://localhost:8080
```

### Step 3: Login

**Sử dụng Admin account**:
- Email: `admin@example.com`
- Password: `password`

---

## 🔧 SEEDERS

Credentials được định nghĩa trong database seeders:

### File 1: `webdashboard/database/seeders/UsersTableSeeder.php`

```php
// Admin User
[
    'username' => 'admin',
    'email' => 'admin@example.com',
    'name' => 'Administrator',
    'password' => Hash::make('password'),
    'is_active' => true,
    'is_verified' => true,
    'role_id' => 1, // Admin
]

// Regular User
[
    'username' => 'hung123',
    'email' => 'anpham25052004@gmail.com',
    'name' => 'annnnn',
    'password' => Hash::make('password2'),
    'is_active' => true,
    'is_verified' => true,
    'role_id' => 2, // User
]
```

### File 2: `webdashboard/database/seeders/AdminUserSeeder.php`

```php
User::create([
    'first_name' => 'Admin',
    'last_name' => 'User',
    'email' => 'admin@example.com',
    'password' => Hash::make('password123'), // Alternative password
    'role' => 1, // Admin
]);
```

---

## 🔄 NẾU CHƯA CÓ DATABASE/USERS

### Step 1: Migrate Database

```bash
cd webdashboard
php artisan migrate:fresh --seed
```

Hoặc:

```bash
php artisan migrate:fresh
php artisan db:seed
```

### Step 2: Run Specific Seeder

```bash
php artisan db:seed --class=UsersTableSeeder
# OR
php artisan db:seed --class=AdminUserSeeder
```

---

## 🔐 ĐỔI MẬT KHẨU

### Option 1: Qua Dashboard

1. Login với admin account
2. Vào **User Management**
3. Edit admin user
4. Change password
5. Save

### Option 2: Qua Artisan (Command Line)

```bash
cd webdashboard
php artisan tinker
```

Trong tinker console:

```php
// Change admin password
$admin = User::where('email', 'admin@example.com')->first();
$admin->password = Hash::make('new_password_here');
$admin->save();
exit
```

### Option 3: Re-run Seeder

**Cảnh báo**: Sẽ reset toàn bộ database!

```bash
cd webdashboard
php artisan migrate:fresh --seed
```

---

## 🎯 TẠO ADMIN MỚI

### Via Artisan Tinker

```bash
cd webdashboard
php artisan tinker
```

```php
use Modules\User\Entities\User;
use Illuminate\Support\Facades\Hash;

User::create([
    'username' => 'newadmin',
    'email' => 'newadmin@example.com',
    'name' => 'New Administrator',
    'password' => Hash::make('your_secure_password'),
    'is_active' => true,
    'is_verified' => true,
    'role_id' => 1, // 1 = Admin, 2 = User
]);

exit
```

---

## ⚠️ SECURITY WARNINGS

### 🔴 PRODUCTION

**QUAN TRỌNG**: Phải đổi credentials mặc định khi deploy production!

```bash
# Default credentials này CHỈ dùng cho DEVELOPMENT
Email:    admin@example.com
Password: password

# ❌ KHÔNG được dùng credentials này trên production
# ✅ Phải tạo admin mới với email/password mạnh
```

### 🔒 Best Practices

1. **Đổi ngay admin password** sau khi setup
2. **Không dùng `admin@example.com`** trên production
3. **Dùng strong password**: Tối thiểu 12 ký tự, chữ hoa/thường/số/ký tự đặc biệt
4. **Enable 2FA** (nếu có)
5. **Regular password rotation**
6. **Disable default test accounts** trên production

---

## 🧪 VERIFICATION

### Test Login

```bash
# Start dashboard
./scripts/start-all.sh

# Open browser
http://localhost:8080

# Try login với:
Email:    admin@example.com
Password: password
```

**Expected**:
- ✅ Login thành công
- ✅ Redirect tới dashboard
- ✅ Thấy admin menu
- ✅ Full access to all features

---

## 📊 USER ROLES

| Role ID | Role Name | Permissions |
|---------|-----------|-------------|
| `1` | **Admin** | Full access, user management, system config |
| `2` | **User** | Limited access, view own data only |

Được định nghĩa trong:
- `webdashboard/database/seeders/UsersTableSeeder.php` (roles table)
- Migration: `webdashboard/database/migrations/*_create_users_table.php`

---

## 🔗 RELATED FILES

### Database Seeders
- `webdashboard/database/seeders/UsersTableSeeder.php` - Main seeder với 2 users
- `webdashboard/database/seeders/AdminUserSeeder.php` - Admin only seeder

### Migrations
- `webdashboard/database/migrations/*_create_users_table.php`
- `webdashboard/database/migrations/*_create_roles_table.php`

### Config
- `webdashboard/config/auth.php` - Authentication config
- `webdashboard/env.example` - Environment template

---

## 🐛 TROUBLESHOOTING

### Issue 1: "Invalid credentials"

**Possible causes**:
- Database chưa được seed
- Password sai
- User chưa được tạo

**Solutions**:
```bash
cd webdashboard
php artisan migrate:fresh --seed
# Try login again
```

---

### Issue 2: "Page not found" khi vào localhost:8080

**Possible causes**:
- Dashboard chưa chạy
- Port 8080 đang bị dùng

**Solutions**:
```bash
# Check if running
ps aux | grep artisan

# Start dashboard
./scripts/start-all.sh
# OR
cd webdashboard && php artisan serve --port=8080
```

---

### Issue 3: Database connection error

**Possible causes**:
- MySQL/SQLite chưa start
- Database config sai trong `.env`

**Solutions**:
```bash
# Check webdashboard/.env
cd webdashboard
cat .env | grep DB_

# For SQLite (simpler for dev)
DB_CONNECTION=sqlite
DB_DATABASE=/absolute/path/to/database.sqlite

# Create database file if needed
touch database/database.sqlite
php artisan migrate:fresh --seed
```

---

## 📝 NOTES

1. **Default credentials chỉ cho development**: Phải đổi trên production
2. **UsersTableSeeder có 2 users**: admin và hung123
3. **AdminUserSeeder có 1 admin**: Có thể dùng seeder nào cũng được
4. **Password được hash**: Dùng Laravel Hash::make()
5. **Roles**: 1 = Admin, 2 = User
6. **Email phải unique**: Không thể tạo 2 users cùng email

---

## 🎉 QUICK REFERENCE

**Login URL**: `http://localhost:8080`

**Admin Credentials**:
```
Email:    admin@example.com
Password: password
```

**User Credentials**:
```
Email:    anpham25052004@gmail.com
Password: password2
```

**Reset Database**:
```bash
cd webdashboard && php artisan migrate:fresh --seed
```

---

*Documentation created: 2025-10-23*  
*Source: Database Seeders in webdashboard/database/seeders/*

