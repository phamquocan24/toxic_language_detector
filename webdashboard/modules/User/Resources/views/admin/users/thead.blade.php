<tr>

    @php
        $sortBy = request()->get('sort_by', 'id'); // Lấy cột hiện tại được sắp xếp
        $sort = request()->get('sort', 'asc'); // Lấy thứ tự sắp xếp hiện tại
        $newSort = ($sort === 'asc') ? 'desc' : 'asc'; // Chuyển đổi trạng thái sắp xếp
    @endphp

    <th style="max-width: 20px;">
        <div class="checkbox">
            <input type="checkbox" class="select-all" id="{{ $name ?? '' }}-select-all">
            <label for="{{ $name ?? '' }}-select-all"></label>
        </div>
    </th>

    {{-- Cột ID --}}
    <th data-dt-column="1" class="dt-orderable-asc dt-orderable-desc" style="width: 6%;">
        <a href="{{ request()->fullUrlWithQuery(['sort_by' => 'id', 'sort' => $newSort]) }}" class="text-decoration-none">
            <span class="dt-column-title">{{ trans('user::users.table.id') }}</span>
            <span class="dt-column-order
                @if($sortBy === 'id') {{ $sort === 'asc' ? 'dt-ordering-asc' : 'dt-ordering-desc' }} @endif"
                role="button">
            </span>
        </a>
    </th>

    {{-- Cột Họ tên --}}
    <th data-dt-column="1" class="dt-orderable-asc dt-orderable-desc" style="width: 20%;">
        <a href="{{ request()->fullUrlWithQuery(['sort_by' => 'name', 'sort' => $newSort]) }}" class="text-decoration-none">
            <span class="dt-column-title">{{ trans('user::users.table.full_name') }}</span>
            <span class="dt-column-order
                @if($sortBy === 'name') {{ $sort === 'asc' ? 'dt-ordering-asc' : 'dt-ordering-desc' }} @endif"
                role="button">
            </span>
        </a>
    </th>

    {{-- Cột Email --}}
    <th data-dt-column="1" class="dt-orderable-asc dt-orderable-desc" style="width: 20%;">
        <a href="{{ request()->fullUrlWithQuery(['sort_by' => 'email', 'sort' => $newSort]) }}" class="text-decoration-none">
            <span class="dt-column-title">{{ trans('user::users.table.email') }}</span>
            <span class="dt-column-order
                @if($sortBy === 'email') {{ $sort === 'asc' ? 'dt-ordering-asc' : 'dt-ordering-desc' }} @endif"
                role="button">
            </span>
        </a>
    </th>

    {{-- Cột Vai trò --}}
    <th data-dt-column="1" class="dt-orderable-asc dt-orderable-desc" style="width: 15%;">
        <a href="{{ request()->fullUrlWithQuery(['sort_by' => 'role', 'sort' => $newSort]) }}" class="text-decoration-none">
            <span class="dt-column-title">{{ trans('user::users.table.role') }}</span>
            <span class="dt-column-order
                @if($sortBy === 'role') {{ $sort === 'asc' ? 'dt-ordering-asc' : 'dt-ordering-desc' }} @endif"
                role="button">
            </span>
        </a>
    </th>

    {{-- Cột Đăng nhập lần cuối --}}
    <th data-dt-column="1" class="dt-orderable-asc dt-orderable-desc" style="width: 20%;">
        <a href="{{ request()->fullUrlWithQuery(['sort_by' => 'last_login', 'sort' => $newSort]) }}" class="text-decoration-none">
            <span class="dt-column-title">{{ trans('user::users.table.last_login') }}</span>
            <span class="dt-column-order
                @if($sortBy === 'last_login') {{ $sort === 'asc' ? 'dt-ordering-asc' : 'dt-ordering-desc' }} @endif"
                role="button">
            </span>
        </a>
    </th>

    {{-- Cột Ngày tạo --}}
    <th data-dt-column="1" class="dt-orderable-asc dt-orderable-desc" style="width: 15%;">
        <a href="{{ request()->fullUrlWithQuery(['sort_by' => 'created_at', 'sort' => $newSort]) }}" class="text-decoration-none">
            <span class="dt-column-title">{{ trans('user::users.table.created_at') }}</span>
            <span class="dt-column-order
                @if($sortBy === 'created_at') {{ $sort === 'asc' ? 'dt-ordering-asc' : 'dt-ordering-desc' }} @endif"
                role="button">
            </span>
        </a>
    </th>
</tr>
