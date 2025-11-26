<?php

namespace Modules\User\Providers;

use Illuminate\Support\ServiceProvider;
use Illuminate\Database\Eloquent\Factory;
use Illuminate\Support\Facades\Route;

class UserServiceProvider extends ServiceProvider
{
    /**
     * @var string $moduleName
     */
    protected $moduleName = 'User';

    /**
     * @var string $moduleNameLower
     */
    protected $moduleNameLower = 'user';

    /**
     * @var string $modulePath
     */
    protected $modulePath;

    /**
     * Create a new service provider instance.
     *
     * @param  \Illuminate\Contracts\Foundation\Application  $app
     * @return void
     */
    public function __construct($app)
    {
        parent::__construct($app);
        $this->modulePath = base_path('modules/' . $this->moduleName);
    }

    /**
     * Boot the application events.
     *
     * @return void
     */
    public function boot()
    {
        $this->registerTranslations();
        $this->registerConfig();
        $this->registerViews();
        $this->loadMigrationsFrom($this->modulePath . '/Database/Migrations');
        $this->mapRoutes();
    }

    /**
     * Register the service provider.
     *
     * @return void
     */
    public function register()
    {
        $this->app->register(RouteServiceProvider::class);
    }

    /**
     * Map all module routes.
     *
     * @return void
     */
    protected function mapRoutes()
    {
        $this->mapWebRoutes();
        $this->mapApiRoutes();
    }

    /**
     * Map web routes.
     *
     * @return void
     */
    protected function mapWebRoutes()
    {
        Route::middleware('web')
            ->group($this->modulePath . '/Routes/web.php');
    }

    /**
     * Map API routes.
     *
     * @return void
     */
    protected function mapApiRoutes()
    {
        Route::prefix('api')
            ->middleware('api')
            ->group($this->modulePath . '/Routes/api.php');
    }

    /**
     * Register config.
     *
     * @return void
     */
    protected function registerConfig()
    {
        $this->publishes([
            $this->modulePath . '/Config/config.php' => config_path($this->moduleNameLower . '.php'),
        ], 'config');
        $this->mergeConfigFrom(
            $this->modulePath . '/Config/config.php', $this->moduleNameLower
        );
    }

    /**
     * Register views.
     *
     * @return void
     */
    protected function registerViews()
    {
        $viewPath = resource_path('views/modules/' . $this->moduleNameLower);

        $sourcePath = $this->modulePath . '/Resources/views';

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
        $langPath = resource_path('lang/modules/' . $this->moduleNameLower);

        if (is_dir($langPath)) {
            $this->loadTranslationsFrom($langPath, $this->moduleNameLower);
        } else {
            $this->loadTranslationsFrom($this->modulePath . '/Resources/lang', $this->moduleNameLower);
        }
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
}
