<?php

namespace Modules\Admin\Http\Controllers\Admin;

use Illuminate\Http\Response;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\DB;
use Modules\Product\Entities\Product;
use Modules\Brand\Entities\Brand;
use Modules\User\Entities\User;
use Illuminate\Support\Facades\Log;


class DashboardController
{
    /**
     * Display the dashboard with its widgets.
     *
     * @return Response
     */
    public function index()
    {
        return response()->view('admin::dashboard.index');
    }
     /**
     * Get product price comparison data
     *
     * @return JsonResponse
     */
    public function getStats()
    {
        try {
            // Lấy tổng doanh số
            $totalSales = Product::sum('price');
            $formattedTotalSales = number_format($totalSales / 1000, 2) . 'K';

            // Đếm số đơn hàng
            $totalOrders = Brand::count() ?? 0;

            // Đếm số sản phẩm
            $totalProducts = Product::count() ?? 0;

            // Đếm số khách hàng
            $totalCustomers = User::where('role', 2)->count() ?? 0; // role 2 là Member

            return response()->json([
                'success' => true,
                'data' => [
                    'totalSales' => $formattedTotalSales,
                    'totalOrders' => $totalOrders,
                    'totalProducts' => $totalProducts,
                    'totalCustomers' => $totalCustomers
                ]
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Error fetching dashboard stats: ' . $e->getMessage()
            ], 500);
        }
    }
    /**
     * Get product price comparison data
     *
     * @return JsonResponse
     */
    public function getProductPrices()
    {
        try {
            // Định nghĩa các mức giá
            $priceRanges = [
                'Normal' => [0, 100],
                'Middle' => [100, 500],
                'Premium' => [500, 1000],
                'Luxury' => [1000, PHP_INT_MAX]
            ];

            // Khởi tạo mảng đếm số lượng sản phẩm cho mỗi mức giá
            $productCounts = [
                'Normal' => 0,
                'Middle' => 0,
                'Premium' => 0,
                'Luxury' => 0
            ];

            // Lấy tất cả sản phẩm với giá
            $products = Product::select('id', 'name', 'price')->get();

            // Phân loại sản phẩm vào các mức giá
            foreach ($products as $product) {
                foreach ($priceRanges as $category => [$min, $max]) {
                    if ($product->price >= $min && $product->price < $max) {
                        $productCounts[$category]++;
                        break;
                    }
                }
            }

            // Tạo mảng dữ liệu cho biểu đồ
            $chartData = [];
            foreach ($priceRanges as $category => [$min, $max]) {
                $chartData[] = [
                    'name' => $category,
                    'price' => $productCounts[$category], // Số lượng sản phẩm trong mỗi mức giá
                    'formatted_price' => $productCounts[$category] . ' products', // Hiển thị số lượng
                    'min_price' => number_format($min, 2).'đ',
                    'max_price' => $max === PHP_INT_MAX ? '1,000+đ' : 'đ' . number_format($max, 2),
                    'price_range' => number_format($min, 2).'đ' . ' - ' . ($max === PHP_INT_MAX ? '1,000+đ' :number_format($max, 2).'đ')
                ];
            }

            return response()->json([
                'success' => true,
                'data' => $chartData
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Error fetching product price categories: ' . $e->getMessage()
            ], 500);
        }
    }


    /**
     * Get latest products data
     *
     * @return JsonResponse
     */
    public function getLatestProducts()
    {
        try {
            $products = Product::select('id', 'brand_id', 'name', 'sku', 'price', 'special_price', 'special_price_type', 'special_price_start', 'special_price_end', 'selling_price', 'manage_stock', 'qty', 'in_stock', 'is_active')
                ->orderBy('created_at', 'desc')
                ->take(5)
                ->get()
                ->map(function ($product) {
                    $statusClass = $product->is_active ? 'active' : 'inactive';
                    $statusText = $product->is_active ? 'Active' : 'Inactive';

                    return [
                        'id' => $product->id,
                        'brand_id' => $product->brand_id,
                        'name' => $product->name,
                        'sku' => $product->sku,
                        'price' => $product->price,
                        'formatted_price' => number_format($product->price, 2).'đ',
                        'special_price' => $product->special_price,
                        'special_price_type' => $product->special_price_type,
                        'special_price_start' => $product->special_price_start,
                        'special_price_end' => $product->special_price_end,
                        'selling_price' => $product->selling_price,
                        'manage_stock' => $product->manage_stock,
                        'qty' => $product->qty,
                        'in_stock' => $product->in_stock,
                        'status' => $statusText,
                        'status_class' => $statusClass
                    ];
                });

            return response()->json([
                'success' => true,
                'data' => $products
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Error fetching latest products: ' . $e->getMessage()
            ], 500);
        }
    }


    /**
     * Get latest brands data
     *
     * @return JsonResponse
     */
    public function getLatestBrands()
    {
        try {
            $brands = Brand::select('id', 'name', 'is_active')
                ->withCount('products')
                ->orderBy('created_at', 'desc')
                ->take(5)
                ->get()
                ->map(function ($brand) {
                    $statusClass = $brand->is_active ? 'enabled' : 'disabled';
                    $statusText = $brand->is_active ? 'Enabled' : 'Disabled';

                    return [
                        'id' => $brand->id,
                        'name' => $brand->name,
                        'products_count' => $brand->products_count,
                        'status' => $statusText,
                        'status_class' => $statusClass
                    ];
                });

            return response()->json([
                'success' => true,
                'data' => $brands
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Error fetching latest brands: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get latest users data
     *
     * @return JsonResponse
     */
    public function getLatestUsers()
    {
        try {
            $users = User::select('id', 'first_name', 'last_name', 'email', 'role', 'last_login')
                ->orderBy('created_at', 'desc')
                ->take(5)
                ->get()
                ->map(function ($user) {
                    $roles = [
                        1 => 'Administrator',
                        2 => 'Member'
                    ];

                    // Xác định status_class dựa vào role
                    $statusClass = $user->role === 1 ? 'role-admin' : 'role-member';

                    // Lấy role_text từ mảng roles hoặc 'Unknown' nếu không tìm thấy
                    $statusText = $roles[$user->role] ?? 'Unknown';

                    return [
                        'id' => $user->id,
                        'first_name' => $user->first_name,
                        'last_name' => $user->last_name,
                        'full_name' => trim($user->first_name . ' ' . $user->last_name),
                        'email' => $user->email,
                        'role' => $user->role,
                        'role_text' => $statusText,
                        'status' => $statusText,
                        'status_class' => $statusClass,
                        'is_admin' => $user->role === 1,
                        'last_login' => $user->last_login ? $user->last_login->toDateTimeString() : null,
                        'last_login_diff' => $user->last_login ? $user->last_login->diffForHumans() : null
                    ];
                });

            return response()->json([
                'success' => true,
                'data' => $users
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Error fetching latest users: ' . $e->getMessage()
            ], 500);
        }
    }
}
