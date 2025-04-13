<?php

namespace Modules\Product\Http\ViewComposers;

use Illuminate\View\View;
use Modules\Brand\Entities\Brand;
use Modules\Category\Entities\Category;
use Modules\Variation\Entities\Variation;

class ProductEditPageComposer
{
    /**
     * Bind data to the view.
     *
     * @param View $view
     *
     * @return void
     */
    public function compose(View $view)
    {
        $brands = Brand::all();
        $categories = Category::all();
        $variations = Variation::with('values')->get();

        $view->with(compact('brands', 'categories', 'variations'));
    }
}
