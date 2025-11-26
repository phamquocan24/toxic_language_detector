@extends('admin::layout')

@component('admin::components.page.header')
    @slot('title', trans('comment::comment.comments'))

    <li class="active">{{ trans('comment::comment.comments') }}</li>
@endcomponent

@component('admin::components.page.index_table', ['showDelete' => $showDelete])
    @slot('buttons', ['create'])
    @slot('resource', 'comments')
    @slot('name', trans('comment::comment.comment'))

    @slot('thead')
        <tr>
            <th>
                <div class="checkbox">
                    <input type="checkbox" class="select-all" id="select-all">
                    <label for="select-all"></label>
                </div>
            </th>
            <th>{{ trans('admin::admin.table.id') }}</th>
            <th>{{ trans('comment::comment.content') }}</th>
            <th>{{ trans('comment::comment.platform') }}</th>
            <th>{{ trans('comment::comment.prediction') }}</th>
            <th>{{ trans('comment::comment.confidence') }}</th>
            <th>{{ trans('comment::comment.reviewed') }}</th>
            <th>{{ trans('admin::admin.table.updated_at') }}</th>
        </tr>
    @endslot

    @slot('tbody')
        @if (!empty($comments) && $comments->count() > 0)
            @foreach ($comments as $comment)
                <tr class="clickable-row">
                    <td>
                        <div class="checkbox">
                            <input type="checkbox" class="select-row" name="ids[]" id="comment-{{ $comment->id }}"
                                value="{{ $comment->id }}">
                            <label for="comment-{{ $comment->id }}"></label>
                        </div>
                    </td>
                    <td class="dt-type-numeric">{{ $comment->id }}</td>
                    <td>
                        {{ Str::limit($comment->content, 50) }}
                    </td>
                    <td>
                        <span class="badge badge-info">{{ $comment->platform }}</span>
                    </td>
                    <td>
                        @php
                            $predictionClass = 'badge-success';
                            if ($comment->prediction == 1) $predictionClass = 'badge-warning';
                            if ($comment->prediction == 2) $predictionClass = 'badge-danger';
                            if ($comment->prediction == 3) $predictionClass = 'badge-secondary';
                        @endphp
                        <span class="badge {{ $predictionClass }}">
                            @if(method_exists($comment, 'getPredictionText'))
                                {{ $comment->getPredictionText() }}
                            @elseif(isset($comment->prediction_text))
                                {{ $comment->prediction_text ?: 'unknown' }}
                            @else
                                @php
                                    $labels = ['clean', 'offensive', 'hate', 'spam'];
                                    $predText = isset($labels[$comment->prediction]) ? $labels[$comment->prediction] : 'unknown';
                                @endphp
                                {{ $predText }}
                            @endif
                        </span>
                    </td>
                    <td>
                        {{ number_format($comment->confidence * 100, 1) }}%
                    </td>
                    <td>
                        <span class="badge {{ isset($comment->is_reviewed) && $comment->is_reviewed ? 'badge-success' : 'badge-danger' }}">
                            {{ isset($comment->is_reviewed) && $comment->is_reviewed ? trans('comment::comment.review_status.reviewed') : trans('comment::comment.review_status.not_reviewed') }}
                        </span>
                    </td>
                    <td class="sorting_1">
                        @if(isset($comment->updated_at) && $comment->updated_at instanceof \Carbon\Carbon)
                            <span data-toggle="tooltip" title="{{ $comment->updated_at }}">
                                {{ $comment->updated_at->diffForHumans() }}
                            </span>
                        @elseif(isset($comment->created_at) && $comment->created_at instanceof \Carbon\Carbon)
                            <span data-toggle="tooltip" title="{{ $comment->created_at }}">
                                {{ $comment->created_at->diffForHumans() }}
                            </span>
                        @else
                            <span class="text-muted">N/A</span>
                        @endif
                    </td>
                </tr>
            @endforeach
        @else
            <tr class="no-data-row">
                <td colspan="8" class="text-center">
                    {{ trans('comment::comment.messages.search_no_results') }}
                </td>
            </tr>
        @endif
    @endslot

    @slot('tResult')
        @php
            // Tính toán chỉ số bản ghi
            $from = (request()->get('page', 1) - 1) * $perPage + 1;
            $to = (request()->get('page', 1) - 1) * $perPage + $comments->count();
            $total = $totalComments;
        @endphp
        {{ $from }} - {{ $to }} of {{ $total }} results entries
    @endslot

    @slot('tPagination')
        {!! $comments->appends(request()->input())->links('admin::pagination.simple') !!}
    @endslot

