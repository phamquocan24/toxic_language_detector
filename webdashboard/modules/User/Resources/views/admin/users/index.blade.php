@extends('admin::layout')

@component('admin::components.page.header')
    @slot('title', trans('user::users.users'))

    <li class="active">{{ trans('user::users.users') }}</li>
@endcomponent

@component('admin::components.page.index_table', ['showDelete' => $showDelete])
    @slot('buttons', ['invite'])
    @slot('resource', 'users')
    @slot('name', trans('user::users.user'))

    @slot('thead')
        @include('user::admin.users.thead', ['name' => 'users-index'])
    @endslot
    @slot('tbody')
        @if (!empty($users))
            @foreach ($users as $user)
                <tr>
                    <td>
                        <div class="checkbox">
                            <input type="checkbox" class="select-row" name="ids[]" value="{{ $user->id }}"
                                id="user-{{ $user->id }}">
                            <label for="user-{{ $user->id }}"></label>
                        </div>
                    </td>
                    <td>{{ $user->id }}</td>
                    <td>{{ $user->name }}</td>
                    <td>{{ $user->email }}</td>
                    <td>
                        @if ($user->isAdmin())
                            <span class="badge badge-warning">{{ isset($user->role_id) && isset($roles[$user->role_id]) ? $roles[$user->role_id] : 'Admin' }}</span>
                        @else
                            <span class="badge badge-primary">{{ isset($user->role_id) && isset($roles[$user->role_id]) ? $roles[$user->role_id] : 'Member' }}</span>
                        @endif
                    </td>
                    <td class="sorting_1">
                        @if ($user->last_login)
                            <span data-toggle="tooltip" title="{{ $user->last_login }}">
                                {{ $user->last_login->diffForHumans() }}
                            </span>
                        @else
                            <span class="text-muted">Chưa đăng nhập</span>
                        @endif
                    </td>
                    <td class="sorting_1">
                        <span data-toggle="tooltip"
                            title="{{ $user->created_at }}">{{ $user->created_at->diffForHumans() }}</span>
                    </td>
                </tr>
            @endforeach
        @else
            <tr>
                <td colspan="8" class="dt-empty">No data available in table</td>
            </tr>
        @endif
    @endslot

    @slot('tResult')
        {{ request()->get('page', 1) * $perPage - $perPage + 1 }} - {{ request()->get('page', 1) * $perPage }} of
        {{ $totalUsers }} results entries
    @endslot

    @slot('tPagination')
        {!! $users->appends(request()->input())->links('admin::pagination.simple') !!}
    @endslot
@endcomponent
@if (session()->has('exit_flash'))
    @push('notifications')
        <div class="alert alert-success fade in alert-dismissible clearfix">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path
                    d="M12 2C6.49 2 2 6.49 2 12C2 17.51 6.49 22 12 22C17.51 22 22 17.51 22 12C22 6.49 17.51 2 12 2ZM11.25 8C11.25 7.59 11.59 7.25 12 7.25C12.41 7.25 12.75 7.59 12.75 8V13C12.75 13.41 12.41 13.75 12 13.75C11.59 13.75 11.25 13.41 11.25 13V8ZM12.92 16.38C12.87 16.51 12.8 16.61 12.71 16.71C12.61 16.8 12.5 16.87 12.38 16.92C12.26 16.97 12.13 17 12 17C11.87 17 11.74 16.97 11.62 16.92C11.5 16.87 11.39 16.8 11.29 16.71C11.2 16.61 11.13 16.51 11.08 16.38C11.03 16.26 11 16.13 11 16C11 15.87 11.03 15.74 11.08 15.62C11.13 15.5 11.2 15.39 11.29 15.29C11.39 15.2 11.5 15.13 11.62 15.08C11.86 14.98 12.14 14.98 12.38 15.08C12.5 15.13 12.61 15.2 12.71 15.29C12.8 15.39 12.87 15.5 12.92 15.62C12.97 15.74 13 15.87 13 16C13 16.13 12.97 16.26 12.92 16.38Z"
                    fill="#555555" />
            </svg>

            <button type="button" class="close" data-dismiss="alert" aria-hidden="true">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M5.00082 14.9995L14.9999 5.00041" stroke="#555555" stroke-width="1.5" stroke-linecap="round"
                        stroke-linejoin="round" />
                    <path d="M14.9999 14.9996L5.00082 5.00049" stroke="#555555" stroke-width="1.5" stroke-linecap="round"
                        stroke-linejoin="round" />
                </svg>
            </button>

            <span class="alert-text">{{ session('exit_flash') }}</span>
        </div>
    @endpush
