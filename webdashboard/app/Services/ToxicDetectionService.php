<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class ToxicDetectionService
{
    /**
     * URL cơ sở cho API phát hiện ngôn từ tiêu cực
     *
     * @var string
     */
    protected $apiBaseUrl;

    /**
     * URL để lấy token OAuth2
     *
     * @var string
     */
    protected $tokenUrl;

    /**
     * Token xác thực API (nếu cần)
     *
     * @var string|null
     */
    protected $apiToken;

    /**
     * Loại header xác thực để sử dụng
     *
     * @var string
     */
    protected $authHeader;

    /**
     * Loại xác thực (Bearer, Basic, etc.)
     *
     * @var string
     */
    protected $authType;

    /**
     * Khởi tạo dịch vụ với cấu hình
     */
    public function __construct()
    {
        $this->apiBaseUrl = config('services.toxic_detection.url', 'http://localhost:7860');
        $this->tokenUrl = config('services.toxic_detection.token_url', '/auth/token');

        // Fetch OAuth2 token
        $oauth = config('services.toxic_detection.oauth', []);
        if (!empty($oauth['username']) && !empty($oauth['password'])) {
            try {
                $response = Http::withBasicAuth(
                        $oauth['client_id'] ?? '',
                        $oauth['client_secret'] ?? ''
                    )
                    ->asForm()
                    ->post($this->apiBaseUrl . $this->tokenUrl, [
                        'grant_type' => 'password',
                        'username' => $oauth['username'],
                        'password' => $oauth['password'],
                    ]);

                if ($response->successful()) {
                    $tokenData = $response->json();
                    $this->apiToken = $tokenData['access_token'] ?? null;
                    Log::info('Fetched OAuth2 token', ['token_length' => strlen($this->apiToken)]);
                } else {
                    Log::error('Failed to fetch OAuth2 token', ['status' => $response->status(), 'body' => $response->body()]);
                }
            } catch (\Exception $e) {
                Log::error('Exception fetching OAuth2 token', ['message' => $e->getMessage()]);
            }
        }

        // Loại header xác thực
        $this->authHeader = config('services.toxic_detection.auth_header', 'Authorization');
        $this->authType = config('services.toxic_detection.auth_type', 'Bearer');

        // Debug log
        Log::debug('ToxicDetectionService initialized', [
            'base_url' => $this->apiBaseUrl,
            'token_url' => $this->tokenUrl,
            'has_token' => !empty($this->apiToken),
        ]);
    }

    /**
     * Phát hiện độc hại trên một đoạn văn bản
     *
     * @param string $text
     * @param string|null $platform
     * @return array
     */
    public function detectSingle($text, $platform = null)
    {
        try {
            $url = "{$this->apiBaseUrl}/predict/single";
            $headers = $this->getHeaders();

            Log::debug('Sending request to toxic detection API', [
                'url' => $url,
                'headers' => $headers,
                'text_length' => strlen($text)
            ]);

            $payload = ['text' => $text];
            if ($platform) {
                $payload['platform'] = $platform;
            }

            $response = Http::withHeaders($headers)
                ->post($url, $payload);

            if ($response->successful()) {
                return $response->json();
            }

            Log::error('Toxic Detection API Error', [
                'status' => $response->status(),
                'body' => $response->body()
            ]);

            return [
                'error' => true,
                'message' => 'Failed to analyze text: ' . $response->body(),
                'status' => $response->status()
            ];
        } catch (\Exception $e) {
            Log::error('Toxic Detection Exception', ['message' => $e->getMessage()]);
            return [
                'error' => true,
                'message' => 'Exception: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Phát hiện độc hại trên nhiều đoạn văn bản
     *
     * @param array $texts
     * @return array
     */
    public function detectBatch(array $texts)
    {
        try {
            $response = Http::withHeaders($this->getHeaders())
                ->post("{$this->apiBaseUrl}/predict/batch", [
                    'texts' => $texts
                ]);

            if ($response->successful()) {
                return $response->json();
            }

            Log::error('Toxic Batch Detection API Error', [
                'status' => $response->status(),
                'body' => $response->body()
            ]);

            return [
                'error' => true,
                'message' => 'Failed to analyze batch texts',
                'status' => $response->status()
            ];
        } catch (\Exception $e) {
            Log::error('Toxic Batch Detection Exception', [
                'message' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return [
                'error' => true,
                'message' => 'Exception: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Lấy các bình luận tương tự
     *
     * @param int $commentId
     * @param int $limit
     * @return array
     */
    public function getSimilarComments($commentId, $limit = 10)
    {
        try {
            $response = Http::withHeaders($this->getHeaders())
                ->get("{$this->apiBaseUrl}/predict/similar/{$commentId}", [
                    'limit' => $limit
                ]);

            if ($response->successful()) {
                return $response->json();
            }

            Log::error('Similar Comments API Error', [
                'status' => $response->status(),
                'body' => $response->body()
            ]);

            return [
                'error' => true,
                'message' => 'Failed to get similar comments',
                'status' => $response->status()
            ];
        } catch (\Exception $e) {
            Log::error('Similar Comments Exception', [
                'message' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return [
                'error' => true,
                'message' => 'Exception: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Phân tích chi tiết văn bản
     *
     * @param string $text
     * @return array
     */
    public function analyzeText($text)
    {
        try {
            $response = Http::withHeaders($this->getHeaders())
                ->post("{$this->apiBaseUrl}/predict/analyze-text", [
                    'text' => $text
                ]);

            if ($response->successful()) {
                return $response->json();
            }

            Log::error('Text Analysis API Error', [
                'status' => $response->status(),
                'body' => $response->body()
            ]);

            return [
                'error' => true,
                'message' => 'Failed to analyze text details',
                'status' => $response->status()
            ];
        } catch (\Exception $e) {
            Log::error('Text Analysis Exception', [
                'message' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return [
                'error' => true,
                'message' => 'Exception: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Lấy thống kê dữ liệu từ API
     *
     * @return array
     */
    public function getStatistics()
    {
        try {
            $response = Http::withHeaders($this->getHeaders())
                ->get("{$this->apiBaseUrl}/toxic/statistics");

            if ($response->successful()) {
                return $response->json();
            }

            Log::error('Statistics API Error', [
                'status' => $response->status(),
                'body' => $response->body()
            ]);

            return [
                'error' => true,
                'message' => 'Failed to get statistics',
                'status' => $response->status()
            ];
        } catch (\Exception $e) {
            Log::error('Statistics Exception', [
                'message' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return [
                'error' => true,
                'message' => 'Exception: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Lấy thông tin về các từ khóa độc hại
     *
     * @return array
     */
    public function getToxicKeywords()
    {
        try {
            $response = Http::withHeaders($this->getHeaders())
                ->get("{$this->apiBaseUrl}/toxic/toxic-keywords");

            if ($response->successful()) {
                return $response->json();
            }

            Log::error('Toxic Keywords API Error', [
                'status' => $response->status(),
                'body' => $response->body()
            ]);

            return [
                'error' => true,
                'message' => 'Failed to get toxic keywords',
                'status' => $response->status()
            ];
        } catch (\Exception $e) {
            Log::error('Toxic Keywords Exception', [
                'message' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return [
                'error' => true,
                'message' => 'Exception: ' . $e->getMessage()
            ];
        }
    }

    /**
     * Lấy các headers cho request
     *
     * @return array
     */
    public function getHeaders()
    {
        $headers = [
            'Accept' => 'application/json',
            'Content-Type' => 'application/json',
        ];

        if (!empty($this->apiToken)) {
            $headers[$this->authHeader] = $this->authType . ' ' . $this->apiToken;
        }

        return $headers;
    }
}
