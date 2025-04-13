<template v-if="section === 'media'">
    <div class="box-header">
        <h5>{{ trans('product::products.group.media') }}</h5>

        <div class="drag-handle">
            <i class="fa fa-ellipsis-h" aria-hidden="true"></i>
            <i class="fa fa-ellipsis-h" aria-hidden="true"></i>
        </div>
    </div>

    <div class="box-body">
        <div class="row">
            <div class="col-md-12">
                <draggable
                    animation="200"
                    class="product-media-grid"
                    force-fallback="true"
                    handle=".handle"
                    :move="preventLastSlideDrag"
                    :list="form.media"
                >
                    <div class="media-grid-item handle" v-for="(media, index) in form.media" :key="index">
                        <div class="image-holder">
                            <img :src="media.path" alt="product media">

                            <button type="button" class="btn remove-image" @click="removeMedia(index)">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
                                    <path d="M6.00098 17.9995L17.9999 6.00053" stroke="#292D32" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                    <path d="M17.9999 17.9995L6.00098 6.00055" stroke="#292D32" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                </svg>
                            </button>
                        </div>
                    </div>

                    <div class="media-grid-item media-picker disabled" @click="addMedia">
                        <div class="image-holder">
                            <img src="{{ asset('build/assets/placeholder_image.png') }}" class="placeholder-image" alt="Placeholder image">
                        </div>
                    </div>
                </draggable>
            </div>
        </div>
    </div>
</template>
