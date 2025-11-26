<?php

namespace Modules\Comment\Http\Controllers\Comment;

use Modules\Comment\Entities\Comment;
use App\Services\ToxicDetectionService;
use Illuminate\Contracts\View\Factory;
use Illuminate\Contracts\View\View;
use Illuminate\Foundation\Application;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\Log;
use Carbon\Carbon;
use Illuminate\Support\Facades\Http;

class CommentController
{
    /**
     * Label of the resource.
     *
     * @var string
     */
    protected string $label = 'comment::comments.comment';

    /**
     * View path of the resource.
     *
     * @var string
     */
    protected string $viewPath = 'comment::';

    /**
     * Toxic detection service.
     *
     * @var ToxicDetectionService
     */
    protected ToxicDetectionService $toxicService;

    /**
     * Constructor
     */
    public function __construct(ToxicDetectionService $toxicService)
    {
        $this->toxicService = $toxicService;
    }

    /**
     * Display a listing of comments.
     *
     * @param Request $request
     * @return View
     */
    public function index(Request $request)
    {
        // Danh sách cột có thể sắp xếp
        $sortableColumns = ['id', 'content', 'platform', 'prediction', 'confidence', 'is_reviewed', 'created_at'];

        // Lấy giá trị cột cần sắp xếp từ request, mặc định là 'id'
        $sortBy = $request->get('sort_by', 'id');

        // Kiểm tra nếu cột không hợp lệ, đặt lại thành 'id'
        if (!in_array($sortBy, $sortableColumns)) {
            $sortBy = 'id';
        }

        // Lấy thứ tự sắp xếp, mặc định là 'desc'
        $sortOrder = $request->get('sort', 'desc');

        $perPage = $request->input('per_page', 10); // Giới hạn số bản ghi trên mỗi trang, đã giảm xuống 5 để tạo nhiều trang hơn
        $currentPage = $request->input('page', 1);

        // Convert currentPage sang int để tránh lỗi
        $currentPage = (int)$currentPage;
        if ($currentPage < 1) $currentPage = 1;

        try {
            // Thử lấy tất cả dữ liệu từ toxic detection API (không giới hạn số lượng)
            $apiUrl = config('services.toxic_detection.url');
            $apiEndpoint = '/admin/comments';
            $queryParams = [
                'limit' => PHP_INT_MAX, // Lấy tất cả bản ghi
                'skip' => 0,
            ];

            // Thêm các filter nếu có
            if ($request->has('prediction')) {
                $queryParams['prediction'] = $request->prediction;
            }

            if ($request->has('platform')) {
                $queryParams['platform'] = $request->platform;
            }

            if ($request->has('is_reviewed')) {
                $queryParams['is_reviewed'] = $request->is_reviewed;
            }

            // Gọi API để lấy tất cả dữ liệu
            $response = Http::withHeaders($this->toxicService->getHeaders())
                ->get($apiUrl . $apiEndpoint, $queryParams);

            Log::info('API response', [
                'status' => $response->status(),
                'url' => $apiUrl . $apiEndpoint,
                'params' => $queryParams,
                'headers' => $this->toxicService->getHeaders(),
                'response_body_length' => strlen($response->body()),
            ]);

            if ($response->successful()) {
                $apiData = $response->json();

                // Kiểm tra và xử lý các cấu trúc phản hồi khác nhau
                $allCommentsData = [];

                // Kiểm tra cấu trúc phản hồi
                if (isset($apiData['data']) && is_array($apiData['data'])) {
                    // Cấu trúc chuẩn: { data: [...], total: X }
                    $allCommentsData = $apiData['data'];
                    $totalComments = count($allCommentsData);
                } elseif (isset($apiData['comments']) && is_array($apiData['comments'])) {
                    // Cấu trúc thay thế: { comments: [...], count: X }
                    $allCommentsData = $apiData['comments'];
                    $totalComments = count($allCommentsData);
                } elseif (is_array($apiData)) {
                    // Cấu trúc đơn giản: mảng trực tiếp các comment - [...]
                    $allCommentsData = $apiData;
                    $totalComments = count($allCommentsData);
                } else {
                    // Nếu không phải định dạng mảng, sử dụng mảng rỗng
                    $allCommentsData = [];
                    $totalComments = 0;
                }

                // Chuyển đổi tất cả dữ liệu thành đối tượng Comment
                $allTransformedComments = $this->transformApiComments($allCommentsData);

                // Sắp xếp dữ liệu theo trường được chọn
                usort($allTransformedComments, function($a, $b) use ($sortBy, $sortOrder) {
                    if ($sortBy === 'id') {
                        $comparison = $a->id <=> $b->id;
                    } elseif ($sortBy === 'content') {
                        $comparison = $a->content <=> $b->content;
                    } elseif ($sortBy === 'platform') {
                        $comparison = $a->platform <=> $b->platform;
                    } elseif ($sortBy === 'prediction') {
                        $comparison = $a->prediction <=> $b->prediction;
                    } elseif ($sortBy === 'confidence') {
                        $comparison = $a->confidence <=> $b->confidence;
                    } elseif ($sortBy === 'is_reviewed') {
                        $comparison = $a->is_reviewed <=> $b->is_reviewed;
                    } elseif ($sortBy === 'created_at') {
                        $comparison = $a->created_at <=> $b->created_at;
                    } else {
                        $comparison = 0;
                    }

                    return $sortOrder === 'desc' ? -$comparison : $comparison;
                });

                // Lọc và phân trang thủ công
                $offset = ($currentPage - 1) * $perPage;
                $currentPageComments = array_slice($allTransformedComments, $offset, $perPage);

                // Tạo đối tượng phân trang với URL chính xác
                $comments = new \Illuminate\Pagination\LengthAwarePaginator(
                    $currentPageComments,
                    $totalComments,
                    $perPage,
                    $currentPage,
                    [
                        'path' => $request->url(),
                        'query' => $request->query()
                    ]
                );

                Log::info('Phân trang client-side hoàn tất', [
                    'total_records' => $totalComments,
                    'page' => $currentPage,
                    'per_page' => $perPage,
                    'current_page_count' => count($currentPageComments)
                ]);
            } else {
                // Nếu API không hoạt động, sử dụng dữ liệu local
                Log::warning('Không thể lấy dữ liệu từ API, sử dụng dữ liệu local', [
                    'status' => $response->status(),
                    'error' => $response->body()
                ]);
                $comments = $this->getLocalComments($request, $perPage, $sortBy, $sortOrder);
                $totalComments = Comment::count();
            }
        } catch (\Exception $e) {
            // Xử lý lỗi khi gọi API
            Log::error('Lỗi khi gọi API lấy comments', [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            // Fallback sử dụng dữ liệu local
            $comments = $this->getLocalComments($request, $perPage, $sortBy, $sortOrder);
            $totalComments = Comment::count();
        }

        $now = Carbon::now();
        foreach ($comments as $comment) {
            if (isset($comment->created_at) && $comment->created_at instanceof \Carbon\Carbon) {
                $days_diff = $now->diffInDays($comment->created_at);
                $comment->formatted_created_at = ($days_diff < 30) ?
                    "<span class='text-success'>{$days_diff} days ago</span>" :
                    "<span class='text-primary'>" . floor($days_diff / 30) . " months ago</span>";
            } else {
                $comment->formatted_created_at = "<span class='text-muted'>N/A</span>";
            }

            // Format updated_at nếu có
            if (isset($comment->updated_at) && $comment->updated_at instanceof \Carbon\Carbon) {
                $days_diff = $now->diffInDays($comment->updated_at);
                $comment->formatted_updated_at = ($days_diff < 30) ?
                    "<span class='text-success'>{$days_diff} days ago</span>" :
                    "<span class='text-primary'>" . floor($days_diff / 30) . " months ago</span>";
            } else {
                $comment->formatted_updated_at = "<span class='text-muted'>N/A</span>";
            }

            // Đảm bảo có prediction_text
            if (!isset($comment->prediction_text) && isset($comment->prediction)) {
                $labels = ['clean', 'offensive', 'hate', 'spam'];
                $comment->prediction_text = isset($labels[$comment->prediction]) ? $labels[$comment->prediction] : 'unknown';
            }
        }

        $showDelete = true;

        // Trả dữ liệu về view
        return view("{$this->viewPath}admin.comments.index", compact('comments', 'sortBy', 'sortOrder', 'perPage', 'totalComments', 'showDelete'));
    }

    /**
     * Lấy comments từ database local
     *
     * @param Request $request
     * @param int $perPage
     * @param string $sortBy
     * @param string $sortOrder
     * @return \Illuminate\Pagination\LengthAwarePaginator
     */
    private function getLocalComments(Request $request, $perPage, $sortBy, $sortOrder)
    {
        $query = Comment::query();

        if ($request->has('prediction')) {
            $query->where('prediction', $request->prediction);
        }

        if ($request->has('platform')) {
            $query->where('platform', $request->platform);
        }

        if ($request->has('is_reviewed')) {
            $query->where('is_reviewed', $request->is_reviewed);
        }

        return $query->orderBy($sortBy, $sortOrder)->paginate($perPage);
    }

    /**
     * Chuyển đổi dữ liệu API thành đối tượng Comment
     *
     * @param array $apiComments
     * @return array
     */
    private function transformApiComments(array $apiComments)
    {
        $comments = [];
        foreach ($apiComments as $apiComment) {
            $comment = new Comment();

            // Map các trường từ API vào model
            if (isset($apiComment['id'])) $comment->id = $apiComment['id'];
            if (isset($apiComment['content'])) $comment->content = $apiComment['content'];
            if (isset($apiComment['platform'])) $comment->platform = $apiComment['platform'];
            if (isset($apiComment['source_user_name'])) $comment->source_user_name = $apiComment['source_user_name'];
            if (isset($apiComment['source_url'])) $comment->source_url = $apiComment['source_url'];

            // Xử lý trường prediction
            if (isset($apiComment['prediction'])) {
                $comment->prediction = is_numeric($apiComment['prediction'])
                    ? $apiComment['prediction']
                    : $this->getLabelId($apiComment['prediction']);
            } elseif (isset($apiComment['label'])) {
                $comment->prediction = is_numeric($apiComment['label'])
                    ? $apiComment['label']
                    : $this->getLabelId($apiComment['label']);
            }

            // Xử lý trường confidence
            if (isset($apiComment['confidence'])) {
                $comment->confidence = $apiComment['confidence'];
            } elseif (isset($apiComment['score']) && is_numeric($apiComment['score'])) {
                $comment->confidence = $apiComment['score'];
            } elseif (isset($apiComment['scores']) && is_array($apiComment['scores'])) {
                // Nếu có scores, lấy giá trị cao nhất làm confidence
                $scores = $apiComment['scores'];
                if (!empty($scores)) {
                    $comment->confidence = max($scores);
                }
            }

            if (isset($apiComment['is_reviewed'])) $comment->is_reviewed = $apiComment['is_reviewed'];
            if (isset($apiComment['user_id'])) $comment->user_id = $apiComment['user_id'];

            // Xử lý timestamps
            if (isset($apiComment['created_at'])) {
                try {
                    $comment->created_at = $apiComment['created_at'] instanceof \DateTime
                        ? Carbon::instance($apiComment['created_at'])
                        : new Carbon($apiComment['created_at']);
                } catch (\Exception $e) {
                    Log::warning('Không thể parse created_at', [
                        'value' => $apiComment['created_at'],
                        'error' => $e->getMessage()
                    ]);
                }
            }

            if (isset($apiComment['updated_at'])) {
                try {
                    $comment->updated_at = $apiComment['updated_at'] instanceof \DateTime
                        ? Carbon::instance($apiComment['updated_at'])
                        : new Carbon($apiComment['updated_at']);
                } catch (\Exception $e) {
                    Log::warning('Không thể parse updated_at', [
                        'value' => $apiComment['updated_at'],
                        'error' => $e->getMessage()
                    ]);
                }
            }

            // Thêm các trường khác
            if (isset($apiComment['probabilities']) && is_array($apiComment['probabilities'])) {
                $comment->setProbabilities($apiComment['probabilities']);
            } elseif (isset($apiComment['scores']) && is_array($apiComment['scores'])) {
                $comment->setProbabilities($apiComment['scores']);
            }

            if (isset($apiComment['vector_representation'])) {
                $comment->setVector($apiComment['vector_representation']);
            } elseif (isset($apiComment['vector'])) {
                $comment->setVector($apiComment['vector']);
            }

            $comments[] = $comment;
        }

        return $comments;
    }

    /**
     * Show the form for creating a new resource.
     *
     * @return Response
     */
    public function create()
    {
        return view("{$this->viewPath}admin.comments.create");
    }

    /**
     * Store a newly created resource in storage.
     *
     * @param Request $request
     * @return Response|JsonResponse
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'content' => 'required|string',
            'platform' => 'required|string|max:50',
            'source_user_name' => 'nullable|string|max:255',
            'source_url' => 'nullable|url',
        ], [
            'content.required' => 'Nội dung bình luận là bắt buộc!',
            'platform.required' => 'Nền tảng là bắt buộc!',
            'source_url.url' => 'URL nguồn phải là định dạng URL hợp lệ!',
        ]);

        // Phân tích nội dung qua API
        $analysisResult = $this->toxicService->detectSingle($validated['content'], $validated['platform']);

        if (isset($analysisResult['error'])) {
            Log::error('Error when calling toxic detection API', [
                'error' => $analysisResult['message'] ?? 'Unknown error',
                'status' => $analysisResult['status'] ?? null,
                'content' => $validated['content'],
                'api_url' => config('services.toxic_detection.url'),
            ]);
            return redirect()->back()->withInput()->withErrors(['api_error' => $analysisResult['message'] ?? 'Error connecting to analysis API']);
        }

        // Tạo comment mới
        $comment = new Comment();
        $comment->content = $validated['content'];
        $comment->platform = $validated['platform'];
        $comment->source_user_name = $validated['source_user_name'] ?? null;
        $comment->source_url = $validated['source_url'] ?? null;
        $comment->user_id = auth()->id();

        // Xác định label dựa trên score cao nhất
        $scores = $analysisResult['scores'] ?? [];
        if (!empty($scores)) {
            $maxCategory = array_search(max($scores), $scores);
            $comment->prediction = $this->getLabelId($maxCategory);
            $comment->confidence = $scores[$maxCategory] ?? 0.5;
        } else {
            $comment->prediction = 0; // Default to clean
            $comment->confidence = 0.5;
        }

        // Lưu các thông tin phụ
        $probabilities = $analysisResult['scores'] ?? [];
        $comment->setProbabilities($probabilities);

        // Lưu vector nếu có
        if (isset($analysisResult['vector'])) {
            $comment->setVector($analysisResult['vector']);
        } else {
            // Đặt vector rỗng nếu API không trả về
            $comment->setVector([]);
        }

        $comment->save();

        return redirect()->route('admin.comments.index')->with('success', 'Bình luận đã được tạo và phân tích thành công!');
    }

    /**
     * Show the form for editing the specified resource.
     *
     * @param int $id
     * @return Factory|View|Application
     */
    public function edit($id)
    {
        try {
            // Thử tìm comment trong database local
            $comment = Comment::find($id);

            // Nếu không tìm thấy trong database local, lấy từ API
            if (!$comment) {
                // Gọi API để lấy thông tin comment
                $apiUrl = config('services.toxic_detection.url');
                $response = Http::withHeaders($this->toxicService->getHeaders())
                    ->get("{$apiUrl}/admin/comments/{$id}");

                Log::info('API response for edit', [
                    'comment_id' => $id,
                    'status' => $response->status(),
                    'response_body_length' => strlen($response->body()),
                ]);

                if ($response->successful()) {
                    $commentData = $response->json();

                    // Tạo đối tượng Comment từ dữ liệu API
                    $transformedComments = $this->transformApiComments([$commentData]);
                    if (!empty($transformedComments)) {
                        $comment = $transformedComments[0];
                    } else {
                        // Không thể tạo comment từ API
                        return back()->with('error', 'Không thể tìm thấy bình luận với ID: ' . $id);
                    }
                } else {
                    // API không thành công
                    return back()->with('error', 'Không thể lấy thông tin bình luận từ API');
                }
            }

            return view("{$this->viewPath}admin.comments.edit", compact('comment'));
        } catch (\Exception $e) {
            Log::error('Error getting comment for edit', [
                'comment_id' => $id,
                'error' => $e->getMessage()
            ]);

            return back()->with('error', 'Có lỗi xảy ra: ' . $e->getMessage());
        }
    }

    /**
     * Update the specified resource in storage.
     *
     * @param Request $request
     * @param int $id
     * @return Response
     */
    public function update(Request $request, $id)
    {
        $validated = $request->validate([
            'content' => 'required|string',
            'platform' => 'required|string|max:50',
            'source_user_name' => 'nullable|string|max:255',
            'source_url' => 'nullable|url',
            're_analyze' => 'nullable|boolean',
        ]);

        $comment = Comment::findOrFail($id);
        $contentChanged = $comment->content !== $validated['content'];

        // Cập nhật thông tin cơ bản
        $comment->content = $validated['content'];
        $comment->platform = $validated['platform'];
        $comment->source_user_name = $validated['source_user_name'] ?? $comment->source_user_name;
        $comment->source_url = $validated['source_url'] ?? $comment->source_url;

        // Phân tích lại nội dung nếu có thay đổi hoặc được yêu cầu
        if ($contentChanged || ($request->has('re_analyze') && $request->re_analyze)) {
            $analysisResult = $this->toxicService->detectSingle($validated['content'], $validated['platform']);

            if (!isset($analysisResult['error'])) {
                // Xác định label dựa trên score cao nhất
                $scores = $analysisResult['scores'] ?? [];
                if (!empty($scores)) {
                    $maxCategory = array_search(max($scores), $scores);
                    $comment->prediction = $this->getLabelId($maxCategory);
                    $comment->confidence = $scores[$maxCategory] ?? 0.5;
                } else {
                    $comment->prediction = 0; // Default to clean
                    $comment->confidence = 0.5;
                }

                // Lưu các thông tin phụ
                $probabilities = $analysisResult['scores'] ?? [];
                $comment->setProbabilities($probabilities);

                // Lưu vector nếu có
                if (isset($analysisResult['vector'])) {
                    $comment->setVector($analysisResult['vector']);
                }
            } else {
                Log::error('Error analyzing comment', ['error' => $analysisResult['message'], 'comment_id' => $id]);
            }
        }

        // Cập nhật trạng thái đánh giá nếu có
        if ($request->has('is_reviewed')) {
            $comment->is_reviewed = (bool) $request->is_reviewed;

            if ($comment->is_reviewed) {
                $comment->review_result = $request->review_result;
                $comment->review_notes = $request->review_notes;
                $comment->review_timestamp = Carbon::now();
            }
        }

        $comment->save();

        return redirect()->route('admin.comments.index')->with('success', 'Bình luận đã được cập nhật thành công!');
    }

    /**
     * Mark a comment as reviewed.
     *
     * @param Request $request
     * @param int $id
     * @return JsonResponse
     */
    public function markReviewed(Request $request, $id)
    {
        $comment = Comment::findOrFail($id);
        $comment->markReviewed($request->review_result, $request->review_notes);

        return response()->json(['success' => true, 'message' => 'Bình luận đã được đánh dấu đã xem xét']);
    }

    /**
     * Get similar comments to the specified comment.
     *
     * @param int $id
     * @return View
     */
    public function similar($id)
    {
        try {
            // Lấy comment hiện tại
        $comment = Comment::findOrFail($id);

            // Gọi API để lấy comments tương tự
            $apiUrl = config('services.toxic_detection.url');
            $apiEndpoint = "/admin/comments/{$id}/similar";

            $response = Http::withHeaders($this->toxicService->getHeaders())
                ->get($apiUrl . $apiEndpoint);

            Log::info('Similar API response', [
                'status' => $response->status(),
                'url' => $apiUrl . $apiEndpoint,
                'response_status' => $response->status()
            ]);

        $similarComments = [];

            if ($response->successful()) {
                $similarResult = $response->json();

                // Nếu API trả về array trực tiếp
                if (is_array($similarResult) && !isset($similarResult['error'])) {
                    $similarComments = $this->transformApiComments($similarResult);
                }
                // Nếu API trả về cấu trúc với trường similar_comments
                elseif (isset($similarResult['similar_comments']) && is_array($similarResult['similar_comments'])) {
                    $similarComments = $this->transformApiComments($similarResult['similar_comments']);
                }
                // Nếu API trả về cấu trúc với trường comments
                elseif (isset($similarResult['comments']) && is_array($similarResult['comments'])) {
                    $similarComments = $this->transformApiComments($similarResult['comments']);
                }
                // Nếu API trả về IDs
                elseif (isset($similarResult['ids']) && is_array($similarResult['ids'])) {
                    $commentIds = $similarResult['ids'];
                    $similarComments = Comment::whereIn('id', $commentIds)->get();
                }
                // Fallback to old implementation
                else {
                    $similarResult = $this->toxicService->getSimilarComments($id);
                    if (!isset($similarResult['error']) && isset($similarResult['similar_comments'])) {
                        $commentIds = array_column($similarResult['similar_comments'], 'id');
                        $similarComments = Comment::whereIn('id', $commentIds)->get();
                    }
                }
            } else {
                // Fallback to old implementation
                $similarResult = $this->toxicService->getSimilarComments($id);
        if (!isset($similarResult['error']) && isset($similarResult['similar_comments'])) {
            $commentIds = array_column($similarResult['similar_comments'], 'id');
            $similarComments = Comment::whereIn('id', $commentIds)->get();
                }
            }

            // Nếu là mảng, chuyển thành collection
            if (is_array($similarComments)) {
                $similarComments = collect($similarComments);
            }

            return view("{$this->viewPath}admin.comments.similar", compact('comment', 'similarComments'));
        } catch (\Exception $e) {
            Log::error('Error getting similar comments', ['error' => $e->getMessage()]);
            return back()->with('error', 'Không thể lấy bình luận tương tự: ' . $e->getMessage());
        }
    }

    /**
     * Bulk delete comments.
     *
     * @param Request $request
     * @return Response
     */
    public function bulkDelete(Request $request)
    {
        // Chuyển đổi JSON thành mảng
        $ids = json_decode($request->input('ids'), true);

        // Kiểm tra nếu không có mục nào được chọn
        if (!is_array($ids) || count($ids) === 0) {
            return redirect()->route('admin.comments.index');
        }

        try {
            // Sử dụng API để xóa comments nếu có thể
            $apiUrl = config('services.toxic_detection.url');
            $success = false;

            // Log ID comments sẽ xóa
            Log::info('Đang thực hiện xóa comments', ['ids' => $ids]);

            // Thử gọi API để xóa từng comment
            foreach ($ids as $id) {
                try {
                    $response = Http::withHeaders($this->toxicService->getHeaders())
                        ->delete("{$apiUrl}/admin/comments/{$id}");

                    Log::info('API delete response', [
                        'comment_id' => $id,
                        'status' => $response->status(),
                        'body' => $response->body()
                    ]);

                    if ($response->successful()) {
                        $success = true;
                    }
                } catch (\Exception $e) {
                    Log::error('Lỗi khi xóa comment qua API', [
                        'comment_id' => $id,
                        'error' => $e->getMessage()
                    ]);
                }
            }

            // Nếu không xóa thành công qua API, vẫn thử xóa trong database local
            if (!$success) {
                $deletedCount = Comment::whereIn('id', $ids)->delete();
                Log::info('Xóa comments từ database local', ['count' => $deletedCount]);
            }

            return redirect()->route('admin.comments.index')->with('success', 'Xóa bình luận thành công!');
        } catch (\Exception $e) {
            // Xử lý lỗi
            Log::error('Error deleting comments', ['error' => $e->getMessage(), 'ids' => $ids]);
            return redirect()->route('admin.comments.index')->with('error', 'Có lỗi xảy ra khi xóa bình luận.');
        }
    }

    /**
     * Analyze existing comment.
     *
     * @param int $id
     * @return JsonResponse
     */
    public function analyze($id)
    {
        $comment = Comment::findOrFail($id);
        $analysisResult = $this->toxicService->detectSingle($comment->content, $comment->platform);

        if (isset($analysisResult['error'])) {
            return response()->json(['success' => false, 'message' => $analysisResult['message']]);
        }

        // Xác định label dựa trên score cao nhất
        $scores = $analysisResult['scores'] ?? [];
        if (!empty($scores)) {
            $maxCategory = array_search(max($scores), $scores);
            $comment->prediction = $this->getLabelId($maxCategory);
            $comment->confidence = $scores[$maxCategory] ?? 0.5;
        } else {
            $comment->prediction = 0; // Default to clean
            $comment->confidence = 0.5;
        }

        // Lưu các thông tin phụ
        $probabilities = $analysisResult['scores'] ?? [];
        $comment->setProbabilities($probabilities);

        // Lưu vector nếu có
        if (isset($analysisResult['vector'])) {
            $comment->setVector($analysisResult['vector']);
        } else {
            // Đặt vector rỗng nếu API không trả về
            $comment->setVector([]);
        }

        $comment->save();

        return response()->json([
            'success' => true,
            'message' => 'Phân tích thành công!',
            'prediction' => $comment->getPredictionText(),
            'confidence' => $comment->confidence
        ]);
    }

    /**
     * Helper to convert text label to numeric ID.
     *
     * @param string $label
     * @return int
     */
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
