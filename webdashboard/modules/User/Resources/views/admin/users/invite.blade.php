@extends('admin::layout')

@component('admin::components.page.header')
    @slot('title', trans('admin::resource.invite', ['resource' => trans('user::users.user')]))
    <li><a href="{{ route('admin.users.index') }}">Users</a></li>
    <li class="active">{{ trans('admin::resource.invite', ['resource' => trans('user::users.user')]) }}</li>
@endcomponent

@section('content')
<div class="row">
    <!-- Invite User Form (Left Side) -->
    <div class="col-md-6">
        <div class="box box-primary">
            <div class="box-header with-border">
                <h3 class="box-title">Invite User</h3>
            </div>
            <div class="box-body">
                <form method="POST" action="{{ route('admin.users.send_invitation') }}">
                    @csrf

                    <div class="form-group">
                        <label for="email">Email<span class="text-red">*</span></label>
                        <input type="email" name="email" id="email" class="form-control" value="{{ old('email') }}" required>
                        @error('email')
                            <span class="help-block text-red">{{ $message }}</span>
                        @enderror
                    </div>

                    <div class="form-group">
                        <label for="role">Role<span class="text-red">*</span></label>
                        <input type="text" class="form-control" value="Administrator" readonly>
                        <input type="hidden" name="role" id="role" value="1">
                    </div>

                    <div class="form-group">
                        <button type="submit" class="btn btn-primary">Send Invitation</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Pending Invitations (Right Side) -->
    <div class="col-md-6">
        <div class="box box-primary">
            <div class="box-header with-border">
                <h3 class="box-title">Pending Invitations</h3>
            </div>

            <div class="box-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Sent At</th>
                                <th>Expires At</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach($pendingInvitations as $invitation)
                                <tr>
                                    <td>{{ $invitation->email }}</td>
                                    <td>
                                        @if($invitation->role == 1)
                                            <span class="badge badge-warning">Administrator</span>
                                        @else
                                            <span class="badge badge-primary">Member</span>
                                        @endif
                                    </td>
                                    <td>{{ $invitation->created_at->format('Y-m-d H:i') }}</td>
                                    <td>
                                        <span class="{{ Carbon\Carbon::parse($invitation->expires_at)->isPast() ? 'text-red' : '' }}">
                                            {{ Carbon\Carbon::parse($invitation->expires_at)->format('Y-m-d H:i') }}
                                        </span>
                                    </td>
                                    <td>
                                        <form method="POST" action="{{ route('admin.users.resend_invitation', $invitation->id) }}" style="display: inline;">
                                            @csrf
                                            <button type="submit" class="btn btn-sm btn-info">Resend</button>
                                        </form>
                                    </td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
@endsection
