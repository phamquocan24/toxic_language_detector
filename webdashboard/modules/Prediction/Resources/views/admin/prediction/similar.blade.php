@extends('admin::layout')

@component('admin::components.page.header')
    @slot('title', trans('prediction::prediction.similar'))

    <li class="active">{{ trans('prediction::prediction.similar') }}</li>
@endcomponent

@section('content')
    <div id="flash-container"></div>

    <div class="box box-primary">
        <div class="box-body">
            <form id="similar-comments-form">
                <div class="form-group row">
                    <label class="col-md-2 text-md-right">{{ trans('prediction::prediction.comment_id') }}</label>
                    <div class="col-md-10">
                        <input type="number" id="comment_id" name="comment_id" class="form-control" required min="1" placeholder="{{ trans('prediction::prediction.placeholders.comment_id') }}">
                    </div>
                </div>

                <div class="form-group row">
                    <label class="col-md-2 text-md-right">{{ trans('prediction::prediction.limit') }}</label>
                    <div class="col-md-10">
                        <input type="number" id="limit" name="limit" class="form-control" value="10" min="1" max="100" placeholder="{{ trans('prediction::prediction.placeholders.limit') }}">
                    </div>
                </div>

                <div class="form-group row">
                    <label class="col-md-2 text-md-right">{{ trans('prediction::prediction.similarity_threshold') }}</label>
                    <div class="col-md-10">
                        <input type="range" id="threshold" name="threshold" class="form-control" min="0" max="1" step="0.01" value="0.7" placeholder="{{ trans('prediction::prediction.placeholders.threshold') }}">
                        <div class="row">
                            <div class="col-md-11">
                                <span class="help-block">{{ trans('prediction::prediction.placeholders.threshold') }}</span>
                            </div>
                            <div class="col-md-1 text-right">
                                <span id="threshold-value">0.7</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="form-group row">
                    <div class="col-md-10 offset-md-2">
                        <button type="submit" class="btn btn-primary">
                            <i class="fa fa-search"></i> {{ trans('prediction::prediction.buttons.find_similar') }}
                        </button>
                    </div>
                </div>
            </form>
        </div>
    </div>

    <div id="source-comment-box" class="box box-primary" style="display: none;">
        <div class="box-header with-border">
            <h3 class="box-title">{{ trans('prediction::prediction.labels.source_comment') }}</h3>
        </div>
        <div class="box-body">
            <div class="row">
                <div class="col-md-12">
                    <div class="well">
                        <h4 id="source-text"></h4>
                        <div class="row">
                            <div class="col-md-4">
                                <span class="label label-default" id="source-prediction"></span>
                            </div>
                            <div class="col-md-8 text-right">
                                <small id="source-metadata"></small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div id="similar-comments-box" class="box box-primary" style="display: none;">
        <div class="box-header with-border">
            <h3 class="box-title">{{ trans('prediction::prediction.labels.similar_comments') }}</h3>
        </div>
        <div class="box-body">
            <div id="no-results-message" class="text-center" style="display: none;">
                <h4>{{ trans('prediction::prediction.messages.no_similar_comments') }}</h4>
                <p>{{ trans('prediction::prediction.messages.search_no_results') }}</p>
            </div>

            <div id="similar-comments-container"></div>
        </div>
    </div>
@endsection

