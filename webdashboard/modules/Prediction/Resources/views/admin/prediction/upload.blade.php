@extends('admin::layout')

@component('admin::components.page.header')
    @slot('title', trans('prediction::prediction.upload'))

    <li class="active">{{ trans('prediction::prediction.upload') }}</li>
@endcomponent

@section('content')
    <div id="flash-container"></div>
    <form id="csv-upload-form" class="form-horizontal" enctype="multipart/form-data">
        <div class="box box-primary">
            <div class="box-body">
                <div class="form-group">
                    <label class="col-md-3 control-label">CSV File</label>
                    <div class="col-md-9">
                        <input type="file" name="file" id="csv-file" class="form-control" accept=".csv" required>
                        <span class="help-block">{{ trans('prediction::prediction.placeholders.text') }}</span>
                    </div>
                </div>

                <div class="form-group">
                    <label class="col-md-3 control-label">{{ trans('prediction::prediction.text') }}</label>
                    <div class="col-md-9">
                        <input type="text" name="text_column" id="text_column" class="form-control" required>
                        <span class="help-block">{{ trans('prediction::prediction.placeholders.text') }}</span>
                    </div>
                </div>

                <div class="form-group">
                    <label class="col-md-3 control-label">{{ trans('prediction::prediction.platform') }}</label>
                    <div class="col-md-9">
                        <select name="platform" id="platform" class="form-control">
                            <option value="unknown">Unknown</option>
                            <option value="facebook">Facebook</option>
                            <option value="twitter">Twitter</option>
                            <option value="instagram">Instagram</option>
                            <option value="youtube">YouTube</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                </div>

                <div class="form-group">
                    <label class="col-md-3 control-label">{{ trans('prediction::prediction.save_results') }}</label>
                    <div class="col-md-9">
                        <div class="checkbox blue-checkbox">
                            <input type="checkbox" name="save_results" id="save_results" value="1" checked>
                            <label for="save_results">{{ trans('prediction::prediction.labels.save_database') }}</label>
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <div class="col-md-offset-3 col-md-9">
                        <button type="submit" class="btn btn-primary">
                            <i class="fa fa-check"></i> {{ trans('prediction::prediction.buttons.upload_analyze') }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </form>

    <div id="preview-box" class="box box-primary" style="display: none;">
        <div class="box-header with-border">
            <h3 class="box-title">{{ trans('prediction::prediction.labels.file_preview') }}</h3>
        </div>
        <div class="box-body">
            <div class="table-responsive">
                <table class="table table-bordered">
                    <thead id="preview-headers">
                    </thead>
                    <tbody id="preview-body">
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div id="analysis-progress" class="box box-primary" style="display: none;">
        <div class="box-header with-border">
            <h3 class="box-title">{{ trans('prediction::prediction.labels.analysis_progress') }}</h3>
        </div>
        <div class="box-body">
            <div class="progress">
                <div class="progress-bar progress-bar-striped active" role="progressbar" style="width: 100%"></div>
            </div>
            <p class="text-center">{{ trans('prediction::prediction.messages.processing') }}</p>
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
                    <div class="row mb-15">
                        <div class="col-md-12">
                            <div class="btn-group">
                                <button type="button" class="btn btn-default filter-btn" data-filter="all">{{ trans('prediction::prediction.categories.all') }}</button>
                                <button type="button" class="btn btn-success filter-btn" data-filter="clean">{{ trans('prediction::prediction.categories.clean') }}</button>
                                <button type="button" class="btn btn-warning filter-btn" data-filter="spam">{{ trans('prediction::prediction.categories.spam') }}</button>
                                <button type="button" class="btn btn-danger filter-btn" data-filter="offensive">{{ trans('prediction::prediction.categories.offensive') }}</button>
                                <button type="button" class="btn btn-primary filter-btn" data-filter="hate">{{ trans('prediction::prediction.categories.hate') }}</button>
                            </div>
                        </div>
                    </div>
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
        // File upload preview
        $('#csv-file').on('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Check if it's a CSV file
                if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
                    showFlashMessage('error', 'Please select a valid CSV file.');
                    $(this).val('');
                    return;
                }

                const reader = new FileReader();
                reader.onload = function(event) {
                    const csvData = event.target.result;
                    const lines = csvData.split('\n');
                    const headers = lines[0].split(',');

                    // Set the default text column to the first column
                    if (headers.length > 0) {
                        $('#text_column').val(headers[0].trim());
                    }

                    // Display headers
                    let headerRow = '<tr>';
                    headers.forEach(header => {
                        headerRow += `<th>${header.trim()}</th>`;
                    });
                    headerRow += '</tr>';
                    $('#preview-headers').html(headerRow);

                    // Display a few rows of data
                    let bodyRows = '';
                    const previewRowCount = Math.min(5, lines.length - 1);
                    for (let i = 1; i <= previewRowCount; i++) {
                        if (lines[i]) {
                            const cells = lines[i].split(',');
                            let row = '<tr>';
                            cells.forEach(cell => {
                                row += `<td>${cell.trim()}</td>`;
                            });
                            row += '</tr>';
                            bodyRows += row;
                        }
                    }
                    $('#preview-body').html(bodyRows);

                    // Show the preview box
                    $('#preview-box').show();
                };
                reader.readAsText(file);
            }
        });

        // Form submission
        $('#csv-upload-form').on('submit', function(e) {
            e.preventDefault();

            // Validate input
            const fileInput = $('#csv-file')[0];
            if (fileInput.files.length === 0) {
                showFlashMessage('error', 'Please select a CSV file to upload.');
                return;
            }

            const textColumn = $('#text_column').val().trim();
            if (!textColumn) {
                showFlashMessage('error', 'Please enter the text column name.');
                return;
            }

            // Tạo FormData từ form
            const formData = new FormData();

            // Thêm file vào FormData với tên chính xác là 'file'
            formData.append('file', fileInput.files[0]);

            // Thêm các trường khác
            formData.append('text_column', textColumn);
            formData.append('platform', $('#platform').val());
            formData.append('save_results', $('#save_results').is(':checked') ? 1 : 0);

            // Debug log
            console.log('Form submission - file attached:', fileInput.files[0].name);

            $.ajax({
                url: '{{ route("admin.prediction.upload.process") }}',
                type: 'POST',
                data: formData,
                contentType: false, // Để browser tự động thêm boundary cho multipart/form-data
                processData: false, // Không chuyển FormData thành query string
                cache: false,
                beforeSend: function() {
                    // Show loading state
                    $('#preview-box').hide();
                    $('#analysis-progress').show();
                    $('button[type="submit"]').prop('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> {{ trans("prediction::prediction.messages.processing") }}');
                    // Also show a flash message
                    showFlashMessage('info', '{{ trans("prediction::prediction.messages.processing") }}' + ($('#save_results').is(':checked') ? ' {{ trans("prediction::prediction.labels.saving_to_database") }}' : ''));
                },
                success: function(response) {
                    $('#analysis-progress').hide();

                    if (response.error) {
                        showFlashMessage('error', response.message || 'Error processing file.');
                        return;
                    }

                    if (response.results && response.results.length > 0) {
                        displayResults(response.results);
                        // Show success message
                        showFlashMessage('success', 'File processed successfully.');
                    } else {
                        showFlashMessage('warning', 'No results returned from analysis.');
                    }
                },
                error: function(xhr, status, error) {
                    $('#analysis-progress').hide();

                    // Parse error response
                    let errorMsg = 'Error processing file. Please try again.';
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response && response.message) {
                            errorMsg = response.message;
                        }
                    } catch (e) {
                        console.error('Error parsing response:', e);
                    }
                    showFlashMessage('error', errorMsg);
                },
                complete: function() {
                    $('button[type="submit"]').prop('disabled', false).html('<i class="fa fa-check"></i> {{ trans("prediction::prediction.buttons.upload_analyze") }}');
                }
            });
        });

        function displayResults(results) {
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

            // Scroll to results
            $('html, body').animate({
                scrollTop: $('#prediction-results').offset().top - 70
            }, 500);

            // Show success message
            const saveResults = $('#save_results').is(':checked');
            const successMessage = saveResults
                ? `{{ trans('prediction::prediction.messages.success_analyze') }} ${results.length} {{ trans('prediction::prediction.labels.comments_lowercase') }} {{ trans('prediction::prediction.messages.saved_to_database') }}.`
                : `{{ trans('prediction::prediction.messages.success_analyze') }} ${results.length} {{ trans('prediction::prediction.labels.comments_lowercase') }}.`;

            showFlashMessage('success', successMessage);

            // Apply filter functionality
            applyFilterFunctionality();
        }

        // Set up filter buttons functionality
        function applyFilterFunctionality() {
            $('.filter-btn').on('click', function() {
                const filter = $(this).data('filter');

                // Update active button
                $('.filter-btn').removeClass('active');
                $(this).addClass('active');

                if (filter === 'all') {
                    $('#results-table-body tr').show();
                } else {
                    $('#results-table-body tr').each(function() {
                        const prediction = $(this).find('td:nth-child(2) span').text().trim().toLowerCase();
                        if (prediction === filter) {
                            $(this).show();
                        } else {
                            $(this).hide();
                        }
                    });
                }
            });
        }

        // Flash message function
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

            // Scroll to top of the page to see the message
            $('html, body').animate({
                scrollTop: $('#flash-container').offset().top - 20
            }, 300);
        }

        function getPredictionClass(prediction) {
            switch(prediction.toLowerCase()) {
                case 'clean': return 'success';
                case 'spam': return 'warning';
                case 'offensive': return 'danger';
                case 'hate': return 'primary';
                default: return 'default';
            }
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
    .ml-10 { margin-left: 10px; }

    .input-group-addon {
        min-width: 40px;
        text-align: center;
    }

    .help-block, .help-text {
        font-size: 13px;
        color: #777;
        margin-top: 5px;
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
