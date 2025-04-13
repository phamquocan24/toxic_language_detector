<?php

namespace Modules\Admin\Providers;

use Illuminate\Support\ServiceProvider;

class ZiggyServiceProvider extends ServiceProvider
{
    public function boot(): void
    {
        $this->registerInAdminPanelState();
        $this->blacklistAdminRoutesOnFrontend();
    }

    private function registerInAdminPanelState(): void
    {
        if ($this->app->runningInConsole()) {
            $this->app['inAdminPanel'] = false;
            return;
        }

        $this->app['inAdminPanel'] = $this->app['request']->segment(1) === 'admin';
    }

    private function blacklistAdminRoutesOnFrontend(): void
    {
        if (!$this->app['inAdminPanel']) {
            $this->app['config']->set('ziggy.except',
                array_merge(
                    $this->app['config']->get('ziggy.except', []),
                    [
                        'admin.*',
                    ]
                )
            );
        }
    }
}
