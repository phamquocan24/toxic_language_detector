@extends('admin::layout')

@component('admin::components.page.header')
    @slot('title', trans('admin::resource.create', ['resource' => trans('user::users.user')]))
    <li><a href="{{ route('admin.users.index') }}">{{ trans('user::users.users') }}</a></li>
    <li class="active">{{ trans('admin::resource.create', ['resource' => trans('user::users.user')]) }}</li>
@endcomponent

@section('content')
    <div id="app">
        <form class="user-form" method="POST" action="{{ route('admin.users.store') }}" id="user-form">
            @csrf
            <input type="hidden" name="redirect_after_save" id="redirect_after_save" value="0">

            <div class="row">
                <div class="user-form-left-column col-lg-8 col-md-12">
                    <div class="box box-primary">
                        <div class="box-header with-border">
                            <h3 class="box-title">{{ trans('user::users.form.basic_information') }}</h3>
                        </div>
                        <div class="box-body">
                            <div class="form-group {{ $errors->has('username') ? 'has-error' : '' }}">
                                <label for="username" class="control-label">
                                    {{ trans('user::users.form.username') }} <span class="text-red">*</span>
                                </label>
                                <input name="username" class="form-control" id="username"
                                       value="{{ old('username') }}" type="text"
                                       placeholder="{{ trans('user::users.placeholders.username') }}"
                                       required>
                                @error('username')
                                    <span class="help-block text-red">{{ $message }}</span>
                                @enderror
                            </div>

                            <div class="form-group {{ $errors->has('email') ? 'has-error' : '' }}">
                                <label for="email" class="control-label">
                                    {{ trans('user::users.form.email') }} <span class="text-red">*</span>
                                </label>
                                <input name="email" class="form-control" id="email"
                                       value="{{ old('email') }}" type="email"
                                       placeholder="{{ trans('user::users.placeholders.email') }}"
                                       required>
                                @error('email')
                                    <span class="help-block text-red">{{ $message }}</span>
                                @enderror
                            </div>

                            <div class="form-group {{ $errors->has('name') ? 'has-error' : '' }}">
                                <label for="name" class="control-label">
                                    {{ trans('user::users.form.name') }} <span class="text-red">*</span>
                                </label>
                                <input name="name" class="form-control" id="name"
                                       value="{{ old('name') }}" type="text"
                                       placeholder="{{ trans('user::users.placeholders.name') }}"
                                       required>
                                @error('name')
                                    <span class="help-block text-red">{{ $message }}</span>
                                @enderror
                            </div>

                        </div>
                    </div>
                </div>

                <div class="user-form-right-column col-lg-4 col-md-12">
                    <div class="box box-primary">
                        <div class="box-header with-border">
                            <h3 class="box-title">{{ trans('user::users.form.additional_information') }}</h3>
                        </div>
                        <div class="box-body">
                            <div class="form-group {{ $errors->has('role') ? 'has-error' : '' }}">
                                <label for="role" class="control-label">
                                    {{ trans('user::users.form.roles') }} <span class="text-red">*</span>
                                </label>
                                <select name="role" class="form-control" id="role" required>
                                    <option value="">{{ trans('user::users.placeholders.select_role') }}</option>
                                    @foreach($roles as $roleId => $roleName)
                                        <option value="{{ $roleId }}" {{ old('role') == $roleId ? 'selected' : '' }}>
                                            {{ $roleName }}
                                        </option>
                                    @endforeach
                                </select>
                                @error('role')
                                    <span class="help-block text-red">{{ $message }}</span>
                                @enderror
                            </div>
                            <div class="form-group {{ $errors->has('password') ? 'has-error' : '' }}">
                                <label for="password" class="control-label">
                                    {{ trans('user::users.form.password') }} <span class="text-red">*</span>
                                </label>
                                <input name="password" class="form-control" id="password"
                                       type="password" placeholder="{{ trans('user::users.placeholders.password') }}"
                                       required>
                                @error('password')
                                    <span class="help-block text-red">{{ $message }}</span>
                                @enderror
                            </div>

                            <div class="form-group {{ $errors->has('password_confirmation') ? 'has-error' : '' }}">
                                <label for="password_confirmation" class="control-label">
                                    {{ trans('user::users.form.password_confirmation') }} <span class="text-red">*</span>
                                </label>
                                <input name="password_confirmation" class="form-control" id="password_confirmation"
                                       type="password" placeholder="{{ trans('user::users.placeholders.password_confirmation') }}"
                                       required>
                                @error('password_confirmation')
                                    <span class="help-block text-red">{{ $message }}</span>
                                @enderror
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="page-form-footer">
                <button type="submit" class="btn btn-primary save-exit-btn">
                    {{ trans('user::users.actions.save_and_exit') }}
                </button>
            </div>
        </form>
    </div>
@endsection

@push('scripts')
<script>
    $(document).ready(function () {
        $('.save-btn').click(function () {
            $('#redirect_after_save').val("0");
        });

        $('.save-exit-btn').click(function () {
            $('#redirect_after_save').val("1");
        });
    });
</script>
@endpush
