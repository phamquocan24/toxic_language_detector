@extends('layouts.user')

@section('title', 'Bình luận của tôi')
@section('page-title', 'Bình luận của tôi')

@section('breadcrumb')
<li class="breadcrumb-item active">Bình luận</li>
@endsection

@section('content')
<div class="card">
    <div class="card-header">
        <h3 class="card-title">Danh sách bình luận của tôi</h3>
        <div class="card-tools">
            <div class="btn-group">
                <a href="{{ route('user.comments.export') }}?format=pdf" class="btn btn-sm btn-primary">
                    <i class="fas fa-file-pdf"></i> Xuất PDF
                </a>
                <a href="{{ route('user.comments.print') }}" class="btn btn-sm btn-info" target="_blank">
                    <i class="fas fa-print"></i> In
                </a>
            </div>
        </div>
    </div>
    
    <div class="card-body">
        <form action="{{ route('user.comments.index') }}" method="GET" class="mb-4 row">
            <div class="col-md-3">
                <div class="form-group">
                    <label>Tìm kiếm</label>
                    <input type="text" name="search" class="form-control" placeholder="Nhập từ khóa..." value="{{ request('search') }}">
                </div>
            </div>
            <div class="col-md-3">
                <div class="form-group">
                    <label>Phân loại</label>
                    <select name="category" class="form-control">
                        <option value="">Tất cả</option>
                        <option value="clean" {{ request('category') == 'clean' ? 'selected' : '' }}>Bình thường</option>
                        <option value="offensive" {{ request('category') == 'offensive' ? 'selected' : '' }}>Xúc phạm</option>
                        <option value="hate" {{ request('category') == 'hate' ? 'selected' : '' }}>Thù ghét</option>
                        <option value="spam" {{ request('category') == 'spam' ? 'selected' : '' }}>Spam</option>
                    </select>
                </div>
            </div>
            <div class="col-md-3">
                <div class="form-group">
                    <label>Nền tảng</label>
                    <select name="platform" class="form-control">
                        <option value="">Tất cả</option>
                        <option value="facebook" {{ request('platform') == 'facebook' ? 'selected' : '' }}>Facebook</option>
                        <option value="youtube" {{ request('platform') == 'youtube' ? 'selected' : '' }}>YouTube</option>
                        <option value="twitter" {{ request('platform') == 'twitter' ? 'selected' : '' }}>Twitter</option>
                        <option value="web" {{ request('platform') == 'web' ? 'selected' : '' }}>Web</option>
                    </select>
                </div>
            </div>
            <div class="col-md-3">
                <div class="form-group">
                    <label>&nbsp;</label>
                    <div>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-search"></i> Lọc
                        </button>
                        <a href="{{ route('user.comments.index') }}" class="btn btn-default">
                            <i class="fas fa-redo"></i> Đặt lại
                        </a>
                    </div>
                </div>
            </div>
        </form>
        
        <div class="table-responsive">
            <table class="table table-bordered table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nội dung</th>
                        <th>Phân loại</th>
                        <th>Độ tin cậy</th>
                        <th>Nền tảng</th>
                        <th>Thời gian</th>
                        <th>Hành động</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($comments as $comment)
                    <tr>
                        <td>{{ $comment->id }}</td>
                        <td>{{ \Illuminate\Support\Str::limit($comment->content, 50) }}</td>
                        <td>
                            @php
                                $badgeClass = 'success';
                                if($comment->category == 'offensive') $badgeClass = 'warning';
                                elseif($comment->category == 'hate') $badgeClass = 'danger';
                                elseif($comment->category == 'spam') $badgeClass = 'primary';
                            @endphp
                            <span class="badge badge-{{ $badgeClass }}">
                                {{ ucfirst($comment->category) }}
                            </span>
                        </td>
                        <td>{{ number_format($comment->confidence_score * 100, 1) }}%</td>
                        <td>{{ ucfirst($comment->platform) }}</td>
                        <td>{{ $comment->created_at->format('d/m/Y H:i') }}</td>
                        <td>
                            <a href="{{ route('user.comments.show', $comment) }}" class="btn btn-sm btn-info">
                                <i class="fas fa-eye"></i>
                            </a>
                        </td>
                    </tr>
                    @empty
                    <tr>
                        <td colspan="7" class="text-center">Không có dữ liệu</td>
                    </tr>
                    @endforelse
                </tbody>
            </table>
        </div>
        
        <div class="mt-3">
            {{ $comments->withQueryString()->links() }}
        </div>
    </div>
</div>
@endsection 