@component('mail::message')
# Lời mời tham gia!

Xin chào,

Bạn đã được mời tham gia {{ config('app.name') }}.

@php
    // Xác định tên vai trò dựa trên giá trị số nguyên
    $roleName = match((int)$invitation->role) {
        \Modules\User\Enums\UserRole::ADMINISTRATOR => 'Quản trị viên',
        \Modules\User\Enums\UserRole::MEMBER => 'Thành viên',
        default => 'Người dùng', // Giá trị dự phòng
    };
@endphp

Bạn được mời với vai trò: **{{ $roleName }}**.

Để chấp nhận lời mời này và tạo tài khoản, vui lòng nhấp vào nút bên dưới:

@component('mail::button', ['url' => route('invitation.accept', ['token' => $invitation->token])])
Chấp nhận lời mời
@endcomponent

Liên kết mời này có hiệu lực đến: {{ $invitation->expires_at->format('d/m/Y H:i') }}.

Nếu bạn không mong đợi lời mời này, bạn có thể bỏ qua email này.

Trân trọng,<br>
{{ config('app.name') }}
@endcomponent