@push('scripts')
<script>
    $(() => {
        // Hàm hiển thị thông báo flash
        function showFlashMessage(type, message) {
            // Xóa thông báo cũ nếu có
            $('#flash-container').empty();

            // Xác định class và icon dựa trên loại thông báo
            const alertClass = type === 'error' ? 'alert-danger' :
                              type === 'success' ? 'alert-success' :
                              type === 'warning' ? 'alert-warning' : 'alert-info';

            // Tạo HTML thông báo theo mẫu mới
            const alertHtml = `
                <div class="alert ${alertClass} fade in alert-dismissible clearfix">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M12 2C6.49 2 2 6.49 2 12C2 17.51 6.49 22 12 22C17.51 22 22 17.51 22 12C22 6.49 17.51 2 12 2ZM11.25 8C11.25 7.59 11.59 7.25 12 7.25C12.41 7.25 12.75 7.59 12.75 8V13C12.75 13.41 12.41 13.75 12 13.75C11.59 13.75 11.25 13.41 11.25 13V8ZM12.92 16.38C12.87 16.51 12.8 16.61 12.71 16.71C12.61 16.8 12.5 16.87 12.38 16.92C12.26 16.97 12.13 17 12 17C11.87 17 11.74 16.97 11.62 16.92C11.5 16.87 11.39 16.8 11.29 16.71C11.2 16.61 11.13 16.51 11.08 16.38C11.03 16.26 11 16.13 11 16C11 15.87 11.03 15.74 11.08 15.62C11.13 15.5 11.2 15.39 11.29 15.29C11.39 15.2 11.5 15.13 11.62 15.08C11.86 14.98 12.14 14.98 12.38 15.08C12.5 15.13 12.61 15.2 12.71 15.29C12.8 15.39 12.87 15.5 12.92 15.62C12.97 15.74 13 15.87 13 16C13 16.13 12.97 16.26 12.92 16.38Z" fill="#555555" />
                    </svg>

                    <button type="button" class="close" data-dismiss="alert" aria-hidden="true">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path d="M5.00082 14.9995L14.9999 5.00041" stroke="#555555" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                            <path d="M14.9999 14.9996L5.00082 5.00049" stroke="#555555" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                        </svg>
                    </button>

                    <span class="alert-text">${message}</span>
                </div>
            `;

            // Chèn thông báo vào container
            $('#flash-container').html(alertHtml);
        }

        // Update threshold value display
        $('#threshold').on('input', function() {
            $('#threshold-value').text($(this).val());
        });

        // Initialize threshold value
        $('#threshold-value').text($('#threshold').val());

        // Form submission
        $('#similar-comments-form').on('submit', function(e) {
            e.preventDefault();

            const commentId = $('#comment_id').val();
            const limit = $('#limit').val();
            const threshold = $('#threshold').val();

            $.ajax({
                url: "{{ route('admin.prediction.similar.get', ['commentId' => '__commentId__']) }}".replace('__commentId__', commentId),
                type: 'GET',
                data: {
                    limit: limit,
                    threshold: threshold
                },
                beforeSend: function() {
                    // Show loading state
                    $('button[type="submit"]').prop('disabled', true).html(`<i class="fa fa-spinner fa-spin"></i> {{ trans('prediction::prediction.messages.processing') }}`);
                    $('#source-comment-box, #similar-comments-box').hide();
                },
                success: function(response) {
                    // Hiển thị comment và các comment tương tự
                    displaySourceComment(response.source_comment);
                    displaySimilarComments(response.similar_comments, response.count);

                    // Hiển thị thông báo thành công nếu tìm thấy comment
                    if (response.source_comment) {
                        const commentText = response.source_comment.content || response.source_comment.text || '';
                        const truncatedText = commentText.length > 30 ? commentText.substring(0, 30) + '...' : commentText;

                        if (response.count > 0) {
                            showFlashMessage('success', `Đã tìm thấy ${response.count} comment tương tự cho comment "${truncatedText}"`);
                        } else {
                            showFlashMessage('info', `Đã tìm thấy comment "${truncatedText}" nhưng không có comment tương tự nào`);
                        }
                    }
                },
                error: function(xhr) {
                    // Hide loading state
                    $('#source-comment-box, #similar-comments-box').hide();

                    // Handle 404 error - Comment not found
                    if (xhr.status === 404) {
                        let errorMsg = `{{ trans('prediction::prediction.messages.comment_not_found') }}`;

                        // Extract detailed message from API if available
                        try {
                            const response = JSON.parse(xhr.responseText);
                            if (response && response.detail) {
                                errorMsg = response.detail;
                            }
                        } catch (e) {
                            console.error('Error parsing response:', e);
                        }

                        // Show error message
                        showFlashMessage('error', errorMsg);
                    } else {
                        // Other errors
                        showFlashMessage('error', 'Lỗi xử lý yêu cầu. Vui lòng thử lại sau.');
                        console.error(xhr.responseText);
                    }
                },
                complete: function() {
                    $('button[type="submit"]').prop('disabled', false).html(`<i class="fa fa-search"></i> {{ trans('prediction::prediction.buttons.find_similar') }}`);
                }
            });
        });

        function displaySourceComment(comment) {
            $('#source-text').text(comment.content || comment.text || 'No text available');

            // Display prediction if available
            if (comment.prediction_text) {
                $('#source-prediction').text(comment.prediction_text);
                $('#source-prediction').removeClass().addClass(`label label-${getPredictionClass(comment.prediction_text)}`);
            } else {
                $('#source-prediction').text('Unknown');
                $('#source-prediction').removeClass().addClass('label label-default');
            }

            // Display metadata if available
            let metadata = [];
            if (comment.platform) {
                metadata.push(`Platform: ${comment.platform}`);
            }
            if (comment.source_user_name) {
                metadata.push(`User: ${comment.source_user_name}`);
            }
            if (comment.timestamp) {
                metadata.push(`Time: ${new Date(comment.timestamp).toLocaleString()}`);
            }

            $('#source-metadata').text(metadata.join(' | '));
            $('#source-comment-box').show();
        }

        function displaySimilarComments(comments, count) {
            const container = $('#similar-comments-container');
            container.empty();

            if (count === 0 || !comments || comments.length === 0) {
                $('#no-results-message').show();
                $('#similar-comments-box').show();
                return;
            }

            $('#no-results-message').hide();

            comments.forEach((comment, index) => {
                const similarity = comment.similarity || 0;
                const similarityPercentage = (similarity * 100).toFixed(2);

                const similarityClass = getSimilarityClass(similarity);

                const commentHtml = `
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            <div class="row">
                                <div class="col-md-8">
                                    <span class="label label-${getPredictionClass(comment.prediction_text)}">
                                        ${comment.prediction_text || 'Unknown'}
                                    </span>
                                    <span class="text-muted ml-10">
                                        <small>
                                            ${comment.platform ? `Platform: ${comment.platform} | ` : ''}
                                            ${comment.source_user_name ? `User: ${comment.source_user_name} | ` : ''}
                                            ${comment.timestamp ? `Time: ${new Date(comment.timestamp).toLocaleString()}` : ''}
                                        </small>
                                    </span>
                                </div>
                                <div class="col-md-4 text-right">
                                    <span class="badge badge-${similarityClass}">
                                        {{ trans('prediction::prediction.similarity_threshold') }}: ${similarityPercentage}%
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="panel-body">
                            <p>${comment.content || comment.text || 'No text available'}</p>
                        </div>
                        <div class="panel-footer text-right">
                            <button class="btn btn-xs btn-info show-details"
                                data-toggle="modal"
                                data-target="#detailsModal"
                                       data-result='${JSON.stringify(comment)}'>
                                <i class="fa fa-eye"></i> {{ trans('prediction::prediction.buttons.details') }}
                                </button>
                        </div>
                    </div>
                `;

                container.append(commentHtml);
            });

            $('#similar-comments-box').show();
        }

        function getSimilarityClass(similarity) {
            if (similarity >= 0.8) return 'success';
            if (similarity >= 0.6) return 'info';
            if (similarity >= 0.4) return 'warning';
            return 'default';
        }

        function getPredictionClass(prediction) {
            switch(prediction.toLowerCase()) {
                case 'clean': return 'success';
                case 'spam': return 'warning';
                case 'offensive': return 'danger';
                case 'hate': return 'danger';
                default: return 'default';
            }
        }

        // Thêm xử lý sự kiện khi click vào nút Details
        $(document).on('click', '.show-details', function() {
            const result = $(this).data('result');

            // Format dữ liệu vào HTML có cấu trúc thay vì JSON
            const detailsHTML = formatCommentDetails(result);
            $('#details-content').html(detailsHTML);
        });

        // Hàm định dạng dữ liệu comment thành HTML có cấu trúc
        function formatCommentDetails(comment) {
            const confidence = comment.confidence ? (comment.confidence * 100).toFixed(2) + '%' : 'N/A';
            const timestamp = comment.created_at || comment.timestamp || 'N/A';
            const formattedDate = timestamp !== 'N/A' ? new Date(timestamp).toLocaleString() : 'N/A';

            return `
                <div class="comment-details">
                    <div class="detail-section">
                        <h4>{{ trans('prediction::prediction.content') }}</h4>
                        <div class="well">${comment.content || comment.text || 'No content available'}</div>
                    </div>

                    <div class="detail-section">
                        <div class="row detail-row">
                            <div class="col-md-6">
                                <span class="detail-label">{{ trans('prediction::prediction.prediction') }}:</span>
                                <span class="label label-${getPredictionClass(comment.prediction_text)}">
                                    ${comment.prediction_text || 'Unknown'}
                                </span>
                            </div>
                            <div class="col-md-6">
                                <span class="detail-label">{{ trans('prediction::prediction.confidence') }}:</span>
                                <span>${confidence}</span>
                            </div>
                        </div>
                    </div>

                    <div class="detail-section">
                        <div class="row detail-row">
                            <div class="col-md-6">
                                <span class="detail-label">{{ trans('prediction::prediction.platform') }}:</span>
                                <span>${comment.platform || 'Unknown'}</span>
                            </div>
                            <div class="col-md-6">
                                <span class="detail-label">ID:</span>
                                <span>${comment.id || 'N/A'}</span>
                            </div>
                        </div>
                    </div>

                    <div class="detail-section">
                        <div class="row detail-row">
                            <div class="col-md-6">
                                <span class="detail-label">{{ trans('prediction::prediction.source_user_name') }}:</span>
                                <span>${comment.source_user_name || 'N/A'}</span>
                            </div>
                            <div class="col-md-6">
                                <span class="detail-label">{{ trans('prediction::prediction.timestamp') }}:</span>
                                <span>${formattedDate}</span>
                            </div>
                        </div>
                    </div>

                    ${comment.keywords ? `
                    <div class="detail-section">
                        <h4>{{ trans('prediction::prediction.keywords') }}</h4>
                        <div>
                            ${Array.isArray(comment.keywords) ? comment.keywords.map(keyword =>
                                `<span class="label label-default keyword-tag">${keyword}</span>`
                            ).join('') : 'N/A'}
                        </div>
                    </div>
                    ` : ''}

                    ${comment.similarity ? `
                    <div class="detail-section">
                        <h4>{{ trans('prediction::prediction.similarity_threshold') }}</h4>
                        <div class="progress">
                            <div class="progress-bar progress-bar-${getSimilarityClass(comment.similarity)}" role="progressbar"
                                 style="width: ${(comment.similarity * 100).toFixed(2)}%;">
                                ${(comment.similarity * 100).toFixed(2)}%
                            </div>
                        </div>
                    </div>
                    ` : ''}
                </div>
            `;
        }
    });
