<?php

namespace Modules\Brand\Http\ViewComposers;

use Illuminate\View\View;

class BrandEditPageComposer
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
        $view->with([]);
    }
}
