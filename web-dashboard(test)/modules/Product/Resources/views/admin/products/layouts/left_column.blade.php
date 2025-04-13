@include('product::admin.products.layouts.sections.general')
<div class="box" v-for="(section, sectionIndex) in formLeftSections" :data-id="section" :key="sectionIndex">
    @include('product::admin.products.layouts.sections.variations')
    @include('product::admin.products.layouts.sections.variants')
</div>
