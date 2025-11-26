<?php

use Illuminate\Support\Facades\Route;
use Modules\Log\Http\Controllers\Log\LogController;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
*/

// Route tương thích ngược cho đường dẫn cũ
Route::redirect('log', '/admin/logs', 301);

Route::group(['middleware' => ['web', 'auth'], 'prefix' => 'admin'], function () {
    // Hiển thị logs
    Route::get('logs', [LogController::class, 'index'])->name('admin.logs.index');
});
