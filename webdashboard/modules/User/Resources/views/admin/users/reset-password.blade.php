@component('mail::message')
# Reset Your Password

You're receiving this email because a password reset request was made for your account.

@component('mail::button', ['url' => route('password.reset', ['token' => $token, 'email' => $email])])
Reset Password
@endcomponent

This password reset link will expire in 60 minutes.

If you did not request a password reset, no further action is required.

Thanks,<br>
{{ config('app.name') }}
@endcomponent
