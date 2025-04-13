<?php

namespace Modules\Product\Http\Request;

use Illuminate\Foundation\Http\FormRequest;

class ProductRequest extends FormRequest
{
    public function authorize()

    {
        return true;
    }

    public function rules(): array
    {
        return [
            'name' => 'required|string|max:191',
            'description' => 'nullable|string',
            'brand_id' => 'required|exists:brands,id',
            'description' => 'nullable|string|max:191',
            'short_description' => 'nullable|string|max:50',
            'category_id' => 'required|exists:categories,id',
            'short_description' => 'nullable|string|max:500',
            'new_from' => 'nullable|date',
            'new_to' => 'nullable|date|after_or_equal:new_from',
            'price' => [
                'nullable',
                'numeric',
                'gte:0',
            ],
            'special_price' => 'nullable|numeric|gte:0',
            'special_price_start' => 'nullable|date|before_or_equal:special_price_end',
            'special_price_end' => 'nullable|date|after_or_equal:special_price_start',
            'manage_stock' => 'boolean',
            'qty' => 'nullable|integer|gte:0|required_if:manage_stock,1',
        ];
    }
    public function withValidator($validator)
    {
        $validator->after(function ($validator) {
            // Lọc tất cả các key có tiền tố "variants_"
            $variants = collect($this->all())->filter(function ($_, $key) {
                return strpos($key, 'variants_') === 0; // Chỉ lấy các key bắt đầu bằng "variants_"
            });

            // Kiểm tra nếu không có biến thể thực sự và price rỗng
            if ($variants->isEmpty() && ($this->missing('price') || $this->input('price') === null)) {
                $validator->errors()->add('price', 'Giá sản phẩm là bắt buộc khi không có biến thể.');
            }
        });
    }


    /**
     * Định nghĩa thông báo lỗi tùy chỉnh.
     */
    public function messages(): array
    {
        return [
            'name.required' => 'Tên sản phẩm không được để trống.',
            'brand_id.required' => 'Vui lòng chọn thương hiệu.',
            'description.max' => 'Mô tả không được quá 191 ký tự.',
            'short_description.max' => 'Mô tả không được quá 50 ký tự.',
            'category_id.required' => 'Vui lòng chọn category.',
            'brand_id.exists' => 'Thương hiệu không hợp lệ.',
            'price.numeric' => 'Giá sản phẩm phải là số.',
            'price.gte' => 'Giá sản phẩm phải lớn hơn hoặc bằng 0.',
            'special_price.gte' => 'Giá sản phẩm phải lớn hơn hoặc bằng 0.',
            'special_price_type.in' => 'Loại giá khuyến mãi không hợp lệ.',
            'special_price_start.before_or_equal' => 'Ngày bắt đầu khuyến mãi phải trước hoặc bằng ngày kết thúc.',
            'special_price_end.after_or_equal' => 'Ngày kết thúc khuyến mãi phải sau hoặc bằng ngày bắt đầu.',
            'sku.max' => 'Mã SKU không được quá 50 ký tự.',
            'qty.required_if' => 'Số lượng là bắt buộc.',
            'qty.gte' => 'Số lượng không được nhỏ hơn 0.',
            'new_to.after_or_equal' => 'Ngày kết thúc mới phải sau hoặc bằng ngày bắt đầu mới.',
        ];
    }
}
