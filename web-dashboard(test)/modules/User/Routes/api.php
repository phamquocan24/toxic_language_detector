<?php

use Illuminate\Support\Facades\Route;
use Modules\User\Http\Controllers\AuthController;

Route::group([
    'middleware' => 'api',
    'prefix' => 'auth'
], function () {
    // Không yêu cầu xác thực
    Route::post('login', [AuthController::class, 'apiLogin']);
    Route::post('register', [AuthController::class, 'register']);

    // Yêu cầu xác thực
    Route::middleware('auth:sanctum')->group(function () {
        Route::post('logout', [AuthController::class, 'apiLogout']);
        Route::get('me', [AuthController::class, 'me']);
    });
});
