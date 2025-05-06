@extends('layouts.auth')

@section('title', 'Đăng ký')

@section('content')
<div class="container">
    <div class="row justify-content-center vh-100 align-items-center">
        <div class="col-md-6">
            <div class="card shadow-lg">
                <div class="card-header bg-primary py-3">
                    <h4 class="text-white mb-0 text-center">Đăng ký tài khoản</h4>
                </div>
                <div class="card-body p-4">
                    <form method="POST" action="{{ route('register') }}">
                        @csrf

                        <div class="mb-3">
                            <label for="name" class="form-label">Họ và tên</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-user"></i></span>
                                <input id="name" type="text" class="form-control @error('name') is-invalid @enderror" name="name" value="{{ old('name') }}" required autocomplete="name" autofocus>
                                @error('name')
                                    <span class="invalid-feedback" role="alert">
                                        <strong>{{ $message }}</strong>
                                    </span>
                                @enderror
                            </div>
                        </div>

                        <div class="mb-3">
                            <label for="email" class="form-label">Email</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-envelope"></i></span>
                                <input id="email" type="email" class="form-control @error('email') is-invalid @enderror" name="email" value="{{ old('email') }}" required autocomplete="email">
                                @error('email')
                                    <span class="invalid-feedback" role="alert">
                                        <strong>{{ $message }}</strong>
                                    </span>
                                @enderror
                            </div>
                        </div>

                        <div class="mb-3">
                            <label for="password" class="form-label">Mật khẩu</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                <input id="password" type="password" class="form-control @error('password') is-invalid @enderror" name="password" required autocomplete="new-password">
                                <button type="button" class="btn btn-outline-secondary" id="password-toggle">
                                    <i class="fas fa-eye" id="password-eye"></i>
                                </button>
                                @error('password')
                                    <span class="invalid-feedback" role="alert">
                                        <strong>{{ $message }}</strong>
                                    </span>
                                @enderror
                            </div>
                            <div class="form-text">Mật khẩu phải có ít nhất 8 ký tự.</div>
                        </div>

                        <div class="mb-4">
                            <label for="password-confirm" class="form-label">Xác nhận mật khẩu</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                <input id="password-confirm" type="password" class="form-control" name="password_confirmation" required autocomplete="new-password">
                                <button type="button" class="btn btn-outline-secondary" id="confirm-toggle">
                                    <i class="fas fa-eye" id="confirm-eye"></i>
                                </button>
                            </div>
                        </div>

                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary btn-lg">
                                <i class="fas fa-user-plus me-2"></i>Đăng ký
                            </button>
                        </div>
                    </form>
                </div>
                <div class="card-footer text-center py-3 bg-light">
                    <div>Đã có tài khoản? <a href="{{ route('login') }}" class="text-decoration-none">Đăng nhập ngay</a></div>
                </div>
            </div>
        </div>
    </div>
</div>
@endsection

@push('scripts')
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const passwordToggle = document.getElementById('password-toggle');
        const passwordInput = document.getElementById('password');
        const passwordEye = document.getElementById('password-eye');
        
        const confirmToggle = document.getElementById('confirm-toggle');
        const confirmInput = document.getElementById('password-confirm');
        const confirmEye = document.getElementById('confirm-eye');
        
        passwordToggle.addEventListener('click', function() {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                passwordEye.classList.remove('fa-eye');
                passwordEye.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                passwordEye.classList.remove('fa-eye-slash');
                passwordEye.classList.add('fa-eye');
            }
        });
        
        confirmToggle.addEventListener('click', function() {
            if (confirmInput.type === 'password') {
                confirmInput.type = 'text';
                confirmEye.classList.remove('fa-eye');
                confirmEye.classList.add('fa-eye-slash');
            } else {
                confirmInput.type = 'password';
                confirmEye.classList.remove('fa-eye-slash');
                confirmEye.classList.add('fa-eye');
            }
        });
    });
</script>
@endpush
