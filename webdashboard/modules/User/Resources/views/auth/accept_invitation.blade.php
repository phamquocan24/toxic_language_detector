@extends('admin::layout')

@component('admin::components.page.header')
    @slot('title', 'Accept Invitation')
@endcomponent

@section('content')
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="box box-primary">
                <div class="box-header with-border">
                    <h3 class="box-title">{{ trans('user::users.invitation.register_form') }}</h3>
                </div>

                <div class="box-body">
                    @if($invitation->isExpired())
                        <div class="alert alert-danger">
                            {{ trans('user::users.messages.invitation_expired') }}
                        </div>
                    @elseif($invitation->isAccepted())
                        <div class="alert alert-info">
                            {{ trans('user::users.messages.invitation_already_accepted') }}
                        </div>
                    @else
                        <form method="POST" action="{{ route('invitation.register') }}" class="form-horizontal">
                            @csrf
                            <input type="hidden" name="token" value="{{ $invitation->token }}">
                            <div class="form-group">
                                <label for="first_name" class="col-md-4 control-label">
                                    {{ trans('user::users.form.first_name') }} <span class="text-red">*</span>
                                </label>
                                <div class="col-md-6">
                                    <input id="first_name" type="text" class="form-control @error('first_name') is-invalid @enderror"
                                           name="first_name" value="{{ old('first_name') }}" required autofocus>
                                    @error('first_name')
                                        <span class="help-block text-red" role="alert">
                                            <strong>{{ $message }}</strong>
                                        </span>
                                    @enderror
                                </div>
                            </div>

                            <div class="form-group">
                                <label for="last_name" class="col-md-4 control-label">
                                    {{ trans('user::users.form.last_name') }} <span class="text-red">*</span>
                                </label>
                                <div class="col-md-6">
                                    <input id="last_name" type="text" class="form-control @error('last_name') is-invalid @enderror"
                                           name="last_name" value="{{ old('last_name') }}" required>
                                    @error('last_name')
                                        <span class="help-block text-red" role="alert">
                                            <strong>{{ $message }}</strong>
                                        </span>
                                    @enderror
                                </div>
                            </div>

                            <div class="form-group">
                                <label for="email" class="col-md-4 control-label">
                                    {{ trans('user::users.form.email') }}
                                </label>
                                <div class="col-md-6">
                                    <input id="email" type="email" class="form-control"
                                           name="email" value="{{ $invitation->email }}" readonly disabled>
                                </div>
                            </div>

                            <div class="form-group">
                                <label for="password" class="col-md-4 control-label">
                                    {{ trans('user::users.form.password') }} <span class="text-red">*</span>
                                </label>
                                <div class="col-md-6">
                                    <input id="password" type="password" class="form-control @error('password') is-invalid @enderror"
                                           name="password" required autocomplete="new-password">
                                    @error('password')
                                        <span class="help-block text-red" role="alert">
                                            <strong>{{ $message }}</strong>
                                        </span>
                                    @enderror
                                </div>
                            </div>

                            <div class="form-group">
                                <label for="password-confirm" class="col-md-4 control-label">
                                    {{ trans('user::users.form.password_confirmation') }} <span class="text-red">*</span>
                                </label>
                                <div class="col-md-6">
                                    <input id="password-confirm" type="password" class="form-control"
                                           name="password_confirmation" required autocomplete="new-password">
                                </div>
                            </div>

                            <div class="form-group">
                                <div class="col-md-6 col-md-offset-4">
                                    <button type="submit" class="btn btn-primary">
                                        {{ trans('user::users.actions.register') }}
                                    </button>
                                </div>
                            </div>
                        </form>
                    @endif
                </div>
            </div>
        </div>
    </div>
</div>
@endsection
