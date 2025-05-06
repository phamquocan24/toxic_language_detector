<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>In danh sách bình luận</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/admin-lte/3.2.0/css/adminlte.min.css">
    <style>
        @media print {
            .no-print {
                display: none;
            }
            body {
                margin: 0;
                padding: 15px;
            }
            .page-header {
                margin-bottom: 20px;
            }
        }
        .badge-clean {
            background-color: #4CAF50;
            color: white;
        }
        .badge-offensive {
            background-color: #FF9800;
            color: white;
        }
        .badge-hate {
            background-color: #F44336;
            color: white;
        }
        .badge-spam {
            background-color: #9C27B0;
            color: white;
        }
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="page-header">
            <h1 class="text-center">Danh sách bình luận</h1>
            <p class="text-center">Ngày in: {{ date('d/m/Y H:i:s') }}</p>
        </div>
        
        <div class="no-print mb-3">
            <button onclick="window.print()" class="btn btn-primary">
                <i class="fas fa-print"></i> In ngay
            </button>
            <button onclick="window.close()" class="btn btn-default">
                <i class="fas fa-times"></i> Đóng
            </button>
        </div>
        
        <div class="card">
            <div class="card-body p-0">
                <table class="table table-striped table-bordered">
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
                            <td>
                                <span class="badge badge-{{ $comment->category }}">
                                    {{ ucfirst($comment->category) }}
                                </span>
                            </td>
                            <td>{{ number_format($comment->confidence_score * 100, 1) }}%</td>
                            <td>{{ $comment->user->name }}</td>
                            <td>{{ ucfirst($comment->platform) }}</td>
                            <td>{{ $comment->created_at->format('d/m/Y H:i') }}</td>
                        </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="text-center mt-4">
            <p>Tổng số: {{ count($comments) }} bình luận</p>
            <p>Toxic Detector Admin - {{ date('Y') }}</p>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/4.6.1/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Tự động mở hộp thoại in khi trang tải xong
            // window.print();
        });
    </script>
</body>
</html> 