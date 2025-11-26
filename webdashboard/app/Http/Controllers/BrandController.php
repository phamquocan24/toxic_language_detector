<?php

namespace Modules\Brand\Http\Controllers\Admin;

use App\Models\Brand;
use Illuminate\Contracts\View\Factory;
use Illuminate\Contracts\View\View;
use Illuminate\Foundation\Application;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Modules\Admin\Traits\HasCrudActions;

class BrandController
{
    /**
     * Model for the resource.
     *
     * @var string
     */
//    protected string $model = Brand::class;

    /**
     * Label of the resource.
     *
     * @var string
     */
    protected string $label = 'brand::brands.brand';

    /**
     * View path of the resource.
     *
     * @var string
     */
    protected string $viewPath = 'brand::admin.brands';

    /**
     * Store a newly created resource in storage.
     *
     * @return Response
     */
    public function index(Request $request)
    {
        $brands = Brand::all();
        return view("{$this->viewPath}.index",compact('brands'));
    }

    /**
     * Show the form for creating a new resource.
     *
     * @return Response
     */
    public function create()
    {
        return view("{$this->viewPath}.create");
    }

    /**
     * Store a newly created resource in storage.
     *
     * @return Response|JsonResponse
     */
    public function store()
    {

    }


    /**
     * Show the form for editing the specified resource.
     *
     * @param int $id
     *
     * @return Factory|View|Application
     */
    public function edit($id)
    {
        return view("{$this->viewPath}.edit", []);
    }


    /**
     * Update the specified resource in storage.
     *
     * @param int $id
     */
    public function update($id)
    {

    }

    /**
     * Get request object
     *
     * @param string $action
     *
     * @return Request
     */
    protected function getRequest(string $action): Request
    {
        return match (true) {
            !isset($this->validation) => request(),
            isset($this->validation[$action]) => resolve($this->validation[$action]),
            default => resolve($this->validation),
        };
    }
}
