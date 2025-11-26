<?php

namespace Modules\Admin\Http\Controllers\Admin;

use Illuminate\Http\Response;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;
use Modules\Comment\Entities\Comment;
use Modules\User\Entities\User;
use Illuminate\Support\Facades\Log;
use App\Services\ToxicDetectionService;


class DashboardController
{
    /**
     * Toxic Detection Service instance
     *
     * @var ToxicDetectionService
     */
    protected $toxicService;

    /**
     * Constructor
     */
    public function __construct(ToxicDetectionService $toxicService)
    {
        $this->toxicService = $toxicService;
    }
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
     * Get dashboard statistics
     *
     * @return JsonResponse
     */
    public function getStats()
    {
        try {
            // Lấy tổng số comments từ database local
            $totalComments = Comment::count();
            $formattedTotalComments = $totalComments > 999 ? number_format($totalComments / 1000, 2) . 'K' : $totalComments;

            // Đếm số platforms
            $totalPlatforms = Comment::distinct('platform')->count('platform');

            // Đếm số feedbacks (comments đã được review)
            $totalFeedbacks = Comment::where('is_reviewed', true)->count();

            // Đếm số users
            $totalUsers = User::count();

            return response()->json([
                'success' => true,
                'data' => [
                    'totalSales' => $formattedTotalComments,
                    'totalOrders' => $totalPlatforms,
                    'totalProducts' => $totalFeedbacks,
                    'totalCustomers' => $totalUsers
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
     * Get comment labels distribution data
     *
     * @return JsonResponse
     */
    public function getProductPrices()
    {
        try {
            // Lấy từ API giống như CommentController
            $apiUrl = config('services.toxic_detection.url', 'http://localhost:7860');
            $response = Http::withHeaders($this->toxicService->getHeaders())
                ->timeout(10)
                ->get($apiUrl . '/admin/comments', [
                    'limit' => PHP_INT_MAX,
                    'skip' => 0
                ]);

            if ($response->successful()) {
                $commentsData = $response->json();
                if (is_array($commentsData)) {
                    $comments = $this->transformApiComments($commentsData);
                } else {
                    $comments = collect();
                }
            } else {
                // Fallback to local
                $comments = Comment::all();
            }

            // Đếm số lượng theo label
            $cleanCount = $comments->where('prediction', 0)->count();
            $offensiveCount = $comments->where('prediction', 1)->count();
            $hateCount = $comments->where('prediction', 2)->count();
            $spamCount = $comments->where('prediction', 3)->count();

            // Tạo mảng dữ liệu cho biểu đồ
            $chartData = [
                [
                    'name' => 'Clean',
                    'price' => $cleanCount,
                    'formatted_price' => $cleanCount . ' comments',
                    'price_range' => 'Normal comments'
                ],
                [
                    'name' => 'Spam',
                    'price' => $spamCount,
                    'formatted_price' => $spamCount . ' comments',
                    'price_range' => 'Spam/Advertisement'
                ],
                [
                    'name' => 'Offensive',
                    'price' => $offensiveCount,
                    'formatted_price' => $offensiveCount . ' comments',
                    'price_range' => 'Offensive language'
                ],
                [
                    'name' => 'Hate',
                    'price' => $hateCount,
                    'formatted_price' => $hateCount . ' comments',
                    'price_range' => 'Hate speech'
                ]
            ];

            return response()->json([
                'success' => true,
                'data' => $chartData
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Error fetching comment labels distribution: ' . $e->getMessage()
            ], 500);
        }
    }


    /**
     * Get latest comments data
     *
     * @return JsonResponse
     */
    public function getLatestProducts()
    {
        try {
            // Lấy từ API giống như CommentController
            $apiUrl = config('services.toxic_detection.url', 'http://localhost:7860');
            $response = Http::withHeaders($this->toxicService->getHeaders())
                ->timeout(10)
                ->get($apiUrl . '/admin/comments', [
                    'limit' => 5,
                    'skip' => 0,
                    'sort_by' => 'created_at',
                    'sort_order' => 'desc'
                ]);

            if ($response->successful()) {
                $commentsData = $response->json();
                if (is_array($commentsData)) {
                    $comments = $this->transformApiComments($commentsData);
                } else {
                    $comments = [];
                }
            } else {
                // Fallback to local
                $comments = Comment::select('id', 'content', 'platform', 'prediction', 'confidence', 'created_at')
                    ->orderBy('created_at', 'desc')
                    ->take(5)
                    ->get();
            }

            $mappedComments = $comments->map(function ($comment) {
                $predictionLabels = ['Clean', 'Offensive', 'Hate', 'Spam'];
                $predictionClasses = ['active', 'offensive', 'hate', 'spam'];

                $predictionText = $predictionLabels[$comment->prediction] ?? 'Unknown';
                $statusClass = $predictionClasses[$comment->prediction] ?? 'inactive';

                return [
                    'id' => $comment->id,
                    'name' => substr($comment->content, 0, 50) . (strlen($comment->content) > 50 ? '...' : ''),
                    'sku' => $comment->platform,
                    'price' => round($comment->confidence * 100, 2),
                    'formatted_price' => round($comment->confidence * 100, 2) . '%',
                    'status' => $predictionText,
                    'status_class' => $statusClass
                ];
            });

            return response()->json([
                'success' => true,
                'data' => $mappedComments
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Error fetching latest comments: ' . $e->getMessage()
            ], 500);
        }
    }


    /**
     * Get latest logs data from Python Backend API
     *
     * @return JsonResponse
     */
    public function getLatestBrands()
    {
        try {
            // Lấy logs từ Python Backend API sử dụng ToxicDetectionService
            $apiUrl = config('services.toxic_detection.url', 'http://localhost:7860');

            $response = Http::withHeaders($this->toxicService->getHeaders())
                ->timeout(10)
                ->get($apiUrl . '/admin/logs', [
                    'limit' => 5,
                    'skip' => 0
                ]);

            if (!$response->successful()) {
                Log::warning('Failed to fetch logs from API', [
                    'status' => $response->status(),
                    'url' => $apiUrl . '/admin/logs'
                ]);

                return response()->json([
                    'success' => false,
                    'message' => 'Unable to fetch logs from backend API'
                ], 500);
            }

            $logsData = $response->json();

            // Transform logs data để phù hợp với format frontend
            $logs = collect($logsData)->take(5)->map(function ($log) {
                // Determine status based on action keywords
                $statusClass = 'enabled';
                $action = $log['action'] ?? '';

                if (stripos($action, 'deleted') !== false || stripos($action, 'error') !== false) {
                    $statusClass = 'disabled';
                } elseif (stripos($action, 'created') !== false || stripos($action, 'login') !== false) {
                    $statusClass = 'enabled';
                }

                // Parse timestamp và format giống System Logs
                $timestamp = $log['timestamp'] ?? $log['created_at'] ?? now();
                try {
                    $logTime = \Carbon\Carbon::parse($timestamp);
                    $now = \Carbon\Carbon::now();
                    $diffInSeconds = $now->diffInSeconds($logTime);

                    if ($diffInSeconds < 60) {
                        $timeDisplay = $diffInSeconds . ' second' . ($diffInSeconds != 1 ? 's' : '') . ' ago';
                    } elseif ($diffInSeconds < 3600) {
                        $minutes = floor($diffInSeconds / 60);
                        $timeDisplay = $minutes . ' minute' . ($minutes != 1 ? 's' : '') . ' ago';
                    } elseif ($diffInSeconds < 86400) {
                        $hours = floor($diffInSeconds / 3600);
                        $timeDisplay = $hours . ' hour' . ($hours != 1 ? 's' : '') . ' ago';
                    } else {
                        $days = floor($diffInSeconds / 86400);
                        $timeDisplay = $days . ' day' . ($days != 1 ? 's' : '') . ' ago';
                    }
                } catch (\Exception $e) {
                    $timeDisplay = 'N/A';
                }

                $logId = isset($log['id']) ? (int) $log['id'] : 0;
                $userId = isset($log['user_id']) ? (int) $log['user_id'] : 0;

                return array_merge($log, [
                    'id' => $logId,
                    'log_id' => $logId,
                    'name' => substr($action, 0, 60) . (strlen($action) > 60 ? '...' : ''),
                    'action' => $action,
                    'products_count' => $userId,
                    'user_id' => $userId,
                    'status' => $timeDisplay,
                    'timestamp' => $timeDisplay,
                    'timestamp_raw' => $timestamp,
                    'status_class' => $statusClass
                ]);
            });

            return response()->json([
                'success' => true,
                'data' => $logs
            ]);
        } catch (\Exception $e) {
            Log::error('Error fetching latest logs from API', [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return response()->json([
                'success' => false,
                'message' => 'Error fetching latest logs: ' . $e->getMessage()
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
            $users = User::select('id', 'name', 'email', 'role_id', 'created_at')
                ->orderBy('created_at', 'desc')
                ->take(5)
                ->get()
                ->map(function ($user) {
                    $roles = [
                        1 => 'Administrator',
                        2 => 'User'
                    ];

                    // Xác định status_class dựa vào role
                    $statusClass = $user->role_id === 1 ? 'role-admin' : 'role-member';

                    // Lấy role_text từ mảng roles hoặc 'Unknown' nếu không tìm thấy
                    $statusText = $roles[$user->role_id] ?? 'Unknown';

                    // Tách first_name và last_name từ name
                    $nameParts = explode(' ', $user->name, 2);
                    $firstName = $nameParts[0] ?? '';
                    $lastName = $nameParts[1] ?? '';

                    return [
                        'id' => $user->id,
                        'first_name' => $firstName,
                        'last_name' => $lastName,
                        'full_name' => $user->name,
                        'email' => $user->email,
                        'role' => $user->role_id,
                        'role_text' => $statusText,
                        'status' => $statusText,
                        'status_class' => $statusClass,
                        'is_admin' => $user->role_id === 1
                    ];
                });

            return response()->json([
                'success' => true,
                'data' => $users
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Error fetching latest users:' . $e->getMessage()
            ], 500);
        }
    }

    // Thêm hàm helper từ CommentController
    private function transformApiComments(array $apiComments)
    {
        $comments = [];
        foreach ($apiComments as $apiComment) {
            $comment = new \Modules\Comment\Entities\Comment();

            // Map các trường từ API vào model
            if (isset($apiComment['id'])) $comment->id = $apiComment['id'];
            if (isset($apiComment['content'])) $comment->content = $apiComment['content'];
            if (isset($apiComment['platform'])) $comment->platform = $apiComment['platform'];

            // Xử lý prediction
            if (isset($apiComment['prediction'])) {
                $comment->prediction = is_numeric($apiComment['prediction'])
                    ? $apiComment['prediction']
                    : $this->getLabelId($apiComment['prediction']);
            }

            // Xử lý confidence
            if (isset($apiComment['confidence'])) {
                $comment->confidence = $apiComment['confidence'];
            }

            if (isset($apiComment['created_at'])) {
                $comment->created_at = \Carbon\Carbon::parse($apiComment['created_at']);
            }

            $comments[] = $comment;
        }
        return collect($comments);
    }

    // Thêm hàm getLabelId
    private function getLabelId(string $label): int
    {
        return match ($label) {
            'toxicity', 'toxic' => 1,
            'severe_toxicity' => 2,
            'obscene' => 1,
            'identity_attack', 'identity_hate' => 2,
            'insult' => 1,
            'threat' => 2,
            'sexual_explicit' => 3,
            'clean' => 0,
            'offensive' => 1,
            'hate' => 2,
            'spam' => 3,
            default => 0,
        };
    }
}

