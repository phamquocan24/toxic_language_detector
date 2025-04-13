<?php

use App\Models\Brand;
use Illuminate\Support\Facades\Route;
use Modules\Brand\Http\Controllers\Admin\BrandController;

Route::get('brands', [BrandController::class, 'index'])->name('admin.brands.index');
Route::get('admin/brands/create', [BrandController::class, 'create'])->name('admin.brands.create');
Route::post('brands', [BrandController::class, 'store'])->name('admin.brands.store');
Route::get('brands/{id}/edit', [BrandController::class, 'edit'])->name('admin.brands.edit');
Route::put('admin/brands/{id}', [BrandController::class, 'update'])->name('admin.brands.update');
Route::delete('admin/brands/bulk-delete', [BrandController::class, 'bulkDelete'])->name('admin.brands.bulkDelete');
Route::get('admin/brands/search', [BrandController::class, 'search'])->name('admin.brands.search');
