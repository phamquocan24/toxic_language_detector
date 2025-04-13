@extends('admin::layout')

@component('admin::components.page.header')
    @slot('title', trans('admin::resource.edit', ['resource' => trans('brand::brands.brands')]))

    <li><a href="{{ route('admin.brands.index') }}">{{ trans('brand::brands.brands') }}</a></li>
    <li class="active">{{ trans('admin::resource.edit', ['resource' => trans('brand::brands.brands')]) }}</li>
@endcomponent
@section('content')
    <form method="POST" action="{{ route('admin.brands.update', $brand->id) }}" class="form-horizontal" id="brand-form">
        @csrf
        <input type="hidden" name="redirect_after_save" id="redirect_after_save" value="0">
        @method('PUT')
        <div class="box">
            <div class="box-body">
                <div class="form-group">
                    <div class="tab-pane fade in active" id="general">
                    <h4 class="tab-content-title">{{ trans('brand::brands.general') }}</h3>
                    </div>
                </div>
                <div class="form-group">
                    <label for="name" class="col-md-3 control-label">{{ trans('brand::brands.form.name') }}<span class="m-l-5 text-red">*</span></label>
                    <div class="col-md-9">
                        <input name="name" id="name" type="text" style="margin-bottom: 10px" class="form-control" value="{{ $brand->name }}">
                        @if ($errors->has('name'))
                            <div class="alert alert-danger">
                                {{ $errors->first('name') }}
                            </div>
                        @endif
                    </div>
                </div>

                <div class="form-group">
                    <label for="is_active" class="col-md-3 control-label">{{ trans('brand::brands.form.status') }}</label>
                    <div class="col-md-9">
                        <div class="checkbox">
                            <input type="hidden" value="0" name="is_active">
                            <input type="checkbox" value="1" name="is_active" id="is_active" {{ $brand->is_active ? 'checked' : '' }}>
                            <label for="is_active">{{ trans('brand::brands.form.enable') }}</label>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="form-group">
            <div class="col-md-10 col-md-offset-2">
                <button type="submit" class="btn btn-primary" data-loading>{{ trans('Save') }}</button>
            </div>
        </div>
    </form>
@endsection

@include('brand::admin.brands.partials.shortcuts')
@if (session()->has('exit_flash'))
    @push('notifications')
        <div class="alert alert-success alert-exit-flash fade in alert-dismissible clearfix">
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

@push('globals')
    @vite([
        'modules/Brand/Resources/assets/admin/sass/app.scss',
        'modules/Brand/Resources/assets/admin/js/create.js',
        'modules/Variation/Resources/assets/admin/sass/main.scss',
        // 'modules/Option/Resources/assets/admin/sass/main.scss',
        'modules/Media/Resources/assets/admin/sass/main.scss',
        'modules/Media/Resources/assets/admin/js/main.js',
    ])
@endpush
@push('scripts')
<script>
    $(document).ready(function () {
        $('.save-btn').click(function () {
            $('#redirect_after_save').val("0");
        });

        $('.save-exit-btn').click(function () {
            $('#redirect_after_save').val("1");
        });
    });
</script>
@endpush