@endif
@push('scripts')
    <script type="module">
        $(document).ready(function() {
            // Handle the "select all" checkbox
            $(document).on('click', '.select-all', function() {
                const isChecked = $(this).is(':checked');
                $('.index-table').find(".select-row").prop('checked', isChecked);
            });

            $(document).on('click', '#delete-records', function(event) {
                const recordsChecked = $('.index-table').find(".select-row:checked");
                const recordsCheckedAll = $('.index-table').find(".select-all:checked");

                let ids = [];

                if (recordsCheckedAll.length > 0) {
                    // If "select all" is checked, get all record IDs
                    ids = $('.index-table').find(".select-row").toArray()
                        .map(row => parseInt(row.value))
                        .filter(id => !isNaN(id)); // Filter out invalid values
                } else {
                    // Otherwise, get only the checked record IDs
                    ids = recordsChecked.toArray()
                        .map(row => parseInt(row.value))
                        .filter(id => !isNaN(id)); // Filter out invalid values
                }

                if (ids.length === 0) {
                    return;
                }

                const confirmationModal = $("#confirmation-modal");
                confirmationModal.modal('show');
                confirmationModal.find("form").find('input[name="ids"][type="hidden"]').val(JSON.stringify(
                    ids));
                confirmationModal.find("form").attr('action', "{{ route('admin.users.delete') }}");
            });


            $('.dt-search input[type="search"]').attr('placeholder', 'Search ID, UserName, Email ...');
            // Xử lý tìm kiếm
            const searchInput = $('.dt-search input[type="search"]');
            const tableRows = $('tbody tr');
            const processingPanel = $('#DataTables_Table_0_processing');
            const noResultsRow = createNoResultsRow();

            // Thêm hàng thông báo không có kết quả vào cuối bảng
            function createNoResultsRow() {
                const row = $('<tr>').addClass('no-results').css('display', 'none');
                const cell = $('<td>').attr('colspan', tableRows.first().children().length)
                    .addClass('text-center text-muted py-3')
                    .text('Không tìm thấy người dùng phù hợp');
                row.append(cell);
                tableRows.first().closest('tbody').append(row);
                return row;
            }

            if (searchInput.length) {
                searchInput.on("keypress", function(e) {
                    if (e.which === 13) { // Kiểm tra phím Enter
                        // Hiển thị panel xử lý
                        processingPanel.css('display', 'block');

                        const query = searchInput.val().toLowerCase().trim();
                        let visibleRowCount = 0;

                        tableRows.each(function() {
                            const row = $(this);
                            const idCell = row.find('td:nth-child(2)');
                            const nameCell = row.find('td:nth-child(3)');
                            const emailCell = row.find('td:nth-child(4)');
                            const roleCell = row.find('td:nth-child(5)');

                            const matches =
                                (idCell.length && containsSearchTerm(idCell.text(), query)) ||
                                (nameCell.length && containsSearchTerm(nameCell.text(), query)) ||
                                (emailCell.length && containsSearchTerm(emailCell.text(), query)) ||
                                (roleCell.length && containsSearchTerm(roleCell.text(), query));

                            if (matches) {
                                row.show();
                                visibleRowCount++;
                            } else {
                                row.hide();
                            }
                        });

                        noResultsRow.css('display', visibleRowCount > 0 ? 'none' : '');
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
                        tableRows.show();
                        noResultsRow.css('display', 'none');

                        // Ẩn panel xử lý sau khi hoàn thành
                        setTimeout(function() {
                            processingPanel.css('display', 'none');
                        }, 300);
                    }
                });
                // Xử lý khi nhấn phím Enter trong ô tìm kiếm
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
