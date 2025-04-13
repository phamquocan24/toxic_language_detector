<tr>
    {{-- @include('admin::partials.table.brand_select_all') --}}

    @php
        $sortBy = request()->get('sort_by', 'id');
        $sort = request()->get('sort', 'asc');
        $newSort = ($sort === 'asc') ? 'desc' : 'asc';
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
            <span class="dt-column-title">{{ trans('admin::admin.table.id') }}</span>
            <span class="dt-column-order
                @if($sortBy === 'id') {{ $sort === 'asc' ? 'dt-ordering-asc' : 'dt-ordering-desc' }} @endif"
                role="button">
            </span>
        </a>
    </th>

    {{-- Column for Logo --}}
    <th>{{ trans('brand::brands.logo') }}</th>

    {{-- Column for Name --}}
    {{-- <th style="width: 32%;" class="dt-orderable-asc dt-orderable-desc" data-dt-column="1">
        <a href="{{ request()->fullUrlWithQuery(['sort_by' => 'name', 'sort' => $newSort]) }}" class="text-decoration-none">
            <span class="dt-column-title">{{ trans('brand::brands.name') }}</span>
            <span class="dt-column-order
                @if($sortBy === 'name') {{ $sort === 'asc' ? 'dt-ordering-asc' : 'dt-ordering-desc' }} @endif"
                role="button">
            </span>
        </a>
    </th> --}}
    {{-- Column for Name --}}
    <th style="width: 32%;" class="" data-dt-column="1">
        <span class="dt-column-title">{{ trans('brand::brands.name') }}</span>
    </th>



    {{-- Cột Status --}}
    <th data-dt-column="1" class="dt-orderable-asc dt-orderable-desc" style="width: 20px;">
        <a href="{{ request()->fullUrlWithQuery(['sort_by' => 'is_active', 'sort' => $sortOrder === 'asc' ? 'desc' : 'asc']) }}">
            <span class="dt-column-title">{{ trans('admin::admin.table.is_active') }}</span>
            <span class="dt-column-order
                @if($sortBy === 'is_active') {{ $sortOrder === 'asc' ? 'dt-ordering-asc' : 'dt-ordering-desc' }} @endif"
                role="button">
            </span>
        </a>
    </th>



    {{-- Cột Created At --}}
    <th data-dt-column="1" class="dt-orderable-asc dt-orderable-desc" style="width: 15%;">
        <a href="{{ request()->fullUrlWithQuery(['sort_by' => 'created_at', 'sort' => $newSort]) }}" class="text-decoration-none">
            <span class="dt-column-title">{{ trans('admin::admin.table.created') }}</span>
            <span class="dt-column-order
                @if($sortBy === 'created_at') {{ $sort === 'asc' ? 'dt-ordering-asc' : 'dt-ordering-desc' }} @endif"
                role="button">
            </span>
        </a>
    </th>
</tr>
