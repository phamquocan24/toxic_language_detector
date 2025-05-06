<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Comment;
use App\Services\ToxicApiService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Validator;

class ExtensionController extends Controller
{
    protected $toxicApiService;
    
    public function __construct(ToxicApiService $toxicApiService)
    {
        $this->toxicApiService = $toxicApiService;
    }
    
    /**
     * Phân tích độc hại của văn bản
     */
    public function detect(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'text' => 'required|string',
            'platform' => 'nullable|string',
            'platform_id' => 'nullable|string',
            'source_url' => 'nullable|string',
            'metadata' => 'nullable|array',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => $validator->errors()], 422);
        }

        try {
            // Gọi API phân tích
            $analysis = $this->toxicApiService->detect(
                $request->text,
                [
                    'platform' => $request->platform ?? 'web',
                    'platform_id' => $request->platform_id,
                    'source_url' => $request->source_url,
                    'metadata' => $request->metadata,
                ]
            );
            
            // Lưu kết quả vào database nếu có người dùng xác thực
            if (Auth::check() && isset($analysis['prediction']) && $analysis['prediction'] > 0) {
                $category = isset($analysis['category']) ? $analysis['category'] : '';
                if (!$category && isset($analysis['prediction'])) {
                    $categories = ['clean', 'offensive', 'hate', 'spam'];
                    $category = $categories[$analysis['prediction']] ?? 'unknown';
                }
                
                Comment::create([
                    'user_id' => Auth::id(),
                    'content' => $request->text,
                    'processed_content' => $analysis['processed_text'] ?? null,
                    'category' => $category,
                    'confidence_score' => $analysis['confidence'] ?? 0.0,
                    'probabilities' => $analysis['probabilities'] ?? null,
                    'platform' => $request->platform ?? 'web',
                    'platform_id' => $request->platform_id,
                    'source_url' => $request->source_url,
                    'commenter_name' => $request->metadata['source_user_name'] ?? null,
                    'keywords' => $analysis['keywords'] ?? null,
                ]);
            }

            return response()->json($analysis);
        } catch (\Exception $e) {
            Log::error('Error detecting toxic content: ' . $e->getMessage());
            return response()->json([
                'error' => 'Không thể phân tích văn bản: ' . $e->getMessage()
            ], 500);
        }
    }
    
    /**
     * Phân tích độc hại của nhiều văn bản
     */
    public function batchDetect(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'items' => 'required|array',
            'items.*.text' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['error' => $validator->errors()], 422);
        }

        // Tạo mảng phản hồi
        $results = [];
        
        // Xử lý từng item
        foreach ($request->items as $item) {
            $text = $item['text'];
            $platform = $item['platform'] ?? 'web';
            $platformId = $item['platform_id'] ?? null;
            $sourceUrl = $item['source_url'] ?? null;
            $metadata = $item['metadata'] ?? [];
            
            try {
                // Gọi API phân tích
                $analysis = $this->toxicApiService->detect(
                    $text,
                    [
                        'platform' => $platform,
                        'platform_id' => $platformId,
                        'source_url' => $sourceUrl,
                        'metadata' => $metadata,
                    ]
                );
                
                // Lưu kết quả vào database nếu có người dùng xác thực
                if (Auth::check() && isset($analysis['prediction']) && $analysis['prediction'] > 0) {
                    $category = isset($analysis['category']) ? $analysis['category'] : '';
                    if (!$category && isset($analysis['prediction'])) {
                        $categories = ['clean', 'offensive', 'hate', 'spam'];
                        $category = $categories[$analysis['prediction']] ?? 'unknown';
                    }
                    
                    Comment::create([
                        'user_id' => Auth::id(),
                        'content' => $text,
                        'processed_content' => $analysis['processed_text'] ?? null,
                        'category' => $category,
                        'confidence_score' => $analysis['confidence'] ?? 0.0,
                        'probabilities' => $analysis['probabilities'] ?? null,
                        'platform' => $platform,
                        'platform_id' => $platformId,
                        'source_url' => $sourceUrl,
                        'commenter_name' => $metadata['source_user_name'] ?? null,
                        'keywords' => $analysis['keywords'] ?? null,
                    ]);
                }
                
                $results[] = $analysis;
            } catch (\Exception $e) {
                Log::error('Error batch detecting toxic content: ' . $e->getMessage());
                $results[] = [
                    'text' => $text,
                    'error' => 'Không thể phân tích văn bản: ' . $e->getMessage()
                ];
            }
        }

        return response()->json([
            'count' => count($results),
            'results' => $results
        ]);
    }
    
    /**
     * Lấy thống kê từ API
     */
    public function getStats(Request $request)
    {
        $period = $request->period ?? 'all';
        
        try {
            $stats = $this->toxicApiService->getStatistics($period);
            return response()->json($stats);
        } catch (\Exception $e) {
            Log::error('Error getting stats: ' . $e->getMessage());
            return response()->json([
                'error' => 'Không thể lấy thống kê: ' . $e->getMessage()
            ], 500);
        }
    }
} 