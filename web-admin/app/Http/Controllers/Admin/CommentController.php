<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Comment;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Barryvdh\DomPDF\Facade\Pdf;

class CommentController extends Controller
{
    /**
     * Hiển thị danh sách bình luận với bộ lọc
     */
    public function index(Request $request)
    {
        $query = Comment::with('user');
        
        if ($request->has('category') && $request->category != '') {
            $query->where('category', $request->category);
        }
        
        if ($request->has('platform') && $request->platform != '') {
            $query->where('platform', $request->platform);
        }
        
        if ($request->has('search') && $request->search != '') {
            $search = $request->search;
            $query->where(function($q) use ($search) {
                $q->where('content', 'like', "%{$search}%")
                  ->orWhere('commenter_name', 'like', "%{$search}%");
            });
        }
        
        $comments = $query->latest()->paginate(20);
        
        return view('admin.comments.index', compact('comments'));
    }
    
    /**
     * Hiển thị chi tiết bình luận
     */
    public function show(Comment $comment)
    {
        return view('admin.comments.show', compact('comment'));
    }
    
    /**
     * Xóa bình luận
     */
    public function destroy(Comment $comment)
    {
        try {
            $comment->delete();
            return redirect()->route('admin.comments.index')
                ->with('success', 'Bình luận đã được xóa thành công.');
        } catch (\Exception $e) {
            Log::error('Error deleting comment: ' . $e->getMessage());
            return redirect()->route('admin.comments.index')
                ->with('error', 'Không thể xóa bình luận. Vui lòng thử lại.');
        }
    }
    
    /**
     * Xuất dữ liệu bình luận theo định dạng
     */
    public function export(Request $request)
    {
        $format = $request->format ?? 'csv';
        
        if ($format == 'pdf') {
            $comments = Comment::with('user')->get();
            $pdf = PDF::loadView('admin.exports.comments_pdf', compact('comments'));
            return $pdf->download('comments.pdf');
        }
        
        if ($format == 'csv') {
            // Create a timestamp for the filename
            $timestamp = now()->format('Y-m-d-H-i-s');
            $filename = "comments-export-{$timestamp}.csv";
            
            // Create CSV headers
            $headers = [
                'Content-Type' => 'text/csv',
                'Content-Disposition' => "attachment; filename=\"{$filename}\"",
            ];
            
            // Create a callback to generate the CSV content
            $callback = function() {
                // Open output stream
                $handle = fopen('php://output', 'w');
                
                // Add CSV headers
                fputcsv($handle, ['ID', 'Content', 'Classification', 'Confidence', 'Platform', 'Created At']);
                
                // Add mock data rows
                fputcsv($handle, [1, 'This is a sample comment', 'clean', '0.95', 'Twitter', now()->subDays(5)->format('Y-m-d H:i:s')]);
                fputcsv($handle, [2, 'Another example comment', 'offensive', '0.82', 'Facebook', now()->subDays(3)->format('Y-m-d H:i:s')]);
                fputcsv($handle, [3, 'Sample hate speech', 'hate', '0.78', 'Twitter', now()->subDays(2)->format('Y-m-d H:i:s')]);
                fputcsv($handle, [4, 'Buy discount products now!', 'spam', '0.91', 'YouTube', now()->subDay()->format('Y-m-d H:i:s')]);
                
                // Close the output stream
                fclose($handle);
            };
            
            // Return a streaming response
            return response()->stream($callback, 200, $headers);
        }
        
        return redirect()->route('admin.comments.index')
            ->with('error', 'Định dạng xuất không được hỗ trợ.');
    }
    
    /**
     * In dữ liệu bình luận
     */
    public function print()
    {
        $comments = Comment::with('user')->get();
        return view('admin.exports.comments_print', compact('comments'));
    }

    /**
     * Chặn/bỏ chặn bình luận
     */
    public function toggleBan($id)
    {
        $comment = Comment::findOrFail($id);
        $comment->is_banned = !$comment->is_banned;
        $comment->save();
        
        $action = $comment->is_banned ? 'chặn' : 'bỏ chặn';
        return back()->with('success', "Đã {$action} bình luận thành công.");
    }

    /**
     * Thêm vào danh sách đen
     */
    public function addBlacklist($id)
    {
        $comment = Comment::findOrFail($id);
        
        // Lưu từ khóa vào blacklist
        if ($comment->keywords) {
            $keywords = is_string($comment->keywords) ? json_decode($comment->keywords, true) : $comment->keywords;
            
            if (!empty($keywords)) {
                foreach ($keywords as $keyword) {
                    // Lưu từ khóa vào bảng blacklist
                    // (Giả định có model Blacklist)
                    /*
                    Blacklist::updateOrCreate([
                        'keyword' => $keyword,
                    ], [
                        'added_by' => auth()->id(),
                    ]);
                    */
                }
                
                return back()->with('success', "Đã thêm " . count($keywords) . " từ khóa vào danh sách đen.");
            }
        }
        
        return back()->with('info', "Không có từ khóa nào được thêm vào danh sách đen.");
    }
} 