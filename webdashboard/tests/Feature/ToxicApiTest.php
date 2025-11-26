<?php

namespace Tests\Feature;

use App\Services\MockToxicDetectionService;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Foundation\Testing\WithFaker;
use Illuminate\Support\Facades\Log;
use Tests\TestCase;

class ToxicApiTest extends TestCase
{
    /**
     * Kiểm tra kết nối API phát hiện độc hại
     */
    public function test_api_connection()
    {
        $service = new MockToxicDetectionService();
        $headers = $service->getHeaders();

        $this->assertArrayHasKey('X-API-Key', $headers);
        $this->assertEquals('extension-api-key', $headers['X-API-Key']);

        // Ghi log chi tiết headers
        Log::info('API Headers:', $headers);

        // Thử gọi API
        $result = $service->detectSingle('Đây là bình luận thử nghiệm');

        // Ghi log kết quả
        Log::info('API Response:', $result);

        // Kiểm tra kết quả
        $this->assertArrayNotHasKey('error', $result);
        $this->assertArrayHasKey('label', $result);
        $this->assertArrayHasKey('confidence', $result);
    }
}
