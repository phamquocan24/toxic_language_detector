<?php

use Illuminate\Support\Facades\Route;
use Modules\Comment\Http\Controllers\Comment\CommentController;

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
Route::redirect('comment', '/admin/comments', 301);

Route::group(['middleware' => ['web', 'auth'], 'prefix' => 'admin'], function () {
    // Các route cơ bản cho comment
    Route::get('comments', [CommentController::class, 'index'])->name('admin.comments.index');
    Route::get('comments/create', [CommentController::class, 'create'])->name('admin.comments.create');
    Route::post('comments', [CommentController::class, 'store'])->name('admin.comments.store');
    Route::get('comments/{id}/edit', [CommentController::class, 'edit'])->name('admin.comments.edit');
    Route::put('comments/{id}', [CommentController::class, 'update'])->name('admin.comments.update');

    // Route để xử lý xóa hàng loạt
    Route::delete('comments/delete', [CommentController::class, 'bulkDelete'])->name('admin.comments.delete');

    // Route để phân tích lại nội dung comment
    Route::post('comments/{id}/analyze', [CommentController::class, 'analyze'])->name('admin.comments.analyze');

    // Route để đánh dấu comment đã xem xét
    Route::post('comments/{id}/mark-reviewed', [CommentController::class, 'markReviewed'])->name('admin.comments.mark_reviewed');

    // Route để tìm comments tương tự
    Route::get('comments/{id}/similar', [CommentController::class, 'similar'])->name('admin.comments.similar');
});
