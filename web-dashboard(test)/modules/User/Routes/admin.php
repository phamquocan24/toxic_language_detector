<?php

use Illuminate\Support\Facades\Route;
use Modules\User\Http\Controllers\AuthController;
use Modules\User\Http\Controllers\User\UserController;
use Modules\Admin\Http\Controllers\Admin\DashboardController;

// Routes không yêu cầu đăng nhập
Route::get('login', [AuthController::class, 'getLogin'])->name('login');
Route::post('login', [AuthController::class, 'postLogin'])->name('auth.login.post');
Route::get('logout', [AuthController::class, 'getLogout'])->name('auth.logout');
Route::get('password/reset', [AuthController::class, 'getReset'])->name('auth.reset');
Route::post('password/reset', [AuthController::class, 'postReset'])->name('auth.password.reset.post');

// Routes yêu cầu đăng nhập và quyền admin
Route::middleware(['web', 'auth', 'is.admin'])->group(function () {
    // Dashboard
    Route::get('/', [DashboardController::class, 'index'])->name('admin.dashboard.index');

    // Quản lý người dùng
    Route::resource('users', UserController::class)->except('destroy')->names([
        'index' => 'admin.users.index',
        'create' => 'admin.users.create',
        'store' => 'admin.users.store',
        'show' => 'admin.users.show',
        'edit' => 'admin.users.edit',
        'update' => 'admin.users.update',
    ]);

    Route::post('users/delete', [UserController::class, 'delete'])->name('admin.users.delete');

    // User Profile - Không cần middleware auth vì đã kiểm tra ở group
    Route::get('profile', [UserController::class, 'profile'])->name('admin.profile');
    Route::post('profile', [UserController::class, 'updateProfile'])->name('admin.profile.update');
    Route::post('change-password', [UserController::class, 'changePassword'])->name('admin.password.change');
});

