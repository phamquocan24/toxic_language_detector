<?php

namespace Modules\Category\Http\Request;

use Illuminate\Foundation\Http\FormRequest;

class CategoryRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true; // Allows access for all authenticated users
    }

    public function rules(): array
    {
        return [
            'name' => 'required|string|max:191',
            'position' => 'nullable|integer',
            'parent_id' => 'nullable|integer|exists:categories,id',
            'is_active' => 'nullable|boolean',
        ];
    }

    public function messages(): array
    {
        return [
            'name.required' => 'Vui lòng nhập tên danh mục hợp lệ!',
            'name.max' => 'Vui lòng nhập tên không quá 191 ký tự!',
            'parent_id.exists' => 'Danh mục cha không hợp lệ!',
        ];
    }
}
