<?php

namespace App\Http\Middleware;

use Illuminate\Auth\Middleware\Authenticate as Middleware;
use Illuminate\Http\Request;

class Authenticate extends Middleware
{
    /**
     * Get the path the user should be redirected to when they are not authenticated.
     */
    protected function redirectTo(Request $request): ?string
    {
        // Nếu request mong đợi JSON response (thường là từ API)
        // thì trả về null để middleware trả về 401 Unauthorized
        if ($request->expectsJson()) {
            return null;
        }

        // Xử lý riêng cho routes admin nếu cần
        if ($request->is('admin*')) {
            return route('login');
        }

        // Trả về route login mặc định cho các trường hợp khác
        return route('login');
    }
}
