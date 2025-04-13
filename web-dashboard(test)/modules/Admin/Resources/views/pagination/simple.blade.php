@if ($paginator->hasPages())
    <nav aria-label="pagination">
        <ul class="pagination">
            {{-- Previous Page Link --}}
            @if ($paginator->onFirstPage())
                <li class="dt-paging-button page-item disabled">
                    <a class="page-link first" data-dt-idx="first">«</a>
                </li>
                <li class="dt-paging-button page-item disabled">
                    <a class="page-link previous" data-dt-idx="previous" tabindex="-1">‹</a>
                </li>
            @else
                <li class="dt-paging-button page-item">
                    <a href="{{ $paginator->url(1) }}" class="page-link first" data-dt-idx="first">«</a>
                </li>
                <li class="dt-paging-button page-item">
                    <a href="{{ $paginator->previousPageUrl() }}" class="page-link previous" data-dt-idx="previous" tabindex="-1">‹</a>
                </li>
            @endif
            {{-- Pagination Elements --}}

            @foreach ($elements as $key => $element)
                @if (is_string($element))
                    <li class="dt-paging-button page-item disabled">
                        <a class="page-link ellipsis" data-dt-idx="ellipsis" tabindex="-1">…</a>
                    </li>
                @endif

                {{-- Array Of Links --}}
                @if (is_array($element))
                    @foreach ($element as $page => $url)
                        @if ($page == $paginator->currentPage())
                            <li class="dt-paging-button page-item active">
                                <a href="javascript:void(0)" class="page-link" data-dt-idx="{{ $page }}">{{ $page }}</a>
                            </li>
                        @else
                            <li class="dt-paging-button page-item">
                                <a href="{{ $url }}" class="page-link" data-dt-idx="{{ $page }}">{{ $page }}</a>
                            </li>
                        @endif
                    @endforeach
                @endif
            @endforeach

            {{-- Previous Page Link --}}
            @if ($paginator->hasMorePages())
                <li class="dt-paging-button page-item">
                    <a href="{{ $paginator->nextPageUrl() }}" class="page-link next" data-dt-idx="next">›</a>
                </li>
                <li class="dt-paging-button page-item">
                    <a href="{{ $paginator->url($paginator->lastPage()) }}" class="page-link last" data-dt-idx="last">»</a>
                </li>
            @else
                <li class="dt-paging-button page-item disabled">
                    <a class="page-link next" data-dt-idx="next">›</a>
                </li>
                <li class="dt-paging-button page-item disabled">
                    <a class="page-link last" data-dt-idx="last">»</a>
                </li>
            @endif
            {{-- Pagination Elements --}}
        </ul>
    </nav>
@endif
