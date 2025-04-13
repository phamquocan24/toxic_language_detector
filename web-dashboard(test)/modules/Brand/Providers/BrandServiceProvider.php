<?php

namespace Modules\Brand\Providers;

use Illuminate\Support\Facades\View;
use Illuminate\Support\ServiceProvider;
use Modules\Brand\Http\ViewComposers\BrandEditPageComposer;
use Modules\Brand\Http\ViewComposers\BrandCreatePageComposer;

class BrandServiceProvider extends ServiceProvider
{
    /**
     * Bootstrap any application services.
     *
     * @return void
     */
    public function boot(): void
    {
        View::composer('brand::admin.brands.create', BrandCreatePageComposer::class);
        View::composer('brand::admin.brands.edit', BrandEditPageComposer::class);

    }


    /**
     * Register the service provider.
     *
     * @return void
     */
    public function register(): void
    {

    }
}
