<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Comment extends Model
{
    use HasFactory;
    
    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
    protected $fillable = [
        'content',
        'processed_content',
        'classification',
        'confidence',
        'keywords',
        'platform',
        'platform_id',
        'source_url', 
        'source_user_name',
        'prediction_text',
        'user_id',
        'probabilities',
        'metadata',
        'feedback',
        'feedback_notes',
        'extension_id'
    ];

    /**
     * The attributes that should be cast.
     *
     * @var array
     */
    protected $casts = [
        'confidence' => 'float',
        'keywords' => 'array',
        'probabilities' => 'array',
        'metadata' => 'array',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the user that owns the comment.
     */
    public function user()
    {
        return $this->belongsTo(User::class);
    }

    /**
     * Get the readable confidence level of the comment.
     *
     * @return string
     */
    public function getConfidenceLevelAttribute()
    {
        $confidence = $this->confidence;
        
        if ($confidence >= 0.8) {
            return 'Cao';
        } elseif ($confidence >= 0.5) {
            return 'Trung bình';
        } else {
            return 'Thấp';
        }
    }

    /**
     * Get the badge color for the classification.
     *
     * @return string
     */
    public function getClassificationColorAttribute()
    {
        switch ($this->classification) {
            case 'clean':
                return 'success';
            case 'offensive':
                return 'warning';
            case 'hate':
                return 'danger';
            case 'spam':
                return 'info';
            default:
                return 'secondary';
        }
    }

    /**
     * Scope a query to only include comments with a specific classification.
     */
    public function scopeWithClassification($query, $classification)
    {
        return $query->where('classification', $classification);
    }

    /**
     * Scope a query to only include comments from a specific platform.
     */
    public function scopeFromPlatform($query, $platform)
    {
        return $query->where('platform', $platform);
    }

    /**
     * Get the localized classification name.
     *
     * @return string
     */
    public function getLocalizedClassificationAttribute()
    {
        switch ($this->classification) {
            case 'clean':
                return 'Bình thường';
            case 'offensive':
                return 'Xúc phạm';
            case 'hate':
                return 'Phân biệt';
            case 'spam':
                return 'Spam';
            default:
                return ucfirst($this->classification);
        }
    }
}
