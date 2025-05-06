@extends('layouts.user')

@section('title', 'Dashboard')
@section('page-title', 'Dashboard')

@section('breadcrumb')
<li class="breadcrumb-item active">Dashboard</li>
@endsection

@section('content')
<div class="row">
    <div class="col-lg-3 col-6">
        <div class="small-box bg-info">
            <div class="inner">
                <h3>{{ $totalComments ?? 0 }}</h3>
                <p>Tổng số bình luận</p>
            </div>
            <div class="icon">
                <i class="fas fa-comment"></i>
            </div>
            <a href="{{ route('user.comments.index') }}" class="small-box-footer">
                Chi tiết <i class="fas fa-arrow-circle-right"></i>
            </a>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Thống kê phân loại</h3>
            </div>
            <div class="card-body">
                <canvas id="categoryChart" height="200"></canvas>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Thống kê theo nền tảng</h3>
            </div>
            <div class="card-body">
                <canvas id="platformChart" height="200"></canvas>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Bình luận gần đây</h3>
            </div>
            <div class="card-body table-responsive p-0">
                <table class="table table-hover text-nowrap">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nội dung</th>
                            <th>Phân loại</th>
                            <th>Nền tảng</th>
                            <th>Thời gian</th>
                            <th>Hành động</th>
                        </tr>
                    </thead>
                    <tbody>
                        @if(isset($recentComments) && count($recentComments) > 0)
                            @foreach($recentComments as $comment)
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
                                <td>{{ ucfirst($comment->platform) }}</td>
                                <td>{{ $comment->created_at->format('d/m/Y H:i') }}</td>
                                <td>
                                    <a href="{{ route('user.comments.show', $comment) }}" class="btn btn-sm btn-info">
                                        <i class="fas fa-eye"></i>
                                    </a>
                                </td>
                            </tr>
                            @endforeach
                        @else
                            <tr>
                                <td colspan="6" class="text-center">Không có dữ liệu</td>
                            </tr>
                        @endif
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
@endsection

@push('scripts')
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Chart dữ liệu theo loại
    const ctxCategory = document.getElementById('categoryChart').getContext('2d');
    const categoryLabels = @json(isset($categoryStats) ? $categoryStats->pluck('category') : []);
    const categoryData = @json(isset($categoryStats) ? $categoryStats->pluck('total') : []);
    const categoryColors = {
        'clean': '#4CAF50',
        'offensive': '#FF9800',
        'hate': '#F44336',
        'spam': '#9C27B0'
    };
    
    const colors = categoryLabels.map(label => categoryColors[label] || '#777');
    
    new Chart(ctxCategory, {
        type: 'pie',
        data: {
            labels: categoryLabels,
            datasets: [{
                data: categoryData,
                backgroundColor: colors
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
    
    // Chart dữ liệu theo nền tảng
    const ctxPlatform = document.getElementById('platformChart').getContext('2d');
    const platformLabels = @json(isset($platformStats) ? $platformStats->pluck('platform') : []);
    const platformData = @json(isset($platformStats) ? $platformStats->pluck('total') : []);
    
    new Chart(ctxPlatform, {
        type: 'bar',
        data: {
            labels: platformLabels,
            datasets: [{
                label: 'Số lượng bình luận',
                data: platformData,
                backgroundColor: '#3498db'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
</script>
@endpush 