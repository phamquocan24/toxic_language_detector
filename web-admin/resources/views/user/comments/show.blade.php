@extends('layouts.user')

@section('title', 'Chi tiết bình luận')

@section('content')
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="page-title-box">
                <div class="page-title-right">
                    <ol class="breadcrumb m-0">
                        <li class="breadcrumb-item"><a href="{{ route('user.dashboard') }}">Trang chủ</a></li>
                        <li class="breadcrumb-item"><a href="{{ route('user.comments.index') }}">Bình luận</a></li>
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
                            <a href="{{ route('user.comments.index') }}" class="btn btn-sm btn-secondary me-1"><i class="mdi mdi-arrow-left"></i> Quay lại</a>
                            <form action="{{ route('user.comments.destroy', $comment->id) }}" method="POST" class="d-inline" onsubmit="return confirm('Bạn có chắc chắn muốn xóa bình luận này?')">
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
        <div class="col-12">
            <div class="card">
                <div class="card-body">
                    <h4 class="header-title mb-3">Phản hồi về kết quả phân tích</h4>
                    
                    <form action="{{ route('user.comments.feedback', $comment->id) }}" method="POST">
                        @csrf
                        <div class="mb-3">
                            <label for="feedback_category" class="form-label">Phân loại đúng</label>
                            <select class="form-select @error('feedback_category') is-invalid @enderror" id="feedback_category" name="feedback_category">
                                <option value="">-- Chọn phân loại --</option>
                                <option value="clean" {{ old('feedback_category') == 'clean' ? 'selected' : '' }}>Bình thường</option>
                                <option value="offensive" {{ old('feedback_category') == 'offensive' ? 'selected' : '' }}>Xúc phạm</option>
                                <option value="hate" {{ old('feedback_category') == 'hate' ? 'selected' : '' }}>Phân biệt</option>
                                <option value="spam" {{ old('feedback_category') == 'spam' ? 'selected' : '' }}>Spam</option>
                            </select>
                            @error('feedback_category')
                                <div class="invalid-feedback">{{ $message }}</div>
                            @enderror
                        </div>

                        <div class="mb-3">
                            <label for="feedback_note" class="form-label">Ghi chú</label>
                            <textarea class="form-control @error('feedback_note') is-invalid @enderror" id="feedback_note" name="feedback_note" rows="3">{{ old('feedback_note') }}</textarea>
                            @error('feedback_note')
                                <div class="invalid-feedback">{{ $message }}</div>
                            @enderror
                        </div>

                        <button type="submit" class="btn btn-primary">Gửi phản hồi</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
@endsection 