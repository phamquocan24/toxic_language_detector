<?php

namespace Modules\User\Http\Controllers\User;

use App\Http\Controllers\Controller;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Modules\User\Entities\User;
use Modules\User\Enums\UserRole;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;
use Carbon\Carbon;

class UserController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        // Lấy tham số sắp xếp từ request
        $sortBy = $request->get('sort_by', 'id');
        $sortOrder = $request->get('sort', 'asc');
        $perPage = $request->input('per_page', 10);
        $search = $request->input('search', '');

        // Danh sách cột có thể sắp xếp
        $sortableColumns = ['id', 'first_name', 'last_name', 'email', 'role', 'last_login', 'created_at'];

        // Kiểm tra nếu cột không hợp lệ, đặt lại thành 'id'
        if (!in_array($sortBy, $sortableColumns)) {
            $sortBy = 'id';
        }

        // Tạo query
        $query = User::query();

        // Thêm tìm kiếm nếu có
        if (!empty($search)) {
            $query->where(function($q) use ($search) {
                $q->where('first_name', 'like', "%{$search}%")
                  ->orWhere('last_name', 'like', "%{$search}%")
                  ->orWhere('email', 'like', "%{$search}%");
            });
        }

        $perPage = $request->input('per_page', 5);
        // Lấy tổng số người dùng
        $totalUsers = $query->count();

        // Lấy danh sách người dùng với phân trang
        $users = $query->orderBy($sortBy, $sortOrder)->paginate($perPage);

        // Thêm thông tin cho view
        $roles = [
            UserRole::ADMINISTRATOR => 'Admin',
            UserRole::MEMBER => 'Member'
        ];

        return view('user::admin.users.index', compact('users', 'sortBy', 'sortOrder', 'perPage', 'search', 'totalUsers', 'roles'));
    }

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {
        $roles = [
            UserRole::ADMINISTRATOR => 'Admin',
            UserRole::MEMBER => 'Member'
        ];

        return view('user::admin.users.create', compact('roles'));
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'first_name' => 'required|string|max:255',
            'last_name' => 'required|string|max:255',
            'email' => 'required|string|email|max:255|unique:users',
            'password' => 'required|string|min:8|confirmed',
            'role' => 'required|integer'
        ]);

        $user = User::create([
            'first_name' => $validated['first_name'],
            'last_name' => $validated['last_name'],
            'email' => $validated['email'],
            'password' => Hash::make($validated['password']),
            'role' => $validated['role'],
            'email_verified_at' => now(),
        ]);

        return redirect()->route('admin.users.index')
            ->with('success', 'Người dùng đã được tạo thành công');
    }

    /**
     * Show the specified resource.
     */
    public function show($id)
    {
        $user = User::findOrFail($id);

        return view('user::admin.users.show', compact('user'));
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit($id)
    {
        $user = User::findOrFail($id);

        $roles = [
            UserRole::ADMINISTRATOR => 'Admin',
            UserRole::MEMBER => 'Member'
        ];

        return view('user::admin.users.edit', compact('user', 'roles'));
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, $id)
    {
        $user = User::findOrFail($id);

        $validated = $request->validate([
            'first_name' => 'required|string|max:255',
            'last_name' => 'required|string|max:255',
            'email' => 'required|string|email|max:255|unique:users,email,'.$id,
            'password' => 'nullable|string|min:8|confirmed',
            'role' => 'required|integer'
        ]);

        $userData = [
            'first_name' => $validated['first_name'],
            'last_name' => $validated['last_name'],
            'email' => $validated['email'],
            'role' => $validated['role']
        ];

        // Chỉ cập nhật mật khẩu nếu được cung cấp
        if (!empty($validated['password'])) {
            $userData['password'] = Hash::make($validated['password']);
        }

        $user->update($userData);

        return redirect()->route('admin.users.index')
            ->with('success', 'Người dùng đã được cập nhật thành công');
    }

    /**
     * Delete one or multiple users
     */
    public function delete(Request $request)
    {
        DB::beginTransaction();
        try {
            $result = [];
            $userIds = json_decode($request->input('ids'));

            // // Debug - kiểm tra giá trị IDs nhận được từ request
            // \Log::info('User IDs to delete:', ['ids' => $userIds]);

            $deletedRows = 0;

            // Kiểm tra nếu danh sách user_ids rỗng
            if (empty($userIds)) {
                DB::rollBack();
                $result['error'] = "Không có người dùng nào được chọn để xóa.";
                return redirect()->route('admin.users.index')->with($result);
            }

            // Kiểm tra xem có đang cố xóa chính mình không
            if (in_array(auth()->id(), $userIds)) {
                DB::rollBack();
                $result['error'] = "Bạn không thể xóa tài khoản của chính mình.";
                return redirect()->route('admin.users.index')->with($result);
            }

            if (!empty($userIds)) {
                $deletedRows = User::whereIn('id', $userIds)->delete();
            }
            if ($deletedRows > 0) {
                DB::commit();
                $result['success'] = "Xóa thành công " . $deletedRows . " người dùng.";
            } else {
                DB::rollBack();
                $result['error'] = "Không có người dùng nào được xóa.";
            }

            return redirect()->route('admin.users.index')->with($result);
        } catch (\Exception $e) {
            \Log::error('User deletion error:', ['error' => $e->getMessage()]);
            DB::rollBack();
            return redirect()->route('admin.users.index')->with([
                'error' => 'Đã xảy ra lỗi khi xóa người dùng: ' . $e->getMessage(),
            ]);
        }
    }
    /**
     * Display user profile
     */
    public function profile(Request $request)
    {
        $user = auth()->user();

        return view('user::profile.profile', compact('user'));
    }

    /**
     * Update user profile information
     */
    public function updateProfile(Request $request)
    {
        $user = auth()->user();

        $validated = $request->validate([
            'first_name' => 'required|string|max:255',
            'last_name' => 'required|string|max:255',
            'email' => 'required|string|email|max:255|unique:users,email,'.$user->id,
            'phone' => 'nullable|string|max:20',
        ]);

        $user->update($validated);

        return redirect()->route('admin.profile')
            ->with('success', 'Thông tin tài khoản đã được cập nhật thành công');
    }

    /**
     * Change user password
     */
    public function changePassword(Request $request)
    {
        $user = auth()->user();

        $validated = $request->validate([
            'password' => 'required|string|min:8|confirmed',
        ]);

        $user->update([
            'password' => Hash::make($validated['password']),
        ]);

        return redirect()->route('admin.profile', ['tab' => 'newPassword'])
            ->with('success', 'Mật khẩu đã được thay đổi thành công');
    }
}
