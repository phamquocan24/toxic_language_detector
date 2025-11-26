<?php

namespace App\Providers;

use App\Services\ToxicDetectionService;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        // Sử dụng service thực tế
        $this->app->singleton(ToxicDetectionService::class, function ($app) {
            Log::info('Using real ToxicDetectionService');
            return new ToxicDetectionService();
        });
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        $this->loadTranslationsFrom(base_path('modules/Admin/Resources/lang'), 'admin');
    }
}
