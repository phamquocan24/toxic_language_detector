<?php

use Illuminate\Support\Facades\Route;
use Modules\User\Http\Controllers\AuthController;
use Modules\User\Http\Controllers\User\UserController;

// Route xác thực (không cần đăng nhập)
// Không cần khai báo lại ở đây vì đã có trong admin.php
// Route::get('login', [AuthController::class, 'getLogin'])->name('login');
// Route::post('login', [AuthController::class, 'postLogin'])->name('auth.login.post');
// Route::get('logout', [AuthController::class, 'getLogout'])->name('auth.logout');

// Routes yêu cầu đăng nhập người dùng
Route::middleware(['web', 'auth'])->group(function () {
    // Trang chủ website
    Route::get('/', function () {
        return view('welcome');
    });

    // User Profile - Chỉ yêu cầu đăng nhập, không yêu cầu quyền admin
    Route::get('profile', [UserController::class, 'profile'])->name('user.profile');
    Route::post('profile', [UserController::class, 'updateProfile'])->name('user.profile.update');
    Route::post('change-password', [UserController::class, 'changePassword'])->name('user.password.change');
});
