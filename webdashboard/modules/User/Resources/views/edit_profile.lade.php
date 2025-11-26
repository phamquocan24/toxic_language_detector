@extends('auth::layout')

@component('admin::components.page.header')
    @slot('title', trans('admin::resource.edit', ['resource' => trans('admin::profile.profile')]))
    <li><a href="{{ route('admin.profile.edit') }}">{{ trans('admin::profile.profile') }}</a></li>
    <li class="active">{{ trans('admin::resource.edit', ['resource' => trans('admin::profile.profile')]) }}</li>
@endcomponent

@section('content')
    <div id="app" v-cloak>
        <form
            class="profile-form"
            method="POST"
            action="{{ route('admin.profile.update') }}"
        >
            @csrf
            @method('PUT')

            <div class="row">
                <div class="profile-form-left-column col-lg-8 col-md-12">
                    <div class="form-group">
                        <label for="first_name">{{ trans('admin::profile.first_name') }}<span class="m-l-5 text-red">*</span></label>
                        <input name="first_name" class="form-control" id="first_name" value="{{ old('first_name', $user->first_name) }}" type="text">
                    </div>

                    <div class="form-group">
                        <label for="last_name">{{ trans('admin::profile.last_name') }}<span class="m-l-5 text-red">*</span></label>
                        <input name="last_name" class="form-control" id="last_name" value="{{ old('last_name', $user->last_name) }}" type="text">
                    </div>

                    <div class="form-group">
                        <label for="phone">{{ trans('admin::profile.phone') }}<span class="m-l-5 text-red">*</span></label>
                        <input name="phone" class="form-control" id="phone" value="{{ old('phone', $user->phone) }}" type="text">
                    </div>

                    <div class="form-group">
                        <label for="email">{{ trans('admin::profile.email') }}<span class="m-l-5 text-red">*</span></label>
                        <input name="email" class="form-control" id="email" value="{{ old('email', $user->email) }}" type="email">
                    </div>
                </div>

                <div class="profile-form-right-column col-lg-4 col-md-12">
                    <div class="form-group">
                        <label for="password">{{ trans('admin::profile.new_password') }}</label>
                        <input name="password" class="form-control" id="password" value="" type="password">
                    </div>

                    <div class="form-group">
                        <label for="password_confirmation">{{ trans('admin::profile.confirm_new_password') }}</label>
                        <input name="password_confirmation" class="form-control" id="password_confirmation" value="" type="password">
                    </div>
                </div>
            </div>

            <div class="page-form-footer">
                <button type="submit" class="btn btn-default save-btn">
                    {{ trans('admin::resource.save') }}
                </button>
                <button type="submit" class="btn btn-primary save-exit-btn">
                    {{ trans('admin::resource.save_exit') }}
                </button>
            </div>
        </form>
    </div>
@endsection
