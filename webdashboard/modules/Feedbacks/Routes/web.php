<?php

use Illuminate\Support\Facades\Route;
use Modules\Feedbacks\Http\Controllers\Admin\FeedbacksController;

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

// Feedbacks Routes
Route::group(['middleware' => ['web', 'auth'], 'prefix' => 'admin', 'as' => 'admin.'], function () {
    // Feedbacks routes - danh sách feedback từ API Python
    Route::get('feedbacks', [FeedbacksController::class, 'index'])->name('feedbacks.index');
    Route::get('feedbacks/json', [FeedbacksController::class, 'getFeedbacksJson'])->name('feedbacks.json');
});
