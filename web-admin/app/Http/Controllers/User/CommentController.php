<?php

namespace App\Http\Controllers\User;

use App\Http\Controllers\Controller;
use App\Models\Comment;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Barryvdh\DomPDF\Facade\Pdf;

class CommentController extends Controller
{
    /**
     * Hiển thị danh sách bình luận của người dùng hiện tại
     */
    public function index(Request $request)
    {
        $query = Comment::where('user_id', Auth::id());

        // Apply filters
        if ($request->has('search') && !empty($request->search)) {
            $query->where('content', 'like', '%' . $request->search . '%');
        }

        if ($request->has('category') && !empty($request->category)) {
            $query->where('category', $request->category);
        }

        if ($request->has('platform') && !empty($request->platform)) {
            $query->where('platform', $request->platform);
        }

        $comments = $query->orderBy('created_at', 'desc')->paginate(10);

        return view('user.comments.index', compact('comments'));
    }
    
    /**
     * Hiển thị chi tiết bình luận
     */
    public function show($id)
    {
        $comment = Comment::where('user_id', Auth::id())->findOrFail($id);
        return view('user.comments.show', compact('comment'));
    }
    
    /**
     * Xuất dữ liệu bình luận theo định dạng
     */
    public function export(Request $request)
    {
        $user = Auth::user();
        $format = $request->format ?? 'pdf';
        
        if ($format == 'pdf') {
            $comments = Comment::where('user_id', $user->id)->get();
            $pdf = PDF::loadView('user.exports.comments_pdf', compact('comments'));
            return $pdf->download('my-comments.pdf');
        }
        
        return redirect()->route('user.comments.index')
            ->with('error', 'Định dạng xuất không được hỗ trợ.');
    }
    
    /**
     * In dữ liệu bình luận
     */
    public function print()
    {
        $user = Auth::user();
        $comments = Comment::where('user_id', $user->id)->get();
        return view('user.exports.comments_print', compact('comments'));
    }

    /**
     * Submit feedback for a comment.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function feedback(Request $request, $id)
    {
        $comment = Comment::where('user_id', Auth::id())->findOrFail($id);
        
        $request->validate([
            'feedback' => 'nullable|in:correct,incorrect',
            'feedback_note' => 'nullable|string|max:500',
        ]);
        
        $comment->feedback = $request->feedback;
        $comment->feedback_note = $request->feedback_note;
        $comment->save();
        
        return redirect()->route('user.comments.show', $comment->id)
            ->with('success', 'Phản hồi của bạn đã được ghi nhận. Cảm ơn!');
    }

    /**
     * Export comments to PDF.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function exportPdf(Request $request)
    {
        $query = Comment::where('user_id', Auth::id());

        // Apply filters
        if ($request->has('search') && !empty($request->search)) {
            $query->where('content', 'like', '%' . $request->search . '%');
        }

        if ($request->has('category') && !empty($request->category)) {
            $query->where('category', $request->category);
        }

        if ($request->has('platform') && !empty($request->platform)) {
            $query->where('platform', $request->platform);
        }

        $comments = $query->orderBy('created_at', 'desc')->get();
        
        $pdf = PDF::loadView('user.comments.pdf', compact('comments'));
        return $pdf->download('comments-' . date('Y-m-d') . '.pdf');
    }

    /**
     * Get statistics for user comments.
     *
     * @return \Illuminate\Http\Response
     */
    public function statistics()
    {
        $user_id = Auth::id();
        
        $total = Comment::where('user_id', $user_id)->count();
        $byCategory = [
            'clean' => Comment::where('user_id', $user_id)->where('category', 'clean')->count(),
            'offensive' => Comment::where('user_id', $user_id)->where('category', 'offensive')->count(),
            'hate' => Comment::where('user_id', $user_id)->where('category', 'hate')->count(),
            'spam' => Comment::where('user_id', $user_id)->where('category', 'spam')->count(),
        ];
        
        $byPlatform = [
            'facebook' => Comment::where('user_id', $user_id)->where('platform', 'facebook')->count(),
            'youtube' => Comment::where('user_id', $user_id)->where('platform', 'youtube')->count(),
            'twitter' => Comment::where('user_id', $user_id)->where('platform', 'twitter')->count(),
            'web' => Comment::where('user_id', $user_id)->where('platform', 'web')->count(),
        ];
        
        $recentComments = Comment::where('user_id', $user_id)
            ->orderBy('created_at', 'desc')
            ->limit(5)
            ->get();
            
        return view('user.comments.statistics', compact('total', 'byCategory', 'byPlatform', 'recentComments'));
    }

    /**
     * Delete a comment.
     *
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function destroy($id)
    {
        $comment = Comment::where('user_id', Auth::id())->findOrFail($id);
        $comment->delete();
        
        return redirect()->route('user.comments.index')
            ->with('success', 'Bình luận đã được xóa thành công.');
    }
} 