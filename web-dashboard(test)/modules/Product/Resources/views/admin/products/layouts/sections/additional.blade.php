<template v-else-if="section === 'additional'">
    <div class="box-header">
        <h5>{{ trans('product::products.group.additional') }}</h5>

        <div class="drag-handle">
            <i class="fa fa-ellipsis-h" aria-hidden="true"></i>
            <i class="fa fa-ellipsis-h" aria-hidden="true"></i>
        </div>
    </div>

    <div class="box-body">
        <div class="form-group row">
            <label for="short-description" class="col-sm-12 control-label text-left">
                {{ trans('product::attributes.short_description') }}
            </label>

            <div class="col-sm-12">
                <textarea name="short_description" rows="6" cols="10" id="short-description" class="form-control">
                    {{ old('short_description ', $product->short_description ?? '') }}
                </textarea>

                @error('short_description')
                    <span class="help-block text-red">{{ $message }}</span>
                @enderror
            </div>
        </div>

        <div class="form-group row">
            <label for="new-from" class="col-sm-12 control-label text-left">
                {{ trans('product::attributes.new_from') }}
            </label>

            <div class="col-sm-12">
                <div class="input-group">
                    <span class="input-group-addon">
                        <i class="fa fa-calendar" aria-hidden="true"></i>
                    </span>

                    <flat-pickr
                        name="new_from"
                        id="new-from"
                        class="form-control"
                        :config="flatPickrConfig"
                        value="{{ old('new_from', $product->new_from ?? '') }}"
                    >
                    </flat-pickr>

                    <span
                        class="input-group-addon cursor-pointer"
                        v-if="form.new_from"
                        @click="removeDatePickerValue('new_from')"
                    >
                        <i class="fa fa-times" aria-hidden="true"></i>
                    </span>
                </div>

                <span class="help-block text-red" v-if="errors.has('new_from')" v-text="errors.get('new_from')"></span>
            </div>
        </div>

        <div class="form-group row">
            <label for="new-to" class="col-sm-12 control-label text-left">
                {{ trans('product::attributes.new_to') }}
            </label>

            <div class="col-sm-12">
                <div class="input-group">
                    <span class="input-group-addon">
                        <i class="fa fa-calendar" aria-hidden="true"></i>
                    </span>

                    <flat-pickr
                        name="new_to"
                        id="new-to"
                        class="form-control"
                        :config="flatPickrConfig"
                        value="{{ old('new_to', $product->new_to ?? '') }}"
                    >
                    </flat-pickr>

                    <span
                        class="input-group-addon cursor-pointer"
                        v-if="form.new_to"
                        @click="removeDatePickerValue('new_to')"
                    >
                        <i class="fa fa-times" aria-hidden="true"></i>
                    </span>
                </div>

                @error('new_to')
                    <span class="help-block text-red">{{ $message }}</span>
                @enderror
            </div>
        </div>
    </div>
</template>
