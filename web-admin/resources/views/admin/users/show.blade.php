@extends('layouts.admin')

@section('title', 'Chi tiết người dùng')

@section('content')
<div class="container-fluid">
    <!-- Page Heading -->
    <div class="d-sm-flex align-items-center justify-content-between mb-4">
        <h1 class="h3 mb-0 text-gray-800">Chi tiết người dùng</h1>
        <div>
            <a href="{{ route('admin.users.edit', $user) }}" class="btn btn-primary btn-sm">
                <i class="fas fa-edit fa-sm text-white-50 mr-1"></i> Chỉnh sửa
            </a>
            <a href="{{ route('admin.users.index') }}" class="btn btn-secondary btn-sm">
                <i class="fas fa-arrow-left fa-sm text-white-50 mr-1"></i> Quay lại
            </a>
        </div>
    </div>

    <!-- Content Row -->
    <div class="row">
        <!-- User Profile Card -->
        <div class="col-xl-4 col-md-12 mb-4">
            <div class="card border-left-primary shadow h-100 py-2">
                <div class="card-body">
                    <div class="text-center mb-4">
                        <img class="img-profile rounded-circle mb-3" src="{{ asset('img/undraw_profile.svg') }}" width="100">
                        <h4 class="font-weight-bold text-primary">{{ $user->name }}</h4>
                        <p class="mb-0">
                            @if($user->role == 'admin')
                                <span class="badge badge-primary">Quản trị viên</span>
                            @else
                                <span class="badge badge-secondary">Người dùng</span>
                            @endif
                            
                            @if($user->is_active)
                                <span class="badge badge-success">Hoạt động</span>
                            @else
                                <span class="badge badge-danger">Không hoạt động</span>
                            @endif
                        </p>
                    </div>
                    
                    <div class="user-details">
                        <div class="row mb-3">
                            <div class="col-5 font-weight-bold text-gray-800">Email:</div>
                            <div class="col-7">{{ $user->email }}</div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-5 font-weight-bold text-gray-800">Ngày tạo:</div>
                            <div class="col-7">{{ $user->created_at->format('d/m/Y H:i') }}</div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-5 font-weight-bold text-gray-800">Cập nhật:</div>
                            <div class="col-7">{{ $user->updated_at->format('d/m/Y H:i') }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- User Statistics -->
        <div class="col-xl-8 col-md-12 mb-4">
            <div class="card shadow mb-4">
                <div class="card-header py-3">
                    <h6 class="m-0 font-weight-bold text-primary">Thống kê người dùng</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <!-- Total Comments Card -->
                        <div class="col-xl-6 col-md-6 mb-4">
                            <div class="card border-left-info shadow h-100 py-2">
                                <div class="card-body">
                                    <div class="row no-gutters align-items-center">
                                        <div class="col mr-2">
                                            <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                                                Tổng bình luận</div>
                                            <div class="h5 mb-0 font-weight-bold text-gray-800">{{ $stats['total_comments'] ?? 0 }}</div>
                                        </div>
                                        <div class="col-auto">
                                            <i class="fas fa-comments fa-2x text-gray-300"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Clean Comments Card -->
                        <div class="col-xl-6 col-md-6 mb-4">
                            <div class="card border-left-success shadow h-100 py-2">
                                <div class="card-body">
                                    <div class="row no-gutters align-items-center">
                                        <div class="col mr-2">
                                            <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                                                Bình thường</div>
                                            <div class="h5 mb-0 font-weight-bold text-gray-800">{{ $stats['clean_comments'] ?? 0 }}</div>
                                        </div>
                                        <div class="col-auto">
                                            <i class="fas fa-check-circle fa-2x text-gray-300"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Offensive Comments Card -->
                        <div class="col-xl-6 col-md-6 mb-4">
                            <div class="card border-left-warning shadow h-100 py-2">
                                <div class="card-body">
                                    <div class="row no-gutters align-items-center">
                                        <div class="col mr-2">
                                            <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                                                Xúc phạm</div>
                                            <div class="h5 mb-0 font-weight-bold text-gray-800">{{ $stats['offensive_comments'] ?? 0 }}</div>
                                        </div>
                                        <div class="col-auto">
                                            <i class="fas fa-exclamation-circle fa-2x text-gray-300"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Hate Comments Card -->
                        <div class="col-xl-6 col-md-6 mb-4">
                            <div class="card border-left-danger shadow h-100 py-2">
                                <div class="card-body">
                                    <div class="row no-gutters align-items-center">
                                        <div class="col mr-2">
                                            <div class="text-xs font-weight-bold text-danger text-uppercase mb-1">
                                                Phân biệt</div>
                                            <div class="h5 mb-0 font-weight-bold text-gray-800">{{ $stats['hate_comments'] ?? 0 }}</div>
                                        </div>
                                        <div class="col-auto">
                                            <i class="fas fa-ban fa-2x text-gray-300"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Recent Activity -->
            <div class="card shadow mb-4">
                <div class="card-header py-3">
                    <h6 class="m-0 font-weight-bold text-primary">Hoạt động gần đây</h6>
                </div>
                <div class="card-body">
                    @if(isset($recentComments) && count($recentComments) > 0)
                        <div class="table-responsive">
                            <table class="table table-bordered" width="100%" cellspacing="0">
                                <thead>
                                    <tr>
                                        <th>Nội dung</th>
                                        <th>Phân loại</th>
                                        <th>Thời gian</th>
                                        <th></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    @foreach($recentComments as $comment)
                                    <tr>
                                        <td>{{ Str::limit($comment->content, 50) }}</td>
                                        <td>
                                            @if($comment->prediction == 'clean')
                                                <span class="badge badge-success">Bình thường</span>
                                            @elseif($comment->prediction == 'offensive')
                                                <span class="badge badge-warning">Xúc phạm</span>
                                            @elseif($comment->prediction == 'hate')
                                                <span class="badge badge-danger">Phân biệt</span>
                                            @elseif($comment->prediction == 'spam')
                                                <span class="badge badge-secondary">Spam</span>
                                            @else
                                                <span class="badge badge-info">{{ $comment->prediction }}</span>
                                            @endif
                                        </td>
                                        <td>{{ $comment->created_at->format('d/m/Y H:i') }}</td>
                                        <td>
                                            <a href="{{ route('user.comments.show', $comment) }}" class="btn btn-info btn-sm">
                                                <i class="fas fa-eye"></i>
                                            </a>
                                        </td>
                                    </tr>
                                    @endforeach
                                </tbody>
                            </table>
                        </div>
                    @else
                        <p class="text-center">Không có hoạt động gần đây</p>
                    @endif
                </div>
            </div>
        </div>
    </div>
</div>
@endsection 