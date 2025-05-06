@extends('layouts.admin')

@section('title', 'Chi tiết bình luận')

@section('content')
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="page-title-box">
                <div class="page-title-right">
                    <ol class="breadcrumb m-0">
                        <li class="breadcrumb-item"><a href="{{ route('admin.dashboard') }}">Trang chủ</a></li>
                        <li class="breadcrumb-item"><a href="{{ route('admin.comments.index') }}">Quản lý bình luận</a></li>
                        <li class="breadcrumb-item active">Chi tiết</li>
                    </ol>
                </div>
                <h4 class="page-title">Chi tiết bình luận</h4>
            </div>
        </div>
    </div>

    @if(session('success'))
    <div class="alert alert-success alert-dismissible fade show" role="alert">
        {{ session('success') }}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
    @endif

    @if(session('error'))
    <div class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ session('error') }}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
    @endif

    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h4 class="header-title">Thông tin bình luận</h4>
                        <div>
                            <a href="{{ route('admin.comments.index') }}" class="btn btn-sm btn-secondary me-1"><i class="mdi mdi-arrow-left"></i> Quay lại</a>
                            <form action="{{ route('admin.comments.destroy', $comment->id) }}" method="POST" class="d-inline" onsubmit="return confirm('Bạn có chắc chắn muốn xóa bình luận này?')">
                                @csrf
                                @method('DELETE')
                                <button type="submit" class="btn btn-sm btn-danger"><i class="mdi mdi-delete"></i> Xóa</button>
                            </form>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-8">
                            <div class="mb-4">
                                <h5 class="text-uppercase"><i class="mdi mdi-message-text me-1"></i> Nội dung</h5>
                                <p class="text-muted border p-3 rounded">{{ $comment->content }}</p>
                            </div>

                            @if($comment->processed_content)
                            <div class="mb-4">
                                <h5 class="text-uppercase"><i class="mdi mdi-message-processing me-1"></i> Nội dung xử lý</h5>
                                <p class="text-muted border p-3 rounded">{{ $comment->processed_content }}</p>
                            </div>
                            @endif

                            @if($comment->keywords && count(json_decode($comment->keywords, true)) > 0)
                            <div class="mb-4">
                                <h5 class="text-uppercase"><i class="mdi mdi-key me-1"></i> Từ khóa phát hiện</h5>
                                <div class="border p-3 rounded">
                                    @foreach(json_decode($comment->keywords, true) as $keyword)
                                    <span class="badge bg-danger me-1">{{ $keyword }}</span>
                                    @endforeach
                                </div>
                            </div>
                            @endif

                            @if($comment->probabilities)
                            <div class="mb-4">
                                <h5 class="text-uppercase"><i class="mdi mdi-chart-bar me-1"></i> Phân tích xác suất</h5>
                                <div class="border p-3 rounded">
                                    @php
                                        $probabilities = json_decode($comment->probabilities, true);
                                    @endphp
                                    @if(is_array($probabilities))
                                        @foreach($probabilities as $category => $probability)
                                        <div class="mb-2">
                                            <div class="d-flex justify-content-between mb-1">
                                                <span>{{ ucfirst($category) }}</span>
                                                <span>{{ number_format($probability * 100, 2) }}%</span>
                                            </div>
                                            <div class="progress" style="height: 6px;">
                                                <div class="progress-bar 
                                                    @if($category == 'clean') bg-success 
                                                    @elseif($category == 'offensive') bg-warning 
                                                    @elseif($category == 'hate') bg-danger 
                                                    @elseif($category == 'spam') bg-info 
                                                    @else bg-secondary @endif" 
                                                    role="progressbar" 
                                                    style="width: {{ $probability * 100 }}%" 
                                                    aria-valuenow="{{ $probability * 100 }}" 
                                                    aria-valuemin="0" 
                                                    aria-valuemax="100">
                                                </div>
                                            </div>
                                        </div>
                                        @endforeach
                                    @endif
                                </div>
                            </div>
                            @endif
                        </div>

                        <div class="col-md-4">
                            <div class="card border">
                                <div class="card-header bg-light">
                                    <h5 class="card-title mb-0">Thông tin chung</h5>
                                </div>
                                <div class="card-body">
                                    <div class="mb-3">
                                        <h5 class="text-uppercase"><i class="mdi mdi-tag me-1"></i> Phân loại</h5>
                                        <div>
                                            @if($comment->category == 'clean')
                                                <span class="badge bg-success">Bình thường</span>
                                            @elseif($comment->category == 'offensive')
                                                <span class="badge bg-warning">Xúc phạm</span>
                                            @elseif($comment->category == 'hate')
                                                <span class="badge bg-danger">Phân biệt</span>
                                            @elseif($comment->category == 'spam')
                                                <span class="badge bg-info">Spam</span>
                                            @else
                                                <span class="badge bg-secondary">{{ $comment->category }}</span>
                                            @endif
                                        </div>
                                    </div>

                                    <div class="mb-3">
                                        <h5 class="text-uppercase"><i class="mdi mdi-percent me-1"></i> Điểm tin cậy</h5>
                                        <div class="progress" style="height: 10px;">
                                            <div class="progress-bar 
                                                @if($comment->category == 'clean') bg-success 
                                                @elseif($comment->category == 'offensive') bg-warning 
                                                @elseif($comment->category == 'hate') bg-danger 
                                                @elseif($comment->category == 'spam') bg-info 
                                                @else bg-secondary @endif" 
                                                role="progressbar" 
                                                style="width: {{ $comment->confidence * 100 }}%" 
                                                aria-valuenow="{{ $comment->confidence * 100 }}" 
                                                aria-valuemin="0" 
                                                aria-valuemax="100">
                                            </div>
                                        </div>
                                        <small class="text-muted">{{ number_format($comment->confidence * 100, 2) }}%</small>
                                    </div>

                                    <div class="mb-3">
                                        <h5 class="text-uppercase"><i class="mdi mdi-account me-1"></i> Người dùng</h5>
                                        <p class="text-muted">
                                            @if($comment->user)
                                                <a href="{{ route('admin.users.show', $comment->user_id) }}">{{ $comment->user->name }}</a>
                                            @else
                                                <span class="text-muted">Không có</span>
                                            @endif
                                        </p>
                                    </div>

                                    <div class="mb-3">
                                        <h5 class="text-uppercase"><i class="mdi mdi-share me-1"></i> Nền tảng</h5>
                                        <p class="text-muted">{{ ucfirst($comment->platform) }}</p>
                                    </div>

                                    <div class="mb-3">
                                        <h5 class="text-uppercase"><i class="mdi mdi-calendar me-1"></i> Thời gian</h5>
                                        <p class="text-muted">{{ $comment->created_at->format('d/m/Y H:i:s') }}</p>
                                    </div>

                                    @if($comment->source_url)
                                    <div class="mb-3">
                                        <h5 class="text-uppercase"><i class="mdi mdi-link me-1"></i> Link gốc</h5>
                                        <a href="{{ $comment->source_url }}" target="_blank" class="text-muted">{{ \Illuminate\Support\Str::limit($comment->source_url, 30) }}</a>
                                    </div>
                                    @endif

                                    @if($comment->source_user_name)
                                    <div class="mb-3">
                                        <h5 class="text-uppercase"><i class="mdi mdi-account me-1"></i> Tài khoản</h5>
                                        <p class="text-muted">{{ $comment->source_user_name }}</p>
                                    </div>
                                    @endif
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-md-6">
            <div class="card">
                <div class="card-body">
                    <h4 class="header-title mb-3">Chỉnh sửa phân loại</h4>
                    
                    <form action="{{ route('admin.comments.update', $comment->id) }}" method="POST">
                        @csrf
                        @method('PUT')
                        <div class="mb-3">
                            <label for="category" class="form-label">Phân loại</label>
                            <select class="form-select @error('category') is-invalid @enderror" id="category" name="category">
                                <option value="clean" {{ $comment->category == 'clean' ? 'selected' : '' }}>Bình thường</option>
                                <option value="offensive" {{ $comment->category == 'offensive' ? 'selected' : '' }}>Xúc phạm</option>
                                <option value="hate" {{ $comment->category == 'hate' ? 'selected' : '' }}>Phân biệt</option>
                                <option value="spam" {{ $comment->category == 'spam' ? 'selected' : '' }}>Spam</option>
                            </select>
                            @error('category')
                                <div class="invalid-feedback">{{ $message }}</div>
                            @enderror
                        </div>

                        <div class="mb-3">
                            <label for="confidence" class="form-label">Điểm tin cậy (0.0 - 1.0)</label>
                            <input type="number" step="0.01" min="0" max="1" class="form-control @error('confidence') is-invalid @enderror" id="confidence" name="confidence" value="{{ $comment->confidence }}">
                            @error('confidence')
                                <div class="invalid-feedback">{{ $message }}</div>
                            @enderror
                        </div>

                        <div class="mb-3">
                            <label for="admin_note" class="form-label">Ghi chú</label>
                            <textarea class="form-control @error('admin_note') is-invalid @enderror" id="admin_note" name="admin_note" rows="3">{{ $comment->admin_note }}</textarea>
                            @error('admin_note')
                                <div class="invalid-feedback">{{ $message }}</div>
                            @enderror
                        </div>

                        <button type="submit" class="btn btn-primary">Cập nhật</button>
                    </form>
                </div>
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="card">
                <div class="card-body">
                    <h4 class="header-title mb-3">Phản hồi của người dùng</h4>
                    
                    @if($comment->feedback_category)
                    <div class="border p-3 rounded mb-3">
                        <div class="d-flex align-items-center mb-2">
                            <div class="me-2">
                                <span class="badge 
                                    @if($comment->feedback_category == 'clean') bg-success 
                                    @elseif($comment->feedback_category == 'offensive') bg-warning 
                                    @elseif($comment->feedback_category == 'hate') bg-danger 
                                    @elseif($comment->feedback_category == 'spam') bg-info 
                                    @else bg-secondary @endif">
                                    {{ ucfirst($comment->feedback_category) }}
                                </span>
                            </div>
                            <div class="text-muted small">{{ $comment->feedback_at ? $comment->feedback_at->format('d/m/Y H:i:s') : 'N/A' }}</div>
                        </div>
                        
                        @if($comment->feedback_note)
                        <div class="p-2 bg-light rounded">
                            <p class="mb-0">{{ $comment->feedback_note }}</p>
                        </div>
                        @else
                        <p class="text-muted mb-0">Không có ghi chú</p>
                        @endif
                    </div>
                    @else
                    <div class="alert alert-info mb-0">
                        <p class="mb-0">Chưa có phản hồi từ người dùng</p>
                    </div>
                    @endif
                    
                    <hr>
                    
                    <h5 class="text-uppercase"><i class="mdi mdi-flag me-1"></i> Hành động</h5>
                    <div class="mt-3">
                        <form action="{{ route('admin.comments.toggle-ban', $comment->id) }}" method="POST" class="d-inline">
                            @csrf
                            <button type="submit" class="btn {{ $comment->is_banned ? 'btn-success' : 'btn-danger' }} mb-2">
                                <i class="mdi {{ $comment->is_banned ? 'mdi-check-circle' : 'mdi-block-helper' }} me-1"></i>
                                {{ $comment->is_banned ? 'Bỏ chặn bình luận' : 'Chặn bình luận' }}
                            </button>
                        </form>
                        
                        @if($comment->user_id)
                        <form action="{{ route('admin.users.toggle-ban', $comment->user_id) }}" method="POST" class="d-inline">
                            @csrf
                            <button type="submit" class="btn {{ $comment->user && $comment->user->is_banned ? 'btn-success' : 'btn-danger' }} mb-2">
                                <i class="mdi {{ $comment->user && $comment->user->is_banned ? 'mdi-account-check' : 'mdi-account-remove' }} me-1"></i>
                                {{ $comment->user && $comment->user->is_banned ? 'Bỏ chặn người dùng' : 'Chặn người dùng' }}
                            </button>
                        </form>
                        @endif
                        
                        <form action="{{ route('admin.comments.add-blacklist', $comment->id) }}" method="POST" class="mt-2">
                            @csrf
                            <button type="submit" class="btn btn-dark">
                                <i class="mdi mdi-playlist-plus me-1"></i> Thêm vào danh sách đen
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
@endsection 