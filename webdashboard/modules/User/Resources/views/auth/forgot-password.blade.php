@extends('admin::layout')
@section('title', trans('user::auth.forgot_password'))
@section('content')
<div class="container">
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h3>{{ trans('user::auth.forgot_password') }}</h3>
                </div>

                <div class="card-body">
                    @if (session('status'))
                        <div class="alert alert-success" role="alert">
                            {{ session('status') }}
                        </div>
                    @endif

                    <form method="POST" action="{{ route('password.email') }}">
                        @csrf

                        <div class="form-group">
                            <label for="email">{{ trans('user::users.form.email') }} <span class="text-danger">*</span></label>
                            <input
                                id="email"
                                type="email"
                                class="form-control @error('email') is-invalid @enderror"
                                name="email"
                                value="{{ old('email') }}"
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
                            <button type="submit" class="btn btn-primary">
                                {{ trans('user::auth.send_reset_link') }}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
@endsection
