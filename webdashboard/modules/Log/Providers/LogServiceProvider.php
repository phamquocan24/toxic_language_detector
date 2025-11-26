<?php

namespace Modules\Log\Providers;

use Illuminate\Support\ServiceProvider;
use Illuminate\Support\Facades\Route;

class LogServiceProvider extends ServiceProvider
{
    /**
     * @var string $moduleName
     */
    protected $moduleName = 'Log';

    /**
     * @var string $moduleNameLower
     */
    protected $moduleNameLower = 'log';

    /**
     * Boot the application events.
     *
     * @return void
     */
    public function boot()
    {
        $this->loadViewsFrom(__DIR__ . '/../Resources/views', $this->moduleNameLower);
        $this->loadTranslationsFrom(__DIR__ . '/../Resources/lang', $this->moduleNameLower);
        $this->loadRoutes();
    }

    /**
     * Register the service provider.
     *
     * @return void
     */
    public function register()
    {
        // Không cần đăng ký thêm providers
    }

    /**
     * Register config.
     *
     * @return void
     */
    protected function registerConfig()
    {
        $this->publishes([
            module_path($this->moduleName, 'Config/config.php') => config_path($this->moduleNameLower . '.php'),
        ], 'config');
        $this->mergeConfigFrom(
            module_path($this->moduleName, 'Config/config.php'), $this->moduleNameLower
        );
    }

    /**
     * Register views.
     *
     * @return void
     */
    public function registerViews()
    {
        $viewPath = resource_path('views/modules/' . $this->moduleNameLower);

        $sourcePath = module_path($this->moduleName, 'Resources/views');

        $this->publishes([
            $sourcePath => $viewPath
        ], ['views', $this->moduleNameLower . '-module-views']);

        $this->loadViewsFrom(array_merge($this->getPublishableViewPaths(), [$sourcePath]), $this->moduleNameLower);
    }

    /**
     * Register translations.
     *
     * @return void
     */
    public function registerTranslations()
    {
        $this->loadTranslationsFrom(__DIR__ . '/../Resources/lang', $this->moduleNameLower);
    }

    /**
     * Get the services provided by the provider.
     *
     * @return array
     */
    public function provides()
    {
        return [];
    }

    private function getPublishableViewPaths(): array
    {
        $paths = [];
        foreach (\Config::get('view.paths') as $path) {
            if (is_dir($path . '/modules/' . $this->moduleNameLower)) {
                $paths[] = $path . '/modules/' . $this->moduleNameLower;
            }
        }
        return $paths;
    }

    /**
     * Load routes.
     */
    protected function loadRoutes()
    {
        Route::middleware('web')
            ->group(__DIR__ . '/../Routes/web.php');
    }
}
