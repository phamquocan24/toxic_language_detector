<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class ToxicApiService
{
    protected $apiUrl;
    protected $credentials;
    protected $token;

    public function __construct()
    {
        $this->apiUrl = config('services.toxic_api.url', 'http://localhost:7860');
        $this->credentials = [
            'username' => config('services.toxic_api.username', 'admin'),
            'password' => config('services.toxic_api.password', 'password'),
        ];
        $this->token = null;
    }

    /**
     * Get authentication token from API
     * 
     * @return string|null
     */
    protected function getToken()
    {
        try {
            if ($this->token) {
                return $this->token;
            }
            
            $response = Http::post($this->apiUrl . '/auth/token', [
                'username' => $this->credentials['username'],
                'password' => $this->credentials['password'],
            ]);
            
            if ($response->successful() && isset($response['access_token'])) {
                $this->token = $response['access_token'];
                return $this->token;
            }
            
            Log::error('Failed to get API token: ' . $response->body());
            return null;
        } catch (\Exception $e) {
            Log::error('Token API Error: ' . $e->getMessage());
            return null;
        }
    }

    /**
     * Phân tích độc hại của một văn bản
     *
     * @param string $text Văn bản cần phân tích
     * @param array $options Các tùy chọn bổ sung
     * @return array Kết quả phân tích
     */
    public function detect($text, $options = [])
    {
        try {
            // Try first with token
            $token = $this->getToken();
            $headers = [];
            
            if ($token) {
                $headers['Authorization'] = 'Bearer ' . $token;
            }
            
            $response = Http::withHeaders($headers)
                ->post($this->apiUrl . '/extension/detect', [
                    'text' => $text,
                    'platform' => $options['platform'] ?? 'web',
                    'platform_id' => $options['platform_id'] ?? null,
                    'source_url' => $options['source_url'] ?? null,
                    'metadata' => $options['metadata'] ?? [
                        'source' => 'web-admin',
                        'browser' => $_SERVER['HTTP_USER_AGENT'] ?? 'Unknown'
                    ],
                ]);

            // Fallback to basic auth if token doesn't work
            if ($response->status() === 401) {
                $response = Http::withBasicAuth(
                    $this->credentials['username'], 
                    $this->credentials['password']
                )->post($this->apiUrl . '/extension/detect', [
                    'text' => $text,
                    'platform' => $options['platform'] ?? 'web',
                    'platform_id' => $options['platform_id'] ?? null,
                    'source_url' => $options['source_url'] ?? null,
                    'metadata' => $options['metadata'] ?? [
                        'source' => 'web-admin',
                        'browser' => $_SERVER['HTTP_USER_AGENT'] ?? 'Unknown'
                    ],
                ]);
            }

            return $response->json();
        } catch (\Exception $e) {
            Log::error('Toxic API Error: ' . $e->getMessage());
            
            // Trả về kết quả giả lập trong trường hợp lỗi
            return [
                'text' => $text,
                'prediction' => 0,
                'prediction_text' => 'clean',
                'category' => 'clean',
                'confidence' => 0.95,
                'error' => $e->getMessage()
            ];
        }
    }

    /**
     * Lấy thống kê từ API
     *
     * @param string $period Khoảng thời gian (day, week, month, all)
     * @return array Dữ liệu thống kê
     */
    public function getStatistics($period = 'all')
    {
        try {
            // Try first with token
            $token = $this->getToken();
            $headers = [];
            
            if ($token) {
                $headers['Authorization'] = 'Bearer ' . $token;
            }
            
            $response = Http::withHeaders($headers)
                ->get($this->apiUrl . '/extension/stats', [
                    'period' => $period
                ]);

            // Fallback to basic auth if token doesn't work
            if ($response->status() === 401) {
                $response = Http::withBasicAuth(
                    $this->credentials['username'], 
                    $this->credentials['password']
                )->get($this->apiUrl . '/extension/stats', [
                    'period' => $period
                ]);
            }

            return $response->json();
        } catch (\Exception $e) {
            Log::error('Toxic API Statistics Error: ' . $e->getMessage());
            
            // Trả về dữ liệu giả lập trong trường hợp lỗi
            return [
                'api_status' => 'offline',
                'total' => 0,
                'clean' => 0,
                'offensive' => 0,
                'hate' => 0,
                'spam' => 0,
                'recent' => [],
                'error' => $e->getMessage()
            ];
        }
    }
} 