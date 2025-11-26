<?php

use Illuminate\Support\Facades\Route;
use Modules\User\Http\Controllers\AuthController;
use Modules\User\Http\Controllers\User\UserController;
use Modules\User\Http\Controllers\User\InvitationController;


// Routes yêu cầu đăng nhập người dùng
Route::middleware(['web', 'auth'])->group(function () {
    // Trang chủ website

    // Public routes cho invitation
    Route::get('invitation/{token}', [InvitationController::class, 'accept'])->name('invitation.accept');
    Route::post('invitation/register', [InvitationController::class, 'register'])->name('invitation.register');
    Route::get('register/invitation/{token}', [InvitationController::class, 'accept'])
        ->name('register.with.invitation');

    // User Profile - Chỉ yêu cầu đăng nhập, không yêu cầu quyền admin
    Route::get('profile', [UserController::class, 'profile'])->name('user.profile');
    Route::post('profile', [UserController::class, 'updateProfile'])->name('user.profile.update');
    Route::post('change-password', [UserController::class, 'changePassword'])->name('user.password.change');
});
