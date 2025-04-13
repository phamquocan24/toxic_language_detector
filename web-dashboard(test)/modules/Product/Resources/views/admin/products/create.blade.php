@extends('admin::layout')

@component('admin::components.page.header')
    @slot('title', trans('admin::resource.create', ['resource' => trans('product::products.product')]))

    <li><a href="{{ route('admin.products.index') }}">{{ trans('product::products.products') }}</a></li>
    <li class="active">{{ trans('admin::resource.create', ['resource' => trans('product::products.product')]) }}</li>
@endcomponent

@section('content')
    <div id="app">
        <form class="product-form" method="POST" action="{{ route('admin.products.store') }}">
            @csrf
            <input type="hidden" name="redirect_after_save" id="redirect_after_save" value="0">
            <div class="row">
                <div class="product-form-left-column col-lg-8 col-md-12">
                    @include('product::admin.products.layouts.left_column')
                </div>

                <div class="product-form-right-column col-lg-4 col-md-12">
                    @include('product::admin.products.layouts.right_column', ['product' => $product])
            </div>

            <div class="page-form-footer">
                <button type="submit" class="btn btn-default save-btn">
                    Save
                </button>
                <button type="submit" class="btn btn-primary save-exit-btn">
                    Save &amp; Exit
                </button>
            </div>
        </form>
    </div>
@endsection

@include('product::admin.products.partials.shortcuts')

@push('globals')
    @vite([
        'modules/Product/Resources/assets/admin/sass/main.scss',
        'modules/Product/Resources/assets/admin/sass/options.scss',
        'modules/Product/Resources/assets/admin/js/create.js',
        'modules/Variation/Resources/assets/admin/sass/main.scss',
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
