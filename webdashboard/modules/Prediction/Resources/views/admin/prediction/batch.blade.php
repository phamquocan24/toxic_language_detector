@extends('admin::layout')

@component('admin::components.page.header')
    @slot('title', trans('prediction::prediction.batch'))

    <li class="active">{{ trans('prediction::prediction.batch') }}</li>
@endcomponent

@section('content')
    <div id="flash-container"></div>

    <div class="row">
        <div class="col-md-12">
            <form id="batch-prediction-form">
                <div class="box box-primary">
                    <div class="box-header with-border">
                        <h3 class="box-title">
                            <i class="fa fa-comments"></i> {{ trans('prediction::prediction.labels.comments') }}
                        </h3>
                    </div>
                    <div class="box-body">
                        <div id="comments-container">
                            <div class="comment-item">
                                <div class="row">
                                    <div class="col-md-12 mb-15">
                                        <textarea class="form-control" name="comments[0][text]" rows="3" placeholder="{{ trans('prediction::prediction.placeholders.text') }}"></textarea>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-15">
                                        <div class="input-group">
                                            <span class="input-group-addon"><i class="fa fa-user"></i></span>
                                            <input type="text" class="form-control" name="comments[0][source_user_name]" placeholder="{{ trans('prediction::prediction.placeholders.source_user_name') }}">
                                        </div>
                                    </div>
                                    <div class="col-md-6 mb-15">
                                        <div class="input-group">
                                            <span class="input-group-addon"><i class="fa fa-link"></i></span>
                                            <input type="text" class="form-control" name="comments[0][source_url]" placeholder="{{ trans('prediction::prediction.placeholders.source_url') }}">
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-15">
                                        <select class="form-control" name="comments[0][platform]">
                                            <option value="unknown">Unknown</option>
                                            <option value="facebook">Facebook</option>
                                            <option value="twitter">Twitter</option>
                                            <option value="instagram">Instagram</option>
                                            <option value="youtube">YouTube</option>
                                            <option value="other">Other</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="mb-15">
                            <button type="button" id="add-comment" class="btn btn-default">
                                <i class="fa fa-plus"></i> {{ trans('prediction::prediction.buttons.add_comment') }}
                            </button>
                        </div>

                        <div class="action-row">
                            <div class="save-results-option">
                                <div class="checkbox blue-checkbox">
                                    <input type="checkbox" name="save_results" id="save_results" value="1">
                                    <label for="save_results">{{ trans('prediction::prediction.labels.save_database') }}</label>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-primary">
                                <i class="fa fa-check"></i> {{ trans('prediction::prediction.buttons.analyze') }}
                            </button>
                        </div>
                    </div>
                </div>
            </form>
        </div>
    </div>

    <div id="prediction-results" class="row" style="display: none;">
        <div class="col-md-12">
            <div class="box box-primary">
                <div class="box-header with-border">
                    <h3 class="box-title">
                        <i class="fa fa-list"></i> {{ trans('prediction::prediction.labels.results') }}
                    </h3>
                </div>
                <div class="box-body">
                    <div class="table-responsive">
                        <table class="table table-striped table-hover">
                            <thead>
                                <tr>
                                    <th>{{ trans('prediction::prediction.text') }}</th>
                                    <th width="120">{{ trans('prediction::prediction.prediction') }}</th>
                                    <th width="120">{{ trans('prediction::prediction.confidence') }}</th>
                                    <th>{{ trans('prediction::prediction.keywords') }}</th>
                                    <th width="100" class="text-center">{{ trans('prediction::prediction.buttons.details') }}</th>
                                </tr>
                            </thead>
                            <tbody id="results-table-body">
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
@endsection

