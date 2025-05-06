<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\User;
use App\Models\Comment;
use Illuminate\Support\Facades\Http;
use Carbon\Carbon;
use Illuminate\Support\Facades\Cache;

class DashboardController extends Controller
{
    /**
     * Display the dashboard with statistics.
     *
     * @return \Illuminate\Http\Response
     */
    public function index()
    {
        // Mock User stats since we're using an API and not local database
        $totalUsers = session('api_user') ? 1 : 0;
        $activeUsers = session('api_user') ? 1 : 0;
        $admins = (session('api_user') && isset(session('api_user')['role']) && session('api_user')['role'] == 'admin') ? 1 : 0;
        $recentUsers = session('api_user') ? [session('api_user')] : [];

        // Mock Comment stats
        $totalComments = 0;
        $commentStats = [
            'clean' => 0,
            'offensive' => 0,
            'hate' => 0,
            'spam' => 0,
        ];
        $recentComments = [];

        // API stats
        $apiStats = $this->getApiStats();

        return view('admin.dashboard', compact(
            'totalUsers',
            'activeUsers',
            'admins',
            'recentUsers',
            'totalComments',
            'commentStats',
            'recentComments',
            'apiStats'
        ));
    }

    /**
     * Get statistics from the API
     * 
     * @return array
     */
    private function getApiStats()
    {
        // Default stats in case API is unavailable
        $defaultStats = [
            'total_requests' => 0,
            'requests_today' => 0,
            'requests_this_week' => 0,
            'requests_this_month' => 0,
            'unique_users' => 0,
            'classification_distribution' => [
                'clean' => 0,
                'offensive' => 0,
                'hate' => 0,
                'spam' => 0
            ],
            'api_status' => 'offline'
        ];

        // Try to fetch data from cache first (5 minute cache)
        if (Cache::has('api_stats')) {
            return Cache::get('api_stats');
        }

        try {
            // Get API_URL and API_TOKEN from .env
            $apiUrl = env('API_URL', 'http://localhost:8000');
            $apiToken = env('API_TOKEN');

            // If no API token is configured, return default stats
            if (!$apiToken) {
                return $defaultStats;
            }

            $response = Http::withHeaders([
                'Authorization' => 'Bearer ' . $apiToken,
            ])->get($apiUrl . '/api/stats');

            if ($response->successful()) {
                $stats = $response->json();
                $stats['api_status'] = 'online';
                
                // Cache the results for 5 minutes
                Cache::put('api_stats', $stats, now()->addMinutes(5));
                
                return $stats;
            }
            
            return $defaultStats;
        } catch (\Exception $e) {
            return $defaultStats;
        }
    }
} 