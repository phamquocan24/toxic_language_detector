<div class="table-responsive">
    <div class="dt-container form-inline dt-bootstrap dt-empty-footer">
        <div class="row dt-layout-row">
            <div class="dt-layout-cell dt-layout-start col-sm-6">
                <div class="dt-length">
                    @if($showDelete)
                    <button type="button" class="btn btn-default btn-delete" id="delete-records">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="16" viewBox="0 0 14 16" fill="none">
                            <path
                                d="M12 3.6665L11.5868 10.3499C11.4813 12.0575 11.4285 12.9113 11.0005 13.5251C10.7889 13.8286 10.5164 14.0847 10.2005 14.2772C9.56141 14.6665 8.70599 14.6665 6.99516 14.6665C5.28208 14.6665 4.42554 14.6665 3.78604 14.2765C3.46987 14.0836 3.19733 13.827 2.98579 13.5231C2.55792 12.9082 2.5063 12.0532 2.40307 10.3433L2 3.6665"
                                stroke="#141B34" stroke-width="1.5" stroke-linecap="round"></path>
                            <path d="M5 7.82324H9" stroke="#141B34" stroke-width="1.5" stroke-linecap="round"></path>
                            <path d="M6 10.436H8" stroke="#141B34" stroke-width="1.5" stroke-linecap="round"></path>
                            <path
                                d="M1 3.66659H13M9.70369 3.66659L9.24858 2.72774C8.94626 2.10409 8.7951 1.79227 8.53435 1.59779C8.47651 1.55465 8.41527 1.51628 8.35122 1.48305C8.06248 1.33325 7.71595 1.33325 7.02289 1.33325C6.31243 1.33325 5.95719 1.33325 5.66366 1.48933C5.59861 1.52392 5.53653 1.56385 5.47807 1.6087C5.2143 1.81105 5.06696 2.13429 4.77228 2.78076L4.36849 3.66659"
                                stroke="#020010" stroke-width="1.5" stroke-linecap="round"></path>
                        </svg>
                        <span>Delete</span>
                    </button>
                    @endif
                </div>
            </div>
            <div class="dt-layout-cell dt-layout-end col-sm-6">
                <div class="dt-search">
                    <label for="dt-search-0">Search:</label>
                    <input
                        type="search"
                        id="dt-search"
                        class="form-control input-sm"
                        placeholder="Search here...">
                </div>
            </div>
        </div>
        <div class="row dt-layout-row dt-layout-table">
            <div class="dt-layout-cell col-12 dt-layout-full col-sm-12">
                {{-- Loading --}}
                <div id="DataTables_Table_0_processing" class="dt-processing panel panel-default" role="status" style="display: none;">
                    <div>
                        <div></div>
                        <div></div>
                        <div></div>
                        <div></div>
                    </div>
                </div>

                <table class="table table-striped table-hover dataTable">
                    <thead>{{ $thead }}</thead>

                    <tbody>{{ $tbody }}</tbody>

                    @isset($tfoot)
                        <tfoot>{{ $tfoot }}</tfoot>
                    @endisset
                </table>
            </div>
        </div>
        <div class="row dt-layout-row">
            <div class="dt-layout-cell dt-layout-start col-sm-6">
                <label class="dt-info" aria-live="polite" id="DataTables_Table_0_info" role="status">
                    @if(isset($tResult))
                        {{ $tResult }}
                    @endif
                </label>
            </div>
            <div class="dt-layout-cell dt-layout-end col-sm-6">
                <div class="dt-paging">
                    @if(isset($tPagination))
                        {{ $tPagination }}
                    @endif
                </div>
            </div>
        </div>
    </div>
</div>
