@extends('admin::layout')

@component('admin::components.page.header')
    @slot('title', trans('brand::brands.brands'))

    <li class="active">{{ trans('brand::brands.brands') }}</li>
@endcomponent

@component('admin::components.page.index_table')
    @slot('buttons', ['create'])
    @slot('resource', 'brands')
    @slot('name', trans('brand::brands.brands'))

    @slot('thead')
        @include('brand::admin.brands.partials.thead', ['name' => 'brands-index'])
    @endslot

    @slot('tbody')
    @if (!empty($brands))
        @foreach ($brands as $brand)
            <tr class="clickable-row">
                <td>
                    <div class="checkbox">
                        <input type="checkbox" class="select-row" name="ids[]" id="brand-{{ $brand->id }}"
                            value="{{ $brand->id }}">
                        <label for="brand-{{ $brand->id }}"></label>
                    </div>
                </td>
                <td class="dt-type-numeric">{{ $brand->id }}</td>
                <td>
                    <div class="thumbnail-holder">
                        <img src="https://demo.fleetcart.envaysoft.com/storage/media/H0BnQ6XoB6vBb1YAkRg22mncLS76Yv0zGz4T4M04.png"
                            alt="thumbnail">
                    </div>
                </td>
                <td>
                    <a class="name" href="{{ route('admin.brands.edit', $brand->id) }}">{{ $brand->name}}</a>
                </td>
                <td>
                    <span class="badge {{ $brand->is_active ? 'badge-success' : 'badge-danger' }}">
                        {{ $brand->is_active ? 'Active' : 'UnActive' }}
                    </span>
                </td>
                <td class="sorting_1">
                        <span data-toggle="tooltip"
                            title="{{ $brand->created_at }}">{{ $brand->created_at->diffForHumans() }}
                        </span>
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
        {{ $totalBrands }} results entries
    @endslot

    @slot('tPagination')
        {!! $brands->appends(request()->input())->links('admin::pagination.simple') !!}
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
    $(document).ready(function () {
        // Xử lý chọn tất cả checkbox
        $(".select-all").on("change", function () {
            $("input[type='checkbox']:not(.select-all)").prop("checked", $(this).prop("checked"));
        });

        // Xử lý khi bấm nút Delete
        $(".btn-delete").on("click", function () {
            const selectedIds = [];
            $("input.select-row:checked").each(function () {
                selectedIds.push($(this).val());
            });

            if (selectedIds.length === 0) {
                toastr.warning("Vui lòng chọn ít nhất một mục để xóa!");
                return;
            }

            const confirmationModal = $("#confirmation-modal");
            confirmationModal.modal('show');
            confirmationModal.find("#delete-ids").val(JSON.stringify(selectedIds));
        });

        // Tìm kiếm trong bảng
        const searchInput = $('.dt-search input[type="search"]');
        const tableRows = $('tbody tr.clickable-row');

        // // Gắn sự kiện lắng nghe
        // searchInput.on("keyup", function () {
        //     const query = $(this).val().toLowerCase();

        //     tableRows.each(function () {
        //         // Lấy giá trị ID và tên từ từng dòng
        //         const idCell = $(this).find('td.dt-type-numeric');
        //         const nameCell = $(this).find('a.name');

        //         // Kiểm tra có khớp không
        //         const matches = idCell.text().includes(query) || nameCell.text().toLowerCase().includes(query);

        //         // Hiển thị hoặc ẩn dòng dựa trên kết quả so khớp
        //         $(this).toggle(matches);
        //     });
        // });
        // Tìm kiếm trong bảng
        $(document).ready(function () {
    const searchInput = $('.dt-search input[type="search"]');
    const tableRows = $('tbody tr.clickable-row');
    const tableBody = $('tbody');
    const processingPanel = $('#DataTables_Table_0_processing'); // Sử dụng đúng ID của processing panel

    searchInput.on("keydown", function (event) {
        if (event.key === "Enter") {
            const query = $(this).val().toLowerCase();
            let hasResults = false;

            // Hiển thị panel xử lý
            processingPanel.css('display', 'block');

            tableRows.each(function () {
                const idCell = $(this).find('td.dt-type-numeric');
                const nameCell = $(this).find('a.name');

                const matches = idCell.text().includes(query) || nameCell.text().toLowerCase().includes(query);

                $(this).toggle(matches);

                if (matches) {
                    hasResults = true;
                }
            });

            tableBody.find('.no-data').remove();
            if (!hasResults) {
                tableBody.append('<tr class="no-data"><td colspan="100%" style="text-align: center;">Không tìm thấy dữ liệu!</td></tr>');
            }

            // Ẩn panel xử lý sau khi hoàn thành
            setTimeout(function () {
                processingPanel.css('display', 'none');
            }, 300);
        }
    });
});

    });
</script>

@endpush
