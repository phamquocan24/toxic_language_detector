<?php

namespace App\Scaffold\Module\Traits;

trait StubHandlerTrait
{
    /**
     * Return the current module path.
     *
     * @param string $path
     *
     * @return string
     */
    protected function getModulesByPath(string $path = ''): string
    {
        return config('modules.paths.modules') . "/{$path}";
    }

    /**
     * Get stub path for the given stub file.
     *
     * @param string $filename
     *
     * @return string
     */
    protected function getStubPath($filename)
    {
        return base_path("app/Scaffold/Module/Stubs/{$filename}");
    }
}
