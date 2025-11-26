<?php

namespace Modules\User\Entities;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Auth\Passwords\CanResetPassword;
use Carbon\Carbon;
use Illuminate\Support\Facades\DB;
use DateTime;
use Modules\User\Entities\Role;

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable, CanResetPassword, SoftDeletes;

    protected $fillable = [
        'username',
        'email',
        'name',
        'password',
        'is_active',
        'is_verified',
        'last_login',
        'last_activity',
        'last_login_ip',
        'reset_token',
        'reset_token_expires',
        'verification_token',
        'verification_token_expires',
        'extension_settings',
        'ui_settings',
        'notification_settings',
        'avatar_url',
        'bio',
        'role_id',
    ];

    protected $hidden = [
        'password',
        'remember_token',
        'reset_token',
        'verification_token',
    ];

    protected $casts = [
        'is_active' => 'boolean',
        'is_verified' => 'boolean',
        'last_login' => 'datetime',
        'last_activity' => 'datetime',
        'reset_token_expires' => 'datetime',
        'verification_token_expires' => 'datetime',
        'extension_settings' => 'json',
        'ui_settings' => 'json',
        'notification_settings' => 'json',
    ];

    /**
     * Mối quan hệ với vai trò
     */
    public function role()
    {
        return $this->belongsTo(Role::class);
    }

    /**
     * Mối quan hệ với comments
     */
    public function comments()
    {
        return $this->hasMany(\Modules\Comment\Entities\Comment::class);
    }

    /**
     * Kiểm tra người dùng có phải admin không
     *
     * @return bool
     */
    public function isAdmin()
    {
        if (is_object($this->role)) {
            return $this->role && $this->role->name === 'admin';
        } else {
            // Khi role_id là 1 (admin)
            return $this->role_id === 1;
        }
    }

    /**
     * Kiểm tra người dùng có quyền cụ thể không
     *
     * @param string $permissionCode
     * @return bool
     */
    public function hasPermission($permissionCode)
    {
        // Admin luôn có tất cả quyền
        if ($this->isAdmin()) {
            return true;
        }

        // Kiểm tra quyền theo vai trò
        if (is_object($this->role) && $this->role) {
            return $this->role->hasPermission($permissionCode);
        } else if ($this->role_id) {
            // Tìm role từ role_id
            $role = \Modules\User\Entities\Role::find($this->role_id);
            return $role ? $role->hasPermission($permissionCode) : false;
        }

        return false;
    }

    /**
     * Lấy danh sách quyền của người dùng
     *
     * @return array
     */
    public function getPermissions()
    {
        if (is_object($this->role) && $this->role) {
            return $this->role->getPermissions();
        } else if ($this->role_id) {
            // Tìm role từ role_id
            $role = \Modules\User\Entities\Role::find($this->role_id);
            return $role ? $role->getPermissions() : [];
        }

        return [];
    }

    /**
     * Lấy cài đặt extension
     *
     * @return array
     */
    public function getExtensionSettings()
    {
        // Nếu không có cài đặt, trả về mặc định
        if (!$this->extension_settings) {
            return config('settings.extension_default_settings', []);
        }

        return $this->extension_settings;
    }

    /**
     * Cập nhật cài đặt extension
     *
     * @param array|string $settingsDict
     * @return void
     */
    public function setExtensionSettings($settingsDict)
    {
        if (is_array($settingsDict)) {
            $this->extension_settings = $settingsDict;
        } else {
            $this->extension_settings = json_decode($settingsDict, true);
        }
    }

    /**
     * Tạo token để đặt lại mật khẩu
     *
     * @return string
     */
    public function generatePasswordResetToken()
    {
        $token = \Illuminate\Support\Str::random(60);
        $this->reset_token = $token;
        $this->reset_token_expires = Carbon::now()->addHours(24);
        $this->save();

        return $token;
    }

    /**
     * Vô hiệu hóa token đặt lại mật khẩu
     *
     * @return void
     */
    public function invalidatePasswordResetToken()
    {
        $this->reset_token = null;
        $this->reset_token_expires = null;
        $this->save();
    }

    /**
     * Tạo token để xác thực email
     *
     * @return string
     */
    public function generateVerificationToken()
    {
        $token = \Illuminate\Support\Str::random(60);
        $this->verification_token = $token;
        $this->verification_token_expires = Carbon::now()->addHours(72);
        $this->save();

        return $token;
    }

    /**
     * Xác thực email
     *
     * @return void
     */
    public function verifyEmail()
    {
        $this->is_verified = true;
        $this->verification_token = null;
        $this->verification_token_expires = null;
        $this->save();
    }

    /**
     * Cập nhật thời gian đăng nhập cuối
     *
     * @param string|null $ip
     * @return void
     */
    public function updateLastLogin($ip = null)
    {
        $this->last_login = Carbon::now();
        $this->last_activity = Carbon::now();
        if ($ip) {
            $this->last_login_ip = $ip;
        }
        $this->save();
    }

    /**
     * Cập nhật thời gian hoạt động cuối
     *
     * @return void
     */
    public function updateLastActivity()
    {
        $this->last_activity = Carbon::now();
        $this->save();
    }

    /**
     * Lấy người dùng theo username
     *
     * @param string $username
     * @return User|null
     */
    public static function getByUsername($username)
    {
        return static::where('username', $username)->first();
    }

    /**
     * Lấy người dùng theo email
     *
     * @param string $email
     * @return User|null
     */
    public static function getByEmail($email)
    {
        return static::where('email', $email)->first();
    }

    /**
     * Lấy người dùng theo token đặt lại mật khẩu
     *
     * @param string $token
     * @return User|null
     */
    public static function getByResetToken($token)
    {
        return static::where('reset_token', $token)
            ->where('reset_token_expires', '>', Carbon::now())
            ->first();
    }

    /**
     * Lấy danh sách người dùng hoạt động trong khoảng thời gian
     *
     * @param int $days
     * @return \Illuminate\Database\Eloquent\Collection
     */
    public static function getActiveUsers($days = 30)
    {
        $cutoffDate = Carbon::now()->subDays($days);
        return static::where('last_activity', '>=', $cutoffDate)->get();
    }

    /**
     * Override the mail body for reset password notification mail.
     *
     * @param string $token
     * @return void
     */
    public function sendPasswordResetNotification($token)
    {
        $this->notify(new \Modules\User\Notifications\ResetPasswordNotification($token));
    }
}
