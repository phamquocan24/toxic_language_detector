<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Auth;
use App\Models\User;

class LoginController extends Controller
{
    /*
    |--------------------------------------------------------------------------
    | Login Controller
    |--------------------------------------------------------------------------
    |
    | This controller handles authenticating users for the application and
    | redirecting them to your home screen. The controller uses a trait
    | to conveniently provide its functionality to your applications.
    |
    */

    /**
     * Display the login form.
     */
    public function showLoginForm()
    {
        return view('auth.login');
    }

    /**
     * Handle a login request to the API backend.
     */
    public function login(Request $request)
    {
        // Validate input
        $request->validate([
            'username' => 'required|string',
            'password' => 'required|string',
        ]);

        // Call the backend token endpoint using form data
        $response = Http::asForm()->post(config('services.api.url').'/auth/token', [
            'username' => $request->username,
            'password' => $request->password,
        ]);

        if ($response->successful()) {
            $token = $response->json('access_token');
            // Retrieve user info from backend
            $userRes = Http::withToken($token)
                ->get(config('services.api.url').'/auth/me');
            
            if ($userRes->successful()) {
                // FastAPI return format might have a 'user' key or direct user data
                $apiUser = $userRes->json();
                if (isset($apiUser['user'])) {
                    $apiUser = $apiUser['user'];
                }
                
                // Store token and user in session
                session([
                    'api_token' => $token,
                    'api_user' => $apiUser,
                ]);
                
                return redirect()->intended(route('admin.dashboard'));
            }
        }

        // On failure, redirect back with error
        return back()->withErrors([
            'username' => $response->json('message', 'Login failed'),
        ]);
    }

    /**
     * Log the user out by revoking API token and clearing session.
     */
    public function logout(Request $request)
    {
        $token = session('api_token');
        if ($token) {
            Http::withHeaders(['Authorization' => "Bearer $token"]);
            // Optional: call backend logout
            Http::post(config('services.api.url').'/auth/logout');
        }
        // Clear session
        $request->session()->flush();
        return redirect()->route('login');
    }
}