@endcomponent

@if (session()->has('exit_flash'))
    @push('notifications')
        <div class="alert alert-success fade in alert-dismissible clearfix">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 2C6.49 2 2 6.49 2 12C2 17.51 6.49 22 12 22C17.51 22 22 17.51 22 12C22 6.49 17.51 2 12 2ZM11.25 8C11.25 7.59 11.59 7.25 12 7.25C12.41 7.25 12.75 7.59 12.75 8V13C12.75 13.41 12.41 13.75 12 13.75C11.59 13.75 11.25 13.41 11.25 13V8ZM12.92 16.38C12.87 16.51 12.8 16.61 12.71 16.71C12.61 16.8 12.5 16.87 12.38 16.92C12.26 16.97 12.13 17 12 17C11.87 17 11.74 16.97 11.62 16.92C11.5 16.87 11.39 16.8 11.29 16.71C11.2 16.61 11.13 16.51 11.08 16.38C11.03 16.26 11 16.13 11 16C11 15.87 11.03 15.74 11.08 15.62C11.13 15.5 11.2 15.39 11.29 15.29C11.39 15.2 11.5 15.13 11.62 15.08C11.86 14.98 12.14 14.98 12.38 15.08C12.5 15.13 12.61 15.2 12.71 15.29C12.8 15.39 12.87 15.5 12.92 15.62C12.97 15.74 13 15.87 13 16C13 16.13 12.97 16.26 12.92 16.38Z" fill="#555555"/>
            </svg>

            <button type="button" class="close" data-dismiss="alert" aria-hidden="true">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M5.00082 14.9995L14.9999 5.00041" stroke="#555555" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M14.9999 14.9996L5.00082 5.00049" stroke="#555555" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>

            <span class="alert-text">{{ session('exit_flash') }}</span>
        </div>
    @endpush
@endif

