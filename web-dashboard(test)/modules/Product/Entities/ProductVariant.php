<?php

namespace Modules\Product\Entities;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\SoftDeletes;

use Illuminate\Support\Str;
use Carbon\Carbon;

class ProductVariant extends Model
{
    use HasFactory, SoftDeletes;

    protected $fillable = [
        'product_id',
        'name',
        'price',
        'special_price',
        'special_price_type',
        'special_price_start',
        'special_price_end',
        'selling_price',
        'sku',
        'manage_stock',
        'qty',
        'in_stock',
        'is_default',
        'is_active',
        'position',
    ];

    protected $casts = [
        'is_active' => 'boolean',
        'is_default' => 'boolean',
        'special_price_start' => 'datetime',
        'special_price_end' => 'datetime',
        'deleted_at' => 'datetime',
    ];

    protected static function boot()
    {
        parent::boot();

        static::creating(function ($variant) {
            if (empty($variant->sku)) {
                $productName = $variant->product ? $variant->product->name : 'PRD';
                $variant->sku = self::generateSku($productName);
            }

            // Tính giá bán khi tạo sản phẩm mới
            $variant->selling_price = $variant->calculateSellingPrice();
        });

        static::updating(function ($variant) {
            // Cập nhật giá bán khi thay đổi dữ liệu
            $variant->selling_price = $variant->calculateSellingPrice();
        });
    }

    // Hàm tạo SKU tự động (7 ký tự)
    public static function generateSku($productName)
    {
        // Lấy tối đa 3 chữ cái đầu tiên từ tên sản phẩm
        $nameAbbreviation = strtoupper(substr(Str::slug($productName, ''), 0, 3));

        // Tạo chuỗi số ngẫu nhiên 4 chữ số
        $randomNumber = mt_rand(1000, 9999);

        // Kết hợp để tạo SKU 7 ký tự
        return str_pad($nameAbbreviation, 3, 'X') . $randomNumber;
    }

    // Phương thức tính giá bán dựa trên logic của trigger
    public function calculateSellingPrice()
    {
        $currentDate = Carbon::now();

        if (
            $this->special_price !== null &&
            $this->special_price_start <= $currentDate &&
            $this->special_price_end >= $currentDate
        ) {

            if ($this->special_price_type == 1) { // fixed
                return max(0, $this->price - $this->special_price);
            } elseif ($this->special_price_type == 2) { // percent
                return max(0, $this->price - ($this->special_price * $this->price / 100));
            }
        }
        return $this->price;
    }

    public function product(): BelongsTo
    {
        return $this->belongsTo(Product::class);
    }

    public function setSpecialPriceTypeAttribute($value)
    {
        $this->attributes['special_price_type'] = ($value === 'fixed') ? 1 : 2;
    }
}
