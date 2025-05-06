<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Cache;

class ApiService
{
    protected $baseUrl;
    protected $timeout;
    protected $token;

    public function __construct()
    {
        $this->baseUrl = config('services.api.url', 'http://localhost:7860');
        $this->timeout = config('services.api.timeout', 30);
        $this->refreshTokenIfNeeded();
    }

    /**
     * Get access token for API authentication
     */
    protected function getToken()
    {
        if ($this->token) {
            return $this->token;
        }

        if (Cache::has('api_token')) {
            $this->token = Cache::get('api_token');
            return $this->token;
        }

        return $this->refreshToken();
    }

    /**
     * Refresh the API token
     */
    protected function refreshToken()
    {
        try {
            $response = Http::timeout($this->timeout)
                ->withHeaders([
                    'Content-Type' => 'application/x-www-form-urlencoded',
                ])
                ->post($this->baseUrl . '/auth/login', [
                    'username' => config('services.api.username', 'admin'),
                    'password' => config('services.api.password', 'password'),
                ]);

            if ($response->successful()) {
                $data = $response->json();
                $token = $data['access_token'];
                
                // Cache the token for 1 hour (or less than the actual expiry time)
                Cache::put('api_token', $token, 3600);
                $this->token = $token;
                
                return $token;
            } else {
                Log::error('API token refresh failed', [
                    'status' => $response->status(),
                    'response' => $response->body(),
                ]);
                
                return null;
            }
        } catch (\Exception $e) {
            Log::error('API token refresh exception', [
                'message' => $e->getMessage(),
            ]);
            
            return null;
        }
    }

    /**
     * Check if token needs refreshing and refresh if necessary
     */
    protected function refreshTokenIfNeeded()
    {
        if (!Cache::has('api_token')) {
            $this->refreshToken();
        }
    }

    /**
     * Get authorized HTTP client with token
     */
    protected function http()
    {
        return Http::timeout($this->timeout)
            ->withHeaders([
                'Authorization' => 'Bearer ' . $this->getToken(),
                'Accept' => 'application/json',
            ]);
    }

    /**
     * Send a detect request to check toxicity of a single comment
     */
    public function detectComment($text, $platform = 'web', $platformId = null, $sourceUserName = null)
    {
        try {
            $response = $this->http()->post($this->baseUrl . '/extension/detect', [
                'text' => $text,
                'platform' => $platform,
                'platform_id' => $platformId ?? 'web-' . time(),
                'source_user_name' => $sourceUserName ?? 'web-user',
                'metadata' => [
                    'source_url' => request()->headers->get('referer', 'web-dashboard'),
                    'user_id' => auth()->id() ?? 'guest',
                ],
            ]);

            if ($response->successful()) {
                return $response->json();
            } else {
                // Handle authentication error
                if ($response->status() === 401) {
                    $this->refreshToken();
                    return $this->detectComment($text, $platform, $platformId, $sourceUserName);
                }
                
                Log::error('Detect API call failed', [
                    'status' => $response->status(),
                    'response' => $response->body(),
                ]);
                
                return [
                    'error' => 'API request failed: ' . $response->status(),
                    'message' => $response->body(),
                ];
            }
        } catch (\Exception $e) {
            Log::error('Detect API exception', [
                'message' => $e->getMessage(),
            ]);
            
            return [
                'error' => 'API request exception',
                'message' => $e->getMessage(),
            ];
        }
    }

    /**
     * Send a batch detect request to check toxicity of multiple comments
     */
    public function batchDetectComments($items)
    {
        try {
            $response = $this->http()->post($this->baseUrl . '/extension/batch-detect', [
                'items' => $items,
            ]);

            if ($response->successful()) {
                return $response->json();
            } else {
                // Handle authentication error
                if ($response->status() === 401) {
                    $this->refreshToken();
                    return $this->batchDetectComments($items);
                }
                
                Log::error('Batch detect API call failed', [
                    'status' => $response->status(),
                    'response' => $response->body(),
                ]);
                
                return [
                    'error' => 'API request failed: ' . $response->status(),
                    'message' => $response->body(),
                ];
            }
        } catch (\Exception $e) {
            Log::error('Batch detect API exception', [
                'message' => $e->getMessage(),
            ]);
            
            return [
                'error' => 'API request exception',
                'message' => $e->getMessage(),
            ];
        }
    }

    /**
     * Get user statistics from the API
     */
    public function getUserStats($period = 'all')
    {
        try {
            $response = $this->http()->get($this->baseUrl . '/extension/stats', [
                'period' => $period,
            ]);

            if ($response->successful()) {
                return $response->json();
            } else {
                // Handle authentication error
                if ($response->status() === 401) {
                    $this->refreshToken();
                    return $this->getUserStats($period);
                }
                
                Log::error('Stats API call failed', [
                    'status' => $response->status(),
                    'response' => $response->body(),
                ]);
                
                return [
                    'error' => 'API request failed: ' . $response->status(),
                    'message' => $response->body(),
                ];
            }
        } catch (\Exception $e) {
            Log::error('Stats API exception', [
                'message' => $e->getMessage(),
            ]);
            
            return [
                'error' => 'API request exception',
                'message' => $e->getMessage(),
            ];
        }
    }

    /**
     * Submit feedback for a comment
     */
    public function submitFeedback($commentId, $category, $notes = null)
    {
        try {
            $response = $this->http()->post($this->baseUrl . '/extension/feedback', [
                'comment_id' => $commentId,
                'category' => $category,
                'notes' => $notes,
            ]);

            if ($response->successful()) {
                return $response->json();
            } else {
                // Handle authentication error
                if ($response->status() === 401) {
                    $this->refreshToken();
                    return $this->submitFeedback($commentId, $category, $notes);
                }
                
                Log::error('Feedback API call failed', [
                    'status' => $response->status(),
                    'response' => $response->body(),
                ]);
                
                return [
                    'error' => 'API request failed: ' . $response->status(),
                    'message' => $response->body(),
                ];
            }
        } catch (\Exception $e) {
            Log::error('Feedback API exception', [
                'message' => $e->getMessage(),
            ]);
            
            return [
                'error' => 'API request exception',
                'message' => $e->getMessage(),
            ];
        }
    }
} 