@push('scripts')
<script type="module">
    $(document).ready(function() {
    // Xử lý checkbox "chọn tất cả"
    $(document).on('change', '.select-all', function() {
        const isChecked = $(this).is(':checked');
        $('.index-table').find(".select-row").prop('checked', isChecked);
    });

    $(document).on('click', '#delete-records', function(event) {
        const recordsChecked = $('.index-table').find(".select-row:checked");
        const recordsCheckedAll = $('.index-table').find(".select-all:checked");

        let ids = [];

        if (recordsCheckedAll.length > 0) {
        // Nếu "chọn tất cả" được chọn, lấy tất cả ID bản ghi
        ids = $('.index-table').find(".select-row").toArray()
            .map(row => parseInt(row.value))
            .filter(id => !isNaN(id)); // Lọc ra các giá trị không hợp lệ
        } else {
        // Nếu không, chỉ lấy các ID bản ghi được chọn
        ids = recordsChecked.toArray()
            .map(row => parseInt(row.value))
            .filter(id => !isNaN(id)); // Lọc ra các giá trị không hợp lệ
        }

        if (ids.length === 0) {
        return;
        }

        const confirmationModal = $("#confirmation-modal");
        confirmationModal.modal('show');
        confirmationModal.find("form").find('input[name="ids"][type="hidden"]').val(JSON.stringify(ids));
        confirmationModal.find("form").attr('action', "{{ route('admin.comments.delete') }}");
    });

    // Lưu trữ các tham chiếu DOM quan trọng
    const tableBody = $('tbody');
    const dataRows = tableBody.find('tr.clickable-row');
    const noDataRow = tableBody.find('tr.no-data-row');
    const processingPanel = $('#DataTables_Table_0_processing');

    // Lấy số cột từ hàng đầu tiên
    const numCols = $('thead tr th').length || 8;

    // Tạo một hàng "No Results" cho tìm kiếm động nếu không có sẵn
    let searchNoResultsRow = tableBody.find('tr.no-results-search');
    if (searchNoResultsRow.length === 0) {
        searchNoResultsRow = $('<tr>').addClass('no-results-search').hide();
        const cell = $('<td>').attr('colspan', numCols)
            .addClass('text-center')
            .text('{{ trans('comment::comment.messages.search_no_results') }}');
        searchNoResultsRow.append(cell);

        // Chỉ thêm vào DOM nếu có các hàng dữ liệu
        if (dataRows.length > 0) {
            tableBody.append(searchNoResultsRow);
        }
    }

    $('.dt-search input[type="search"]').attr('placeholder', '{{ trans('comment::comment.placeholders.search') }}');

    // Thiết lập sự kiện tìm kiếm
    const searchInput = $('.dt-search input[type="search"]');

    if (searchInput.length) {
        // Xử lý tìm kiếm khi nhấn Enter
        searchInput.on("keypress", function(e) {
            if (e.which === 13) { // Kiểm tra phím Enter
                // Hiển thị panel xử lý
                processingPanel.css('display', 'block');

                const query = $(this).val().toLowerCase().trim();
                let visibleRowCount = 0;

                // Nếu đang có hàng "Không có dữ liệu", ẩn đi để tìm kiếm
                if (noDataRow.length > 0) {
                    noDataRow.hide();
                }

                dataRows.each(function() {
                    const row = $(this);
                    const idCell = row.find('td:nth-child(2)');
                    const contentCell = row.find('td:nth-child(3)');
                    const platformCell = row.find('td:nth-child(4)');
                    const predictionCell = row.find('td:nth-child(5)');

                    const matches =
                        (idCell.length && containsSearchTerm(idCell.text(), query)) ||
                        (contentCell.length && containsSearchTerm(contentCell.text(), query)) ||
                        (platformCell.length && containsSearchTerm(platformCell.text(), query)) ||
                        (predictionCell.length && containsSearchTerm(predictionCell.text(), query));

                    if (matches) {
                        row.show();
                        visibleRowCount++;
                    } else {
                        row.hide();
                    }
                });

                // Hiển thị thông báo tìm kiếm không có kết quả nếu cần
                if (visibleRowCount === 0 && dataRows.length > 0) {
                    searchNoResultsRow.show();
                } else {
                    searchNoResultsRow.hide();

                    // Hiển thị lại hàng "Không có dữ liệu" nếu không có dữ liệu ban đầu
                    if (dataRows.length === 0 && noDataRow.length > 0) {
                        noDataRow.show();
                    }
                }

                // Ẩn panel xử lý sau khi hoàn thành tìm kiếm
                setTimeout(function() {
                    processingPanel.css('display', 'none');
                }, 300);
            }
        });

        // Xử lý khi xóa toàn bộ nội dung ô tìm kiếm
        searchInput.on('search', function() {
            if ($(this).val() === '') {
                // Hiển thị panel xử lý
                processingPanel.css('display', 'block');

                // Reset lại bảng khi ô tìm kiếm trống
                dataRows.show();
                searchNoResultsRow.hide();

                // Nếu không có dữ liệu ban đầu, hiển thị lại thông báo không có dữ liệu
                if (dataRows.length === 0 && noDataRow.length > 0) {
                    noDataRow.show();
                }

                // Ẩn panel xử lý sau khi hoàn thành
                setTimeout(function() {
                    processingPanel.css('display', 'none');
                }, 300);
            }
        });

        // Hàm kiểm tra từ khóa có trong văn bản
        function containsSearchTerm(text, query) {
            if (!text) return false;

            const normalizedText = text.toLowerCase().trim();
            const normalizedQuery = query.toLowerCase().trim();

            return normalizedText.includes(normalizedQuery) ||
                normalizedText.split(/\s+/).some(word => word.startsWith(normalizedQuery));
        }
    }
    });
</script>
@endpush
