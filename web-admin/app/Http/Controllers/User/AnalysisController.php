<?php

namespace App\Http\Controllers\User;

use App\Http\Controllers\Controller;
use App\Services\ApiService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;

class AnalysisController extends Controller
{
    protected $apiService;

    public function __construct(ApiService $apiService)
    {
        $this->middleware('auth');
        $this->apiService = $apiService;
    }

    /**
     * Display the analysis form
     */
    public function index()
    {
        return view('user.analysis.index');
    }

    /**
     * Analyze a single comment
     */
    public function analyze(Request $request)
    {
        $request->validate([
            'text' => 'required|string|max:1000',
            'platform' => 'nullable|string|max:50',
        ]);

        $result = $this->apiService->detectComment(
            $request->text,
            $request->platform ?? 'web',
            null,
            auth()->user()->name
        );

        if (isset($result['error'])) {
            return response()->json([
                'success' => false,
                'message' => 'Lỗi khi phân tích bình luận',
                'error' => $result['error'],
                'details' => $result['message'] ?? null,
            ], 500);
        }

        // Ensure all necessary data is present
        $prediction = $result['prediction'] ?? 'clean';
        $confidence = $result['confidence'] ?? 0;
        $keywords = $result['keywords'] ?? [];

        // Convert prediction to Vietnamese display text
        $predictionText = $this->getPredictionText($prediction);
        
        // Get bootstrap color class for the prediction
        $colorClass = $this->getPredictionColorClass($prediction);

        return response()->json([
            'success' => true,
            'prediction' => $prediction,
            'predictionText' => $predictionText,
            'confidence' => $confidence,
            'confidencePercent' => round($confidence * 100, 1) . '%',
            'keywords' => $keywords,
            'colorClass' => $colorClass,
            'processed_content' => $result['processed_content'] ?? $request->text,
            'probabilities' => $result['probabilities'] ?? [],
        ]);
    }

    /**
     * Analyze multiple comments
     */
    public function batchAnalyze(Request $request)
    {
        $request->validate([
            'comments' => 'required|array',
            'comments.*.text' => 'required|string|max:1000',
            'comments.*.platform' => 'nullable|string|max:50',
        ]);

        $items = [];
        foreach ($request->comments as $comment) {
            $items[] = [
                'text' => $comment['text'],
                'platform' => $comment['platform'] ?? 'web',
                'platform_id' => 'web-' . time() . '-' . uniqid(),
                'source_user_name' => auth()->user()->name,
                'metadata' => [
                    'source_url' => $request->headers->get('referer', 'web-dashboard'),
                    'user_id' => auth()->id(),
                ],
            ];
        }

        $result = $this->apiService->batchDetectComments($items);

        if (isset($result['error'])) {
            return response()->json([
                'success' => false,
                'message' => 'Lỗi khi phân tích hàng loạt bình luận',
                'error' => $result['error'],
                'details' => $result['message'] ?? null,
            ], 500);
        }

        // Process the results to include Vietnamese translations and color classes
        $processedResults = [];
        foreach ($result['results'] as $index => $item) {
            $prediction = $item['prediction'] ?? 'clean';
            
            $processedResults[] = [
                'text' => $request->comments[$index]['text'],
                'prediction' => $prediction,
                'predictionText' => $this->getPredictionText($prediction),
                'confidence' => $item['confidence'] ?? 0,
                'confidencePercent' => round(($item['confidence'] ?? 0) * 100, 1) . '%',
                'keywords' => $item['keywords'] ?? [],
                'colorClass' => $this->getPredictionColorClass($prediction),
                'processed_content' => $item['processed_content'] ?? $request->comments[$index]['text'],
                'probabilities' => $item['probabilities'] ?? [],
            ];
        }

        return response()->json([
            'success' => true,
            'results' => $processedResults,
        ]);
    }

    /**
     * Get user statistics
     */
    public function getStats(Request $request)
    {
        $period = $request->period ?? 'all';
        $result = $this->apiService->getUserStats($period);

        if (isset($result['error'])) {
            return response()->json([
                'success' => false,
                'message' => 'Lỗi khi lấy thống kê',
                'error' => $result['error'],
                'details' => $result['message'] ?? null,
            ], 500);
        }

        return response()->json([
            'success' => true,
            'stats' => $result,
        ]);
    }

    /**
     * Submit feedback for a comment
     */
    public function submitFeedback(Request $request)
    {
        $request->validate([
            'comment_id' => 'required|string',
            'category' => 'required|string|in:clean,offensive,hate,spam',
            'notes' => 'nullable|string|max:500',
        ]);

        $result = $this->apiService->submitFeedback(
            $request->comment_id,
            $request->category,
            $request->notes
        );

        if (isset($result['error'])) {
            return response()->json([
                'success' => false,
                'message' => 'Lỗi khi gửi phản hồi',
                'error' => $result['error'],
                'details' => $result['message'] ?? null,
            ], 500);
        }

        return response()->json([
            'success' => true,
            'message' => 'Phản hồi đã được ghi nhận thành công',
            'result' => $result,
        ]);
    }

    /**
     * Get Vietnamese text for prediction category
     */
    private function getPredictionText($prediction)
    {
        switch ($prediction) {
            case 'clean':
                return 'Bình thường';
            case 'offensive':
                return 'Xúc phạm';
            case 'hate':
                return 'Phân biệt';
            case 'spam':
                return 'Spam';
            default:
                return ucfirst($prediction);
        }
    }

    /**
     * Get Bootstrap color class for prediction category
     */
    private function getPredictionColorClass($prediction)
    {
        switch ($prediction) {
            case 'clean':
                return 'success';
            case 'offensive':
                return 'warning';
            case 'hate':
                return 'danger';
            case 'spam':
                return 'secondary';
            default:
                return 'info';
        }
    }
} 