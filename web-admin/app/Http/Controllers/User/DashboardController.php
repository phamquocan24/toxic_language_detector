<?php

namespace App\Http\Controllers\User;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Http;

class DashboardController extends Controller
{
    /**
     * Hiển thị dashboard user với thống kê cá nhân
     */
    public function index()
    {
        // Lấy thông tin người dùng từ session
        $apiUser = session('api_user');
        
        // Thống kê giả
        $dbStats = [
            'total' => 0,
            'clean' => 0,
            'offensive' => 0,
            'hate' => 0,
            'spam' => 0,
            'recent_comments' => [],
        ];
        
        // Thử lấy thống kê từ API nếu có token
        $apiStats = null;
        if ($token = session('api_token')) {
            try {
                $response = Http::withToken($token)
                    ->get(config('services.api.url').'/user/stats');
                
                if ($response->successful()) {
                    $apiStats = $response->json();
                }
            } catch (\Exception $e) {
                // Xử lý lỗi khi gọi API
                $apiStats = null;
            }
        }
        
        // Kết hợp thống kê
        $stats = [
            'api' => $apiStats,
            'db' => $dbStats,
            'user' => $apiUser
        ];
        
        return view('user.dashboard', compact('stats'));
    }
} 