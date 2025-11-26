<?php

namespace Modules\Admin\Providers;

use Illuminate\Foundation\AliasLoader;
use Illuminate\Support\ServiceProvider;
use Modules\Admin\UI\Facades\Form;

class AdminServiceProvider extends ServiceProvider
{
    /**
     * Bootstrap any application services.
     *
     * @return void
     */
    public function boot()
    {

    }

    /**
     * Register the service provider.
     *
     * @return void
     */
    public function register()
    {
        AliasLoader::getInstance()->alias('Form', Form::class);
    }
}
