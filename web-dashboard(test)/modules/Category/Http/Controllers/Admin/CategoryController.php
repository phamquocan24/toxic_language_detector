<?php

namespace Modules\Category\Http\Controllers\Admin;

use App\Models\Category;
use Illuminate\Contracts\View\Factory;
use Illuminate\Contracts\View\View;
use Illuminate\Foundation\Application;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Modules\Admin\Traits\HasCrudActions;
use Modules\Category\Entities\Category as EntitiesCategory;
use Carbon\Carbon;
use Modules\Category\Http\Request\CategoryRequest;

class CategoryController
{
    /**
     * Model for the resource.
     *
     * @var string
     */
//    protected string $model = Category::class;

    /**
     * Label of the resource.
     *
     * @var string
     */
    protected string $label = 'category::categories.category';

    /**
     * View path of the resource.
     *
     * @var string
     */
    protected string $viewPath = 'category::admin.categories';

    /**
     * Store a newly created resource in storage.
     *
     * @return Response
     */
    // public function index(Request $request)
    // {
    //     $categories = Category::all();
    //     return view("{$this->viewPath}.index",compact('categories'));
    // }
    // public function index(Request $request)
    // {
    //     $categories= EntitiesCategory::all();
    //     // Trả dữ liệu về view
    //     return view("{$this->viewPath}.index", compact('categories'));
    // }
    // public function index()
    // {
    //     $categories = EntitiesCategory::all();
    //     $tree = $this->buildTree($categories);

    //     return view('category::admin.categories.index', compact('tree'));
    // }

    // private function buildTree($categories, $parentId = null)
    // {
    //     $tree = [];
    //     foreach ($categories as $category) {
    //         if ($category->parent_id == $parentId) {
    //             $category->children = $this->buildTree($categories, $category->id);
    //             $tree[] = $category;
    //         }
    //     }
    //     return $tree;
    // }

    public function index()
    {
        // Lấy tất cả các danh mục và tổ chức thành cấu trúc cây
        $categories = EntitiesCategory::all();
        $categoriesTree = $this->buildCategoryTree($categories);

                // Trả các danh mục đã tổ chức vào view
        // return view('category::index', compact('categoriesTree'));
        return view('category::admin.categories.index', compact('categoriesTree'));

    }
    private function buildCategoryTree($categories, $parentId = null)
    {
                // Lọc các danh mục con có parent_id tương ứng
        $branch = $categories->filter(function ($category) use ($parentId) {
            return $category->parent_id == $parentId;
        });

               // Với mỗi danh mục con, đệ quy tìm các danh mục con của nó
        foreach ($branch as $category) {
            $category->children = $this->buildCategoryTree($categories, $category->id);
        }

        return $branch;
    }


    /**
     * Show the form for creating a new resource.
     *
     * @return Response
     */
    public function create()
    {
        // return view("{$this->viewPath}.create");
        $category = EntitiesCategory::findOrFail($id);
        return response()->json($category);
    }

    /**
     * Store a newly created resource in storage.
     *
     * @return Response|JsonResponse
     */
    public function store(CategoryRequest $request)
    {
        try {
            $category = new EntitiesCategory();
            $category->fill($request->validated());
            $category->is_active = $request->has('is_active') && $request->is_active == 1 ? 1 : 0;
            $category->save();

            return redirect()->route('admin.categories.index')->with('success', 'Danh mục đã được thêm thành công!');
        } catch (\Exception $e) {
            return redirect()->back()->with('error', 'Đã xảy ra lỗi khi thêm danh mục: ' . $e->getMessage());
        }
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

    }


    /**
     * Update the specified resource in storage.
     *
     * @param int $id
     */
    public function update(Request $request, $id)
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

    public function bulkDelete(Request $request)
    {

    }


}
