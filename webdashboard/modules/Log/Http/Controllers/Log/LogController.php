<?php

namespace Modules\Log\Http\Controllers\Log;

use App\Http\Controllers\Controller;
use Carbon\Carbon;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Exception;
use Illuminate\Support\Facades\Log;
use Illuminate\Pagination\LengthAwarePaginator;

class LogController extends Controller
{
    /**
     * URL cơ sở API
     */
    protected $apiBaseUrl;

    /**
     * Timeout cho HTTP requests (giây)
     */
    protected $timeout;

    /**
     * Số bản ghi mặc định trên mỗi trang
     */
    protected $perPage = 10;

    /**
     * ToxicDetectionService
     */
    protected $toxicService;

    /**
     * Constructor
     */
    public function __construct(\App\Services\ToxicDetectionService $toxicService)
    {
        // Lưu service để sử dụng sau này
        $this->toxicService = $toxicService;

        // Thiết lập URL API từ file cấu hình, sử dụng localhost:7860 theo API docs
        $this->apiBaseUrl = config('log.api_url', env('LOG_API_URL', 'http://localhost:7860'));

        // Loại bỏ dấu gạch chéo ở cuối URL nếu có
        $this->apiBaseUrl = rtrim($this->apiBaseUrl, '/');

        // Timeout ngắn để tránh chờ đợi quá lâu
        $this->timeout = config('log.api_timeout', env('LOG_API_TIMEOUT', 10));
    }

    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        // Lấy tham số tìm kiếm và phân trang từ request
        $page = $request->input('page', 1);
        $perPage = $request->input('per_page', $this->perPage);
        $user_id = $request->input('user_id');
        $action = $request->input('action');
        $start_date = $request->input('start_date');
        $end_date = $request->input('end_date');
        $sortBy = $request->input('sort_by', 'timestamp');
        $sortOrder = $request->input('sort_order', 'desc');

        // Khởi tạo biến mặc định
        $logs = [];
        $totalLogs = 0;
        $errorMessage = null;
        $apiEnabled = config('log.api_enabled', env('LOG_API_ENABLED', true));

        // Chỉ gọi API nếu được bật trong cấu hình
        if ($apiEnabled) {
            try {
                // Thử lấy tất cả dữ liệu từ API
                $allLogs = $this->getLogsFromApi(0, PHP_INT_MAX, $user_id, $action, $start_date, $end_date);
                $totalLogs = count($allLogs);

                // Sắp xếp dữ liệu theo trường được chọn
                if ($sortBy && $sortOrder) {
                    usort($allLogs, function($a, $b) use ($sortBy, $sortOrder) {
                        if (!isset($a[$sortBy]) || !isset($b[$sortBy])) {
                            return 0;
                        }

                        $comparison = $a[$sortBy] <=> $b[$sortBy];
                        return $sortOrder === 'desc' ? -$comparison : $comparison;
                    });
                }

                // Lọc và phân trang thủ công
                $offset = ($page - 1) * $perPage;
                $currentPageLogs = array_slice($allLogs, $offset, $perPage);

                // Tạo đối tượng phân trang với URL chính xác
                $logs = new LengthAwarePaginator(
                    $currentPageLogs,
                    $totalLogs,
                    $perPage,
                    $page,
                    [
                        'path' => $request->url(),
                        'query' => $request->query()
                    ]
                );

                // Xóa session lỗi nếu thành công
                if (session()->has('log_api_error')) {
                    session()->forget('log_api_error');
                }
            } catch (Exception $e) {
                // Nếu không kết nối được với API, ghi log và hiển thị thông báo
                $errorMessage = $e->getMessage();
                Log::warning('Không thể kết nối đến Log API: ' . $errorMessage);

                // Lưu lỗi vào session để tránh hiển thị quá nhiều lần
                session()->put('log_api_error', $errorMessage);

                // Tạo phân trang trống
                $logs = new LengthAwarePaginator(
                    [],
                    0,
                    $perPage,
                    $page,
                    [
                        'path' => $request->url(),
                        'query' => $request->query()
                    ]
                );

                // Thêm thông báo flash để người dùng biết
                session()->flash('error', 'Không thể kết nối đến máy chủ nhật ký. Vui lòng kiểm tra cấu hình hoặc thử lại sau.');
            }
        } else {
            // API bị tắt, sử dụng phân trang trống
            $logs = new LengthAwarePaginator(
                [],
                0,
                $perPage,
                $page,
                [
                    'path' => $request->url(),
                    'query' => $request->query()
                ]
            );

            // Thông báo API đang tắt
            session()->flash('warning', 'API Log đang bị tắt trong cấu hình.');
        }

