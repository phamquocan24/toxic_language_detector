<?php

use Illuminate\Support\Facades\Route;
use Modules\Product\Http\Controllers\Admin\ProductController;

Route::get('products', [ProductController::class, 'index'])->name('admin.products.index');

Route::get('products/create', [ProductController::class, 'create'])->name('admin.products.create');

Route::post('products', [ProductController::class, 'store'])->name('admin.products.store');

Route::get('products/{id}/edit', [ProductController::class, 'edit'])->name('admin.products.edit');

Route::put('products/{id}', [ProductController::class, 'update'])->name('admin.products.update');

Route::delete('products/{ids}', [ProductController::class, 'delete'])->name('admin.products.delete');

Route::get('products/index/table', [ProductController::class, 'table'])->name('admin.products.table');

Route::post('products/delete', [ProductController::class, 'delete'])->name('admin.products.delete');
