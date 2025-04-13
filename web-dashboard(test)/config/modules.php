<?php

$str = 'Commands';
return [
    'namespace' => 'Modules',
    'paths' => [
        'modules' => base_path('modules'),
        'assets' => public_path('modules'),
        'migration' => base_path('database/migrations'),
        'generator' => [
            'config' => ['path' => 'Config', 'generate' => true],
            'command' => ['path' => 'Console', 'generate' => false],
            'migration' => ['path' => 'Database/Migrations', 'generate' => true],
            'seeder' => ['path' => 'Database/Seeders', 'generate' => true],
            'factory' => ['path' => 'Database/factories', 'generate' => true],
            'model' => ['path' => 'Entities', 'generate' => true],
            'routes' => ['path' => 'Routes', 'generate' => true],
            'controller' => ['path' => 'Http/Controllers', 'generate' => true],
            'filter' => ['path' => 'Http/Middleware', 'generate' => true],
            'request' => ['path' => 'Http/Requests', 'generate' => true],
            'provider' => ['path' => 'Providers', 'generate' => true],
            'assets' => ['path' => 'Assets', 'generate' => false],
            'lang' => ['path' => 'Resources/lang', 'generate' => true],
            'views' => ['path' => 'Resources/views', 'generate' => true],
            'test' => ['path' => 'Tests/Unit', 'generate' => false],
            'test-feature' => ['path' => 'Tests/Feature', 'generate' => false],
            'repository' => ['path' => 'Repositories', 'generate' => false],
            'event' => ['path' => 'Events', 'generate' => false],
            'listener' => ['path' => 'Listeners', 'generate' => false],
            'policies' => ['path' => 'Policies', 'generate' => false],
            'rules' => ['path' => 'Rules', 'generate' => false],
            'jobs' => ['path' => 'Jobs', 'generate' => false],
            'emails' => ['path' => 'Emails', 'generate' => false],
            'notifications' => ['path' => 'Notifications', 'generate' => false],
            'resource' => ['path' => 'Transformers', 'generate' => false],
        ],
    ],
    'composer' => [
        'vendor' => 'ecommerce',
        'author' => [
            'name' => 'Envay Soft',
            'email' => 'envaysoft@gmail.com',
        ],
    ],
    'stubs' => [
        'enabled' => true,
        'path' => base_path() . '/Scaffold/Module/Stubs',
        'files' => [
            'routes/web' => 'Routes/web.php',
            'routes/api' => 'Routes/api.php',
            'controller' => 'Http/Controllers/$CONTROLLER_NAMESPACE$/$STUDLY_NAME$Controller.php',
//            'provider/service-provider' => 'Providers/$STUDLY_NAME$ServiceProvider.php',
            'views/index' => 'Resources/views/index.blade.php',
            'views/master' => 'Resources/views/layouts/master.blade.php',
            'scaffold/config' => 'Config/config.php',
            'composer' => 'composer.json',
            'assets/js/app' => 'Resources/assets/js/app.js',
            'assets/sass/app' => 'Resources/assets/sass/app.scss',
            'package' => 'package.json',
        ],
        'gitkeep' => false,
    ],
    'activators' => [
        'file' => [
            'class' => FileActivator::class,
            'statuses-file' => base_path('modules.json'),
            'cache-key' => 'activator.installed',
            'cache-lifetime' => 604800,
        ],
    ],

    'activator' => 'file',
];
