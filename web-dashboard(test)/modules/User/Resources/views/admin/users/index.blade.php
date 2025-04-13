@extends('admin::layout')

@component('admin::components.page.header')
    @slot('title', 'Users')

    <li class="active">Users</li>
@endcomponent

@section('content')
    <div class="box box-primary">
        <div class="box-body index-table">
            @component('admin::components.table')
                @slot('thead')
                    @include('user::admin.users.thead', ['name' => 'users'])
                @endslot

                @slot('tbody')
                    @foreach($users as $user)
                        <tr>
                            <td>
                                <div class="checkbox">
                                    <input type="checkbox" class="select-row" name="ids[]" value="{{ $user->id }}" id="user-{{ $user->id }}">
                                    <label for="user-{{ $user->id }}"></label>
                                </div>
                            </td>
                            <td>{{ $user->id }}</td>
                            <td>{{ $user->first_name }} {{ $user->last_name }}</td>
                            <td>{{ $user->email }}</td>
                            <td>
                                @if($user->isAdmin())
                                    <span class="badge badge-warning">{{ $roles[$user->role] }}</span>
                                @else
                                    <span class="badge badge-primary">{{ $roles[$user->role] }}</span>
                                @endif
                            </td>
                            <td>
                                @if($user->last_login)
                                    {{ $user->last_login->diffForHumans() }}
                                @else
                                    <span class="text-muted">Chưa đăng nhập</span>
                                @endif
                            </td>
                            <td class="sorting_1">
                                <span data-toggle="tooltip" title="{{ $user->created_at }}">
                                    {{ $user->created_at->diffForHumans() }}
                                </span>
                            </td>
                        </tr>
                    @endforeach
                @endslot

                {{-- @slot('tfoot')
                    <tr>
                        <td colspan="8">
                            <div>
                                {{ $users->appends(request()->all())->links() }}
                            </div>
                        </td>
                    </tr>
                @endslot --}}

                {{-- @slot('ttotal')
                    <div>
                        <label class="dt-info" aria-live="polite" id="DataTables_Table_0_info" role="status">
                            {{ "Show $perPage of $totalUsers users" }}
                        </label>
                    </div>
                @endslot

                @slot('tchange')
                    <div class="row dt-layout-row">
                        <div class="dt-paging">
                            <nav aria-label="pagination">
                                <ul class="pagination">
                                    <li class="dt-paging-button page-item">
                                        {{ $users->appends(request()->query())->links('pagination::bootstrap-4') }}
                                    </li>
                                </ul>
                            </nav>
                        </div>
                    </div>
                @endslot --}}
                @slot('tResult')
                    {{ request()->get('page', 1) * $perPage - $perPage + 1 }} - {{ request()->get('page', 1) * $perPage }} of
                    {{ $totalUsers }} results entries
                @endslot

                @slot('tPagination')
                    {!! $users->appends(request()->input())->links('admin::pagination.simple') !!}
                @endslot
            @endcomponent
        </div>
    </div>
@endsection

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
            confirmationModal.find("form").find('input[name="ids"][type="hidden"]').val(JSON.stringify(ids));
            confirmationModal.find("form").attr('action', "{{ route('admin.users.delete') }}");
        });



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
            searchInput.on("keypress", function (e) {
                if (e.which === 13) { // Kiểm tra phím Enter
                    // Hiển thị panel xử lý
                    processingPanel.css('display', 'block');

                    const query = searchInput.val().toLowerCase().trim();
                    let visibleRowCount = 0;

                    tableRows.each(function () {
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
