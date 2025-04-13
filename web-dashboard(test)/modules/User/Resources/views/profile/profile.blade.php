@extends('admin::layout')

@component('admin::components.page.header')
    @slot('title', 'Edit Profile')

    <li class="active">Edit Profile</li>
@endcomponent

@section('content')
<section class="content">
    <form method="POST" action="{{ route('admin.profile.update') }}" class="form-horizontal" id="profile-form" novalidate>
        @csrf


        <div class="accordion-content clearfix">
            <div class="col-lg-3 col-md-4">
                <div class="accordion-box">
                    <div class="panel-group" id="ProfileTabs">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h4 class="panel-title">
                                    <a>
                                        Profile Information
                                    </a>
                                </h4>
                            </div>

                            <div id="profile_information" class="panel-collapse collapse in">
                                <div class="panel-body">
                                    <ul class="accordion-tab nav nav-tabs">
                                        <li class="{{ request()->input('tab') !== 'newPassword' ? 'active' : '' }}">
                                            <a href="#account" data-toggle="tab">Account</a>
                                        </li>
                                        <li class="{{ request()->input('tab') === 'newPassword' ? 'active' : '' }}">
                                            <a href="#newPassword" data-toggle="tab">New Password</a>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-lg-9 col-md-8">
                <div class="accordion-box-content">
                    <div class="tab-content clearfix">
                        <div class="tab-pane fade {{ request()->input('tab') !== 'newPassword' ? 'active in' : '' }}" id="account">
                            <h4 class="tab-content-title">Account</h4>
                            <div class="row">
                                <div class="col-md-8">
                                    <div class="form-group">
                                        <label for="first_name" class="col-md-3 control-label text-left">
                                            First Name<span class="m-l-5 text-red">*</span>
                                        </label>
                                        <div class="col-md-9">
                                            <input name="first_name" class="form-control {{ $errors->has('first_name') ? 'is-invalid' : '' }}"
                                                id="first_name" value="{{ old('first_name', $user->first_name) }}" type="text">
                                            @error('first_name')
                                                <span class="help-block text-red">{{ $message }}</span>
                                            @enderror
                                        </div>
                                    </div>

                                    <div class="form-group">
                                        <label for="last_name" class="col-md-3 control-label text-left">
                                            Last Name<span class="m-l-5 text-red">*</span>
                                        </label>
                                        <div class="col-md-9">
                                            <input name="last_name" class="form-control {{ $errors->has('last_name') ? 'is-invalid' : '' }}"
                                                id="last_name" value="{{ old('last_name', $user->last_name) }}" type="text">
                                            @error('last_name')
                                                <span class="help-block text-red">{{ $message }}</span>
                                            @enderror
                                        </div>
                                    </div>

                                    <div class="form-group">
                                        <label for="phone" class="col-md-3 control-label text-left">
                                            Phone<span class="m-l-5 text-red">*</span>
                                        </label>
                                        <div class="col-md-9">
                                            <input name="phone" class="form-control {{ $errors->has('phone') ? 'is-invalid' : '' }}"
                                                id="phone" value="{{ old('phone', $user->phone ?? '') }}" type="text">
                                            @error('phone')
                                                <span class="help-block text-red">{{ $message }}</span>
                                            @enderror
                                        </div>
                                    </div>

                                    <div class="form-group">
                                        <label for="email" class="col-md-3 control-label text-left">
                                            Email<span class="m-l-5 text-red">*</span>
                                        </label>
                                        <div class="col-md-9">
                                            <input name="email" class="form-control {{ $errors->has('email') ? 'is-invalid' : '' }}"
                                                id="email" value="{{ old('email', $user->email) }}" type="email">
                                            @error('email')
                                                <span class="help-block text-red">{{ $message }}</span>
                                            @enderror
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="tab-pane fade {{ request()->input('tab') === 'newPassword' ? 'active in' : '' }}" id="newPassword">
                            <h4 class="tab-content-title">New Password</h4>
                            <div class="row">
                                <div class="col-md-8">
                                    <div class="form-group">
                                        <label for="password" class="col-md-3 control-label text-left">New Password</label>
                                        <div class="col-md-9">
                                            <input name="password" class="form-control {{ $errors->has('password') ? 'is-invalid' : '' }}"
                                                id="password" value="" type="password">
                                            @error('password')
                                                <span class="help-block text-red">{{ $message }}</span>
                                            @enderror
                                        </div>
                                    </div>

                                    <div class="form-group">
                                        <label for="password_confirmation" class="col-md-3 control-label text-left">
                                            Confirm New Password
                                        </label>
                                        <div class="col-md-9">
                                            <input name="password_confirmation" class="form-control"
                                                id="password_confirmation" value="" type="password">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="form-group">
                            <div class="col-md-10 col-md-offset-2">
                                <button type="submit" class="btn btn-primary" data-loading>
                                    Save
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </form>
</section>
@endsection

@push('scripts')
<script>
    $(function () {
        // Lưu active tab vào localStorage
        $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
            var activeTab = $(e.target).attr('href').substring(1);

            // Cập nhật URL khi chuyển tab
            var url = new URL(window.location.href);
            if (activeTab === 'account') {
                url.searchParams.delete('tab');
            } else {
                url.searchParams.set('tab', activeTab);
            }
            history.replaceState(null, '', url);

            // Cập nhật action của form tùy theo tab đang active
            if (activeTab === 'newPassword') {
                $('#profile-form').attr('action', '{{ route("admin.password.change") }}');
            } else {
                $('#profile-form').attr('action', '{{ route("admin.profile.update") }}');
            }
        });

        // Cập nhật action của form khi trang load
        const urlParams = new URLSearchParams(window.location.search);
        const tab = urlParams.get('tab');
        if (tab === 'newPassword') {
            $('#profile-form').attr('action', '{{ route("admin.password.change") }}');
        }

        // Hiển thị thông báo thành công
        @if(session('success'))
            $.notify({
                message: '{{ session("success") }}'
            }, {
                type: 'success',
                placement: {
                    from: 'top',
                    align: 'center'
                }
            });
        @endif

        // Hiển thị thông báo lỗi
        @if(session('error'))
            $.notify({
                message: '{{ session("error") }}'
            }, {
                type: 'danger',
                placement: {
                    from: 'top',
                    align: 'center'
                }
            });
        @endif
    });
</script>
@endpush
