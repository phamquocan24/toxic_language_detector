@extends('admin::layout')

@component('admin::components.page.header')
    @slot('title', trans('admin::resource.edit', ['resource' => trans('category::categories.categories')]))

    <li><a href="{{ route('admin.categories.index') }}">{{ trans('category::categories.categories') }}</a></li>
    <li class="active">{{ trans('admin::resource.edit', ['resource' => trans('category::categories.categories')]) }}</li>
@endcomponent

@section('content')
    <form method="POST" action="{{ route('admin.categories.store') }}" class="form-horizontal" id="category-form">
        @csrf

        <div class="box">
            <div class="box-body">
                <div class="tab-pane fade in active" id="general">
                    <h3 class="tab-content-title">{{ trans('category::categories.general') }}</h3>

                    <div id="id-field" class="form-group hide">
                        <label for="id" class="col-md-3 control-label">{{ trans('category::categories.form.id') }}</label>
                        <div class="col-md-9">
                            <input name="id" class="form-control" id="id" type="text" value="id" disabled>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="name" class="col-md-3 control-label">{{ trans('category::categories.form.name') }}<span class="m-l-5 text-red">*</span></label>
                        <div class="col-md-9">
                            <input name="name" class="form-control" id="name" type="text" value="'name'>
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
            </div>
        </div>

        <div class="form-group">
            <div class="col-md-10 col-md-offset-2">
                <button type="submit" class="btn btn-primary" data-loading>
                    {{ trans('admin::resource.save') }}
                </button>
            </div>
        </div>
    </form>
@endsection

@include('brand::admin.brands.partials.shortcuts')

@push('globals')
    @vite([
        'modules/Brand/Resources/assets/admin/sass/app.scss',
        // 'modules/Brand/Resources/assets/admin/js/edit.js',
        'modules/Variation/Resources/assets/admin/sass/main.scss',
        // 'modules/Option/Resources/assets/admin/sass/main.scss',
        'modules/Media/Resources/assets/admin/sass/main.scss',
        'modules/Media/Resources/assets/admin/js/main.js',
    ])
@endpush
