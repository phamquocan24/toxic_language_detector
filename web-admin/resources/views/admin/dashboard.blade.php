@extends('layouts.admin')

@section('title', 'Dashboard')

@section('content')
<div class="container-fluid">
    <!-- Statistics Cards -->
    <div class="row mb-4">
        <!-- Total Analysis Card -->
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="stats-card primary">
                <div class="stats-content">
                    <div class="stats-title">TỔNG PHÂN TÍCH</div>
                    <div class="stats-number">{{ number_format($totalComments) }}</div>
                </div>
                <div class="icon">
                    <i class="fas fa-chart-line"></i>
                </div>
            </div>
        </div>

        <!-- Inappropriate Card -->
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="stats-card warning">
                <div class="stats-content">
                    <div class="stats-title">KHÔNG PHÙ HỢP</div>
                    <div class="stats-number">{{ number_format($commentStats['offensive'] + $commentStats['hate'] + $commentStats['spam']) }}</div>
                </div>
                <div class="icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
            </div>
        </div>

        <!-- Total Users Card -->
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="stats-card info">
                <div class="stats-content">
                    <div class="stats-title">TỔNG NGƯỜI DÙNG</div>
                    <div class="stats-number">{{ number_format($totalUsers) }}</div>
                </div>
                <div class="icon">
                    <i class="fas fa-users"></i>
                </div>
            </div>
        </div>

        <!-- Appropriate Card -->
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="stats-card success">
                <div class="stats-content">
                    <div class="stats-title">PHÙ HỢP</div>
                    <div class="stats-number">{{ number_format($commentStats['clean']) }}</div>
                </div>
                <div class="icon">
                    <i class="fas fa-check-circle"></i>
                </div>
            </div>
        </div>
    </div>

    <!-- Charts and Tables Row -->
    <div class="row">
        <!-- Chart Column -->
        <div class="col-xl-8 col-lg-7">
            <div class="dashboard-card mb-4">
                <div class="card-header">
                    <h5>Thống kê phân tích</h5>
                </div>
                <div class="card-body">
                    <div class="chart-container">
                        <canvas id="analyticChart"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- Latest Comments -->
            <div class="dashboard-card mb-4">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5>Bình luận gần đây</h5>
                    <a href="{{ route('admin.comments.index') }}" class="btn btn-sm btn-primary">Xem tất cả</a>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Người dùng</th>
                                    <th>Nội dung</th>
                                    <th>Phân loại</th>
                                    <th>Độ tin cậy</th>
                                    <th>Thao tác</th>
                                </tr>
                            </thead>
                            <tbody>
                                @forelse($recentComments as $comment)
                                <tr>
                                    <td>#{{ $comment->id }}</td>
                                    <td>{{ $comment->user->name ?? 'N/A' }}</td>
                                    <td>{{ \Illuminate\Support\Str::limit($comment->content, 40) }}</td>
                                    <td>
                                        <span class="status-badge {{ strtolower($comment->classification) }}">
                                            {{ $comment->getLocalizedClassificationAttribute() }}
                                        </span>
                                    </td>
                                    <td>{{ number_format($comment->confidence * 100, 1) }}%</td>
                                    <td>
                                        <a href="{{ route('admin.comments.show', $comment) }}" class="btn btn-sm btn-info">
                                            <i class="fas fa-eye"></i>
                                        </a>
                                    </td>
                                </tr>
                                @empty
                                <tr>
                                    <td colspan="6" class="text-center">Không có bình luận nào gần đây</td>
                                </tr>
                                @endforelse
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Sidebar Column -->
        <div class="col-xl-4 col-lg-5">
            <!-- Latest Searches -->
            <div class="dashboard-card mb-4">
                <div class="card-header">
                    <h5>Tìm kiếm gần đây</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Từ khóa</th>
                                    <th class="text-end">Kết quả</th>
                                    <th class="text-end">Lượt xem</th>
                                </tr>
                            </thead>
                            <tbody>
                                @if(isset($recentSearches) && count($recentSearches) > 0)
                                    @foreach($recentSearches as $search)
                                    <tr>
                                        <td>{{ $search->keyword }}</td>
                                        <td class="text-end">{{ $search->results }}</td>
                                        <td class="text-end">{{ $search->hits }}</td>
                                    </tr>
                                    @endforeach
                                @else
                                    <tr>
                                        <td colspan="3" class="text-center">Không có dữ liệu tìm kiếm</td>
                                    </tr>
                                @endif
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Latest Reviews -->
            <div class="dashboard-card mb-4">
                <div class="card-header">
                    <h5>Đánh giá gần đây</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Người dùng</th>
                                    <th>Đánh giá</th>
                                    <th class="text-end">Sao</th>
                                </tr>
                            </thead>
                            <tbody>
                                @if(isset($recentReviews) && count($recentReviews) > 0)
                                    @foreach($recentReviews as $review)
                                    <tr>
                                        <td>{{ $review->user->name }}</td>
                                        <td>{{ \Illuminate\Support\Str::limit($review->content, 30) }}</td>
                                        <td class="text-end">
                                            <span class="text-warning">
                                                @for($i = 1; $i <= 5; $i++)
                                                    @if($i <= $review->rating)
                                                        <i class="fas fa-star"></i>
                                                    @else
                                                        <i class="far fa-star"></i>
                                                    @endif
                                                @endfor
                                            </span>
                                        </td>
                                    </tr>
                                    @endforeach
                                @else
                                    <tr>
                                        <td colspan="3" class="text-center">Không có dữ liệu đánh giá</td>
                                    </tr>
                                @endif
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- API Status -->
            @if(isset($apiStats) && !empty($apiStats))
            <div class="dashboard-card mb-4">
                <div class="card-header">
                    <h5>Trạng thái API</h5>
                </div>
                <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                        <div class="flex-shrink-0 me-3">
                            @if(isset($apiStats['api_status']) && $apiStats['api_status'] == 'online')
                                <span class="badge rounded-pill bg-success p-2"><i class="fas fa-server"></i></span>
                            @else
                                <span class="badge rounded-pill bg-danger p-2"><i class="fas fa-server"></i></span>
                            @endif
                        </div>
                        <div class="flex-grow-1">
                            <h6 class="mb-0">API Status</h6>
                            <p class="text-muted mb-0">
                                @if(isset($apiStats['api_status']) && $apiStats['api_status'] == 'online')
                                    <span class="text-success">Online</span>
                                @else
                                    <span class="text-danger">Offline</span>
                                @endif
                            </p>
                        </div>
                    </div>
                    
                    <div class="row g-3 mt-2">
                        <div class="col-6">
                            <div class="p-3 bg-light rounded">
                                <h6 class="mb-0">Hôm nay</h6>
                                <p class="display-6 mb-0">{{ number_format($apiStats['requests_today'] ?? 0) }}</p>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="p-3 bg-light rounded">
                                <h6 class="mb-0">Tuần này</h6>
                                <p class="display-6 mb-0">{{ number_format($apiStats['requests_this_week'] ?? 0) }}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            @endif
        </div>
    </div>