@push('scripts')
<script>
    $(() => {
        let commentCount = 1;

        // Add new comment form
        $('#add-comment').on('click', function() {
            const newComment = `
                <div class="comment-item">
                    <hr>
                    <div class="row">
                        <div class="col-md-12 mb-15">
                            <textarea class="form-control" name="comments[${commentCount}][text]" rows="3" placeholder="{{ trans('prediction::prediction.placeholders.text') }}"></textarea>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-15">
                            <div class="input-group">
                                <span class="input-group-addon"><i class="fa fa-user"></i></span>
                                <input type="text" class="form-control" name="comments[${commentCount}][source_user_name]" placeholder="{{ trans('prediction::prediction.placeholders.source_user_name') }}">
                            </div>
                        </div>
                        <div class="col-md-6 mb-15">
                            <div class="input-group">
                                <span class="input-group-addon"><i class="fa fa-link"></i></span>
                                <input type="text" class="form-control" name="comments[${commentCount}][source_url]" placeholder="{{ trans('prediction::prediction.placeholders.source_url') }}">
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-15">
                            <select class="form-control" name="comments[${commentCount}][platform]">
                                <option value="unknown">Unknown</option>
                                <option value="facebook">Facebook</option>
                                <option value="twitter">Twitter</option>
                                <option value="instagram">Instagram</option>
                                <option value="youtube">YouTube</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                        <div class="col-md-6 mb-15 text-right">
                            <button type="button" class="btn btn-danger remove-comment">
                                <i class="fa fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;

            $('#comments-container').append(newComment);
            commentCount++;
        });

        // Remove comment form
        $(document).on('click', '.remove-comment', function() {
            $(this).closest('.comment-item').remove();
        });

        // Form submission
        $('#batch-prediction-form').on('submit', function(e) {
            e.preventDefault();

            // Validate form - check if at least one comment is provided
            let hasComments = false;
            $('textarea[name^="comments"]').each(function() {
                if ($(this).val().trim() !== '') {
                    hasComments = true;
                    return false; // Break the loop
                }
            });

            if (!hasComments) {
                showFlashMessage('error', '{{ trans("prediction::prediction.messages.no_comments") }}');
                return;
            }

            const formData = $(this).serializeArray();
            const comments = [];

            // Process form data
            formData.forEach(item => {
                if (item.name.includes('comments')) {
                    const matches = item.name.match(/comments\[(\d+)\]\[([a-z_]+)\]/);
                    if (matches) {
                        const index = matches[1];
                        const field = matches[2];

                        if (!comments[index]) {
                            comments[index] = {};
                        }

                        comments[index][field] = item.value;
                    }
                }
            });

            // Filter out empty objects and undefined entries
            const filteredComments = comments.filter(comment => comment && comment.text);

            const saveResults = $('#save_results').is(':checked');

            // Show debug message for save option
            console.log('Save to database option:', saveResults);

            $.ajax({
                url: '{{ route("admin.prediction.batch.process") }}',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    comments: filteredComments,
                    save_results: saveResults,
                    _token: '{{ csrf_token() }}'
                }),
                beforeSend: function() {
                    // Show loading state
                    $('button[type="submit"]').prop('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> {{ trans("prediction::prediction.messages.processing") }}');
                    // Also show a flash message
                    showFlashMessage('info', '{{ trans("prediction::prediction.messages.processing") }}' + (saveResults ? ' {{ trans("prediction::prediction.labels.saving_to_database") }}' : ''));
                },
                success: function(response) {
                    displayResults(response.results, saveResults);

                    // Scroll to results
                    $('html, body').animate({
                        scrollTop: $('#prediction-results').offset().top - 70
                    }, 500);
                },
                error: function(xhr) {
                    // Show flash message
                    let errorMsg = 'Error processing request. Please try again.';

                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response && response.message) {
                            errorMsg = response.message;
                        }
                    } catch (e) {
                        console.error('Error parsing response:', e);
                    }

                    showFlashMessage('error', errorMsg);
                    console.error(xhr.responseText);
                },
                complete: function() {
                    $('button[type="submit"]').prop('disabled', false).html('<i class="fa fa-check"></i> {{ trans("prediction::prediction.buttons.analyze") }}');
                }
            });
        });

        function displayResults(results, saveToDatabase) {
            $('#results-table-body').empty();

            results.forEach((result, index) => {
                // Truncate text if too long for display
                const displayText = result.text.length > 100 ?
                    result.text.substring(0, 100) + '...' :
                    result.text;

                const row = `
                    <tr>
                        <td>${displayText}</td>
                        <td>
                            <span class="label label-${getPredictionClass(result.prediction_text)}">
                                ${result.prediction_text}
                            </span>
                        </td>
                        <td>${(result.confidence * 100).toFixed(2)}%</td>
                        <td>
                            ${result.keywords ? result.keywords.map(keyword =>
                                `<span class="label label-default keyword-tag">${keyword}</span>`
                            ).join(' ') : ''}
                        </td>
                        <td class="text-center">
                            <button type="button" class="btn btn-xs btn-info show-details"
                                   data-toggle="modal" data-target="#detailsModal"
                                   data-result='${JSON.stringify(result)}'>
                                <i class="fa fa-eye"></i> {{ trans('prediction::prediction.buttons.details') }}
                            </button>
                        </td>
                    </tr>
                `;

                $('#results-table-body').append(row);
            });

            $('#prediction-results').show();

            // Show success message
            const successMessage = saveToDatabase
                ? `{{ trans('prediction::prediction.messages.success_analyze') }} ${results.length} {{ trans('prediction::prediction.labels.comments_lowercase') }} {{ trans('prediction::prediction.messages.saved_to_database') }}.`
                : `{{ trans('prediction::prediction.messages.success_analyze') }} ${results.length} {{ trans('prediction::prediction.labels.comments_lowercase') }}.`;

            showFlashMessage('success', successMessage);
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

        // Flash message function
        function showFlashMessage(type, message) {
            // Xóa thông báo cũ nếu có
            $('.alert').remove();

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

            // Chèn thông báo vào đầu content
            $('#flash-container').html(alertHtml);

            // Scroll to top of the page to see the message
            $('html, body').animate({
                scrollTop: $('#flash-container').offset().top - 20
            }, 300);
        }

        // Function to format similarity class
        function getSimilarityClass(similarity) {
            if (similarity >= 0.8) return 'success';
            if (similarity >= 0.6) return 'info';
            if (similarity >= 0.4) return 'warning';
            return 'default';
        }

        // Details modal
        $('body').append(`
            <div class="modal fade" id="detailsModal" tabindex="-1" role="dialog">
                <div class="modal-dialog modal-lg" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                            <h4 class="modal-title">{{ trans('prediction::prediction.labels.prediction_details') }}</h4>
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
        `);

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
                        <div class="well">${comment.text || 'No content available'}</div>
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
                </div>
            `;
        }
    });
</script>

<style>
    /* Form & general styling */
    .mb-15 { margin-bottom: 15px; }
    .pt-5 { padding-top: 5px; }

    .input-group-addon {
        min-width: 40px;
        text-align: center;
    }

    .comment-item {
        margin-bottom: 20px;
    }

    .help-block, .help-text {
        font-size: 13px;
        color: #777;
        margin-top: 5px;
    }

    .checkbox label, .checkbox-inline {
        font-weight: normal;
    }

    /* Action row styling */
    .action-row {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        margin-bottom: 15px;
    }

    .save-results-option {
        margin-right: 15px;
        display: flex;
        align-items: center;
    }

    /* Custom blue checkbox styling */
    .blue-checkbox input[type="checkbox"] {
        position: relative;
        appearance: none;
        -webkit-appearance: none;
        width: 16px;
        height: 16px;
        border: 1px solid #ccc;
        border-radius: 3px;
        outline: none;
        vertical-align: middle;
        margin-right: 6px;
        margin-top: -2px;
    }

    .blue-checkbox input[type="checkbox"]:checked {
        background-color: #337ab7;
        border-color: #337ab7;
    }

    .blue-checkbox input[type="checkbox"]:checked:after {
        content: '';
        position: absolute;
        left: 5px;
        top: 2px;
        width: 5px;
        height: 10px;
        border: solid white;
        border-width: 0 2px 2px 0;
        transform: rotate(45deg);
    }

    /* Modal styles */
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

    /* Flash alert styling */
    #flash-container {
        margin-bottom: 20px;
    }
</style>
@endpush
