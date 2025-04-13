<?php

use App\Models\Category;
use Illuminate\Support\Facades\Route;
use Modules\Category\Http\Controllers\Admin\CategoryController;

Route::get('categories', [CategoryController::class, 'index'])->name('admin.categories.index');
Route::get('categories/create', [CategoryController::class, 'create'])->name('admin.categories.create');
Route::post('categories', [CategoryController::class, 'store'])->name('admin.categories.store');
Route::get('categories/{id}', [CategoryController::class, 'show'])->name('admin.categories.show');