</div>
@endsection

@push('scripts')
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Chart for daily analytics
        var ctx = document.getElementById('analyticChart').getContext('2d');
        
        // Generate dates for the last 7 days
        var dates = [];
        var today = new Date();
        for (var i = 6; i >= 0; i--) {
            var day = new Date(today);
            day.setDate(today.getDate() - i);
            dates.push(day.toLocaleDateString('vi-VN', { weekday: 'long' }));
        }
        
        // Sample data
        var analyticChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: 'Phân tích',
                        data: [1200, 1900, 800, 1700, 1600, 1800, 7000],
                        backgroundColor: '#6366f1',
                        borderColor: '#6366f1',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value;
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return '$' + context.parsed.y;
                            }
                        }
                    }
                }
            }
        });
        
        // Format tables with DataTables
        $('table').DataTable({
            paging: false,
            searching: false,
            info: false
        });
    });
</script>
@endpush

@push('styles')
<style>
    /* Status badge colors */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .status-badge.clean {
        background-color: rgba(34, 197, 94, 0.1);
        color: #22c55e;
    }
    
    .status-badge.offensive {
        background-color: rgba(245, 158, 11, 0.1);
        color: #f59e0b;
    }
    
    .status-badge.hate {
        background-color: rgba(239, 68, 68, 0.1);
        color: #ef4444;
    }
    
    .status-badge.spam {
        background-color: rgba(99, 102, 241, 0.1);
        color: #6366f1;
    }
    
    /* Table hovering */
    .table-hover tbody tr:hover {
        background-color: rgba(0, 0, 0, 0.02);
    }
</style>
@endpush 