<?php

namespace Modules\Feedbacks\Http\Controllers\Admin;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Routing\Controller;
use App\Services\ToxicDetectionService;

class FeedbacksController extends Controller
{
    protected $toxicService;

    public function __construct(ToxicDetectionService $toxicService)
    {
        $this->toxicService = $toxicService;
    }

    /**
     * Display the feedbacks list page
     */
    public function index(Request $request)
    {
        $limit = $request->input('limit', 50);
        $page = $request->input('page', 1);
        $skip = ($page - 1) * $limit;
        $feedbackType = $request->input('feedback_type');

        // Fetch feedbacks from Python API
        $feedbacksData = $this->getFeedbacks($limit, $skip, $feedbackType);

        return view('feedbacks::admin.feedbacks.index', [
            'feedbacks' => $feedbacksData['data'] ?? [],
            'total' => $feedbacksData['total'] ?? 0,
            'limit' => $limit,
            'page' => $page,
            'feedbackType' => $feedbackType
        ]);
    }

    /**
     * Get feedbacks data from Python API
     */
    private function getFeedbacks($limit = 50, $skip = 0, $feedbackType = null)
    {
        try {
            $apiUrl = config('services.toxic_detection.url', 'http://localhost:7860');

            $queryParams = [
                'limit' => $limit,
                'skip' => $skip
            ];

            if ($feedbackType) {
                $queryParams['feedback_type'] = $feedbackType;
            }

            $response = Http::withHeaders($this->toxicService->getHeaders())
                ->timeout(10)
                ->get($apiUrl . '/feedback/list', $queryParams);

            if ($response->successful()) {
                return $response->json();
            }

            return [
                'total' => 0,
                'data' => [],
                'limit' => $limit,
                'skip' => $skip
            ];

        } catch (\Exception $e) {
            return [
                'total' => 0,
                'data' => [],
                'limit' => $limit,
                'skip' => $skip
            ];
        }
    }

    /**
     * API endpoint for AJAX requests
     */
    public function getFeedbacksJson(Request $request)
    {
        $limit = $request->input('limit', 50);
        $skip = $request->input('skip', 0);
        $feedbackType = $request->input('feedback_type');

        $feedbacksData = $this->getFeedbacks($limit, $skip, $feedbackType);

        return response()->json([
            'success' => true,
            'data' => $feedbacksData['data'] ?? [],
            'total' => $feedbacksData['total'] ?? 0
        ]);
    }
}
