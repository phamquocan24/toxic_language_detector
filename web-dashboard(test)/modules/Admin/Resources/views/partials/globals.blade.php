<script>
    window.Ecommerce = {
        version: '{{ ecommerce_version() }}',
        csrfToken: '{{ csrf_token() }}',
        baseUrl: '{{ url('/') }}',
        langs: {},
        data: {},
        errors: {},
        selectize: [],
    };

    Ecommerce.langs['admin::admin.buttons.delete'] = '{{ trans('admin::admin.buttons.delete') }}';
    Ecommerce.langs['media::media.file_manager.title'] = '{{ trans('media::media.file_manager.title') }}';
    Ecommerce.langs['admin::admin.table.search_here'] = '{{ trans('admin::admin.table.search_here') }}';
    Ecommerce.langs['admin::admin.table.showing_start_end_total_entries'] = '{{ trans('admin::admin.table.showing_start_end_total_entries') }}';
    Ecommerce.langs['admin::admin.table.showing_empty_entries'] = '{{ trans('admin::admin.table.showing_empty_entries') }}';
    Ecommerce.langs['admin::admin.table.show_menu_entries'] = '{{ trans('admin::admin.table.show_menu_entries') }}';
    Ecommerce.langs['admin::admin.table.filtered_from_max_total_entries'] = '{{ trans('admin::admin.table.filtered_from_max_total_entries') }}';
    Ecommerce.langs['admin::admin.table.no_data_available_table'] = '{{ trans('admin::admin.table.no_data_available_table') }}';
    Ecommerce.langs['admin::admin.table.loading'] = '{{ trans('admin::admin.table.loading') }}';
    Ecommerce.langs['admin::admin.table.no_matching_records_found'] = '{{ trans('admin::admin.table.no_matching_records_found') }}';
</script>

@stack('globals')

@routes
