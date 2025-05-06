@extends('layouts.app')

@section('title', 'Phân tích bình luận')

@section('content')
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">Phân tích bình luận</h5>
                </div>
                <div class="card-body">
                    <ul class="nav nav-tabs mb-4" id="myTab" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active" id="single-tab" data-bs-toggle="tab" data-bs-target="#single-analysis" type="button" role="tab" aria-controls="single-analysis" aria-selected="true">
                                <i class="fas fa-comment me-2"></i>Phân tích đơn
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="batch-tab" data-bs-toggle="tab" data-bs-target="#batch-analysis" type="button" role="tab" aria-controls="batch-analysis" aria-selected="false">
                                <i class="fas fa-comments me-2"></i>Phân tích hàng loạt
                            </button>
                        </li>
                    </ul>
                    
                    <div class="tab-content" id="myTabContent">
                        <!-- Phân tích đơn -->
                        <div class="tab-pane fade show active" id="single-analysis" role="tabpanel" aria-labelledby="single-tab">
                            <form id="single-analysis-form">
                                <div class="mb-3">
                                    <label for="text" class="form-label">Nội dung bình luận <span class="text-danger">*</span></label>
                                    <textarea class="form-control" id="text" name="text" rows="4" required></textarea>
                                    <div class="form-text">Nhập nội dung bình luận cần phân tích (tối đa 1000 ký tự)</div>
                                </div>
                                <div class="mb-3">
                                    <label for="platform" class="form-label">Nền tảng</label>
                                    <select class="form-select" id="platform" name="platform">
                                        <option value="web" selected>Web</option>
                                        <option value="facebook">Facebook</option>
                                        <option value="youtube">YouTube</option>
                                        <option value="twitter">Twitter</option>
                                        <option value="other">Khác</option>
                                    </select>
                                </div>
                                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                                    <button type="submit" class="btn btn-primary">
                                        <i class="fas fa-search me-2"></i>Phân tích
                                    </button>
                                    <button type="reset" class="btn btn-secondary">
                                        <i class="fas fa-redo me-2"></i>Làm mới
                                    </button>
                                </div>
                            </form>
                            
                            <!-- Kết quả phân tích đơn -->
                            <div id="single-result" class="mt-4" style="display: none;">
                                <h5>Kết quả phân tích</h5>
                                <div class="card">
                                    <div class="card-body">
                                        <div class="row">
                                            <div class="col-md-6">
                                                <div class="mb-3">
                                                    <strong>Nội dung:</strong>
                                                    <p id="result-content" class="mt-2"></p>
                                                </div>
                                                <div class="mb-3">
                                                    <strong>Phân loại:</strong>
                                                    <div class="mt-2">
                                                        <span id="result-category-badge" class="badge"></span>
                                                    </div>
                                                </div>
                                                <div class="mb-3">
                                                    <strong>Độ tin cậy:</strong>
                                                    <div class="progress mt-2">
                                                        <div id="result-confidence" class="progress-bar" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="col-md-6">
                                                <div class="mb-3">
                                                    <strong>Từ khóa phát hiện:</strong>
                                                    <div id="result-keywords" class="mt-2">
                                                        <span class="badge bg-secondary">Không có</span>
                                                    </div>
                                                </div>
                                                <div class="mb-3">
                                                    <strong>Nội dung đã xử lý:</strong>
                                                    <p id="result-processed" class="mt-2 text-muted fst-italic"></p>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div class="mt-3">
                                            <strong>Phân tích xác suất:</strong>
                                            <div class="row mt-2">
                                                <div class="col-md-3 mb-2">
                                                    <label class="form-label text-success">Bình thường:</label>
                                                    <div class="progress">
                                                        <div id="prob-clean" class="progress-bar bg-success" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
                                                    </div>
                                                </div>
                                                <div class="col-md-3 mb-2">
                                                    <label class="form-label text-warning">Xúc phạm:</label>
                                                    <div class="progress">
                                                        <div id="prob-offensive" class="progress-bar bg-warning" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
                                                    </div>
                                                </div>
                                                <div class="col-md-3 mb-2">
                                                    <label class="form-label text-danger">Phân biệt:</label>
                                                    <div class="progress">
                                                        <div id="prob-hate" class="progress-bar bg-danger" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
                                                    </div>
                                                </div>
                                                <div class="col-md-3 mb-2">
                                                    <label class="form-label text-secondary">Spam:</label>
                                                    <div class="progress">
                                                        <div id="prob-spam" class="progress-bar bg-secondary" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Lỗi phân tích đơn -->
                            <div id="single-error" class="mt-4 alert alert-danger" style="display: none;">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                <span id="single-error-message">Đã xảy ra lỗi khi phân tích bình luận.</span>
                            </div>
                        </div>
                        
                        <!-- Phân tích hàng loạt -->
                        <div class="tab-pane fade" id="batch-analysis" role="tabpanel" aria-labelledby="batch-tab">
                            <form id="batch-analysis-form">
                                <div class="mb-3">
                                    <label for="batch-text" class="form-label">Danh sách bình luận <span class="text-danger">*</span></label>
                                    <textarea class="form-control" id="batch-text" name="batch-text" rows="6" required></textarea>
                                    <div class="form-text">Nhập mỗi bình luận trên một dòng (tối đa 20 bình luận)</div>
                                </div>
                                <div class="mb-3">
                                    <label for="batch-platform" class="form-label">Nền tảng</label>
                                    <select class="form-select" id="batch-platform" name="batch-platform">
                                        <option value="web" selected>Web</option>
                                        <option value="facebook">Facebook</option>
                                        <option value="youtube">YouTube</option>
                                        <option value="twitter">Twitter</option>
                                        <option value="other">Khác</option>
                                    </select>
                                </div>
                                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                                    <button type="submit" class="btn btn-primary">
                                        <i class="fas fa-search me-2"></i>Phân tích hàng loạt
                                    </button>
                                    <button type="reset" class="btn btn-secondary">
                                        <i class="fas fa-redo me-2"></i>Làm mới
                                    </button>
                                </div>
                            </form>
                            
                            <!-- Kết quả phân tích hàng loạt -->
                            <div id="batch-result" class="mt-4" style="display: none;">
                                <h5>Kết quả phân tích hàng loạt</h5>
                                <div class="table-responsive">
                                    <table class="table table-bordered table-hover">
                                        <thead class="table-light">
                                            <tr>
                                                <th width="5%">#</th>
                                                <th width="35%">Nội dung</th>
                                                <th width="15%">Phân loại</th>
                                                <th width="10%">Độ tin cậy</th>
                                                <th width="35%">Từ khóa</th>
                                            </tr>
                                        </thead>
                                        <tbody id="batch-results-body">
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            
                            <!-- Lỗi phân tích hàng loạt -->
                            <div id="batch-error" class="mt-4 alert alert-danger" style="display: none;">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                <span id="batch-error-message">Đã xảy ra lỗi khi phân tích hàng loạt bình luận.</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