</script>

<style>
    /* Cập nhật style cho modal chi tiết */
    .comment-details .detail-section {
        margin-bottom: 15px;
    }
    .comment-details h4 {
        font-size: 16px;
        color: #337ab7;
        margin-bottom: 10px;
        font-weight: bold;
        }
    .comment-details .detail-row {
        margin-bottom: 5px;
    }
    .comment-details .detail-label {
        font-weight: bold;
        color: #337ab7;
        margin-right: 5px;
    }
    .comment-details .well {
        margin-bottom: 0;
        background-color: #f9f9f9;
    }
    .keyword-tag {
        margin-right: 5px;
        margin-bottom: 5px;
        display: inline-block;
    }
    .modal-lg {
        width: 90%;
        max-width: 900px;
    }
</style>

<!-- Details Modal -->
            <div class="modal fade" id="detailsModal" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-lg" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                <h4 class="modal-title">{{ trans('prediction::prediction.labels.comment_details') }}</h4>
                        </div>
                        <div class="modal-body">
                <div id="details-content"></div>
                        </div>
                        <div class="modal-footer">
                <button type="button" class="btn btn-default" data-dismiss="modal">{{ trans('prediction::prediction.buttons.close') }}</button>
                        </div>
                    </div>
                </div>
            </div>
@endpush