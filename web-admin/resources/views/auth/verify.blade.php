@extends('layouts.auth')

@section('title', 'Xác thực email')

@section('content')
<div class="container">
    <div class="row justify-content-center vh-100 align-items-center">
        <div class="col-md-6">
            <div class="card shadow-lg">
                <div class="card-header bg-primary py-3">
                    <h4 class="text-white mb-0 text-center">Xác thực địa chỉ email</h4>
                </div>
                <div class="card-body p-4">
                    @if (session('resent'))
                        <div class="alert alert-success" role="alert">
                            Đã gửi một liên kết xác thực mới đến địa chỉ email của bạn.
                        </div>
                    @endif

                    <div class="text-center mb-4">
                        <i class="fas fa-envelope-open-text text-primary" style="font-size: 4rem;"></i>
                    </div>

                    <p class="mb-3">Trước khi tiếp tục, vui lòng kiểm tra email của bạn để xác thực địa chỉ email. Email xác thực đã được gửi đến <strong>{{ auth()->user()->email }}</strong>.</p>
                    
                    <p class="mb-4">Nếu bạn không nhận được email, bạn có thể yêu cầu gửi lại bằng cách nhấn vào nút dưới đây.</p>

                    <form class="d-flex justify-content-center" method="POST" action="{{ route('verification.resend') }}">
                        @csrf
                        <button type="submit" class="btn btn-primary px-4">
                            <i class="fas fa-paper-plane me-2"></i>Gửi lại email xác thực
                        </button>
                    </form>
                </div>
                <div class="card-footer text-center py-3 bg-light">
                    <form action="{{ route('logout') }}" method="POST" class="d-inline">
                        @csrf
                        <button type="submit" class="btn btn-link text-decoration-none">
                            <i class="fas fa-sign-out-alt me-1"></i>Đăng xuất
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
@endsection