@endsection

@push('scripts')
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Xử lý form phân tích đơn
        const singleForm = document.getElementById('single-analysis-form');
        const singleResult = document.getElementById('single-result');
        const singleError = document.getElementById('single-error');
        
        singleForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const text = document.getElementById('text').value;
            const platform = document.getElementById('platform').value;
            
            if (!text) {
                alert('Vui lòng nhập nội dung bình luận');
                return;
            }
            
            // Ẩn kết quả và lỗi cũ
            singleResult.style.display = 'none';
            singleError.style.display = 'none';
            
            // Hiển thị loading
            const submitBtn = singleForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Đang phân tích...';
            submitBtn.disabled = true;
            
            // Gửi request API
            fetch('{{ route("user.analysis.analyze") }}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': '{{ csrf_token() }}'
                },
                body: JSON.stringify({
                    text: text,
                    platform: platform
                })
            })
            .then(response => response.json())
            .then(data => {
                // Khôi phục nút submit
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                
                if (data.success) {
                    // Hiển thị kết quả
                    document.getElementById('result-content').textContent = text;
                    
                    // Cập nhật badge
                    const badge = document.getElementById('result-category-badge');
                    badge.className = 'badge bg-' + data.colorClass;
                    badge.textContent = data.predictionText;
                    
                    // Cập nhật độ tin cậy
                    const confidenceBar = document.getElementById('result-confidence');
                    const confidencePercent = parseFloat(data.confidence) * 100;
                    confidenceBar.style.width = confidencePercent + '%';
                    confidenceBar.textContent = Math.round(confidencePercent * 10) / 10 + '%';
                    confidenceBar.className = 'progress-bar bg-' + data.colorClass;
                    
                    // Cập nhật từ khóa
                    const keywordsEl = document.getElementById('result-keywords');
                    keywordsEl.innerHTML = '';
                    
                    if (data.keywords && data.keywords.length > 0) {
                        data.keywords.forEach(keyword => {
                            const span = document.createElement('span');
                            span.className = 'badge bg-info me-1 mb-1';
                            span.textContent = keyword;
                            keywordsEl.appendChild(span);
                        });
                    } else {
                        const span = document.createElement('span');
                        span.className = 'badge bg-secondary';
                        span.textContent = 'Không có';
                        keywordsEl.appendChild(span);
                    }
                    
                    // Cập nhật nội dung đã xử lý
                    document.getElementById('result-processed').textContent = data.processed_content || text;
                    
                    // Cập nhật xác suất
                    const probabilities = data.probabilities || {};
                    updateProbabilityBar('prob-clean', probabilities.clean || 0);
                    updateProbabilityBar('prob-offensive', probabilities.offensive || 0);
                    updateProbabilityBar('prob-hate', probabilities.hate || 0);
                    updateProbabilityBar('prob-spam', probabilities.spam || 0);
                    
                    // Hiển thị kết quả
                    singleResult.style.display = 'block';
                } else {
                    // Hiển thị lỗi
                    document.getElementById('single-error-message').textContent = data.message || 'Đã xảy ra lỗi khi phân tích bình luận.';
                    singleError.style.display = 'block';
                }
            })
            .catch(error => {
                // Khôi phục nút submit
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                
                // Hiển thị lỗi
                document.getElementById('single-error-message').textContent = 'Đã xảy ra lỗi khi kết nối tới máy chủ: ' + error.message;
                singleError.style.display = 'block';
            });
        });
        
        // Xử lý form phân tích hàng loạt
        const batchForm = document.getElementById('batch-analysis-form');
        const batchResult = document.getElementById('batch-result');
        const batchError = document.getElementById('batch-error');
        
        batchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const batchText = document.getElementById('batch-text').value;
            const platform = document.getElementById('batch-platform').value;
            
            if (!batchText) {
                alert('Vui lòng nhập danh sách bình luận');
                return;
            }
            
            // Tách danh sách bình luận
            const lines = batchText.split('\n').filter(line => line.trim() !== '');
            
            if (lines.length > 20) {
                alert('Số lượng bình luận vượt quá giới hạn (tối đa 20 bình luận)');
                return;
            }
            
            // Chuẩn bị dữ liệu
            const comments = lines.map(line => ({
                text: line.trim(),
                platform: platform
            }));
            
            // Ẩn kết quả và lỗi cũ
            batchResult.style.display = 'none';
            batchError.style.display = 'none';
            
            // Hiển thị loading
            const submitBtn = batchForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Đang phân tích...';
            submitBtn.disabled = true;
            
            // Gửi request API
            fetch('{{ route("user.analysis.batch") }}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': '{{ csrf_token() }}'
                },
                body: JSON.stringify({
                    comments: comments
                })
            })
            .then(response => response.json())
            .then(data => {
                // Khôi phục nút submit
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                
                if (data.success) {
                    // Hiển thị kết quả
                    const resultsBody = document.getElementById('batch-results-body');
                    resultsBody.innerHTML = '';
                    
                    data.results.forEach((result, index) => {
                        const row = document.createElement('tr');
                        
                        // Cột #
                        const numCell = document.createElement('td');
                        numCell.textContent = index + 1;
                        row.appendChild(numCell);
                        
                        // Cột nội dung
                        const contentCell = document.createElement('td');
                        contentCell.textContent = result.text;
                        row.appendChild(contentCell);
                        
                        // Cột phân loại
                        const categoryCell = document.createElement('td');
                        const categoryBadge = document.createElement('span');
                        categoryBadge.className = 'badge bg-' + result.colorClass;
                        categoryBadge.textContent = result.predictionText;
                        categoryCell.appendChild(categoryBadge);
                        row.appendChild(categoryCell);
                        
                        // Cột độ tin cậy
                        const confidenceCell = document.createElement('td');
                        const confidenceProgress = document.createElement('div');
                        confidenceProgress.className = 'progress';
                        const confidenceBar = document.createElement('div');
                        confidenceBar.className = 'progress-bar bg-' + result.colorClass;
                        confidenceBar.style.width = parseFloat(result.confidence) * 100 + '%';
                        confidenceBar.textContent = result.confidencePercent;
                        confidenceProgress.appendChild(confidenceBar);
                        confidenceCell.appendChild(confidenceProgress);
                        row.appendChild(confidenceCell);
                        
                        // Cột từ khóa
                        const keywordsCell = document.createElement('td');
                        if (result.keywords && result.keywords.length > 0) {
                            result.keywords.forEach(keyword => {
                                const span = document.createElement('span');
                                span.className = 'badge bg-info me-1 mb-1';
                                span.textContent = keyword;
                                keywordsCell.appendChild(span);
                            });
                        } else {
                            const span = document.createElement('span');
                            span.className = 'badge bg-secondary';
                            span.textContent = 'Không có';
                            keywordsCell.appendChild(span);
                        }
                        row.appendChild(keywordsCell);
                        
                        resultsBody.appendChild(row);
                    });
                    
                    batchResult.style.display = 'block';
                } else {
                    // Hiển thị lỗi
                    document.getElementById('batch-error-message').textContent = data.message || 'Đã xảy ra lỗi khi phân tích hàng loạt bình luận.';
                    batchError.style.display = 'block';
                }
            })
            .catch(error => {
                // Khôi phục nút submit
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                
                // Hiển thị lỗi
                document.getElementById('batch-error-message').textContent = 'Đã xảy ra lỗi khi kết nối tới máy chủ: ' + error.message;
                batchError.style.display = 'block';
            });
        });
        
        // Hàm cập nhật thanh xác suất
        function updateProbabilityBar(id, probability) {
            const bar = document.getElementById(id);
            const percent = probability * 100;
            bar.style.width = percent + '%';
            bar.textContent = Math.round(percent * 10) / 10 + '%';
        }
        
        // Reset form
        document.querySelectorAll('button[type="reset"]').forEach(button => {
            button.addEventListener('click', function() {
                singleResult.style.display = 'none';
                singleError.style.display = 'none';
                batchResult.style.display = 'none';
                batchError.style.display = 'none';
            });
        });
    });
</script>
@endpush 