        // Truyền dữ liệu vào view
        return view('log::admin.logs.index', [
            'logs' => $logs,
            'totalLogs' => $totalLogs,
            'perPage' => $perPage,
            'currentPage' => $page,
            'showDelete' => false, // Không cho phép xóa log
            'errorMessage' => $errorMessage,
            'apiEnabled' => $apiEnabled,
            'sortBy' => $sortBy,
            'sortOrder' => $sortOrder,
            // Truyền các tham số tìm kiếm hiện tại để duy trì trạng thái form
            'filters' => [
                'user_id' => $user_id,
                'action' => $action,
                'start_date' => $start_date,
                'end_date' => $end_date
            ]
        ]);
    }

    /**
     * Lấy dữ liệu log từ API
     */
    private function getLogsFromApi($skip = 0, $limit = PHP_INT_MAX, $user_id = null, $action = null, $start_date = null, $end_date = null)
    {
        // Kiểm tra URL API
        if (empty($this->apiBaseUrl)) {
            throw new Exception('URL API không được cấu hình. Vui lòng kiểm tra cấu hình LOG_API_URL.');
        }

        // Xây dựng tham số query
        $params = [
            'skip' => $skip,
            'limit' => $limit
        ];

        // Thêm các tham số tìm kiếm nếu có
        if ($user_id) {
            $params['user_id'] = $user_id;
        }

        if ($action) {
            $params['action'] = $action;
        }

        if ($start_date) {
            $params['start_date'] = Carbon::parse($start_date)->startOfDay()->toIso8601String();
        }

        if ($end_date) {
            $params['end_date'] = Carbon::parse($end_date)->endOfDay()->toIso8601String();
        }

        // Sử dụng endpoint chính xác
        $endpoint = '/admin/logs';
        $fullUrl = $this->apiBaseUrl . $endpoint;

        try {
            // Sử dụng ToxicDetectionService để lấy headers xác thực
            $headers = $this->toxicService->getHeaders();

            // Chuẩn bị HTTP client với timeout và retry
            $httpClient = Http::timeout($this->timeout)
                ->acceptJson()
                ->withHeaders(array_merge([
                    'Accept' => 'application/json'
                ], $headers))
                ->retry(1, 500, function ($exception, $request) {
                    return $exception instanceof \Illuminate\Http\Client\ConnectionException
                        || ($exception instanceof \Illuminate\Http\Client\RequestException && $exception->response->status() >= 500);
                });

            // Log thông tin trước khi gọi API
            Log::info('Gọi Log API để lấy tất cả dữ liệu', [
                'url' => $fullUrl,
                'params' => $params,
                'timeout' => $this->timeout
            ]);

            // Gọi API
            $response = $httpClient->get($fullUrl, $params);

            // Kiểm tra phản hồi
            if ($response->successful()) {
                $data = $response->json();

                // Log để debug
                Log::debug('API trả về dữ liệu thành công', [
                    'count' => is_array($data) ? count($data) : 'không phải mảng',
                    'type' => gettype($data)
                ]);

                return is_array($data) ? $data : [];
            } else {
                // Phản hồi không thành công, log lỗi và ném ngoại lệ
                $errorMessage = $response->status() . ': ' . $response->body();

                // Log chi tiết lỗi để debug
                Log::error('Lỗi khi gọi Log API: ' . $response->json('message', 'Lỗi không xác định'), [
                    'api_url' => $fullUrl,
                    'params' => $params,
                    'status' => $response->status(),
                    'response' => $response->body(),
                    'headers_sent' => $headers
                ]);

                throw new Exception($response->json('message', 'Lỗi khi kết nối đến API Log'));
            }
        } catch (Exception $e) {
            // Ghi log lỗi chi tiết hơn và ném ngoại lệ để xử lý ở trên
            Log::error('Lỗi khi gọi Log API: ' . $e->getMessage(), [
                'api_url' => $fullUrl,
                'params' => $params,
                'timeout' => $this->timeout
            ]);
            throw $e;
        }
    }
}
