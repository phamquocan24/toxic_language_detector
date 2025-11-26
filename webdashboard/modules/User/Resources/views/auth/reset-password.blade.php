@extends('admin::layout')
@section('title', trans('user::auth.reset_password'))

@section('content')
<div class="container">
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h3>{{ trans('user::auth.reset_password') }}</h3>
                </div>

                <div class="card-body">
                    <form method="POST" action="{{ route('password.update') }}">
                        @csrf

                        <input type="hidden" name="token" value="{{ $token }}">

                        <div class="form-group">
                            <label for="email">{{ trans('user::users.form.email') }} <span class="text-danger">*</span></label>
                            <input
                                id="email"
                                type="email"
                                class="form-control @error('email') is-invalid @enderror"
                                name="email"
                                value="{{ $email ?? old('email') }}"
                                placeholder="Enter email address"
                                required
                                autocomplete="email"
                                autofocus
                            >
                            @error('email')
                                <span class="invalid-feedback" role="alert">
                                    <strong>{{ $message }}</strong>
                                </span>
                            @enderror
                        </div>

                        <div class="form-group">
                            <label for="password">{{ trans('user::users.form.password') }} <span class="text-danger">*</span></label>
                            <input
                                id="password"
                                type="password"
                                class="form-control @error('password') is-invalid @enderror"
                                name="password"
                                placeholder="Enter password"
                                required
                                autocomplete="new-password"
                            >
                            @error('password')
                                <span class="invalid-feedback" role="alert">
                                    <strong>{{ $message }}</strong>
                                </span>
                            @enderror
                        </div>

                        <div class="form-group">
                            <label for="password-confirm">{{ trans('user::users.form.password_confirmation') }} <span class="text-danger">*</span></label>
                            <input
                                id="password-confirm"
                                type="password"
                                class="form-control"
                                name="password_confirmation"
                                placeholder="Enter password confirmation"
                                required
                                autocomplete="new-password"
                            >
                        </div>

                        <div class="form-group">
                            <button type="submit" class="btn btn-primary">
                                {{ trans('user::auth.reset_password') }}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
@endsection
