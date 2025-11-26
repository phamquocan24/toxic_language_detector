<?php

namespace Modules\Admin\UI\Facades;

use Illuminate\Support\Facades\Facade;
use Modules\Admin\UI\Form as FormBuilder;

class Form extends Facade
{
    /**
     * Get the registered name of the component.
     *
     * @return string
     */
    protected static function getFacadeAccessor()
    {
        return FormBuilder::class;
    }
}
