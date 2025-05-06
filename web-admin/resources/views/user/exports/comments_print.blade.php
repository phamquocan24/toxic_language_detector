<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Danh sách bình luận - In</title>
    <style>
        body {
            font-family: 'Roboto', Arial, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 15px;
        }
        .title {
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .subtitle {
            font-size: 16px;
            color: #555;
        }
        .logo {
            max-width: 120px;
            margin-bottom: 10px;
        }
        .info-section {
            margin-bottom: 15px;
        }
        .info-row {
            display: flex;
            margin-bottom: 5px;
        }
        .info-label {
            font-weight: bold;
            width: 120px;
        }
        .table-container {
            width: 100%;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .category {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            text-align: center;
        }
        .clean {
            background-color: #d4edda;
            color: #155724;
        }
        .offensive {
            background-color: #fff3cd;
            color: #856404;
        }
        .hate {
            background-color: #f8d7da;
            color: #721c24;
        }
        .spam {
            background-color: #d6d8db;
            color: #383d41;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            font-size: 12px;
            color: #666;
            border-top: 1px solid #ddd;
            padding-top: 15px;
        }
        @media print {
            body {
                padding: 0;
                margin: 0;
            }
            .no-print {
                display: none;
            }
            .print-button {
                display: none;
            }
        }
        .print-button {
            background-color: #4e73df;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .print-button:hover {
            background-color: #3a5fc8;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">Danh Sách Bình Luận</div>
        <div class="subtitle">Toxic Language Detector</div>
    </div>

    <button class="print-button no-print" onclick="window.print()">In danh sách</button>

    <div class="info-section">
        <div class="info-row">
            <div class="info-label">Ngày tạo:</div>
            <div>{{ date('d/m/Y H:i:s') }}</div>
        </div>
        <div class="info-row">
            <div class="info-label">Người dùng:</div>
            <div>{{ auth()->user()->name }}</div>
        </div>
        <div class="info-row">
            <div class="info-label">Tổng số:</div>
            <div>{{ count($comments) }} bình luận</div>
        </div>
    </div>

    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nội dung</th>
                    <th>Phân loại</th>
                    <th>Từ khóa</th>
                    <th>Nền tảng</th>
                    <th>Thời gian</th>
                </tr>
            </thead>
            <tbody>
                @forelse($comments as $comment)
                <tr>
                    <td>{{ $comment->id }}</td>
                    <td>{{ $comment->content }}</td>
                    <td>
                        @php
                            $categoryClass = '';
                            $categoryText = '';
                            
                            switch($comment->prediction) {
                                case 'clean':
                                    $categoryClass = 'clean';
                                    $categoryText = 'Bình thường';
                                    break;
                                case 'offensive':
                                    $categoryClass = 'offensive';
                                    $categoryText = 'Xúc phạm';
                                    break;
                                case 'hate':
                                    $categoryClass = 'hate';
                                    $categoryText = 'Phân biệt';
                                    break;
                                case 'spam':
                                    $categoryClass = 'spam';
                                    $categoryText = 'Spam';
                                    break;
                                default:
                                    $categoryClass = '';
                                    $categoryText = $comment->prediction;
                            }
                        @endphp
                        <span class="category {{ $categoryClass }}">{{ $categoryText }}</span>
                    </td>
                    <td>{{ $comment->keywords ?? 'N/A' }}</td>
                    <td>{{ $comment->platform ?? 'N/A' }}</td>
                    <td>{{ $comment->created_at->format('d/m/Y H:i') }}</td>
                </tr>
                @empty
                <tr>
                    <td colspan="6" style="text-align: center">Không có bình luận nào</td>
                </tr>
                @endforelse
            </tbody>
        </table>
    </div>

    <div class="footer">
        <p>© {{ date('Y') }} Toxic Language Detector - In lúc {{ date('d/m/Y H:i:s') }}</p>
    </div>

    <script>
        window.onload = function() {
            // Auto-print when page loads
            // Uncomment the line below to enable auto-print
            // window.print();
        }
    </script>
</body>
</html> 