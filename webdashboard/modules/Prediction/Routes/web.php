<?php

use Illuminate\Support\Facades\Route;
use Modules\Prediction\Http\Controllers\PredictionController;

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

Route::group(['prefix' => 'prediction'], function () {
    Route::get('/batch', [PredictionController::class, 'batch'])->name('admin.prediction.batch');
    Route::post('/batch/process', [PredictionController::class, 'processBatch'])->name('admin.prediction.batch.process');

    Route::get('/upload', [PredictionController::class, 'upload'])->name('admin.prediction.upload');
    Route::post('/upload/process', [PredictionController::class, 'processUpload'])->name('admin.prediction.upload.process');

    Route::get('/similar', [PredictionController::class, 'similar'])->name('admin.prediction.similar');
    Route::get('/similar/{commentId}', [PredictionController::class, 'getSimilar'])->name('admin.prediction.similar.get');
});
