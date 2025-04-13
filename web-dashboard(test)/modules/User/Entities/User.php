<?php

namespace Modules\User\Entities;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;
use Illuminate\Database\Eloquent\SoftDeletes;
use Modules\User\Enums\UserRole;
use Carbon\Carbon;

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable, SoftDeletes;

    protected $fillable = [
        'first_name',
        'last_name',
        'email',
        'password',
        'email_verified_at',
        'role',
        'last_login',
        'phone',
        'api_token', // Thêm api_token nếu sử dụng token authentication đơn giản
    ];

    protected $hidden = [
        'password',
        'remember_token',
        'api_token', // Ẩn token khỏi các truy vấn
    ];

    protected $casts = [
        'email_verified_at' => 'datetime',
        'last_login' => 'datetime',
    ];

    /**
     * Get the user's full name.
     *
     * @return string
     */
    public function getFullNameAttribute()
    {
        return "{$this->first_name} {$this->last_name}";
    }

    /**
     * Kiểm tra xem người dùng có phải là admin không
     *
     * @return bool
     */
    public function isAdmin()
    {
        return $this['role'] == UserRole::ADMINISTRATOR;
    }

    /**
     * Kiểm tra xem người dùng có phải là thành viên thông thường không
     *
     * @return bool
     */
    public function isUser()
    {
        return $this['role'] == UserRole::MEMBER;
    }
}
