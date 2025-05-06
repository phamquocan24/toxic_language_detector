<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <title>Danh sách bình luận</title>
    <style>
        body {
            font-family: DejaVu Sans, sans-serif;
            font-size: 12px;
        }
        h1 {
            text-align: center;
            font-size: 18px;
            margin-bottom: 20px;
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
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            font-size: 10px;
        }
        .clean {
            color: green;
        }
        .offensive {
            color: orange;
        }
        .hate {
            color: red;
        }
        .spam {
            color: purple;
        }
    </style>
</head>
<body>
    <h1>Danh sách bình luận</h1>
    
    <p>Ngày xuất: {{ date('d/m/Y H:i:s') }}</p>
    <p>Tổng số: {{ count($comments) }} bình luận</p>
    
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Nội dung</th>
                <th>Phân loại</th>
                <th>Độ tin cậy</th>
                <th>Người dùng</th>
                <th>Nền tảng</th>
                <th>Thời gian</th>
            </tr>
        </thead>
        <tbody>
            @foreach($comments as $comment)
            <tr>
                <td>{{ $comment->id }}</td>
                <td>{{ \Illuminate\Support\Str::limit($comment->content, 50) }}</td>
                <td class="{{ $comment->category }}">{{ ucfirst($comment->category) }}</td>
                <td>{{ number_format($comment->confidence_score * 100, 1) }}%</td>
                <td>{{ $comment->user->name }}</td>
                <td>{{ ucfirst($comment->platform) }}</td>
                <td>{{ $comment->created_at->format('d/m/Y H:i') }}</td>
            </tr>
            @endforeach
        </tbody>
    </table>
    
    <div class="footer">
        <p>Toxic Detector Admin - {{ date('Y') }}</p>
    </div>
</body>
</html> 