<div class="box">
    <div class="box-header">
        <h5>{{ trans('product::products.group.general') }}</h5>
    </div>

    <div class="box-body">
        <div class="form-group row">
            <label for="name" class="col-sm-12 control-label text-left">
                {{ trans('product::attributes.name') }}
                <span class="text-red">*</span>
            </label>

            <div class="col-sm-12">
                <input
                    type="text"
                    name="name"
                    id="name"
                    class="form-control"
                    value="{{ old('name', $product->name ?? '') }}"
                >
                @error('name')
                    <span class="help-block text-red">{{ $message }}</span>
                @enderror
            </div>
        </div>

        <div class="form-group row">
            <label for="description" class="col-sm-12 control-label text-left">
                {{ trans('product::attributes.description') }}
            </label>

            <div class="col-sm-12">
                <textarea
                    name="description"
                    id="description"
                    class="form-control wysiwyg"
                >
                    {{ old('description', $product->description ?? '') }}
                </textarea>
                @error('description')
                    <span class="help-block text-red">{{ $message }}</span>
                @enderror
            </div>
        </div>

        <div class="form-group row">
            <label for="brand-id" class="col-sm-12 control-label text-left">
                {{ trans('product::attributes.brand_id') }}
                <span class="text-red">*</span>
            </label>
            <div class="col-sm-6">
                <select name="brand_id" id="brand-id" class="form-control custom-select-black">
                    <option value="">Please Select</option>
                        @foreach($brands as $brand)
                            <option value="{{ $brand->id }}" {{ old('brand_id', $product->brand_id ?? '') == $brand->id ? 'selected' : '' }}>
                                {{ $brand->name }}
                            </option>
                        @endforeach
                </select>
                @error('brand_id')
                    <span class="help-block text-red">{{ $message }}</span>
                @enderror
            </div>
        </div>

        <div class="form-group row">
            <label for="categories" class="col-sm-12 control-label text-left">
                {{ trans('product::attributes.categories') }}
                <span class="text-red">*</span>
            </label>

            <div class="col-sm-6">
                <select name="category_id" id="category-id" class="form-control custom-select-black">
                    <option value="">Please Select</option>
                        @foreach($categories as $category)
                            <option value="{{ $category->id }}"
                                {{ in_array($category->id, $product->categories->pluck('id')->toArray() ?? []) ? 'selected' : '' }}>
                                {{ $category->name }}
                            </option>
                        @endforeach
                </select>
                </select>
                @error('category_id')
                    <span class="help-block text-red">{{ $message }}</span>
                @enderror
            </div>
        </div>

        <div class="form-group row">
            <label for="is-active" class="col-sm-12 control-label text-left">
                {{ trans('product::attributes.is_active') }}
                <span class="text-red">*</span>
            </label>

            <div class="col-sm-9">
                <div class="switch">
                    <input type="checkbox" name="is_active" id="is-active" {{ old('is_active', $product->is_active ?? false) ? 'checked' : '' }}>

                    <label for="is-active">
                        {{ trans('product::products.form.enable_the_product') }}
                    </label>
                </div>
            </div>
        </div>
    </div>
</div>
