@extends('admin::layout')

@component('admin::components.page.header')
    @slot('title', trans('Feedbacks'))

    <li class="active">Feedbacks</li>
@endcomponent

@section('content')
    <div id="flash-container"></div>

    <!-- Filters -->
    <div class="box box-primary">
        <div class="box-header with-border">
            <h3 class="box-title">
                <i class="fa fa-filter"></i> Bộ Lọc
            </h3>
        </div>
        <div class="box-body">
            <form action="{{ route('admin.feedbacks.index') }}" method="GET" class="form-inline">
                <div class="form-group">
                    <label>Loại Feedback:</label>
                    <select name="feedback_type" class="form-control">
                        <option value="">Tất Cả</option>
                        <option value="general" {{ request('feedback_type') == 'general' ? 'selected' : '' }}>General</option>
                        <option value="bug" {{ request('feedback_type') == 'bug' ? 'selected' : '' }}>Bug Report</option>
                        <option value="feature" {{ request('feedback_type') == 'feature' ? 'selected' : '' }}>Feature Request</option>
                        <option value="improvement" {{ request('feedback_type') == 'improvement' ? 'selected' : '' }}>Improvement</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Số Lượng:</label>
                    <select name="limit" class="form-control">
                        <option value="25" {{ request('limit', 50) == 25 ? 'selected' : '' }}>25</option>
                        <option value="50" {{ request('limit', 50) == 50 ? 'selected' : '' }}>50</option>
                        <option value="100" {{ request('limit', 50) == 100 ? 'selected' : '' }}>100</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">
                    <i class="fa fa-search"></i> Lọc
                </button>
                <a href="{{ route('admin.feedbacks.index') }}" class="btn btn-default">
                    <i class="fa fa-refresh"></i> Đặt Lại
                </a>
            </form>
        </div>
    </div>

    <!-- Feedbacks Table -->
    <div class="box box-primary">
        <div class="box-header with-border">
            <h3 class="box-title">
                <i class="fa fa-comments"></i> Danh Sách Feedback (Tổng: {{ number_format($total) }})
            </h3>
        </div>
        <div class="box-body">
            @if(count($feedbacks) > 0)
                <div class="table-responsive">
                    <table class="table table-bordered table-striped">
                        <thead>
                            <tr>
                                <th width="80">ID</th>
                                <th width="100">User ID</th>
                                <th width="150">Loại</th>
                                <th width="150">Nguồn</th>
                                <th>Nội Dung</th>
                                <th width="180">Thời Gian</th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach($feedbacks as $feedback)
                                <tr>
                                    <td>{{ $feedback['id'] }}</td>
                                    <td>
                                        @if($feedback['user_id'])
                                            <a href="{{ route('admin.users.edit', $feedback['user_id']) }}" class="btn btn-xs btn-primary">
                                                <i class="fa fa-user"></i> {{ $feedback['user_id'] }}
                                            </a>
                                        @else
                                            <span class="text-muted">Anonymous</span>
                                        @endif
                                    </td>
                                    <td>
                                        @php
                                            $typeClass = 'label-default';
                                            switch($feedback['feedback_type']) {
                                                case 'bug':
                                                    $typeClass = 'label-danger';
                                                    break;
                                                case 'feature':
                                                    $typeClass = 'label-success';
                                                    break;
                                                case 'improvement':
                                                    $typeClass = 'label-info';
                                                    break;
                                            }
                                        @endphp
                                        <span class="label {{ $typeClass }}">{{ ucfirst($feedback['feedback_type']) }}</span>
                                    </td>
                                    <td>
                                        <span class="label label-primary">{{ ucfirst($feedback['source']) }}</span>
                                    </td>
                                    <td>{{ $feedback['action'] }}</td>
                                    <td>
                                        @if($feedback['timestamp'])
                                            <i class="fa fa-clock-o"></i>
                                            {{ \Carbon\Carbon::parse($feedback['timestamp'])->format('d/m/Y H:i:s') }}
                                            <br>
                                            <small class="text-muted">{{ \Carbon\Carbon::parse($feedback['timestamp'])->diffForHumans() }}</small>
                                        @else
                                            <span class="text-muted">N/A</span>
                                        @endif
                                    </td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>

                <!-- Pagination -->
                @if($total > $limit)
                    <div class="text-center">
                        <nav>
                            <ul class="pagination">
                                @php
                                    $totalPages = ceil($total / $limit);
                                    $currentPage = $page;
                                @endphp

                                <!-- Previous Button -->
                                @if($currentPage > 1)
                                    <li>
                                        <a href="{{ route('admin.feedbacks.index', array_merge(request()->all(), ['page' => $currentPage - 1])) }}" aria-label="Previous">
                                            <span aria-hidden="true">&laquo;</span>
                                        </a>
                                    </li>
                                @endif

                                <!-- Page Numbers -->
                                @for($i = 1; $i <= $totalPages; $i++)
                                    @if($i == $currentPage)
                                        <li class="active"><span>{{ $i }}</span></li>
                                    @elseif($i <= 3 || $i > $totalPages - 3 || abs($i - $currentPage) <= 2)
                                        <li>
                                            <a href="{{ route('admin.feedbacks.index', array_merge(request()->all(), ['page' => $i])) }}">{{ $i }}</a>
                                        </li>
                                    @elseif($i == 4 || $i == $totalPages - 3)
                                        <li class="disabled"><span>...</span></li>
                                    @endif
                                @endfor

                                <!-- Next Button -->
                                @if($currentPage < $totalPages)
                                    <li>
                                        <a href="{{ route('admin.feedbacks.index', array_merge(request()->all(), ['page' => $currentPage + 1])) }}" aria-label="Next">
                                            <span aria-hidden="true">&raquo;</span>
                                        </a>
                                    </li>
                                @endif
                            </ul>
                        </nav>
                    </div>
                @endif
            @else
                <div class="alert alert-info text-center">
                    <i class="fa fa-info-circle"></i> Không có feedback nào.
                </div>
            @endif
        </div>
    </div>
@endsection

@push('styles')
<style>
    .table > tbody > tr > td {
        vertical-align: middle;
    }
</style>
@endpush

