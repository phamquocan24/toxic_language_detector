<?php

namespace Modules\User\Entities;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Modules\User\Entities\User;

class Role extends Model
{
    use HasFactory;

    protected $fillable = [
        'name',
        'description'
    ];

    /**
     * Mối quan hệ với người dùng
     */
    public function users()
    {
        return $this->hasMany(User::class);
    }

    /**
     * Kiểm tra vai trò có quyền cụ thể không
     *
     * @param string $permissionCode
     * @return bool
     */
    public function hasPermission($permissionCode)
    {
        // TODO: Implement permission checking logic
        // Đây là phương thức giả định cho việc kiểm tra quyền
        // Bạn có thể cài đặt theo cơ chế phân quyền thực tế của bạn
        return false;
    }

    /**
     * Lấy danh sách quyền của vai trò
     *
     * @return array
     */
    public function getPermissions()
    {
        // TODO: Implement permission fetching logic
        // Đây là phương thức giả định cho việc lấy danh sách quyền
        // Bạn có thể cài đặt theo cơ chế phân quyền thực tế của bạn
        return [];
    }
}
