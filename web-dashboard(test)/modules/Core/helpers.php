<?php

use App\Ecommerce;
use Illuminate\Support\Str;
use Illuminate\Support\Facades\Request;

if (! function_exists('module_path')) {
    function module_path($name, $path = '')
    {
        $module = app('modules')->find($name);

        return $module->getPath() . ($path ? DIRECTORY_SEPARATOR . $path : $path);
    }
}

if (! function_exists('camel_case')) {
    /**
     * Convert a value to camel case.
     *
     * @param string $value
     * @return string
     */
    function camel_case(string $value): string
    {
        return Str::camel($value);
    }
}

if (! function_exists('kebab_case')) {
    /**
     * Convert a string to kebab case.
     *
     * @param  string  $value
     * @return string
     */
    function kebab_case($value)
    {
        return Str::kebab($value);
    }
}

if (! function_exists('snake_case')) {
    /**
     * Convert a string to snake case.
     *
     * @param  string  $value
     * @param  string  $delimiter
     * @return string
     */
    function snake_case($value, $delimiter = '_')
    {
        return Str::snake($value, $delimiter);
    }
}

if (! function_exists('studly_case')) {
    /**
     * Convert a value to studly caps case.
     *
     * @param  string  $value
     * @return string
     */
    function studly_case($value)
    {
        return Str::studly($value);
    }
}

if (! function_exists('title_case')) {
    /**
     * Convert a value to title case.
     *
     * @param  string  $value
     * @return string
     */
    function title_case($value)
    {
        return Str::title($value);
    }
}

if (! function_exists('str_plural')) {
    /**
     * Get the plural form of an English word.
     *
     * @param  string  $value
     * @param  int  $count
     * @return string
     */
    function str_plural($value, $count = 2)
    {
        return Str::plural($value, $count);
    }
}

if (!function_exists('locale')) {
    /**
     * Get current locale.
     *
     * @return string
     */
    function locale()
    {
        return app()->getLocale();
    }
}

if (!function_exists('v')) {
    /**
     * Version a relative asset using the time its contents last changed.
     *
     * @param string $value
     *
     * @return string
     */
    function v($path)
    {
        if (config('app.env') === 'local') {
            $version = uniqid();
        } else {
            $version = Ecommerce::VERSION;
        }

        return "{$path}?v=" . $version;
    }
}

if (!function_exists('ecommerce_version')) {
    /**
     * Get the ecommerce version.
     *
     * @return string
     */
    function ecommerce_version()
    {
        return Ecommerce::VERSION;
    }
}

if (!function_exists('activeMenu')) {
    function activeMenu($url, $subUrl = null)
    {
        $segment2 = Request::segment(2);
        $segment3 = Request::segment(3);

        $class = ['main' => null, 'sub' => null];
        if ($segment2 == $url) {
            $class['main'] = 'active';
            if ($segment2 == 'setting' && $segment3 == $subUrl) {
                $class['sub'] = 'active';
            }
            if ($segment3 == $subUrl) {
                $class['sub'] = 'active';
            }
        }

        return $class;
    }
}
