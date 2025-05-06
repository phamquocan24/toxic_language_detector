<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Admin\DashboardController as AdminDashboardController;
use App\Http\Controllers\Admin\CommentController as AdminCommentController;
use App\Http\Controllers\Admin\UserController as AdminUserController;
use App\Http\Controllers\User\DashboardController as UserDashboardController;
use App\Http\Controllers\User\CommentController as UserCommentController;
use App\Http\Controllers\User\AnalysisController;
use App\Http\Controllers\Auth\LoginController;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "web" middleware group. Make something great!
|
*/

// Home route
Route::get('/', function () {
    return redirect()->route('login');
});

// Auth routes (custom API-based login)
Route::get('login', [LoginController::class, 'showLoginForm'])->name('login');
Route::post('login', [LoginController::class, 'login']);
Route::post('logout', [LoginController::class, 'logout'])->name('logout');

// Admin routes
Route::middleware(['auth'])->prefix('admin')->name('admin.')->group(function () {
    // Dashboard
    Route::get('/', [AdminDashboardController::class, 'index'])->name('dashboard');
    
    // Comments
    Route::resource('comments', AdminCommentController::class);
    Route::put('comments/{comment}/feedback', [AdminCommentController::class, 'feedback'])->name('comments.feedback');
    Route::get('comments-export', [AdminCommentController::class, 'export'])->name('comments.export');
    
    // Users
    Route::resource('users', AdminUserController::class);
    Route::put('users/{user}/toggle-status', [AdminUserController::class, 'toggleStatus'])->name('users.toggle-status');
    Route::get('users/{user}/comments', [AdminUserController::class, 'comments'])->name('users.comments');
    
    // Settings route temporarily disabled
    // Route::get('settings', [SettingController::class, 'index'])->name('settings.index');
    // Route::post('settings', [SettingController::class, 'update'])->name('settings.update');
});

// User routes
Route::middleware(['auth'])->prefix('user')->name('user.')->group(function () {
    // Dashboard
    Route::get('/dashboard', [UserDashboardController::class, 'index'])->name('dashboard');
    
    // Analysis routes
    Route::get('/analysis', [AnalysisController::class, 'index'])->name('analysis.index');
    Route::post('/analysis/analyze', [AnalysisController::class, 'analyze'])->name('analysis.analyze');
    Route::post('/analysis/batch', [AnalysisController::class, 'batchAnalyze'])->name('analysis.batch');
    Route::get('/analysis/stats', [AnalysisController::class, 'getStats'])->name('analysis.stats');
    Route::post('/analysis/feedback', [AnalysisController::class, 'submitFeedback'])->name('analysis.feedback');
    
    // Comments
    Route::get('/comments', [UserCommentController::class, 'index'])->name('comments.index');
    Route::get('/comments/{comment}', [UserCommentController::class, 'show'])->name('comments.show');
    Route::post('/comments/{comment}/feedback', [UserCommentController::class, 'feedback'])->name('comments.feedback');
    Route::delete('/comments/{comment}', [UserCommentController::class, 'destroy'])->name('comments.destroy');
    Route::get('/comments-export', [UserCommentController::class, 'export'])->name('comments.export');
    Route::get('/comments-print', [UserCommentController::class, 'print'])->name('comments.print');
    Route::get('/comments/statistics', [UserCommentController::class, 'statistics'])->name('comments.statistics');
});

// Fallback for authenticated users
Route::middleware(['auth'])->get('/home', function () {
    if (auth()->user()->is_admin) {
        return redirect()->route('admin.dashboard');
    }
    return redirect()->route('user.dashboard');
})->name('home');
