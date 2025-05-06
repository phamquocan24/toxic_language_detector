<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\ExtensionController;
use App\Http\Controllers\Api\AuthController;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "api" middleware group. Make something great!
|
*/

Route::middleware('auth:sanctum')->get('/user', function (Request $request) {
    return $request->user();
});

// Authentication routes
Route::prefix('auth')->group(function () {
    Route::post('/login', [AuthController::class, 'login']);
    Route::post('/token', [AuthController::class, 'token']);
    Route::post('/logout', [AuthController::class, 'logout'])->middleware('auth:sanctum');
    Route::get('/user', [AuthController::class, 'user'])->middleware('auth:sanctum');
});

// API routes for Extension
Route::prefix('extension')->group(function () {
    // Public API endpoint
    Route::post('/detect', [ExtensionController::class, 'detect']);
    Route::post('/batch-detect', [ExtensionController::class, 'batchDetect']);
    
    // Protected API endpoints
    Route::middleware('auth:sanctum')->group(function () {
        Route::get('/stats', [ExtensionController::class, 'getStats']);
    });
}); 