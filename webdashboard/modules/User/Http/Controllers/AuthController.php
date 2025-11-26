<?php

namespace Modules\User\Http\Controllers;
use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Modules\User\Entities\User;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\Auth;
use Modules\User\Enums\UserRole;
use Illuminate\Support\Str;
use Illuminate\Support\Facades\Session;
use Illuminate\Support\Facades\Password;
use Illuminate\Auth\Events\PasswordReset;
use Illuminate\Support\Facades\Http;

class AuthController extends Controller
{
    public function __construct()
    {
        $this->middleware('auth')->except([
            'getLogin', 'postLogin', 'getReset', 'postReset', 'login', 'register', 'apiLogin',
            'showForgotForm', 'sendResetLinkEmail', 'showResetForm', 'resetPassword'
        ]);
    }

    // Web auth methods - sử dụng cho admin panel
    public function getLogin()
    {
        return view('user::auth.login');
    }

    public function postLogin(Request $request)
    {
        \Log::info('Đang thử đăng nhập với:', $request->only('email'));

        $validator = Validator::make($request->all(), [
            'email' => 'required|email',
            'password' => 'required|string',
        ]);

        if ($validator->fails()) {
            \Log::info('Validation failed:', $validator->errors()->toArray());
            return back()->withErrors($validator)->withInput();
        }

        $credentials = $request->only('email', 'password');

        try {
            \Log::info('Đang thử xác thực với dữ liệu local trước');

            // Xác thực local
            if (!Auth::attempt($credentials)) {
                \Log::info('Auth thất bại');
                return back()
                    ->withInput($request->only('email'))
                    ->withErrors(['email' => 'Thông tin đăng nhập không hợp lệ']);
            }

            \Log::info('Xác thực local thành công');

            // Người dùng đã xác thực thành công với database local
            $user = Auth::user();
            $user->last_login = now();
            $user->save();

            // Đồng bộ với API backend
            try {
                \Log::info('Đang đồng bộ với backend');

                // Gọi API backend để lấy token và thông tin người dùng
                $response = Http::withBasicAuth(
                        config('services.toxic_detection.oauth.client_id', ''),
                        config('services.toxic_detection.oauth.client_secret', '')
                    )
                    ->asForm()
                    ->post(config('services.toxic_detection.url') . config('services.toxic_detection.token_url'), [
                        'grant_type' => 'password',
                        'username' => $credentials['email'],
                        'password' => $credentials['password'],
                    ]);

                if ($response->successful()) {
                    $backendData = $response->json();
                    \Log::info('Đồng bộ backend thành công', ['status' => $response->status()]);

                    // Lưu token từ backend vào user
                    if (isset($backendData['access_token'])) {
                        $user->api_token = $backendData['access_token'];
                        $user->save();
                    }

                    // Nếu có thông tin bổ sung từ backend, có thể lưu thêm
                    Session::put('backend_user_data', $backendData['user'] ?? null);
                } else {
                    \Log::warning('Đồng bộ với backend thất bại nhưng vẫn cho phép đăng nhập', [
                        'status' => $response->status(),
                        'body' => $response->body()
                    ]);
                }
            } catch (\Exception $e) {
                \Log::error('Lỗi khi đồng bộ với backend: ' . $e->getMessage());
                // Vẫn tiếp tục đăng nhập ngay cả khi backend không khả dụng
            }

            // Tái tạo session để tránh session fixation
            $request->session()->regenerate();

            \Log::info('Session đã được tái tạo');

            // Nếu yêu cầu là AJAX hoặc mong đợi JSON
            if ($request->expectsJson()) {
                return response()->json([
                    'token' => $user->api_token ?? Str::random(60),
                    'user' => $user
                ]);
            }

            // Kiểm tra role và chuyển hướng phù hợp
            if ($user->isAdmin()) {
                return redirect()->intended(route('admin.dashboard.index'));
            }

            return redirect()->intended('/');

        } catch (\Exception $e) {
            \Log::error('Exception: ' . $e->getMessage());

            return back()
                ->withInput($request->only('email'))
                ->withErrors(['email' => 'Có lỗi không xác định: ' . $e->getMessage()]);
        }
    }

    public function getLogout(Request $request)
    {
        try {
            // Đăng xuất người dùng
            Auth::logout();

            // Vô hiệu hóa session
            $request->session()->invalidate();

            // Tái tạo CSRF token
            $request->session()->regenerateToken();

            // Xử lý phản hồi dựa trên loại yêu cầu
            if ($request->expectsJson()) {
                // API response
                return response()->json(['message' => 'Đăng xuất thành công']);
            } else {
                // Web response - chuyển hướng đến trang login
                return redirect()->route('login');
            }
        } catch (\Exception $e) {
            // Xử lý lỗi
            if ($request->expectsJson()) {
                return response()->json(['error' => 'Không thể đăng xuất: ' . $e->getMessage()], 500);
            }

            return back()->withErrors(['error' => 'Không thể đăng xuất. Vui lòng thử lại.']);
        }
    }

    public function getReset()
    {
        return view('user::auth.reset');
    }

