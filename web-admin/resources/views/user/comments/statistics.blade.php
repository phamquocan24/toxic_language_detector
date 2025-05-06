@extends('layouts.user')

@section('title', 'Thống kê bình luận')

@section('content')
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="page-title-box">
                <div class="page-title-right">
                    <ol class="breadcrumb m-0">
                        <li class="breadcrumb-item"><a href="{{ route('user.dashboard') }}">Trang chủ</a></li>
                        <li class="breadcrumb-item"><a href="{{ route('user.comments.index') }}">Bình luận</a></li>
                        <li class="breadcrumb-item active">Thống kê</li>
                    </ol>
                </div>
                <h4 class="page-title">Thống kê bình luận</h4>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-md-6 col-xl-3">
            <div class="card">
                <div class="card-body">
                    <div class="row">
                        <div class="col-6">
                            <div class="avatar-sm bg-primary rounded">
                                <i class="fe-message-square avatar-title font-22 text-white"></i>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="text-end">
                                <h3 class="text-dark my-1">{{ $total }}</h3>
                                <p class="text-muted mb-0">Tổng bình luận</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-md-6 col-xl-3">
            <div class="card">
                <div class="card-body">
                    <div class="row">
                        <div class="col-6">
                            <div class="avatar-sm bg-success rounded">
                                <i class="fe-check-circle avatar-title font-22 text-white"></i>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="text-end">
                                <h3 class="text-dark my-1">{{ $byCategory['clean'] }}</h3>
                                <p class="text-muted mb-0">Bình thường</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-md-6 col-xl-3">
            <div class="card">
                <div class="card-body">
                    <div class="row">
                        <div class="col-6">
                            <div class="avatar-sm bg-warning rounded">
                                <i class="fe-alert-triangle avatar-title font-22 text-white"></i>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="text-end">
                                <h3 class="text-dark my-1">{{ $byCategory['offensive'] }}</h3>
                                <p class="text-muted mb-0">Xúc phạm</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-md-6 col-xl-3">
            <div class="card">
                <div class="card-body">
                    <div class="row">
                        <div class="col-6">
                            <div class="avatar-sm bg-danger rounded">
                                <i class="fe-alert-octagon avatar-title font-22 text-white"></i>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="text-end">
                                <h3 class="text-dark my-1">{{ $byCategory['hate'] }}</h3>
                                <p class="text-muted mb-0">Phân biệt</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-lg-6">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h4 class="header-title">Phân loại bình luận</h4>
                </div>
                <div class="card-body">
                    <div class="chart-container" style="position: relative; height:350px;">
                        <canvas id="categoryChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-lg-6">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h4 class="header-title">Nền tảng</h4>
                </div>
                <div class="card-body">
                    <div class="chart-container" style="position: relative; height:350px;">
                        <canvas id="platformChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h4 class="header-title">Bình luận gần đây</h4>
                    <a href="{{ route('user.comments.index') }}" class="btn btn-sm btn-primary">Xem tất cả</a>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-centered table-nowrap table-hover mb-0">
                            <thead>
                                <tr>
                                    <th>Nội dung</th>
                                    <th>Phân loại</th>
                                    <th>Nền tảng</th>
                                    <th>Thời gian</th>
                                    <th>Hành động</th>
                                </tr>
                            </thead>
                            <tbody>
                                @forelse($recentComments as $comment)
                                <tr>
                                    <td>{{ \Illuminate\Support\Str::limit($comment->content, 100) }}</td>
                                    <td>
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
                                    </td>
                                    <td>{{ ucfirst($comment->platform) }}</td>
                                    <td>{{ $comment->created_at->format('d/m/Y H:i') }}</td>
                                    <td>
                                        <a href="{{ route('user.comments.show', $comment->id) }}" class="action-icon"> <i class="mdi mdi-eye"></i></a>
                                    </td>
                                </tr>
                                @empty
                                <tr>
                                    <td colspan="5" class="text-center">Không có bình luận nào</td>
                                </tr>
                                @endforelse
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
@endsection

@section('scripts')
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Categories chart
        var categoryCtx = document.getElementById('categoryChart').getContext('2d');
        var categoryChart = new Chart(categoryCtx, {
            type: 'pie',
            data: {
                labels: ['Bình thường', 'Xúc phạm', 'Phân biệt', 'Spam'],
                datasets: [{
                    data: [
                        {{ $byCategory['clean'] }}, 
                        {{ $byCategory['offensive'] }}, 
                        {{ $byCategory['hate'] }}, 
                        {{ $byCategory['spam'] }}
                    ],
                    backgroundColor: [
                        '#28a745',
                        '#ffc107',
                        '#dc3545',
                        '#17a2b8'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                    }
                }
            }
        });
        
        // Platform chart
        var platformCtx = document.getElementById('platformChart').getContext('2d');
        var platformChart = new Chart(platformCtx, {
            type: 'bar',
            data: {
                labels: ['Facebook', 'YouTube', 'Twitter', 'Web'],
                datasets: [{
                    label: 'Số bình luận',
                    data: [
                        {{ $byPlatform['facebook'] }}, 
                        {{ $byPlatform['youtube'] }}, 
                        {{ $byPlatform['twitter'] }}, 
                        {{ $byPlatform['web'] }}
                    ],
                    backgroundColor: [
                        '#4267B2',
                        '#FF0000',
                        '#1DA1F2',
                        '#6c757d'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    });
</script>
@endsection 