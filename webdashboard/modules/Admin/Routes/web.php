<?php

use Illuminate\Support\Facades\Route;
use Modules\Admin\Http\Controllers\Admin\DashboardController;

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

Route::group(['prefix' => 'admin', 'middleware' => ['web', 'auth:api']], function () {
    Route::get('/', [DashboardController::class, 'index'])->name('admin.dashboard.index');
    Route::get('api/dashboard/latest-products', [DashboardController::class, 'getLatestProducts']);
    Route::get('api/dashboard/latest-brands', [DashboardController::class, 'getLatestBrands']);
    Route::get('api/dashboard/latest-users', [DashboardController::class, 'getLatestUsers']);
    Route::get('api/dashboard/product-prices', [DashboardController::class, 'getProductPrices']);
    Route::get('api/dashboard/stats', [DashboardController::class, 'getStats']);
});


