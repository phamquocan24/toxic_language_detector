@extends('admin::layout')

@component('admin::components.page.header')
    @slot('title', trans('category::categories.categories'))

    <li class="active">{{ trans('category::categories.categories') }}</li>
@endcomponent
<link rel="stylesheet" href="{{ asset('js/edit.js') }}">
@section('content')
    <form method="POST" action="" class="form-horizontal" id="category-form" novalidate>
        @csrf

        <div class="box">
            <div class="box-body">
                <div class="row">
                    <button class="btn btn-default add-root-category">Add Root Category</button></br>
                    <button class="btn btn-default add-sub-category disabled" style="margin-top: 10px">Add Subcategory</button>

                    <div class="m-b-10" style="margin-top: 20px">
                        <a href="#" class="collapse-all">Collapse All</a> |
                        <a href="#" class="expand-all">Expand All</a>
                    </div>
                </div>
                {{-- <div id="category-tree" class="form-group">
                    @foreach ($categoriesTree as $category)
                        @include('category::admin.categories.partials.category_item', ['category' => $category])
                    @endforeach
                </div> --}}

                <div class="tab-pane fade in active" id="general">
                    <h3 class="tab-content-title">{{ trans('category::categories.general') }}</h3>

                    <div id="id-field" class="form-group hide">
                        <label for="id" class="col-md-3 control-label">{{ trans('category::categories.form.id') }}</label>
                        <div class="col-md-9">
                            <input name="id" class="form-control" id="id" type="text" value="" disabled>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="name" class="col-md-3 control-label">{{ trans('category::categories.form.name') }}<span class="m-l-5 text-red">*</span></label>
                        <div class="col-md-9">
                            <input name="name" class="form-control" id="name" type="text" value="">
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="is_searchable" class="col-md-3 control-label">{{ trans('category::categories.form.searchable') }}</label>
                        <div class="col-md-9">
                            <div class="checkbox">
                                <input type="hidden" value="0" name="is_searchable">
                                <input type="checkbox" name="is_searchable" class="" id="is_searchable" value="1">
                                <label for="is_searchable">{{ trans('category::categories.form.show_in_search') }}</label>
                            </div>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="is_active" class="col-md-3 control-label">{{ trans('category::categories.form.status') }}</label>
                        <div class="col-md-9">
                            <div class="checkbox">
                                <input type="hidden" value="0" name="is_active">
                                <input type="checkbox" name="is_active" class="" id="is_active" value="1">
                                <label for="is_active">{{ trans('category::categories.form.enable') }}</label>
                            </div>
                        </div>
                    </div>

                </div>
                <div class="form-group">
                    <div class="col-md-10 col-md-offset-2">
                        <button type="submit" class="btn btn-primary" data-loading>
                            {{ trans('admin::resource.save') }}
                        </button>
                        <button type="button" class="btn btn-link text-red btn-delete p-l-0 hide" data-confirm>
                            Delete
                        </button>
                    </div>
                </div>
            </div>
        </div>

    </form>
@endsection

@component('admin::components.page.index_table')
    @slot('buttons', ['create'])
    @slot('resource', 'categories')
    @slot('name', trans('category::categories.categories'))


@endcomponent

@push('scripts')
    <script type="module">
        document.querySelector('.collapse-all').addEventListener('click', function(e) {
            e.preventDefault();
            const items = document.querySelectorAll('.category-item');
            items.forEach(item => {
                if (!item.classList.contains('collapsed')) {
                    item.classList.add('collapsed');
                    item.querySelector('.children').style.display = 'none';
                }
            });
        });

        document.querySelector('.expand-all').addEventListener('click', function(e) {
            e.preventDefault();
            const items = document.querySelectorAll('.category-item');
            items.forEach(item => {
                if (item.classList.contains('collapsed')) {
                    item.classList.remove('collapsed');
                    item.querySelector('.children').style.display = 'block';
                }
            });
        });
    </script>
@endpush
