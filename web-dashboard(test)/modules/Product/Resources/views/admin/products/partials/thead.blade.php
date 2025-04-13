<tr>
    @include('admin::partials.table.select_all')

    @php
        $sortBy = request()->get('sort_by', 'id'); // Lấy cột hiện tại được sắp xếp
        $sort = request()->get('sort', 'asc'); // Lấy thứ tự sắp xếp hiện tại
        $newSort = ($sort === 'asc') ? 'desc' : 'asc'; // Chuyển đổi trạng thái sắp xếp
    @endphp



    {{-- Cột ID --}}
    <th data-dt-column="1" class="dt-orderable-asc dt-orderable-desc" style="width: 6%;">
        <a href="{{ request()->fullUrlWithQuery(['sort_by' => 'id', 'sort' => $newSort]) }}" class="text-decoration-none">
            <span class="dt-column-title">{{ trans('admin::admin.table.id') }}</span>
            <span class="dt-column-order
                @if($sortBy === 'id') {{ $sort === 'asc' ? 'dt-ordering-asc' : 'dt-ordering-desc' }} @endif"
                role="button">
            </span>
        </a>
    </th>

    {{-- Cột Hình ảnh --}}
    <th>{{ trans('product::products.table.thumbnail') }}</th>

    {{-- Cột Tên --}}
    <th style="width: 32%;" class="dt-orderable-asc dt-orderable-desc" data-dt-column="1">
        <a href="{{ request()->fullUrlWithQuery(['sort_by' => 'name', 'sort' => $newSort]) }}" class="text-decoration-none">
            <span class="dt-column-title">{{ trans('product::products.table.name') }}</span>
            <span class="dt-column-order
                @if($sortBy === 'name') {{ $sort === 'asc' ? 'dt-ordering-asc' : 'dt-ordering-desc' }} @endif"
                role="button">
            </span>
        </a>
    </th>

    {{-- Cột Giá --}}
    <th data-dt-column="1" class="dt-orderable-asc dt-orderable-desc" style="width: 16%;">
        <a href="{{ request()->fullUrlWithQuery(['sort_by' => 'price', 'sort' => $newSort]) }}" class="text-decoration-none">
            <span class="dt-column-title">{{ trans('product::products.table.price') }}</span>
            <span class="dt-column-order
                @if($sortBy === 'price') {{ $sort === 'asc' ? 'dt-ordering-asc' : 'dt-ordering-desc' }} @endif"
                role="button">
            </span>
        </a>
    </th>

    {{-- Cột Kho hàng --}}
    <th data-dt-column="1" class="dt-orderable-asc dt-orderable-desc" style="width: 20px;">
        <a href="{{ request()->fullUrlWithQuery(['sort_by' => 'stock', 'sort' => $newSort]) }}" class="text-decoration-none">
            <span class="dt-column-title">{{ trans('product::products.table.stock') }}</span>
            <span class="dt-column-order
                @if($sortBy === 'stock') {{ $sort === 'asc' ? 'dt-ordering-asc' : 'dt-ordering-desc' }} @endif"
                role="button">
            </span>
        </a>
    </th>

    {{-- Cột Trạng thái --}}
    <th data-dt-column="1" class="dt-orderable-asc dt-orderable-desc" style="width: 20px;">
        <a href="{{ request()->fullUrlWithQuery(['sort_by' => 'status', 'sort' => $newSort]) }}" class="text-decoration-none">
            <span class="dt-column-title">{{ trans('admin::admin.table.status') }}</span>
            <span class="dt-column-order
                @if($sortBy === 'status') {{ $sort === 'asc' ? 'dt-ordering-asc' : 'dt-ordering-desc' }} @endif"
                role="button">
            </span>
        </a>
    </th>

    {{-- Cột Ngày cập nhật --}}
    <th data-dt-column="1" class="dt-orderable-asc dt-orderable-desc" style="width: 15%;">
        <a href="{{ request()->fullUrlWithQuery(['sort_by' => 'updated_at', 'sort' => $newSort]) }}" class="text-decoration-none">
            <span class="dt-column-title">{{ trans('admin::admin.table.updated') }}</span>
            <span class="dt-column-order
                @if($sortBy === 'updated_at') {{ $sort === 'asc' ? 'dt-ordering-asc' : 'dt-ordering-desc' }} @endif"
                role="button">
            </span>
        </a>
    </th>
</tr>

