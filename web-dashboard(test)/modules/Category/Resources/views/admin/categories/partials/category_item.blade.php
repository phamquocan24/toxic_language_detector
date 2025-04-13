<div class="category-item">
    <div class="category">
        <span>{{ $category->name }}</span>
        @if ($category->children->isNotEmpty())
            {{-- <button class="btn btn-sm btn-info toggle-children">+</button> --}}
        @endif
    </div>

    @if ($category->children->isNotEmpty())
        <div class="children" style="display: none;">
            @foreach ($category->children as $child)
                @include('category::admin.categories.partials.category_item', ['category' => $child])
            @endforeach
        </div>
    @endif
</div>
