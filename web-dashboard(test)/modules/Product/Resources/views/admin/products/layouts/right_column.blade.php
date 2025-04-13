<div class="box" v-for="(section, index) in formRightSections" :data-id="section" :key="index">
    @include('product::admin.products.layouts.sections.pricing', ['product' => $product])
    @include('product::admin.products.layouts.sections.inventory')
    @include('product::admin.products.layouts.sections.media')
    @include('product::admin.products.layouts.sections.additional', ['product' => $product])
</div>
