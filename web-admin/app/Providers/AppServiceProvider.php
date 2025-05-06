<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use Illuminate\Support\Facades\Auth;
use Illuminate\Http\Request;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        //
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        // Register a custom auth driver that uses the session API token
        Auth::viaRequest('api-session', function (Request $request) {
            // If we have an API token and user in the session, consider the user authenticated
            if ($token = session('api_token')) {
                if ($apiUser = session('api_user')) {
                    // Create and return a proper User model instance
                    return new \App\Models\User((array) $apiUser);
                }
            }
            
            return null;
        });
    }
}
