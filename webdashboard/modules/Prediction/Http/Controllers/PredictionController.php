<?php

namespace Modules\Prediction\Http\Controllers;

use App\Services\ToxicDetectionService;
use Illuminate\Http\Request;
use Illuminate\Routing\Controller;
use Illuminate\Support\Facades\Http;
use Illuminate\Contracts\View\View;
use Illuminate\Support\Facades\Log;
use GuzzleHttp\Client;
use GuzzleHttp\Psr7\MultipartStream;
use GuzzleHttp\Exception\RequestException;

class PredictionController extends Controller
{
    /**
     * Toxic detection service
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
     * Display batch prediction page
     */
    public function batch(): View
    {
        return view('prediction::admin.prediction.batch');
    }

    /**
     * Process batch prediction
     */
    public function processBatch(Request $request)
    {
        try {
            $comments = $request->input('comments', []);
            $saveResults = $request->boolean('save_results', true);

            // Log detailed request data
            Log::info('Batch Prediction Request', [
                'comments_count' => count($comments),
                'save_results' => $saveResults,
                'comments_data' => $comments, // Log actual comments data
                'request_headers' => $request->headers->all()
            ]);

            // Validate comments data
            if (empty($comments)) {
                return response()->json([
                    'error' => true,
                    'message' => 'No comments provided for analysis'
                ], 422);
            }

            // Thêm base URL từ cấu hình và headers xác thực
            $apiUrl = config('services.toxic_detection.url');
            $response = Http::withHeaders($this->toxicService->getHeaders())
                ->post("{$apiUrl}/predict/batch", [
                    'comments' => $comments,
                    'save_results' => $saveResults
                ]);

            Log::info('API Batch Prediction Response', [
                'status' => $response->status(),
                'url' => "{$apiUrl}/predict/batch",
                'response_body' => $response->json(),
                'headers' => $response->headers()
            ]);

            if (!$response->successful()) {
                Log::error('API Error in processBatch', [
                    'status' => $response->status(),
                    'body' => $response->body(),
                    'validation_errors' => $response->json()['detail'] ?? null
                ]);

                return response()->json([
                    'error' => true,
                    'message' => 'API Error: ' . ($response->json()['detail'] ?? $response->body()),
                ], $response->status());
            }

            return response()->json($response->json());
        } catch (\Exception $e) {
            Log::error('Error in processBatch', [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return response()->json([
                'error' => true,
                'message' => 'Failed to process batch: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Display upload CSV page
     */
    public function upload(): View
    {
        return view('prediction::admin.prediction.upload');
    }

    /**
     * Process CSV upload
     */
    public function processUpload(Request $request)
    {
        try {
            // Validate request
            if (!$request->hasFile('file')) {
                return response()->json([
                    'error' => true,
                    'message' => 'No file uploaded'
                ], 422);
            }

            $textColumn = $request->input('text_column');
            $platform = $request->input('platform', 'unknown');
            $saveResults = $request->boolean('save_results', true);
            $file = $request->file('file');

            // Log request data
            Log::info('CSV Upload Request', [
                'text_column' => $textColumn,
                'platform' => $platform,
                'save_results' => $saveResults,
                'file_name' => $file->getClientOriginalName(),
                'file_size' => $file->getSize()
            ]);

            // Validate file type
            if (!in_array($file->getClientOriginalExtension(), ['csv'])) {
                return response()->json([
                    'error' => true,
                    'message' => 'Invalid file type. Only CSV files are allowed.'
                ], 422);
            }

            // Validate text column
            if (empty($textColumn)) {
                return response()->json([
                    'error' => true,
                    'message' => 'Text column name is required'
                ], 422);
            }

            // Xác minh file tồn tại và có thể đọc được
            $tmpFilePath = $file->getRealPath();
            if (!file_exists($tmpFilePath) || !is_readable($tmpFilePath)) {
                Log::error('File issue', [
                    'exists' => file_exists($tmpFilePath),
                    'readable' => is_readable($tmpFilePath),
                    'path' => $tmpFilePath
                ]);

                return response()->json([
                    'error' => true,
                    'message' => 'Unable to read uploaded file'
                ], 500);
            }

            // Thêm base URL từ cấu hình
            $apiUrl = config('services.toxic_detection.url');

            // Xây dựng endpoint URL với query parameters
            $queryParams = http_build_query([
                'text_column' => $textColumn,
                'platform' => $platform,
                'save_results' => $saveResults ? 'true' : 'false'
            ]);

            $url = "{$apiUrl}/predict/upload-csv?{$queryParams}";

            // Tạo cURL request
            $ch = curl_init();

            // Lấy auth headers từ service
            $authHeaders = $this->toxicService->getHeaders();

            // Tạo mảng headers, không bao gồm Content-Type
            $headers = [];
            foreach ($authHeaders as $key => $value) {
                if (strtolower($key) !== 'content-type') {
                    $headers[] = "$key: $value";
                }
            }

            // Thêm Accept header
            $headers[] = 'Accept: application/json';

            // Chuẩn bị file cho multipart/form-data
            $cFile = new \CURLFile(
                $tmpFilePath,
                'text/csv',
                $file->getClientOriginalName()
            );

            // Sử dụng mảng để PHP thiết lập boundary tự động
            $postFields = [
                'file' => $cFile
            ];

            // Log chi tiết
            Log::info('cURL Setup', [
                'url' => $url,
                'headers' => $headers,
                'file_path' => $tmpFilePath,
                'file_exists' => file_exists($tmpFilePath),
                'file_size' => filesize($tmpFilePath)
            ]);

            // Thiết lập các options cơ bản cho cURL
            curl_setopt($ch, CURLOPT_URL, $url);
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
            curl_setopt($ch, CURLOPT_POSTFIELDS, $postFields);

            // Bật verbose để debug
            $verbose = fopen('php://temp', 'w+');
            curl_setopt($ch, CURLOPT_STDERR, $verbose);
            curl_setopt($ch, CURLOPT_VERBOSE, true);

            // Thực hiện request
            $response = curl_exec($ch);
            $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            $error = curl_error($ch);
            $errno = curl_errno($ch);

            // Lấy thông tin verbose
            rewind($verbose);
            $verboseLog = stream_get_contents($verbose);
            fclose($verbose);

            // Log thông tin
            Log::info('cURL Response', [
                'status_code' => $httpCode,
                'curl_error' => $error,
                'response_length' => strlen($response)
            ]);

            Log::debug('cURL Verbose Log', [
                'verbose' => $verboseLog
            ]);

            // Kiểm tra lỗi cURL
            if ($errno) {
                Log::error('cURL Error', [
                    'error' => $error,
                    'code' => $errno
                ]);

                curl_close($ch);
                return response()->json([
                    'error' => true,
                    'message' => 'cURL Error: ' . $error
                ], 500);
            }

            // Đóng curl
            curl_close($ch);

            // Parse JSON response
            $responseData = json_decode($response, true);

            // Kiểm tra lỗi parsing JSON
            if (json_last_error() !== JSON_ERROR_NONE) {
                Log::error('JSON Parse Error', [
                    'error' => json_last_error_msg(),
                    'response' => $response
                ]);

                return response()->json([
                    'error' => true,
                    'message' => 'Failed to parse API response: ' . json_last_error_msg(),
                    'raw_response' => substr($response, 0, 500)
                ], 500);
            }

            // Kiểm tra lỗi API
            if ($httpCode >= 400 || isset($responseData['detail'])) {
                Log::error('API Error', [
                    'http_code' => $httpCode,
                    'response' => $responseData
                ]);

                $errorMsg = 'API Error';

                if (isset($responseData['detail'])) {
                    if (is_array($responseData['detail'])) {
                        $errors = [];
                        foreach ($responseData['detail'] as $detail) {
                            $errors[] = $detail['msg'] ?? 'Unknown validation error';
                        }
                        $errorMsg .= ': ' . implode(', ', $errors);
                    } else {
                        $errorMsg .= ': ' . $responseData['detail'];
                    }
                }

                return response()->json([
                    'error' => true,
                    'message' => $errorMsg
                ], $httpCode);
            }

            // Trả về kết quả thành công
            return response()->json($responseData);

        } catch (\Exception $e) {
            Log::error('Exception in processUpload', [
                'error' => $e->getMessage(),
                'file' => $e->getFile(),
                'line' => $e->getLine(),
                'trace' => $e->getTraceAsString()
            ]);

            return response()->json([
                'error' => true,
                'message' => 'Failed to process CSV upload: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Display similar comments page
     */
    public function similar(Request $request): View
    {
        return view('prediction::admin.prediction.similar');
    }

    /**
     * Get similar comments
     */
    public function getSimilar(Request $request, int $commentId)
    {
        try {
            $limit = $request->input('limit', 10);
            $threshold = $request->input('threshold', 0.7);

            // Thêm base URL từ cấu hình và headers xác thực
            $apiUrl = config('services.toxic_detection.url');
            $response = Http::withHeaders($this->toxicService->getHeaders())
                ->get("{$apiUrl}/predict/similar/{$commentId}", [
                    'limit' => $limit,
                    'threshold' => $threshold
                ]);

            Log::info('API Similar Comments Response', [
                'status' => $response->status(),
                'url' => "{$apiUrl}/predict/similar/{$commentId}",
                'params' => [
                    'limit' => $limit,
                    'threshold' => $threshold
                ]
            ]);

            // Kiểm tra lỗi 404 và forward đến client
            if ($response->status() === 404) {
                Log::warning('Comment không tồn tại', [
                    'comment_id' => $commentId,
                    'response' => $response->body()
                ]);

                // Trả về lỗi 404 với cùng response từ API
                return response()->json(
                    $response->json(),
                    404
                );
            }

            return response()->json($response->json());
        } catch (\Exception $e) {
            Log::error('Error in getSimilar', [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return response()->json([
                'error' => true,
                'message' => 'Failed to get similar comments: ' . $e->getMessage()
            ], 500);
        }
    }
}
