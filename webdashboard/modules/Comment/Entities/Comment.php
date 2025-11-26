<?php

namespace Modules\Comment\Entities;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Modules\User\Entities\User;

class Comment extends Model
{
    /**
     * Các trường có thể gán hàng loạt.
     *
     * @var array
     */
    protected $fillable = [
        'content',
        'processed_content',
        'platform',
        'source_user_name',
        'source_url',
        'prediction',
        'confidence',
        'probabilities',
        'vector_representation',
        'is_reviewed',
        'review_result',
        'review_notes',
        'review_timestamp',
        'user_id',
        'meta_data',
        'is_in_report',
        'report_ids',
    ];

    /**
     * Các trường nên được chuyển đổi.
     *
     * @var array
     */
    protected $casts = [
        'meta_data' => 'array',
        'is_reviewed' => 'boolean',
        'is_in_report' => 'boolean',
        'confidence' => 'float',
        'review_timestamp' => 'datetime',
    ];

    /**
     * Lấy user liên quan đến comment này.
     */
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    /**
     * Lấy vector dưới dạng mảng.
     *
     * @return array|null
     */
    public function getVector(): ?array
    {
        if (empty($this->vector_representation)) {
            return null;
        }

        return json_decode($this->vector_representation, true);
    }

    /**
     * Đặt vector representation.
     *
     * @param array $vector
     * @return void
     */
    public function setVector(?array $vector): void
    {
        $this->vector_representation = $vector ? json_encode($vector) : null;
    }

    /**
     * Lấy xác suất dưới dạng mảng.
     *
     * @return array
     */
    public function getProbabilities(): array
    {
        if (empty($this->probabilities)) {
            return [];
        }

        return json_decode($this->probabilities, true) ?: [];
    }

    /**
     * Đặt xác suất.
     *
     * @param array|null $probs
     * @return void
     */
    public function setProbabilities(?array $probs): void
    {
        $this->probabilities = $probs ? json_encode($probs) : null;
    }

    /**
     * Lấy nhãn dự đoán dưới dạng text.
     *
     * @return string
     */
    public function getPredictionText(): string
    {
        $labels = ['clean', 'offensive', 'hate', 'spam'];

        if ($this->prediction === null || $this->prediction >= count($labels)) {
            return 'unknown';
        }

        return $labels[$this->prediction];
    }

    /**
     * Thêm comment vào báo cáo.
     *
     * @param int $reportId
     * @return void
     */
    public function addToReport(int $reportId): void
    {
        $reportIds = $this->report_ids ? json_decode($this->report_ids, true) : [];

        if (!in_array($reportId, $reportIds)) {
            $reportIds[] = $reportId;
            $this->report_ids = json_encode($reportIds);
            $this->is_in_report = true;
            $this->save();
        }
    }

    /**
     * Đánh dấu comment đã được xem xét.
     *
     * @param int|null $result
     * @param string|null $notes
     * @return void
     */
    public function markReviewed(?int $result = null, ?string $notes = null): void
    {
        $this->is_reviewed = true;

        if ($result !== null) {
            $this->review_result = $result;
        }

        if ($notes !== null) {
            $this->review_notes = $notes;
        }

        $this->review_timestamp = now();
        $this->save();
    }

    /**
     * Scope để lấy comments theo nhãn dự đoán.
     */
    public function scopeByPrediction($query, int $prediction)
    {
        return $query->where('prediction', $prediction);
    }

    /**
     * Scope để lấy comments theo nền tảng.
     */
    public function scopeByPlatform($query, string $platform)
    {
        return $query->where('platform', $platform);
    }

    /**
     * Scope để lấy comments theo người dùng.
     */
    public function scopeByUser($query, int $userId)
    {
        return $query->where('user_id', $userId);
    }
}