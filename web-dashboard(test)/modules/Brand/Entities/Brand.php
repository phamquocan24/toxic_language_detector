<?php

namespace Modules\Brand\Entities;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Modules\Product\Entities\Product;

class Brand extends Model
{
    use HasFactory;

    protected $fillable = [
        'name',
        'is_active',
    ];

    protected $casts = [
        'is_active' => 'boolean',
    ];

    public static function findBySlug($slug)
    {
        return self::where('slug', $slug)->firstOrNew([]);
    }

    public function products(): HasMany
    {
        return $this->hasMany(Product::class);
    }
}
