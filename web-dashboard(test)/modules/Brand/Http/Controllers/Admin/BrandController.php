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
use Modules\Brand\Entities\Brand as EntitiesBrand;
use Carbon\Carbon;
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
    // public function index(Request $request)
    // {
    //     $brands = Brand::all();
    //     return view("{$this->viewPath}.index",compact('brands'));
    // }
    public function index(Request $request)
    {
        // Danh sách cột có thể sắp xếp
        $sortableColumns = ['id', 'is_active', 'created_at'];

        // Lấy giá trị cột cần sắp xếp từ request, mặc định là 'id'
        $sortBy = $request->get('sort_by', 'id');

        // Kiểm tra nếu cột không hợp lệ, đặt lại thành 'id'
        if (!in_array($sortBy, $sortableColumns)) {
            $sortBy = 'id';
        }

        // Lấy thứ tự sắp xếp, mặc định là 'asc'
        $sortOrder = $request->get('sort', 'asc');
        if (!in_array(strtolower($sortOrder), ['asc', 'desc'])) {
            $sortOrder = 'asc';
        }

        $perPage = $request->input('per_page', 10); // Giới hạn số bản ghi trên mỗi trang
        if ($sortBy === 'is_active') {
            $brands = EntitiesBrand::orderBy('is_active', 'desc') // Nhóm Active trước
                ->orderBy('id', $sortOrder) // Sau đó sắp xếp theo 'id' hoặc tiêu chí khác
                ->paginate($perPage);
        } else {
            $brands = EntitiesBrand::orderBy($sortBy, $sortOrder)->paginate($perPage);
        }
        // Truy vấn các bản ghi và sắp xếp theo cột yêu cầu
        $brands = EntitiesBrand::orderBy($sortBy, $sortOrder)->paginate($perPage);

        $now = Carbon::now();
        foreach ($brands as $brand) {
            $days_diff = $now->diffInDays($brand->created_at);
            $brand->formatted_created_at = ($days_diff < 30) ?
                "<span class='text-success'>{$days_diff} days ago</span>" :
                "<span class='text-primary'>" . floor($days_diff / 30) . " months ago</span>";
        }
        // Tổng số thương hiệu
        $totalBrands = EntitiesBrand::count();


        // Trả dữ liệu về view
        return view("{$this->viewPath}.index", compact('brands', 'sortBy', 'sortOrder', 'perPage', 'totalBrands'));
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
    public function store(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:191',
        ], [
            'name.required' => 'Vui lòng nhập hợp lệ !',
            'name.max' => 'Vui lòng nhập hợp lệ !',
        ]);
        $brand = new EntitiesBrand();
        $brand->name = $validated['name'];
        $brand->is_active = $request->has('is_active') && $request->is_active == 1 ? 1 : 0;
        $brand ->save();
        return redirect()->route('admin.brands.index');

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
        $brand = EntitiesBrand::find($id);
        return view("{$this->viewPath}.edit", compact('brand'));
    }


    /**
     * Update the specified resource in storage.
     *
     * @param int $id
     */
    public function update(Request $request, $id)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:191',
        ], [
            'name.required' => 'Vui lòng nhập hợp lệ !',
            'name.max' => 'Vui lòng nhập hợp lệ !',
        ]);
        $brand = EntitiesBrand::find($id);
        if($brand) {
            $brand->name = $request->name;
            $brand->is_active = $request->has('is_active') && $request->is_active == 1 ? 1 : 0;
            $brand ->save();
        }
        return redirect()->route('admin.brands.index');
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
        // Chuyển đổi JSON thành mảng
        $ids = json_decode($request->input('ids'), true);

        // Kiểm tra nếu không có mục nào được chọn
        if (!is_array($ids) || count($ids) === 0) {
            return redirect()->route('admin.brands.index');
        }

        try {
            // Thực hiện xóa
            EntitiesBrand::whereIn('id', $ids)->delete();
            return redirect()->route('admin.brands.index');
        } catch (\Exception $e) {
            // Xử lý lỗi
            return redirect()->route('admin.brands.index');
        }
    }


}