    public function postReset(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'email' => 'required|email',
            'password' => 'required|string|min:6|confirmed',
            'token' => 'required|string'
        ]);

        if ($validator->fails()) {
            return back()->withErrors($validator)->withInput();
        }

        $user = User::where('email', $request->email)->first();

        if (!$user) {
            return back()->withErrors(['email' => 'Email không tồn tại'])->withInput();
        }

        $user->password = Hash::make($request->password);
        $user->save();

        return redirect()->route('login')->with('success', 'Mật khẩu đã được đặt lại thành công');
    }

    // Password reset methods
    public function showForgotForm()
    {
        return view('user::auth.forgot-password');
    }

    public function sendResetLinkEmail(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'email' => 'required|email'
        ]);

        if ($validator->fails()) {
            return back()->withErrors($validator)->withInput();
        }

        \Log::info('Đang gửi link reset password đến:', $request->only('email'));

        $status = Password::sendResetLink(
            $request->only('email')
        );

        \Log::info('Kết quả gửi reset link:', ['status' => $status]);

        return $status === Password::RESET_LINK_SENT
            ? back()->with(['status' => __($status)])
            : back()->withErrors(['email' => __($status)]);
    }

    public function showResetForm(Request $request, $token)
    {
        \Log::info('Hiển thị form reset password', [
            'token' => $token,
            'email' => $request->email
        ]);

        return view('user::auth.reset-password', [
            'token' => $token,
            'email' => $request->email
        ]);
    }

    public function resetPassword(Request $request)
    {
        \Log::info('Đang thực hiện reset password');

        $validator = Validator::make($request->all(), [
            'token' => 'required',
            'email' => 'required|email',
            'password' => 'required|string|min:8|confirmed',
        ]);

        if ($validator->fails()) {
            \Log::info('Validation failed:', $validator->errors()->toArray());
            return back()->withErrors($validator)->withInput();
        }

        $status = Password::reset(
            $request->only('email', 'password', 'password_confirmation', 'token'),
            function ($user, $password) {
                $user->forceFill([
                    'password' => Hash::make($password)
                ])->save();

                \Log::info('Password đã được reset cho user:', ['user_id' => $user->id]);
                event(new PasswordReset($user));
            }
        );

        \Log::info('Kết quả reset password:', ['status' => $status]);

        return $status === Password::PASSWORD_RESET
            ? redirect()->route('login')->with('status', __($status))
            : back()->withErrors(['email' => [__($status)]]);
    }

    // API auth methods
    // Sử dụng token authentication hoặc Sanctum thay cho JWT
    public function apiLogin(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'email' => 'required|email',
            'password' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json($validator->errors(), 422);
        }

        $credentials = $request->only('email', 'password');

        // Kiểm tra xác thực local trước
        if (!Auth::attempt($credentials)) {
            return response()->json(['error' => 'Unauthorized'], 401);
        }

        // Cập nhật thời gian đăng nhập cuối
        $user = Auth::user();
        $user->last_login = now();
        $user->save();

        // Đồng bộ với API backend
        try {
            $response = Http::withBasicAuth(
                config('services.toxic_detection.oauth.client_id', ''),
                config('services.toxic_detection.oauth.client_secret', '')
            )
            ->asForm()
            ->post(config('services.toxic_detection.url') . config('services.toxic_detection.token_url'), [
                'grant_type' => 'password',
                'username' => $credentials['email'],
                'password' => $credentials['password'],
            ]);

            if ($response->successful()) {
                $backendData = $response->json();

                // Sử dụng token từ backend nếu có
                if (isset($backendData['access_token'])) {
                    $token = $backendData['access_token'];
                    $user->api_token = $token;
                    $user->save();

                    return response()->json([
                        'access_token' => $token,
                        'token_type' => 'bearer',
                        'user' => $user,
                        'backend_user' => $backendData['user'] ?? null
                    ]);
                }
            }
        } catch (\Exception $e) {
            \Log::error('Lỗi khi đồng bộ API backend: ' . $e->getMessage());
        }

        // Fallback to local token if backend fails
        $token = Str::random(60);
        $user->api_token = $token;
        $user->save();

        return response()->json([
            'access_token' => $token,
            'token_type' => 'bearer',
            'user' => $user
        ]);
    }

    public function register(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'first_name' => 'required|string|max:255',
            'last_name' => 'required|string|max:255',
            'email' => 'required|string|email|max:255|unique:users',
            'password' => 'required|string|min:6|confirmed',
        ]);

        if ($validator->fails()) {
            return response()->json($validator->errors(), 422);
        }

        $user = User::create([
            'first_name' => $request->first_name,
            'last_name' => $request->last_name,
            'email' => $request->email,
            'password' => Hash::make($request->password),
            'role' => UserRole::MEMBER,
        ]);

        // Nếu muốn đăng nhập người dùng sau khi đăng ký
        Auth::login($user);

        // Tạo token cho API
        // Với Sanctum
        // $token = $user->createToken('api-token')->plainTextToken;

        // Hoặc với token đơn giản
        $token = Str::random(60);
        $user->api_token = $token;
        $user->save();

        return response()->json([
            'access_token' => $token,
            'token_type' => 'bearer',
            'user' => $user
        ]);
    }

    public function apiLogout(Request $request)
    {
        $user = Auth::user();

        // Với Sanctum:
        // $user->tokens()->delete();

        // Hoặc với token đơn giản:
        $user->api_token = null;
        $user->save();

        return response()->json(['message' => 'Successfully logged out']);
    }

    public function me()
    {
        return response()->json(Auth::user());
    }
}
