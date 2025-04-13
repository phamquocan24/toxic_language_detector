<template v-else-if="section === 'inventory'">
    <div class="box-header">
        <h5>{{ trans('product::products.group.inventory') }}</h5>

        <div class="drag-handle">
            <i class="fa fa-ellipsis-h" aria-hidden="true"></i>
            <i class="fa fa-ellipsis-h" aria-hidden="true"></i>
        </div>
    </div>

    <div class="box-body">
        <div v-if="hasAnyVariant" class="alert alert-info">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 2C6.49 2 2 6.49 2 12C2 17.51 6.49 22 12 22C17.51 22 22 17.51 22 12C22 6.49 17.51 2 12 2ZM11.25 8C11.25 7.59 11.59 7.25 12 7.25C12.41 7.25 12.75 7.59 12.75 8V13C12.75 13.41 12.41 13.75 12 13.75C11.59 13.75 11.25 13.41 11.25 13V8ZM12.92 16.38C12.87 16.51 12.8 16.61 12.71 16.71C12.61 16.8 12.5 16.87 12.38 16.92C12.26 16.97 12.13 17 12 17C11.87 17 11.74 16.97 11.62 16.92C11.5 16.87 11.39 16.8 11.29 16.71C11.2 16.61 11.13 16.51 11.08 16.38C11.03 16.26 11 16.13 11 16C11 15.87 11.03 15.74 11.08 15.62C11.13 15.5 11.2 15.39 11.29 15.29C11.39 15.2 11.5 15.13 11.62 15.08C11.86 14.98 12.14 14.98 12.38 15.08C12.5 15.13 12.61 15.2 12.71 15.29C12.8 15.39 12.87 15.5 12.92 15.62C12.97 15.74 13 15.87 13 16C13 16.13 12.97 16.26 12.92 16.38Z" fill="#555555"/>
            </svg>

            <span>
                {{ trans('product::products.variants.has_product_variant') }}
            </span>
        </div>

        <template v-else>
            <div class="form-group row">
                <label for="sku" class="col-sm-12 control-label text-left">
                    {{ trans('product::attributes.sku') }}
                </label>

                <div class="col-sm-12">
                    <input
                        type="text"
                        name="sku"
                        id="sku"
                        class="form-control"
                        value="{{ old('sku', $product->sku ?? '') }}"
                    >
                    @error('sku')
                        <span class="help-block text-red">{{ $message }}</span>
                    @enderror
                </div>
            </div>

            <div class="form-group row">
                <label for="manage_stock" class="col-sm-12 control-label text-left">
                    {{ trans('product::attributes.manage_stock') }}

                </label>

                <div class="col-sm-12">
                    <select name="manage_stock" id="manage-stock" class="form-control custom-select-black">
                        <option value="0" {{ old('manage_stock', $product->manage_stock ?? '') == 0 ? 'selected' : '' }}>
                            {{ trans('product::products.form.manage_stock_states.0') }}
                        </option>

                        <option value="1" {{ old('manage_stock', $product->manage_stock ?? '') == 1 ? 'selected' : '' }}>
                            {{ trans('product::products.form.manage_stock_states.1') }}
                        </option>
                    </select>
                    <span class="help-block text-red"></span>
                </div>
            </div>

            <div class="form-group row" id="qty-group" style="display: {{ old('manage_stock', $product->manage_stock ?? '') == 1 ? 'block' : 'none' }};">
                <label for="qty" class="col-sm-12 control-label text-left">
                    {{ trans('product::attributes.qty') }}
                    <span class="text-red">*</span>
                </label>

                <div class="col-sm-12">
                    <input
                        type="number"
                        name="qty"
                        step="1"
                        id="qty"
                        class="form-control"
                        onwheel="this.blur();"
                        value="{{ old('qty', $product->qty ?? '') }}"

                    >
                    @error('qty')
                        <span class="help-block text-red">{{ $message }}</span>
                    @enderror
                </div>
            </div>

            <div class="form-group row">
                <label for="in_stock" class="col-sm-12 control-label text-left">
                    {{  trans('product::attributes.in_stock') }}

                </label>

                <div class="col-sm-12">
                    <select name="in_stock" id="in-stock" class="form-control custom-select-black">
                        <option value="0" {{ old('in_stock', $product->in_stock ?? '') == 0 ? 'selected' : '' }}>
                            {{ trans('product::products.form.stock_availability_states.0') }}
                        </option>

                        <option value="1" {{ old('in_stock', $product->in_stock ?? '') == 1 ? 'selected' : '' }}>
                            {{ trans('product::products.form.stock_availability_states.1') }}
                        </option>
                    </select>
                    <span class="help-block text-red"></span>
                </div>
            </div>

        </template>
    </div>
</template>

<script>
    document.addEventListener("DOMContentLoaded", function() {
        const manageStock = document.getElementById("manage-stock");
        const qtyGroup = document.getElementById("qty-group");

        manageStock.addEventListener("change", function() {
            if (this.value == "1") {
                qtyGroup.style.display = "block";
            } else {
                qtyGroup.style.display = "none";
            }
        });
    });
</script>
