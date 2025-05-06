<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Danh sách bình luận - PDF</title>
    <style>
        body {
            font-family: DejaVu Sans, sans-serif;
            margin: 0;
            padding: 20px;
            color: #333;
            font-size: 12pt;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #3c4b64;
            margin-bottom: 5px;
            font-size: 24pt;
        }
        .header p {
            color: #777;
            margin-top: 0;
            font-size: 14pt;
        }
        .date {
            text-align: right;
            margin-bottom: 20px;
            font-style: italic;
            color: #777;
        }
        .summary-box {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 30px;
        }
        .summary-title {
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 14pt;
        }
        .summary-stats {
            display: flex;
            justify-content: space-between;
        }
        .stat-item {
            text-align: center;
            padding: 10px;
        }
        .stat-value {
            font-size: 18pt;
            font-weight: bold;
        }
        .stat-label {
            color: #777;
            font-size: 10pt;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }
        th, td {
            border: 1px solid #dee2e6;
            padding: 8px;
            text-align: left;
            vertical-align: top;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .badge {
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 10pt;
            font-weight: bold;
            text-align: center;
            display: inline-block;
        }
        .badge-success {
            background-color: #d1e7dd;
            color: #0f5132;
        }
        .badge-warning {
            background-color: #fff3cd;
            color: #856404;
        }
        .badge-danger {
            background-color: #f8d7da;
            color: #721c24;
        }
        .badge-info {
            background-color: #cff4fc;
            color: #055160;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            font-size: 10pt;
            color: #777;
            border-top: 1px solid #dee2e6;
            padding-top: 20px;
        }
        .comment-content {
            max-width: 300px;
            word-wrap: break-word;
        }
        .page-break {
            page-break-after: always;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Danh sách bình luận</h1>
        <p>Toxic Language Detector System</p>
    </div>

    <div class="date">
        Ngày xuất: {{ date('d/m/Y H:i:s') }}
    </div>

    <div class="summary-box">
        <div class="summary-title">Tổng quan</div>
        <div class="summary-stats">
            <div class="stat-item">
                <div class="stat-value">{{ $comments->count() }}</div>
                <div class="stat-label">Tổng số bình luận</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{{ $comments->where('prediction_text', 'clean')->count() }}</div>
                <div class="stat-label">Bình thường</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{{ $comments->where('prediction_text', 'offensive')->count() }}</div>
                <div class="stat-label">Xúc phạm</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{{ $comments->where('prediction_text', 'hate')->count() }}</div>
                <div class="stat-label">Phân biệt</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{{ $comments->where('prediction_text', 'spam')->count() }}</div>
                <div class="stat-label">Spam</div>
            </div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th width="5%">ID</th>
                <th width="30%">Nội dung</th>
                <th width="15%">Phân loại</th>
                <th width="15%">Từ khóa</th>
                <th width="15%">Nền tảng</th>
                <th width="20%">Thời gian</th>
            </tr>
        </thead>
        <tbody>
            @forelse($comments as $comment)
            <tr>
                <td>{{ $comment->id }}</td>
                <td class="comment-content">{{ $comment->content }}</td>
                <td>
                    @if($comment->prediction_text == 'clean')
                        <div class="badge badge-success">Bình thường</div>
                    @elseif($comment->prediction_text == 'offensive')
                        <div class="badge badge-warning">Xúc phạm</div>
                    @elseif($comment->prediction_text == 'hate')
                        <div class="badge badge-danger">Phân biệt</div>
                    @elseif($comment->prediction_text == 'spam')
                        <div class="badge badge-info">Spam</div>
                    @endif
                    <div style="margin-top: 5px; font-size: 10pt;">
                        {{ number_format($comment->confidence * 100, 1) }}%
                    </div>
                </td>
                <td>{{ $comment->keywords ? implode(", ", json_decode($comment->keywords, true)) : '' }}</td>
                <td>{{ ucfirst($comment->platform) }}</td>
                <td>{{ $comment->created_at->format('d/m/Y H:i:s') }}</td>
            </tr>
            @empty
            <tr>
                <td colspan="6" style="text-align: center;">Không có dữ liệu</td>
            </tr>
            @endforelse
        </tbody>
    </table>

    <div class="footer">
        <p>© {{ date('Y') }} Toxic Language Detector - Báo cáo được tạo tự động</p>
    </div>
</body>
</html> 