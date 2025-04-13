<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class AdminVerify
{
    /**
     * Handle an incoming request.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \Closure  $next
     * @return mixed
     */
    public function handle(Request $request, Closure $next)
    {
        if (Auth::check() && Auth::user()->isAdmin()) {
            return $next($request);
        }

        // Nếu không phải admin, xử lý dựa trên loại request
        if ($request->expectsJson()) {
            return response()->json(['error' => 'Unauthorized. Admin access required.'], 403);
        }

        // Đối với request web, chuyển hướng hoặc trả về lỗi 403
        return abort(403, 'Unauthorized. Admin access required.');
    }
}
